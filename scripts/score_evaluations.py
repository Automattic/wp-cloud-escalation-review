#!/usr/bin/env python3
"""Score public evaluation outputs against reviewable fixture expectations."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_evaluations import RESULT_SCHEMA, source_digest

READINESS_LINE = re.compile(r"(?im)^Readiness:\s*(.+?)\s*$")
COPY_PASTE_BLOCK = re.compile(
    r"(?is)###\s+Copy/paste.*?```markdown\s*(.*?)```"
)
MARKDOWN_FENCE = re.compile(r"(?is)```markdown\s*.+?```")
MINIMUM_DRAFT_CHARACTERS = 20


class ScoringError(ValueError):
    pass


def normalize_readiness(value: str) -> str:
    value = value.strip()
    for marker in ("**", "__", "`"):
        if value.startswith(marker) and value.endswith(marker):
            return value[len(marker) : -len(marker)].strip()
    return value


def score_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expectation = case["expect"]
    output = result.get("output", "")
    failures: list[str] = []
    if result.get("status") != "completed":
        failures.append(f"run status was {result.get('status', 'missing')}")

    matches = READINESS_LINE.findall(output)
    actual_readiness = normalize_readiness(matches[0]) if matches else None
    if len(matches) != 1:
        failures.append(
            f"expected exactly one readiness declaration; found {len(matches)}"
        )
    if actual_readiness not in expectation["readiness"]:
        failures.append(
            "readiness was "
            f"{actual_readiness!r}; expected one of {expectation['readiness']!r}"
        )

    copy_paste = COPY_PASTE_BLOCK.search(output)
    draft_body = copy_paste.group(1).strip() if copy_paste else ""
    has_draft = bool(MARKDOWN_FENCE.search(output))
    if has_draft != expectation["draft"]:
        failures.append(
            f"draft presence was {has_draft}; expected {expectation['draft']}"
        )
    if expectation["draft"] and copy_paste is None:
        failures.append("ready result did not contain a Copy/paste markdown draft")
    if (
        expectation["draft"]
        and copy_paste is not None
        and len(draft_body) < MINIMUM_DRAFT_CHARACTERS
    ):
        failures.append("Copy/paste draft was not substantive")

    text_scope = draft_body if expectation["draft"] and copy_paste else output
    lowered = text_scope.casefold()
    for required in expectation["include"]:
        if required.casefold() not in lowered:
            failures.append(f"missing required text: {required!r}")
    for forbidden in expectation["exclude"]:
        if forbidden.casefold() in lowered:
            failures.append(f"contained forbidden text: {forbidden!r}")
    return {
        "id": case["id"],
        "passed": not failures,
        "readiness": actual_readiness,
        "draft": has_draft,
        "failures": failures,
    }


def score_suite(
    fixture: dict[str, Any],
    results: dict[str, Any],
) -> dict[str, Any]:
    if results.get("schema") != RESULT_SCHEMA:
        raise ScoringError("results have an invalid schema")
    if results.get("suite") != fixture["suite"]:
        raise ScoringError("result suite does not match fixture")
    if results.get("source_digest") != source_digest(fixture["cases"]):
        raise ScoringError("results do not match the current fixture inputs")
    result_cases = results.get("cases")
    if not isinstance(result_cases, list):
        raise ScoringError("results cases must be a list")
    result_ids = [
        result.get("id")
        for result in result_cases
        if isinstance(result, dict) and isinstance(result.get("id"), str)
    ]
    expected_ids = [case["id"] for case in fixture["cases"]]
    if len(result_ids) != len(result_cases) or len(set(result_ids)) != len(result_ids):
        raise ScoringError("results contain missing or duplicate case IDs")
    if set(result_ids) != set(expected_ids):
        raise ScoringError("result case IDs do not match the fixture")
    by_id = {result["id"]: result for result in result_cases}
    scores = []
    for case in fixture["cases"]:
        result = by_id.get(
            case["id"],
            {"id": case["id"], "status": "missing", "output": ""},
        )
        scores.append(score_case(case, result))
    passed = sum(score["passed"] for score in scores)
    return {
        "schema": "wp-cloud-escalation-review-scores/v1",
        "suite": fixture["suite"],
        "passed": passed,
        "total": len(scores),
        "success": passed == len(scores),
        "cases": scores,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        results = json.loads(args.results.read_text(encoding="utf-8"))
        score = score_suite(fixture, results)
        rendered = json.dumps(score, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ScoringError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0 if score["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
