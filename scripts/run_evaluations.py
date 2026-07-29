#!/usr/bin/env python3
"""Run input-only evaluation cases against a disposable public skill package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

INPUT_SCHEMA = "wp-cloud-escalation-review-inputs/v1"
RESULT_SCHEMA = "wp-cloud-escalation-review-results/v1"
SKILL_NAME = "wp-cloud-escalation-review"
RUNTIME_MANIFEST = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/api-and-managed-operations.md",
    "references/challenge.md",
    "references/documentation-routing.md",
    "references/domains-network-and-protocol-access.md",
    "references/guided-workflow.md",
    "references/http-and-automation.md",
    "references/performance-and-capacity.md",
    "references/security-handoffs.md",
    "references/style-guide.md",
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[ _-]?key|auth(?:entication)?[ _-]?token|password|secret)"
    r"(\s*[:=]\s*)([^\s,;]+)"
)
AUTHORIZATION_LINE = re.compile(
    r"(?im)^(\s*(?:proxy-)?authorization\s*:\s*).*$"
)


class EvaluationError(RuntimeError):
    pass


def runtime_files(package: Path) -> set[str]:
    return {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def source_digest(cases: list[dict[str, Any]]) -> str:
    inputs = [
        {
            "id": case["id"],
            "entry": case["entry"],
            "input": case["input"],
        }
        for case in cases
    ]
    payload = json.dumps(
        inputs,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_runtime_manifest(package: Path) -> None:
    if not package.is_dir():
        raise EvaluationError(f"skill package does not exist: {package}")
    actual = runtime_files(package)
    expected = set(RUNTIME_MANIFEST)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise EvaluationError(
            f"runtime manifest mismatch; missing={missing}, extra={extra}"
        )
    symlinks = [
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_symlink()
    ]
    if symlinks:
        raise EvaluationError(f"runtime package contains symlinks: {sorted(symlinks)}")


def stage_runtime(package: Path, workspace: Path) -> Path:
    verify_runtime_manifest(package)
    staged = workspace / ".agents" / "skills" / SKILL_NAME
    for relative in RUNTIME_MANIFEST:
        source = package / relative
        target = staged / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return staged


def validate_projection(projection: Any) -> dict[str, Any]:
    if not isinstance(projection, dict):
        raise EvaluationError("input projection must be an object")
    if set(projection) != {"schema", "suite", "source_digest", "cases"}:
        raise EvaluationError("input projection has unexpected fields")
    if projection.get("schema") != INPUT_SCHEMA:
        raise EvaluationError("input projection has an invalid schema")
    if not re.fullmatch(r"[0-9a-f]{64}", str(projection.get("source_digest", ""))):
        raise EvaluationError("input projection has an invalid source digest")
    cases = projection.get("cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 8:
        raise EvaluationError("input projection must contain one to eight cases")
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "entry", "input"}:
            raise EvaluationError("each projected case must contain id, entry, input")
        if case["entry"] not in {"Direct", "Guided"}:
            raise EvaluationError("projected case entry must be Direct or Guided")
        if not all(isinstance(case[key], str) and case[key] for key in case):
            raise EvaluationError("projected case values must be non-empty strings")
    return projection


def build_prompt(case: dict[str, str]) -> str:
    return (
        f"${SKILL_NAME}\n"
        "Use only the staged public skill and its linked references. "
        "Follow it exactly. Do not inspect paths outside this workspace. "
        f"Use the {case['entry']} entry path.\n\n"
        "Material to review:\n"
        f"{case['input']}"
    )


def sanitize_text(text: str) -> str:
    text = AUTHORIZATION_LINE.sub(r"\1<redacted authentication material>", text)
    return SECRET_ASSIGNMENT.sub(
        lambda match: (
            f"{match.group(1)}{match.group(2)}<redacted authentication material>"
        ),
        text,
    )


def run_case(
    package: Path,
    case: dict[str, str],
    *,
    model: str | None,
    effort: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    if not 1 <= timeout_seconds <= 900:
        raise EvaluationError("timeout must be between one and nine hundred seconds")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="wp-cloud-review-eval-") as directory:
        temp_root = Path(directory)
        workspace = temp_root / "workspace"
        workspace.mkdir()
        stage_runtime(package, workspace)
        final_message = temp_root / "final.txt"
        command = [
            "codex",
            "exec",
            "-",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--cd",
            str(workspace),
            "--output-last-message",
            str(final_message),
            "--config",
            f'model_reasoning_effort="{effort}"',
        ]
        if model:
            command.extend(("--model", model))
        try:
            completed = subprocess.run(
                command,
                input=build_prompt(case),
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
        except FileNotFoundError as error:
            raise EvaluationError("Codex CLI is not installed or not on PATH") from error
        except subprocess.TimeoutExpired:
            return {
                "id": case["id"],
                "status": "timeout",
                "output": "",
                "diagnostic": "model run exceeded the configured timeout",
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        output = final_message.read_text(encoding="utf-8") if final_message.exists() else ""
        diagnostic = sanitize_text(completed.stderr.strip())
        return {
            "id": case["id"],
            "status": "completed" if completed.returncode == 0 and output else "error",
            "output": sanitize_text(output),
            "diagnostic": diagnostic,
            "duration_seconds": round(time.monotonic() - started, 3),
        }


def run_projection(
    package: Path,
    projection: dict[str, Any],
    *,
    model: str | None = None,
    effort: str = "medium",
    timeout_seconds: float = 300,
) -> dict[str, Any]:
    projection = validate_projection(projection)
    verify_runtime_manifest(package)
    return {
        "schema": RESULT_SCHEMA,
        "suite": projection["suite"],
        "source_digest": projection["source_digest"],
        "model": model or "configured-default",
        "effort": effort,
        "cases": [
            run_case(
                package,
                case,
                model=model,
                effort=effort,
                timeout_seconds=timeout_seconds,
            )
            for case in projection["cases"]
        ],
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model")
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    parser.add_argument("--timeout-seconds", type=float, default=300)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        projection = validate_projection(
            json.loads(args.cases.read_text(encoding="utf-8"))
        )
        result = run_projection(
            args.package,
            projection,
            model=args.model,
            effort=args.effort,
            timeout_seconds=args.timeout_seconds,
        )
        write_json(args.output, result)
    except (OSError, json.JSONDecodeError, EvaluationError) as error:
        print(f"error: {sanitize_text(str(error))}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
