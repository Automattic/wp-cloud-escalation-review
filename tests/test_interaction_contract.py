from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expectation(
    outcome: str,
    *,
    draft: str = "forbidden",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_question_turns: int = 1,
    required_references: list[str] | None = None,
    forbidden_references: list[str] | None = None,
) -> dict:
    return {
        "outcome": outcome,
        "draft": draft,
        "messages": {
            "include": include or [],
            "exclude": exclude or [],
            "max_question_turns": max_question_turns,
        },
        "references": {
            "required": required_references or [],
            "forbidden": forbidden_references or [],
        },
    }


class ProviderAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_script("run_evaluations")
        self.package = ROOT / "skills" / "wp-cloud-escalation-review"

    def test_runtime_stages_in_each_clients_project_skill_directory(self) -> None:
        for provider, prefix in (
            ("codex", ".agents/skills"),
            ("claude", ".claude/skills"),
        ):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                staged = self.runner.stage_runtime(
                    self.package,
                    workspace,
                    provider=provider,
                )
                self.assertEqual(
                    workspace / prefix / "wp-cloud-escalation-review",
                    staged,
                )
                self.assertTrue((staged / "SKILL.md").is_file())

    def test_codex_events_normalize_messages_and_reference_reads(self) -> None:
        events = "\n".join(
            (
                json.dumps(
                    {
                        "type": "item" + ".completed",
                        "item": {
                            "type": "agent_message",
                            "text": "Please check the dashboard first.",
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "item" + ".completed",
                        "item": {
                            "type": "command_execution",
                            "command": "sed -n '1,80p' .agents/skills/wp-cloud-escalation-review/references/style-guide.md",
                            "aggregated_output": (
                                "references/challenge.md\n"
                                "references/http-and-automation.md\n"
                            ),
                        },
                    }
                ),
                json.dumps({"type": "future" + ".event", "ignored": True}),
            )
        )

        normalized = self.runner.normalize_event_stream(
            "codex",
            events,
            final_output="Please check the dashboard first.",
        )

        self.assertEqual("Please check the dashboard first.", normalized["output"])
        self.assertEqual(
            ["references/style-guide.md"],
            normalized["references"],
        )
        self.assertEqual("final", normalized["messages"][-1]["phase"])

    def test_claude_events_normalize_messages_and_reference_reads(self) -> None:
        events = "\n".join(
            (
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "I’ll check the relevant guidance.",
                                },
                                {
                                    "type": "tool_use",
                                    "name": "Read",
                                    "input": {
                                        "file_path": ".claude/skills/wp-cloud-escalation-review/references/challenge.md"
                                    },
                                },
                            ]
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "result",
                        "is_error": False,
                        "result": "Is the problem still happening?",
                    }
                ),
            )
        )

        normalized = self.runner.normalize_event_stream("claude", events)

        self.assertEqual("Is the problem still happening?", normalized["output"])
        self.assertEqual(
            ["references/challenge.md"],
            normalized["references"],
        )
        self.assertEqual(
            ["commentary", "final"],
            [message["phase"] for message in normalized["messages"]],
        )

    def test_normalization_sanitizes_every_persisted_text_field(self) -> None:
        events = json.dumps(
            {
                "type": "item" + ".completed",
                "item": {
                    "type": "agent_message",
                    "text": "api_" + "key=synthetic-sensitive-value",
                },
            }
        )

        normalized = self.runner.normalize_event_stream(
            "codex",
            events,
            final_output="pass" + "word=synthetic-sensitive-value",
        )
        serialized = json.dumps(normalized)

        self.assertNotIn("synthetic-sensitive-value", serialized)
        self.assertIn("<redacted authentication material>", serialized)


class SemanticScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scorer = load_script("score_evaluations")

    def score(
        self,
        expected: dict,
        *,
        output: str,
        messages: list[dict] | None = None,
        references: list[str] | None = None,
    ) -> dict:
        case = {
            "id": "semantic-check",
            "input": "Review this.",
            "expect": expected,
        }
        result = {
            "id": "semantic-check",
            "status": "completed",
            "output": output,
            "messages": messages or [{"phase": "final", "text": output}],
            "references": references or [],
        }
        return self.scorer.score_case(case, result)

    def test_no_post_outcome_does_not_require_a_readiness_line(self) -> None:
        score = self.score(
            expectation(
                "no_post",
                include=["don’t post"],
                forbidden_references=["references/http-and-automation.md"],
            ),
            output="Don’t post this escalation. There is nothing left for WP Cloud to answer.",
        )

        self.assertTrue(score["passed"], score["failures"])
        self.assertEqual("no_post", score["outcome"])

    def test_one_compatible_readiness_line_is_allowed(self) -> None:
        score = self.score(
            expectation("no_post", include=["don’t post"]),
            output=(
                "Readiness: Resolved during validation\n"
                "Don’t post this escalation. The remaining work belongs with the site developer."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_plain_resolved_wording_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["nothing left for WP Cloud"]),
            output=(
                "This is resolved during validation. "
                "There is nothing left for WP Cloud to answer or do."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_close_without_escalation_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["nothing left for WP Cloud"]),
            output=(
                "This can close without a WP Cloud escalation. "
                "There is nothing left for WP Cloud to answer or do."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_close_without_escalating_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["nothing left for WP Cloud"]),
            output=(
                "Close this without escalating to WP Cloud. "
                "There is nothing left for WP Cloud to answer or do."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_close_this_without_escalating_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["nothing left"]),
            output=(
                "Close this without escalating. WP Cloud has nothing left "
                "to answer or do."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_do_not_escalate_with_nothing_left_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["do not escalate"]),
            output=(
                "There is nothing left for WP Cloud to answer or act on. "
                "Do not escalate."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_do_not_escalate_with_no_remaining_question_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["do not escalate"]),
            output=(
                "Do not escalate. There is no demonstrated broken workload "
                "or remaining question for WP Cloud."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_do_not_escalate_with_no_platform_action_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["do not escalate"]),
            output=(
                "Do not escalate this to WP Cloud. The affected workflow now "
                "passes, and there is no remaining platform-owned action."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_plain_caveat_variants_map_to_ready_with_caveat(self) -> None:
        for wording in (
            "The cause remains unknown.",
            "The full cause remains unconfirmed.",
            "The control completed without reproducing the failure.",
            "The remaining evidence is available only to WP Cloud.",
        ):
            with self.subTest(wording=wording):
                output = (
                    f"{wording}\n\n### Copy/paste\n```markdown\n"
                    "Please inspect the recorded failure and advise how to "
                    "complete the blocked operation safely.\n```"
                )
                score = self.score(
                    expectation("ready_with_caveat", draft="required"),
                    output=output,
                )
                self.assertTrue(score["passed"], score["failures"])

    def test_plain_belongs_in_wording_maps_to_alternate_owner(self) -> None:
        score = self.score(
            expectation("alternate_owner"),
            output=(
                "This belongs in the public documentation issue tracker, "
                "not a platform escalation."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_alternate_owner_can_include_requested_destination_copy(self) -> None:
        output = (
            "This belongs in the public documentation issue tracker rather "
            "than a platform escalation.\n\n### Copy/paste\n```markdown\n"
            "Please clarify whether clients must retain the returned job "
            "ticket for later support lookup.\n```"
        )
        score = self.score(
            expectation("alternate_owner", draft="required"),
            output=output,
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_documentation_tracker_copy_maps_to_alternate_owner(self) -> None:
        output = (
            "This belongs in the public documentation issue tracker because "
            "the documentation owner must decide the requirement.\n\n"
            "### Copy/paste\n```markdown\nPlease clarify the documented "
            "retention requirement for managed-operation job tickets.\n```"
        )
        score = self.score(
            expectation("alternate_owner", draft="required"),
            output=output,
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_optional_alternate_owner_copy_accepts_both_forms(self) -> None:
        for output in (
            "Route this through the public WP Cloud documentation issue "
            "tracker, not a platform escalation.",
            (
                "This belongs in the public documentation issue tracker.\n\n"
                "### Copy/paste\n```markdown\nPlease clarify the retention "
                "requirement.\n```"
            ),
        ):
            with self.subTest(output=output):
                score = self.score(
                    expectation("alternate_owner", draft="optional"),
                    output=output,
                )
                self.assertTrue(score["passed"], score["failures"])

    def test_warning_without_impact_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post"),
            output=(
                "Do not escalate this to WP Cloud. The scheduled work "
                "completed, and the warnings show no functional impact."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_natural_development_outcome_variants_are_classified(self) -> None:
        cases = (
            (
                expectation("no_post"),
                "WP Cloud has nothing left to investigate or change.",
            ),
            (
                expectation("needs_reporter_check"),
                "Correct the request, then retry one representative call.",
            ),
            (
                expectation("needs_reporter_check"),
                "Retry it with the documented field. Escalate only if it fails.",
            ),
            (
                expectation("needs_reporter_check"),
                "Confirm whether demo-site-k is a typo or a second site.",
            ),
            (
                expectation("ready_with_caveat", draft="required"),
                (
                    "This requires platform data the reporter cannot access.\n\n"
                    "### Copy/paste\n```markdown\nPlease inspect the failed "
                    "request in platform logs and report the recorded reason.\n```"
                ),
            ),
        )
        for expected, output in cases:
            with self.subTest(output=output):
                score = self.score(expected, output=output)
                self.assertTrue(score["passed"], score["failures"])

    def test_natural_no_post_and_caveat_variants_are_classified(self) -> None:
        cases = (
            "Do not escalate. WP Cloud has nothing to investigate or decide.",
            "No WP Cloud escalation is needed because the fix now passes.",
            "This does not need a WP Cloud escalation.",
            "Do not escalate. Close the review unless expected work later fails.",
        )
        for output in cases:
            with self.subTest(output=output):
                score = self.score(expectation("no_post"), output=output)
                self.assertTrue(score["passed"], score["failures"])

        output = (
            "The failing layer is pending receiver telemetry.\n\n"
            "### Copy/paste\n```markdown\nPlease match the failed handshake "
            "in platform telemetry.\n```"
        )
        score = self.score(
            expectation("ready_with_caveat", draft="required"),
            output=output,
        )
        self.assertTrue(score["passed"], score["failures"])

    def test_valid_technical_language_is_not_globally_rejected(self) -> None:
        output = (
            "This is ready to send.\n\n### Copy/paste\n```markdown\n"
            "## Description\nThe customer reports that `demo_callback` has "
            "failed twice on `demo-site-a`.\n\n## Mechanism\nThe request "
            "routes through `demo_filter` before the platform returns HTTP "
            "503: this is the supported scope, not all traffic. The longer "
            "sentence keeps the callback, request, and returned error together "
            "because separating them would hide the technical relationship.\n\n"
            "## Troubleshooting Steps Taken\n- Repeated `demo-request-a` in "
            "the traffic and PHP logs.\n- Confirmed the same identifier in the "
            "full trace.\n\n## Stack trace\n`demo_callback -> demo_filter -> "
            "demo_callback`\n\n## Ask\nPlease inspect `demo-request-a` and "
            "explain why it returned HTTP 503.\n```"
        )
        score = self.score(expectation("ready", draft="required"), output=output)

        self.assertTrue(score["passed"], score["failures"])

    def test_warning_does_not_support_escalation_maps_to_no_post(self) -> None:
        score = self.score(
            expectation("no_post", include=["nothing left"]),
            output=(
                "The warnings do not support an escalation. There is nothing "
                "left for WP Cloud to answer or act on."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_request_for_existing_time_window_maps_to_needs_evidence(self) -> None:
        score = self.score(
            expectation("needs_existing_evidence", include=["existing UTC"]),
            output=(
                "Add the existing UTC start and end time so WP Cloud can match "
                "the failed operation in platform logs."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_plain_imperative_maps_to_reporter_action(self) -> None:
        score = self.score(
            expectation("needs_reporter_check", include=["dashboards"]),
            output=(
                "Check the dashboards available to you and report how many "
                "matching requests failed."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_plain_owner_wording_maps_to_alternate_owner(self) -> None:
        score = self.score(
            expectation("alternate_owner", include=["reporter owns"]),
            output=(
                "Do not escalate this to WP Cloud. The reporter owns the "
                "required setting change."
            ),
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_workflow_jargon_in_commentary_fails_a_clean_final_answer(self) -> None:
        score = self.score(
            expectation("no_post", include=["don’t post"]),
            output="Don’t post this escalation.",
            messages=[
                {
                    "phase": "commentary",
                    "text": "I’m running the HTTP-routing review and challenge pass.",
                },
                {"phase": "final", "text": "Don’t post this escalation."},
            ],
        )

        self.assertFalse(score["passed"])
        self.assertIn("workflow jargon", " ".join(score["failures"]))

    def test_reporter_facing_internal_terms_fail(self) -> None:
        score = self.score(
            expectation("needs_reporter_check", include=["URL"]),
            output=(
                "Which URL and request class failed? We need receiver-side "
                "visibility based on reporter-visible evidence before continuing."
            ),
        )

        self.assertFalse(score["passed"])
        failures = " ".join(score["failures"])
        self.assertIn("request class", failures)
        self.assertIn("receiver-side", failures)
        self.assertIn("reporter-visible evidence", failures)

    def test_question_and_reference_limits_cover_the_whole_interaction(self) -> None:
        score = self.score(
            expectation(
                "needs_reporter_check",
                include=["still happening"],
                max_question_turns=1,
                forbidden_references=["references/http-and-automation.md"],
            ),
            output="Is the problem still happening?",
            messages=[
                {"phase": "commentary", "text": "What changed?"},
                {"phase": "final", "text": "Is the problem still happening?"},
            ],
            references=["references/http-and-automation.md"],
        )

        self.assertFalse(score["passed"])
        failures = " ".join(score["failures"])
        self.assertIn("question turns", failures)
        self.assertIn("forbidden reference", failures)

    def test_several_questions_in_one_turn_are_allowed(self) -> None:
        score = self.score(
            expectation(
                "needs_reporter_check",
                include=["still happening", "site ID", "WP Cloud"],
                max_question_turns=1,
            ),
            output=(
                "Before posting, can you confirm whether this is still happening? "
                "Which site ID is affected? What still needs WP Cloud to answer?"
            ),
        )

        self.assertTrue(score["passed"], score["failures"])
        self.assertEqual(1, score["question_turns"])

    def test_repeated_question_across_turns_fails(self) -> None:
        score = self.score(
            expectation(
                "needs_reporter_check",
                include=["still happening"],
                max_question_turns=2,
            ),
            output="Is this still happening?",
            messages=[
                {"phase": "commentary", "text": "Is this still happening?"},
                {"phase": "final", "text": "Is this still happening?"},
            ],
        )

        self.assertFalse(score["passed"])
        self.assertIn("repeated a question", " ".join(score["failures"]))

    def test_ready_result_requires_a_substantive_copy_paste_block(self) -> None:
        score = self.score(
            expectation("ready", draft="required", max_question_turns=2),
            output=(
                "This is ready to send.\n\n"
                "### Copy/paste\n"
                "```markdown\n"
                "Please review the verified managed-operation failure and confirm the result.\n"
                "```"
            ),
        )

        self.assertTrue(score["passed"], score["failures"])


if __name__ == "__main__":
    unittest.main()
