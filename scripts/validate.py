#!/usr/bin/env python3
"""Validate the public package, evaluation fixtures, and repository safety."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_plugin as plugin_package
from run_evaluations import RUNTIME_MANIFEST, SKILL_NAME, runtime_files

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SCHEMA = "wp-cloud-escalation-review-evals/v3"
OUTCOMES = {
    "ready",
    "ready_with_caveat",
    "needs_reporter_check",
    "needs_existing_evidence",
    "split",
    "alternate_owner",
    "no_post",
}
CONDITIONAL_REFERENCES = {
    path for path in RUNTIME_MANIFEST if path.startswith("references/")
}
PUBLIC_TEXT_SUFFIXES = {".md", ".json", ".py", ".yaml", ".yml", ".txt"}
FILELIKE_SUFFIXES = {
    "json", "md", "py", "toml", "txt", "yaml", "yml",
}
ALLOWED_PUBLIC_DOMAINS = {"code.claude.com", "github.com", "wp.cloud"}
DOMAIN_SHAPE = re.compile(
    r"(?<![\w./-])(?:[a-z0-9-]+\.)+"
    r"[a-z]{2,63}(?![\w-])",
    re.IGNORECASE,
)
EMAIL_SHAPE = re.compile(
    r"(?<![\w@])[a-z0-9._%+-]+@(?:[a-z0-9-]+\.)+[a-z]{2,63}(?![\w-])",
    re.IGNORECASE,
)
URL_HOST_SHAPE = re.compile(
    r"https?://((?:[a-z0-9-]+\.)+[a-z]{2,63})(?=[:/?#]|\Z)",
    re.IGNORECASE,
)
QUOTED_DOMAIN_SHAPE = re.compile(
    r"""[\"']((?:[a-z0-9-]+\.)+[a-z]{2,63})[\"']""",
    re.IGNORECASE,
)
IPV4_SHAPE = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")
IPV6_SHAPE = re.compile(
    r"(?<![0-9a-f:])(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{0,4}(?![0-9a-f:])",
    re.IGNORECASE,
)
UUID_SHAPE = re.compile(
    r"(?<![0-9a-f])[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
    r"(?![0-9a-f])",
    re.IGNORECASE,
)
LONG_NUMBER = re.compile(r"(?<!\d)\d{9,}(?!\d)")
LONG_HASH = re.compile(r"(?<![0-9a-f])[0-9a-f]{24,}(?![0-9a-f])", re.IGNORECASE)
PINNED_GITHUB_ACTION = re.compile(
    r"^\s*uses:\s*[a-z0-9_.-]+/[a-z0-9_.-]+@[0-9a-f]{40}\s*(?:#.*)?$",
    re.IGNORECASE,
)
USERNAME_SHAPE = re.compile(r"(?<![\w@])@[a-z0-9][a-z0-9_-]{2,}", re.IGNORECASE)
IDENTIFIER_VALUE = re.compile(
    r"\b(?:site|account|job|request)[ _-]+(?:id|identifier)\s*[:=]\s*"
    r"[a-z0-9][a-z0-9_-]{4,}",
    re.IGNORECASE,
)
AUTHORIZATION_HEADER = re.compile(
    r"(?im)^\s*(?:proxy-)?authorization\s*:\s*\S+"
)
COOKIE_HEADER = re.compile(r"(?im)^\s*(?:set-)?cookie\s*:\s*\S+")
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api[ _-]?(?:key|token)|access[ _-]?token|password|secret)"
    r"\s*[:=]\s*[\"']?(?!<(?:redacted|removed|placeholder)[^>]*>)\S+"
)
PRIVATE_KEY_BOUNDARY = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
GITHUB_EXPRESSION = re.compile(r"\$\{\{.*?\}\}", re.DOTALL)


class ValidationError(ValueError):
    pass


def validate_manifest(package: Path) -> list[str]:
    actual = runtime_files(package) if package.is_dir() else set()
    expected = set(RUNTIME_MANIFEST)
    errors = [f"missing skill package: {package}"] if not package.is_dir() else []
    for path in sorted(expected - actual):
        errors.append(f"missing runtime file: {path}")
    for path in sorted(actual - expected):
        errors.append(f"unexpected runtime file: {path}")
    return errors


def validate_skill(package: Path) -> list[str]:
    errors = validate_manifest(package)
    skill_path = package / "SKILL.md"
    agent_path = package / "agents" / "openai.yaml"
    if not skill_path.is_file() or not agent_path.is_file():
        return errors

    skill = skill_path.read_text(encoding="utf-8")
    agent = agent_path.read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
    if f"name: {SKILL_NAME}\n" not in skill:
        errors.append(f"SKILL.md name must be {SKILL_NAME}")
    if f"$" + SKILL_NAME not in agent:
        errors.append("openai.yaml default prompt must invoke the public skill name")
    if "WP Cloud Atomic API" not in skill:
        errors.append("SKILL.md must use the public WP Cloud Atomic API term")
    if "atomic-api-and-managed-operations.md" in skill:
        errors.append("SKILL.md contains the retired Atomic API reference filename")

    errors.extend(relative_link_errors(package))
    return errors


def relative_link_errors(package: Path) -> list[str]:
    errors: list[str] = []
    package_root = package.resolve()
    for source in sorted(package.rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target:
                continue
            resolved = (source.parent / target).resolve()
            try:
                resolved.relative_to(package_root)
            except ValueError:
                errors.append(
                    f"link escapes runtime package: "
                    f"{source.relative_to(package)} -> {raw_target}"
                )
                continue
            if not resolved.is_file():
                errors.append(
                    f"broken runtime link: "
                    f"{source.relative_to(package)} -> {raw_target}"
                )
    return errors


def _expectation_errors(expect: Any, label: str) -> list[str]:
    if not isinstance(expect, dict):
        return [f"{label}.expect must be an object"]
    errors: list[str] = []
    if not {"outcome", "draft", "messages", "references"} <= set(expect):
        errors.append(
            f"{label}.expect must contain outcome, draft, messages, and references"
        )
    unexpected = set(expect) - {
        "outcome",
        "draft",
        "messages",
        "references",
        "max_narrative_words",
    }
    if unexpected:
        errors.append(f"{label}.expect contains unexpected fields: {sorted(unexpected)}")
    if expect.get("outcome") not in OUTCOMES:
        errors.append(f"{label}.expect.outcome contains an invalid value")
    if expect.get("draft") not in {"required", "forbidden", "optional"}:
        errors.append(
            f"{label}.expect.draft must be required, forbidden, or optional"
        )

    messages = expect.get("messages")
    if not isinstance(messages, dict) or set(messages) != {
        "include",
        "exclude",
        "max_question_turns",
    }:
        errors.append(
            f"{label}.expect.messages must contain include, exclude, and max_question_turns"
        )
        messages = {}
    for key in ("include", "exclude"):
        values = messages.get(key)
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value.strip() for value in values)
        ):
            errors.append(f"{label}.expect.messages.{key} must be a string list")
    max_question_turns = messages.get("max_question_turns")
    if not isinstance(max_question_turns, int) or not 0 <= max_question_turns <= 3:
        errors.append(
            f"{label}.expect.messages.max_question_turns must be between zero and three"
        )

    max_narrative_words = expect.get("max_narrative_words")
    if max_narrative_words is not None and (
        not isinstance(max_narrative_words, int)
        or not 40 <= max_narrative_words <= 1200
    ):
        errors.append(
            f"{label}.expect.max_narrative_words must be null or 40 to 1200"
        )

    references = expect.get("references")
    if not isinstance(references, dict) or set(references) != {
        "required",
        "forbidden",
    }:
        errors.append(
            f"{label}.expect.references must contain required and forbidden"
        )
        references = {}
    reference_sets: dict[str, set[str]] = {}
    for key in ("required", "forbidden"):
        values = references.get(key)
        if (
            not isinstance(values, list)
            or any(value not in CONDITIONAL_REFERENCES for value in values)
        ):
            errors.append(
                f"{label}.expect.references.{key} contains an invalid reference"
            )
            reference_sets[key] = set()
        else:
            reference_sets[key] = set(values)
    overlap = reference_sets.get("required", set()) & reference_sets.get(
        "forbidden", set()
    )
    if overlap:
        errors.append(
            f"{label}.expect.references requires and forbids {sorted(overlap)}"
        )
    return errors


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"{path}: {error}") from error
    errors: list[str] = []
    if not isinstance(fixture, dict):
        raise ValidationError(f"{path}: fixture must be an object")
    if fixture.get("schema") != FIXTURE_SCHEMA:
        errors.append(f"{path}: invalid schema")
    if fixture.get("suite") not in {"development", "regression"}:
        errors.append(f"{path}: invalid suite")
    if not isinstance(fixture.get("description"), str):
        errors.append(f"{path}: description must be a string")
    cases = fixture.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{path}: cases must be a non-empty list")
        cases = []
    ids: set[str] = set()
    for index, case in enumerate(cases):
        label = f"{path}: case {index + 1}"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(case) != {"id", "input", "expect"}:
            errors.append(f"{label} must contain id, input, and expect")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9-]+", case_id):
            errors.append(f"{label}.id must be a kebab-case label")
        elif case_id in ids:
            errors.append(f"{label}.id is duplicated")
        else:
            ids.add(case_id)
        if not isinstance(case.get("input"), str) or not case["input"].strip():
            errors.append(f"{label}.input must be non-empty")
        errors.extend(_expectation_errors(case.get("expect"), label))
    if errors:
        raise ValidationError("\n".join(errors))
    return fixture


def _private_markers() -> tuple[str, ...]:
    return (
        "github." + "a8c." + "com",
        "wordpress." + "com/forums/internal",
        "slack." + "com/archives",
        "automattic." + "p2",
    )


def _scan_text(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for marker in _private_markers():
        if marker in lowered:
            errors.append(f"{path}: private/internal marker: {marker}")
    if path.name != "LICENSE":
        domain_source = GITHUB_EXPRESSION.sub("", text)
        domain_values = [
            match.group(1) for match in URL_HOST_SHAPE.finditer(domain_source)
        ]
        domain_values.extend(
            match.group(1) for match in QUOTED_DOMAIN_SHAPE.finditer(domain_source)
        )
        if path.suffix.lower() != ".py":
            domain_values.extend(
                match.group(0) for match in DOMAIN_SHAPE.finditer(domain_source)
            )
        for candidate in domain_values:
            value = candidate.lower()
            suffix = value.rsplit(".", 1)[-1]
            if value in ALLOWED_PUBLIC_DOMAINS or suffix in FILELIKE_SUFFIXES:
                continue
            errors.append(f"{path}: real-looking domain: {value}")
    patterns = (
        ("IPv4 address", IPV4_SHAPE),
        ("IPv6 address", IPV6_SHAPE),
        ("UUID", UUID_SHAPE),
        ("long numeric identifier", LONG_NUMBER),
        ("username", USERNAME_SHAPE),
        ("assigned service identifier", IDENTIFIER_VALUE),
        ("email address", EMAIL_SHAPE),
        ("authorization header", AUTHORIZATION_HEADER),
        ("cookie header", COOKIE_HEADER),
        ("credential assignment", CREDENTIAL_ASSIGNMENT),
        ("private-key boundary", PRIVATE_KEY_BOUNDARY),
    )
    for label, pattern in patterns:
        if pattern.search(text):
            errors.append(f"{path}: real-looking {label}")
    hash_text = "\n".join(
        line for line in text.splitlines() if not PINNED_GITHUB_ACTION.fullmatch(line)
    )
    if LONG_HASH.search(hash_text):
        errors.append(f"{path}: real-looking long hash")
    return errors


def scan_public_files(root: Path) -> list[str]:
    errors: list[str] = []
    resolved_root = root.resolve()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            if not path.exists():
                errors.append(f"{relative}: dangling symlink is not allowed")
                continue
            try:
                path.resolve().relative_to(resolved_root)
            except ValueError:
                errors.append(f"{relative}: external symlink is not allowed")
            continue
        if not path.is_file():
            continue
        if any(part in {".git", "__pycache__", "results"} for part in relative.parts):
            continue
        if path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES and path.name != "LICENSE":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        errors.extend(_scan_text(relative, text))
    return errors


def tracked_result_errors(root: Path) -> list[str]:
    if not (root / ".git").exists():
        return []
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", "evals/results"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        return ["could not inspect tracked evaluation results"]
    return [
        f"tracked generated evaluation result: {path}"
        for path in completed.stdout.splitlines()
        if path
    ]


def validate_repository(root: Path = ROOT) -> list[str]:
    errors = validate_skill(root / "skills" / SKILL_NAME)
    try:
        plugin_package.validate_source()
    except plugin_package.PluginBuildError as error:
        errors.append(f"invalid plugin package: {error}")
    fixtures: list[dict[str, Any]] = []
    for suite in ("development", "regression"):
        path = root / "evals" / f"{suite}.json"
        try:
            fixture = load_fixture(path)
            if fixture["suite"] != suite:
                errors.append(f"{path}: suite does not match filename")
            fixtures.append(fixture)
        except ValidationError as error:
            errors.extend(str(error).splitlines())
    if len(fixtures) == 2:
        development_ids = {case["id"] for case in fixtures[0]["cases"]}
        regression_ids = {case["id"] for case in fixtures[1]["cases"]}
        overlap = development_ids & regression_ids
        if overlap:
            errors.append(f"case IDs overlap between suites: {sorted(overlap)}")
        if len(fixtures[0]["cases"]) > 8:
            errors.append("development suite must have at most eight cases")
        if len(fixtures[1]["cases"]) <= len(fixtures[0]["cases"]):
            errors.append("regression suite must be broader than development")
    errors.extend(scan_public_files(root))
    errors.extend(tracked_result_errors(root))
    return errors


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    development = load_fixture(ROOT / "evals" / "development.json")
    regression = load_fixture(ROOT / "evals" / "regression.json")
    print(
        "Valid public package: "
        f"{len(RUNTIME_MANIFEST)} runtime files, "
        f"{len(development['cases'])} development cases, "
        f"{len(regression['cases'])} regression cases."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
