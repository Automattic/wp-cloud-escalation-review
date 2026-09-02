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

from run_evaluations import ADAPTER_VERSION, PROVIDERS, RESULT_SCHEMA, source_digest

READINESS_LINE = re.compile(r"(?im)^Readiness:\s*(.+?)\s*$")
COPY_PASTE_BLOCK = re.compile(
    r"(?is)###\s+Copy/paste.*?```markdown\s*(.*?)```"
)
MARKDOWN_FENCE = re.compile(r"(?is)```markdown\s*.+?```")
QUESTION = re.compile(r"(?m)([^?\n]{2,}\?)")
WORD = re.compile(r"\b[\w’-]+\b")
MINIMUM_DRAFT_CHARACTERS = 20
READINESS_OUTCOMES = {
    "Ready": "ready",
    "Ready with caveats": "ready_with_caveat",
    "Reporter action required": "needs_reporter_check",
    "Resolved during validation": "no_post",
    "Belongs elsewhere": "alternate_owner",
    "Needs evidence": "needs_existing_evidence",
    "Split required": "split",
}
WORKFLOW_JARGON = (
    "active causal investigation",
    "smallest reporter-owned evidence",
    "bounded incident window",
    "coherent causal hypothesis",
    "clears the earlier attribution blocker",
    "http-routing review and challenge pass",
    "reported platform behavior",
    "no further wp cloud decision appears outstanding",
    "guided challenge",
    "challenge reference",
    "guided entry path",
    "guided path",
    "direct entry path",
    "direct path",
    "i’m using the staged",
    "i'm using the staged",
    "request class",
    "receiver-only",
    "receiver-side",
    "reporter-visible evidence",
)
INTERNAL_LABEL = re.compile(r"(?im)^(?:Blocking|Challenged|Checked):")


class ScoringError(ValueError):
    pass


def normalize_readiness(value: str) -> str:
    value = value.strip()
    for marker in ("**", "__", "`"):
        if value.startswith(marker) and value.endswith(marker):
            return value[len(marker) : -len(marker)].strip()
    return value


def classify_outcome(output: str, *, has_draft: bool) -> str | None:
    matches = READINESS_LINE.findall(output)
    if len(matches) == 1:
        readiness = normalize_readiness(matches[0])
        mapped = READINESS_OUTCOMES.get(readiness)
        if mapped:
            return mapped
    lowered = output.casefold()
    if "split" in lowered or "separate issue" in lowered:
        return "split"
    if (
        "belongs in the public documentation issue tracker" in lowered
        or "public wp cloud documentation issue tracker" in lowered
        or "route this through the public wp cloud documentation issue tracker"
        in lowered
        or (
            "belongs in" in lowered
            and "rather than" in lowered
            and "platform escalation" in lowered
        )
    ):
        return "alternate_owner"
    if has_draft:
        if (
            "caveat" in lowered
            or "limitation" in lowered
            or "outside the reporter’s access" in lowered
            or "outside the reporter's access" in lowered
            or "do not have access" in lowered
            or "cannot access the platform logs" in lowered
            or "cannot access more detailed platform data" in lowered
            or "platform data the reporter cannot access" in lowered
            or "no more detailed platform data" in lowered
            or "platform logs are required" in lowered
            or "only wp cloud can complete" in lowered
            or "available only to wp cloud" in lowered
            or "unavailable to the reporter" in lowered
            or "pending receiver telemetry" in lowered
            or "could not identify where the response originated" in lowered
            or "remain unverified" in lowered
            or "remains unconfirmed" in lowered
            or "remains unknown" in lowered
            or "cause remains unknown" in lowered
            or "not reproduced" in lowered
            or "did not reproduce" in lowered
            or "without reproducing" in lowered
            or "does not establish why" in lowered
            or "cannot identify the producing layer" in lowered
            or "cannot establish what terminated" in lowered
            or "does not identify which layer" in lowered
            or "does not establish where the response was generated" in lowered
            or "cannot establish the platform layer" in lowered
            or "do not establish the failing platform layer" in lowered
            or "does not establish which platform layer" in lowered
            or "exhausted the dashboards and logs available" in lowered
        ):
            return "ready_with_caveat"
        return "ready"
    if (
        "not ready" in lowered
        or "before escalating" in lowered
        or "before sending" in lowered
        or "before deciding whether to involve wp cloud" in lowered
    ):
        return "needs_reporter_check"
    if any(
        phrase in lowered
        for phrase in (
            "belongs with",
            "belongs in",
            "belongs elsewhere",
            "not as a platform escalation",
            "another owner",
            "reporter-controlled",
            "controlled by the reporter",
            "reporter controls",
            "reporter owns",
            "reporter should",
        )
    ):
        return "alternate_owner"
    if (
        "existing" in lowered
        or "already-known" in lowered
        or "exact blocked request" in lowered
        or ("utc" in lowered and "locate the event" in lowered)
    ) and any(
        phrase in lowered
        for phrase in (
            "share the",
            "provide the",
            "send the",
            "attach the",
            "needs the",
            "please add",
            "add the",
            "add that",
            "existing artifact",
        )
    ):
        return "needs_existing_evidence"
    if "yet" in lowered or "?" in output or any(
        phrase in lowered
        for phrase in (
            "please check",
            "please confirm",
            "confirm whether",
            "please provide",
            "can you check",
            "need to check",
            "please verify",
            "please retest",
            "check the application",
            "check the dashboards",
            "trace the affected request",
            "report how many",
            "retry once",
            "retry with",
            "retry it with",
            "retry the operation",
            "retry one representative",
            "correct the request",
            "before escalating",
            "before resubmitting",
            "escalate only if",
            "cannot proceed while",
            "revoke or rotate",
            "rotate it",
            "rotate the exposed",
            "not ready to escalate",
            "do not share the draft until",
            "blocked until",
        )
    ):
        return "needs_reporter_check"
    if (
        (
            "do not escalate" in lowered
            or "do not support an escalation" in lowered
        )
        and (
            "nothing left for wp cloud" in lowered
            or "no remaining platform-owned action" in lowered
            or "no remaining wp cloud action" in lowered
            or "no wp cloud action remains" in lowered
            or "wp cloud has no remaining action" in lowered
            or "warnings show no functional impact" in lowered
            or "no unresolved action for wp cloud" in lowered
            or "no platform work remains" in lowered
            or "no wp cloud action is needed" in lowered
            or "wp cloud has nothing to investigate or decide" in lowered
            or (
                "remaining question for wp cloud" in lowered
                and "no demonstrated" in lowered
            )
        )
    ):
        return "no_post"
    if (
        "no current impact" in lowered
        and "remaining question for wp cloud" in lowered
    ):
        return "no_post"
    if any(
        phrase in lowered
        for phrase in (
            "don’t post",
            "don't post",
            "do not post",
            "no escalation is needed",
            "no wp cloud escalation is needed",
            "does not need a wp cloud escalation",
            "no need to post",
            "close the wp cloud escalation",
            "close this escalation",
            "close this without escalating",
            "resolved during validation",
            "no escalation draft is needed",
            "the review can stop here",
            "close the review unless",
            "stop the escalation",
            "without a wp cloud escalation",
            "without escalating to wp cloud",
            "the issue is resolved",
            "wp cloud has nothing left to investigate or change",
            "should not be escalated",
        )
    ):
        return "no_post"
    return None


def interaction_messages(result: dict[str, Any]) -> list[dict[str, str]]:
    raw = result.get("messages")
    messages = [
        {"phase": message.get("phase", "commentary"), "text": message["text"]}
        for message in raw
        if isinstance(message, dict)
        and isinstance(message.get("text"), str)
        and message["text"].strip()
    ] if isinstance(raw, list) else []
    output = result.get("output", "")
    if isinstance(output, str) and output.strip() and (
        not messages or messages[-1]["text"].strip() != output.strip()
    ):
        messages.append({"phase": "final", "text": output.strip()})
    return messages


def question_texts(messages: list[dict[str, str]]) -> list[str]:
    questions: list[str] = []
    for message in messages:
        for match in QUESTION.findall(message["text"]):
            normalized = " ".join(match.casefold().split())
            if normalized:
                questions.append(normalized)
    return questions


def narrative_word_count(output: str) -> int:
    narrative: list[str] = []
    in_fence = False
    include_fence = False
    for line in output.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if in_fence:
                in_fence = False
                include_fence = False
            else:
                language = stripped[3:].strip().casefold()
                in_fence = True
                include_fence = language in {"markdown", "md"}
            continue
        if not in_fence or include_fence:
            narrative.append(line)
    return len(WORD.findall("\n".join(narrative)))


def score_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expectation = case["expect"]
    output = result.get("output", "")
    failures: list[str] = []
    if result.get("status") != "completed":
        failures.append(f"run status was {result.get('status', 'missing')}")

    matches = READINESS_LINE.findall(output)
    actual_readiness = normalize_readiness(matches[0]) if len(matches) == 1 else None
    if len(matches) > 1:
        failures.append(f"expected at most one readiness declaration; found {len(matches)}")
    if actual_readiness and actual_readiness not in READINESS_OUTCOMES:
        failures.append(f"unknown readiness declaration: {actual_readiness!r}")

    copy_paste = COPY_PASTE_BLOCK.search(output)
    draft_body = copy_paste.group(1).strip() if copy_paste else ""
    has_draft = bool(MARKDOWN_FENCE.search(output))
    draft_rule = expectation["draft"]
    expected_draft = draft_rule == "required"
    if (draft_rule == "required" and not has_draft) or (
        draft_rule == "forbidden" and has_draft
    ):
        failures.append(
            f"draft presence was {has_draft}; expected {draft_rule}"
        )
    if expected_draft and copy_paste is None:
        failures.append("ready result did not contain a Copy/paste markdown draft")
    if (
        expected_draft
        and copy_paste is not None
        and len(draft_body) < MINIMUM_DRAFT_CHARACTERS
    ):
        failures.append("Copy/paste draft was not substantive")

    actual_outcome = classify_outcome(output, has_draft=has_draft)
    if actual_outcome != expectation["outcome"]:
        failures.append(
            f"outcome was {actual_outcome!r}; expected {expectation['outcome']!r}"
        )

    messages = interaction_messages(result)
    interaction = "\n".join(message["text"] for message in messages)
    lowered = interaction.casefold()
    message_expectation = expectation["messages"]
    for required in message_expectation["include"]:
        if required.casefold() not in lowered:
            failures.append(f"missing required text: {required!r}")
    for forbidden in message_expectation["exclude"]:
        if forbidden.casefold() in lowered:
            failures.append(f"contained forbidden text: {forbidden!r}")
    for forbidden in WORKFLOW_JARGON:
        if forbidden in lowered:
            failures.append(f"contained workflow jargon: {forbidden!r}")
    internal_labels = INTERNAL_LABEL.findall(interaction)
    if internal_labels:
        failures.append(
            "contained internal review labels: " + ", ".join(sorted(set(internal_labels)))
        )
    question_turns = sum("?" in message["text"] for message in messages)
    if question_turns > message_expectation["max_question_turns"]:
        failures.append(
            f"interaction contained {question_turns} question turns; "
            f"expected at most {message_expectation['max_question_turns']}"
        )
    questions = question_texts(messages)
    repeated_questions = {
        question for question in questions if questions.count(question) > 1
    }
    if repeated_questions:
        failures.append("repeated a question across the interaction")

    narrative_words = narrative_word_count(output)
    max_narrative_words = expectation.get("max_narrative_words")
    if max_narrative_words is not None and narrative_words > max_narrative_words:
        failures.append(
            f"narrative contained {narrative_words} words; "
            f"expected at most {max_narrative_words}"
        )

    references = result.get("references")
    actual_references = set(references) if isinstance(references, list) else set()
    reference_expectation = expectation["references"]
    for required in reference_expectation["required"]:
        if required not in actual_references:
            failures.append(f"missing required reference: {required!r}")
    for forbidden in reference_expectation["forbidden"]:
        if forbidden in actual_references:
            failures.append(f"opened forbidden reference: {forbidden!r}")
    return {
        "id": case["id"],
        "passed": not failures,
        "outcome": actual_outcome,
        "readiness": actual_readiness,
        "draft": has_draft,
        "question_turns": question_turns,
        "narrative_words": narrative_words,
        "failures": failures,
    }


def score_suite(
    fixture: dict[str, Any],
    results: dict[str, Any],
) -> dict[str, Any]:
    if results.get("schema") != RESULT_SCHEMA:
        raise ScoringError("results have an invalid schema")
    provider = results.get("provider")
    if provider not in PROVIDERS:
        raise ScoringError("results have an invalid provider")
    if results.get("adapter_version") != ADAPTER_VERSION:
        raise ScoringError("results have an invalid adapter version")
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
    if any(result.get("provider") != provider for result in result_cases):
        raise ScoringError("result cases do not match the declared provider")
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
