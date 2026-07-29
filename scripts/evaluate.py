#!/usr/bin/env python3
"""Project, run, and score a public WP Cloud Escalation Review eval suite."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_evaluations as runner
import score_evaluations as scorer
import validate


def render_input(text: str, *, eval_date: str | None = None) -> str:
    current_date = eval_date or datetime.now(timezone.utc).date().isoformat()
    return text.replace("<eval-date>", current_date)


def project_cases(suite: str, cases: Iterable[dict[str, Any]]) -> dict[str, Any]:
    case_list = list(cases)
    return {
        "schema": runner.INPUT_SCHEMA,
        "suite": suite,
        "source_digest": runner.source_digest(case_list),
        "cases": [
            {
                "id": case["id"],
                "entry": case["entry"],
                "input": render_input(case["input"]),
            }
            for case in case_list
        ],
    }


def project_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    return project_cases(fixture["suite"], fixture["cases"])


def chunks(cases: list[dict[str, Any]], size: int = 8):
    for index in range(0, len(cases), size):
        yield cases[index : index + size]


def run_suite(
    fixture: dict[str, Any],
    *,
    provider: str,
    model: str | None,
    effort: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    package = ROOT / "skills" / runner.SKILL_NAME
    combined: dict[str, Any] = {
        "schema": runner.RESULT_SCHEMA,
        "suite": fixture["suite"],
        "source_digest": runner.source_digest(fixture["cases"]),
        "provider": provider,
        "adapter_version": runner.ADAPTER_VERSION,
        "model": model or "configured-default",
        "effort": effort,
        "cases": [],
    }
    for batch in chunks(fixture["cases"]):
        projection = project_cases(fixture["suite"], batch)
        result = runner.run_projection(
            package,
            projection,
            provider=provider,
            model=model,
            effort=effort,
            timeout_seconds=timeout_seconds,
        )
        combined["cases"].extend(result["cases"])
    return combined


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("development", "regression"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--provider", choices=runner.PROVIDERS, default="codex")
    parser.add_argument("--model")
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    parser.add_argument("--timeout-seconds", type=float, default=300)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors = validate.validate_repository(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    fixture_path = ROOT / "evals" / f"{args.suite}.json"
    try:
        fixture = validate.load_fixture(fixture_path)
        projection = project_fixture(fixture)
        if args.dry_run:
            print(json.dumps(projection, indent=2, ensure_ascii=False))
            return 0

        results = run_suite(
            fixture,
            provider=args.provider,
            model=args.model,
            effort=args.effort,
            timeout_seconds=args.timeout_seconds,
        )
        scores = scorer.score_suite(fixture, results)
        output_dir = ROOT / "evals" / "results"
        runner.write_json(
            output_dir / f"{args.suite}-{args.provider}-latest.json",
            results,
        )
        runner.write_json(
            output_dir / f"{args.suite}-{args.provider}-scores-latest.json",
            scores,
        )
    except (OSError, validate.ValidationError, runner.EvaluationError) as error:
        print(f"error: {runner.sanitize_text(str(error))}", file=sys.stderr)
        return 1

    print(
        f"{args.suite} ({args.provider}): "
        f"{scores['passed']}/{scores['total']} cases passed; "
        f"results: {output_dir}"
    )
    for case in scores["cases"]:
        if not case["passed"]:
            print(f"- {case['id']}: {'; '.join(case['failures'])}")
    return 0 if scores["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
