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

INPUT_SCHEMA = "wp-cloud-escalation-review-inputs/v2"
RESULT_SCHEMA = "wp-cloud-escalation-review-results/v3"
ADAPTER_VERSION = "wp-cloud-escalation-review-adapter/v2"
SKILL_NAME = "wp-cloud-escalation-review"
PROVIDERS = ("codex", "claude")
PROVIDER_SKILL_ROOTS = {
    "codex": Path(".agents/skills"),
    "claude": Path(".claude/skills"),
}
CODEX_ITEM_COMPLETED = "item" + ".completed"
RUNTIME_MANIFEST = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/api-and-managed-operations.md",
    "references/challenge.md",
    "references/documentation-routing.md",
    "references/domains-network-and-protocol-access.md",
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


def stage_runtime(
    package: Path,
    workspace: Path,
    *,
    provider: str = "codex",
) -> Path:
    verify_runtime_manifest(package)
    try:
        skill_root = PROVIDER_SKILL_ROOTS[provider]
    except KeyError as error:
        raise EvaluationError(f"unsupported evaluation provider: {provider}") from error
    staged = workspace / skill_root / SKILL_NAME
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
        if not isinstance(case, dict) or set(case) != {"id", "input"}:
            raise EvaluationError("each projected case must contain id and input")
        if not all(isinstance(case[key], str) and case[key] for key in case):
            raise EvaluationError("projected case values must be non-empty strings")
    return projection


def build_prompt(case: dict[str, str], *, provider: str = "codex") -> str:
    if provider not in PROVIDERS:
        raise EvaluationError(f"unsupported evaluation provider: {provider}")
    invocation = (
        f"${SKILL_NAME}"
        if provider == "codex"
        else f"/{SKILL_NAME}"
    )
    return (
        f"{invocation}\n"
        "Use only the staged public skill and its linked references. "
        "Follow it exactly. Do not inspect paths outside this workspace. "
        "Return only the review response: no progress updates, tool narration, "
        "or announcements about the skill or references.\n\n"
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


def _reference_paths(value: Any) -> list[str]:
    serialized = json.dumps(value, ensure_ascii=False)
    return [
        relative
        for relative in RUNTIME_MANIFEST
        if relative.startswith("references/") and relative in serialized
    ]


def _append_message(messages: list[dict[str, str]], text: Any) -> None:
    if not isinstance(text, str) or not text.strip():
        return
    cleaned = sanitize_text(text.strip())
    if messages and messages[-1]["text"] == cleaned:
        return
    messages.append({"phase": "commentary", "text": cleaned})


def normalize_event_stream(
    provider: str,
    event_stream: str,
    *,
    final_output: str = "",
) -> dict[str, Any]:
    """Normalize provider events into the public evaluation result contract."""
    if provider not in PROVIDERS:
        raise EvaluationError(f"unsupported evaluation provider: {provider}")
    messages: list[dict[str, str]] = []
    references: list[str] = []
    provider_final = ""
    for line in event_stream.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if provider == "codex":
            item = event.get("item")
            if event.get("type") == CODEX_ITEM_COMPLETED and isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "agent_message":
                    _append_message(messages, item.get("text"))
                elif item_type == "command_execution":
                    for reference in _reference_paths(item.get("command")):
                        if reference not in references:
                            references.append(reference)
                elif item_type == "mcp_tool_call":
                    for reference in _reference_paths(item.get("arguments")):
                        if reference not in references:
                            references.append(reference)
        else:
            if event.get("type") == "assistant":
                message = event.get("message")
                content = message.get("content") if isinstance(message, dict) else None
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "text":
                            _append_message(messages, block.get("text"))
                        elif (
                            block.get("type") == "tool_use"
                            and block.get("name") == "Read"
                        ):
                            for reference in _reference_paths(block.get("input")):
                                if reference not in references:
                                    references.append(reference)
            elif event.get("type") == "result":
                result = event.get("result")
                if isinstance(result, str) and result.strip():
                    provider_final = result.strip()

    output = sanitize_text((final_output or provider_final).strip())
    if output:
        if not messages or messages[-1]["text"] != output:
            messages.append({"phase": "final", "text": output})
        else:
            messages[-1]["phase"] = "final"
    return {
        "output": output,
        "messages": messages,
        "references": references,
    }


def run_case(
    package: Path,
    case: dict[str, str],
    *,
    provider: str,
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
        stage_runtime(package, workspace, provider=provider)
        final_message = temp_root / "final.txt"
        if provider == "codex":
            command = [
                "codex",
                "exec",
                "-",
                "--json",
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
        elif provider == "claude":
            command = [
                "claude",
                "-p",
                "--output-format",
                "stream-json",
                "--verbose",
                "--no-session-persistence",
                "--permission-mode",
                "dontAsk",
                "--tools",
                "Read,Glob,Grep,Skill",
                "--setting-sources",
                "project",
                "--effort",
                effort,
            ]
        else:
            raise EvaluationError(f"unsupported evaluation provider: {provider}")
        if model:
            command.extend(("--model", model))
        try:
            completed = subprocess.run(
                command,
                input=build_prompt(case, provider=provider),
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
                cwd=workspace,
            )
        except FileNotFoundError as error:
            raise EvaluationError(
                f"{provider.title()} CLI is not installed or not on PATH"
            ) from error
        except subprocess.TimeoutExpired:
            return {
                "id": case["id"],
                "provider": provider,
                "status": "timeout",
                "output": "",
                "messages": [],
                "references": [],
                "diagnostic": "model run exceeded the configured timeout",
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        final_output = (
            final_message.read_text(encoding="utf-8")
            if provider == "codex" and final_message.exists()
            else ""
        )
        normalized = normalize_event_stream(
            provider,
            completed.stdout,
            final_output=final_output,
        )
        diagnostic = sanitize_text(completed.stderr.strip())
        return {
            "id": case["id"],
            "provider": provider,
            "status": (
                "completed"
                if completed.returncode == 0 and normalized["output"]
                else "error"
            ),
            **normalized,
            "diagnostic": diagnostic,
            "duration_seconds": round(time.monotonic() - started, 3),
        }


def run_projection(
    package: Path,
    projection: dict[str, Any],
    *,
    provider: str = "codex",
    model: str | None = None,
    effort: str = "medium",
    timeout_seconds: float = 300,
) -> dict[str, Any]:
    projection = validate_projection(projection)
    verify_runtime_manifest(package)
    if provider not in PROVIDERS:
        raise EvaluationError(f"unsupported evaluation provider: {provider}")
    return {
        "schema": RESULT_SCHEMA,
        "suite": projection["suite"],
        "source_digest": projection["source_digest"],
        "provider": provider,
        "adapter_version": ADAPTER_VERSION,
        "model": model or "configured-default",
        "effort": effort,
        "cases": [
            run_case(
                package,
                case,
                provider=provider,
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
    parser.add_argument("--provider", choices=PROVIDERS, default="codex")
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
            provider=args.provider,
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
