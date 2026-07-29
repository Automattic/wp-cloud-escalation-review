from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FixtureContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validate = load_script("validate")
        self.evaluate = load_script("evaluate")

    def test_public_fixtures_are_valid_and_distinct(self) -> None:
        development = self.validate.load_fixture(ROOT / "evals" / "development.json")
        regression = self.validate.load_fixture(ROOT / "evals" / "regression.json")

        self.assertLessEqual(len(development["cases"]), 8)
        self.assertGreater(len(regression["cases"]), len(development["cases"]))
        self.assertEqual(
            set(),
            {case["id"] for case in development["cases"]}
            & {case["id"] for case in regression["cases"]},
        )

    def test_projection_never_contains_expectations(self) -> None:
        fixture = self.validate.load_fixture(ROOT / "evals" / "development.json")
        projection = self.evaluate.project_fixture(fixture)
        serialized = json.dumps(projection)

        self.assertNotIn("expect", serialized)
        self.assertNotIn("include", serialized)
        self.assertNotIn("exclude", serialized)
        self.assertEqual(
            {"id", "entry", "input"},
            set(projection["cases"][0]),
        )

    def test_projection_renders_the_synthetic_current_date(self) -> None:
        rendered = self.evaluate.render_input(
            "Observed on <eval-date>.",
            eval_date="2040-02-03",
        )

        self.assertEqual("Observed on 2040-02-03.", rendered)


class RuntimeIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_script("run_evaluations")
        self.evaluate = load_script("evaluate")
        self.package = ROOT / "skills" / "wp-cloud-escalation-review"

    def test_staging_copies_only_the_exact_runtime_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            staged = Path(directory) / "workspace"
            self.runner.stage_runtime(self.package, staged)
            files = {
                path.relative_to(staged).as_posix()
                for path in staged.rglob("*")
                if path.is_file()
            }

        expected = {
            f".agents/skills/wp-cloud-escalation-review/{path}"
            for path in self.runner.RUNTIME_MANIFEST
        }
        self.assertEqual(expected, files)

    def test_prompt_and_workspace_do_not_receive_expectations(self) -> None:
        sentinel = "expectation-" + "must-not-cross"
        case = {
            "id": "isolation-check",
            "entry": "Direct",
            "input": "Review the supplied material.",
            "expect": {"include": [sentinel]},
        }
        projection = self.evaluate.project_cases("check", [case])
        prompt = self.runner.build_prompt(projection["cases"][0])

        self.assertNotIn(sentinel, json.dumps(projection))
        self.assertNotIn(sentinel, prompt)
        self.assertIn("$wp-cloud-escalation-review", prompt)
        with tempfile.TemporaryDirectory() as directory:
            staged = Path(directory) / "workspace"
            self.runner.stage_runtime(self.package, staged)
            staged_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in staged.rglob("*")
                if path.is_file()
            )
        self.assertNotIn(sentinel, staged_text)

    def test_unexpected_runtime_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            for relative in self.runner.RUNTIME_MANIFEST:
                target = package / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("placeholder\n", encoding="utf-8")
            (package / "unexpected.md").write_text("extra\n", encoding="utf-8")

            with self.assertRaises(self.runner.EvaluationError):
                self.runner.verify_runtime_manifest(package)

    def test_runtime_symlinks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "package"
            for relative in self.runner.RUNTIME_MANIFEST:
                target = package / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("placeholder\n", encoding="utf-8")
            external = root / "external.md"
            external.write_text("private source\n", encoding="utf-8")
            (package / "SKILL.md").unlink()
            (package / "SKILL.md").symlink_to(external)

            with self.assertRaises(self.runner.EvaluationError):
                self.runner.verify_runtime_manifest(package)


class PluginPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = load_script("build_plugin")

    def test_dual_plugin_metadata_is_valid_and_versioned_together(self) -> None:
        version = self.builder.validate_source()

        self.assertRegex(version, self.builder.SEMVER)
        self.assertEqual(
            version,
            self.builder.load_json(self.builder.CODEX_MANIFEST)["version"],
        )
        self.assertEqual(
            version,
            self.builder.load_json(self.builder.CLAUDE_MANIFEST)["version"],
        )

    def test_release_version_must_match_the_manifests(self) -> None:
        version = self.builder.validate_source()
        different_version = "0.0.1" if version == "0.0.0" else "0.0.0"

        with self.assertRaises(self.builder.PluginBuildError):
            self.builder.validate_source(different_version)

    def test_built_archive_contains_exact_canonical_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dist = Path(directory)
            with mock.patch.object(self.builder, "DIST", dist):
                version = self.builder.validate_source()
                plugin_root, archive = self.builder.build_plugin(version)
                self.builder.validate_build(plugin_root, archive)

                self.assertTrue(archive.is_file())
                packaged_skill = (
                    plugin_root
                    / "skills"
                    / "wp-cloud-escalation-review"
                    / "SKILL.md"
                )
                canonical_skill = (
                    ROOT
                    / "skills"
                    / "wp-cloud-escalation-review"
                    / "SKILL.md"
                )
                self.assertEqual(
                    canonical_skill.read_bytes(),
                    packaged_skill.read_bytes(),
                )

    def test_claude_marketplace_uses_the_repository_plugin(self) -> None:
        marketplace = self.builder.load_json(self.builder.CLAUDE_MARKETPLACE)

        self.assertEqual("./", marketplace["plugins"][0]["source"])

    def test_codex_marketplace_uses_the_repository_plugin(self) -> None:
        marketplace = self.builder.load_json(self.builder.CODEX_MARKETPLACE)

        self.assertEqual(
            {
                "source": "local",
                "path": "./",
            },
            marketplace["plugins"][0]["source"],
        )


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scorer = load_script("score_evaluations")

    def expectation(
        self,
        outcome: str,
        *,
        draft: str = "forbidden",
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> dict:
        return {
            "outcome": outcome,
            "draft": draft,
            "messages": {
                "include": include or [],
                "exclude": exclude or [],
                "max_questions": 2,
            },
            "references": {"required": [], "forbidden": []},
        }

    def test_ready_draft_and_text_expectations_are_scored(self) -> None:
        case = {
            "id": "ready-check",
            "entry": "Direct",
            "input": "Review this.",
            "expect": self.expectation(
                "ready",
                draft="required",
                include=["verified outcome"],
                exclude=["unsupported cause"],
            ),
        }
        output = (
            "This is ready to send.\n\n### Copy/paste\n"
            "```markdown\nVerified outcome with complete context.\n```"
        )
        score = self.scorer.score_case(
            case,
            {
                "status": "completed",
                "output": output,
                "messages": [{"phase": "final", "text": output}],
                "references": [],
            },
        )

        self.assertTrue(score["passed"], score["failures"])
        self.assertEqual([], score["failures"])

    def test_skill_requires_a_canonical_readiness_state(self) -> None:
        skill = (
            ROOT / "skills" / "wp-cloud-escalation-review" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Every result uses exactly one readiness state", skill)
        self.assertIn("readiness stays internal", skill)

    def test_plain_language_blockers_do_not_require_a_readiness_label(self) -> None:
        case = {
            "id": "plain-blocker",
            "entry": "Direct",
            "input": "Review this.",
            "expect": self.expectation(
                "needs_reporter_check",
                draft="forbidden",
            ),
        }

        for output in (
            "The draft cannot proceed while the exposed credential remains active. "
            "Rotate it before resubmitting.",
            "Retry with the documented field before escalating.",
            "Retry the operation with the documented field before escalating.",
        ):
            with self.subTest(output=output):
                score = self.scorer.score_case(
                    case,
                    {
                        "status": "completed",
                        "output": output,
                        "messages": [{"phase": "final", "text": output}],
                        "references": [],
                    },
                )
                self.assertTrue(score["passed"], score["failures"])

    def test_plain_language_alternate_owner_needs_no_readiness_label(self) -> None:
        case = {
            "id": "plain-alternate-owner",
            "entry": "Direct",
            "input": "Review this.",
            "expect": self.expectation("alternate_owner", draft="forbidden"),
        }
        output = (
            "Handle this through the extension settings. The reporter controls "
            "the correction, and there is nothing for WP Cloud to change."
        )

        score = self.scorer.score_case(
            case,
            {
                "status": "completed",
                "output": output,
                "messages": [{"phase": "final", "text": output}],
                "references": [],
            },
        )

        self.assertTrue(score["passed"], score["failures"])

    def test_skill_uses_client_available_evidence_sources(self) -> None:
        skill = (
            ROOT / "skills" / "wp-cloud-escalation-review" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("dashboards and logs available", skill)
        self.assertIn("Grafana dashboard", skill)
        self.assertIn("nginx or PHP logs", skill)
        self.assertIn("metrics from the WP Cloud", skill)
        self.assertNotIn("single-site dashboard", skill)

    def test_skill_advances_investigation_without_timestamp_or_access_dead_ends(self) -> None:
        package = ROOT / "skills" / "wp-cloud-escalation-review"
        skill = (package / "SKILL.md").read_text(encoding="utf-8")
        guided = (package / "references" / "guided-workflow.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("which URL and HTTP method", skill)
        self.assertIn("PHP fatal", skill)
        self.assertIn("Do not ask the reporter to\n  restate an adequate window", skill)
        self.assertIn("permit a narrow escalation", skill)
        self.assertIn("State what the latest answer changed", guided)
        self.assertIn("narrow last-resort escalation", guided)

    def test_skill_preserves_shareable_log_links_without_generic_sanitization(self) -> None:
        package = ROOT / "skills" / "wp-cloud-escalation-review"
        skill = (package / "SKILL.md").read_text(encoding="utf-8")
        http = (package / "references" / "http-and-automation.md").read_text(
            encoding="utf-8"
        )
        style = (package / "references" / "style-guide.md").read_text(
            encoding="utf-8"
        )
        guided = (package / "references" / "guided-workflow.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Always keep a supplied, shareable link", skill)
        self.assertIn("count, percentage, or rate", skill)
        self.assertIn("log, saved-search, dashboard, or evidence link", skill)
        self.assertIn("never block only because there is no link", skill)
        self.assertIn("Do not ask the reporter to sanitize ordinary traffic", skill)
        self.assertIn("Always carry it into the handoff", http)
        self.assertIn("absolute bounded interval and denominator", http)
        self.assertIn("Always include a supplied, shareable link", style)
        self.assertIn("do not rely on a drifting", style)
        self.assertIn("do not ask for\n  generic sanitization of traffic", guided)

    def test_skill_requires_failed_work_and_safe_diagnostics(self) -> None:
        package = ROOT / "skills" / "wp-cloud-escalation-review"
        skill = (package / "SKILL.md").read_text(encoding="utf-8")
        managed = (
            package / "references" / "api-and-managed-operations.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Functional impact first", skill)
        self.assertIn("execution and its observable result", skill)
        self.assertIn("warnings without failed work", skill)
        self.assertIn("Never make the warning ready", skill)
        self.assertIn("Treat diagnostic commands by what they execute", skill)
        self.assertIn("ordinary WordPress, PHP, plugin", skill)
        self.assertIn("Start with the work result, not callback attribution", managed)
        self.assertIn("Treat `wp eval` as arbitrary PHP execution", managed)
        self.assertIn("reporter analysis, not raw log output", managed)

        challenge = (package / "references" / "challenge.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("breaking recurring cron", challenge)
        self.assertIn("real-world damage", challenge)

    def test_multiple_readiness_lines_are_rejected(self) -> None:
        case = {
            "id": "contradictory-readiness",
            "entry": "Direct",
            "input": "Review this.",
            "expect": self.expectation("ready", draft="required"),
        }
        output = (
            "Readiness: Ready\nReadiness: Ready with caveats\n"
            "### Copy/paste\n```markdown\nA complete escalation draft.\n```"
        )

        score = self.scorer.score_case(case, {"status": "completed", "output": output})

        self.assertFalse(score["passed"])
        self.assertIn("at most one readiness", " ".join(score["failures"]))

    def test_ready_draft_must_be_substantive(self) -> None:
        case = {
            "id": "short-draft",
            "entry": "Direct",
            "input": "Review this.",
            "expect": self.expectation("ready", draft="required"),
        }
        output = "Readiness: Ready\n### Copy/paste\n```markdown\nx\n```"

        score = self.scorer.score_case(case, {"status": "completed", "output": output})

        self.assertFalse(score["passed"])
        self.assertIn("substantive", " ".join(score["failures"]))

    def test_blocked_result_rejects_a_misheaded_markdown_draft(self) -> None:
        case = {
            "id": "misheaded-draft",
            "entry": "Direct",
            "input": "Review this.",
            "expect": self.expectation("needs_reporter_check"),
        }
        output = (
            "Readiness: Reporter action required\n"
            "### Draft\n```markdown\nA complete but impermissible draft.\n```"
        )

        score = self.scorer.score_case(case, {"status": "completed", "output": output})

        self.assertFalse(score["passed"])

    def test_result_envelope_must_match_the_fixture(self) -> None:
        fixture = {
            "suite": "development",
            "cases": [
                {
                    "id": "envelope-check",
                    "entry": "Direct",
                    "input": "Review this.",
                    "expect": self.expectation("needs_reporter_check"),
                }
            ],
        }
        results = {
            "schema": "unrelated/v0",
            "suite": "regression",
            "source_digest": "wrong",
            "cases": [],
        }

        with self.assertRaises(self.scorer.ScoringError):
            self.scorer.score_suite(fixture, results)

        digest = self.scorer.source_digest(fixture["cases"])
        completed_case = {
            "id": "envelope-check",
            "provider": "codex",
            "status": "completed",
            "output": "Please check the current state.",
            "messages": [
                {"phase": "final", "text": "Please check the current state."}
            ],
            "references": [],
        }
        valid_results = {
            "schema": self.scorer.RESULT_SCHEMA,
            "suite": "development",
            "source_digest": digest,
            "provider": "codex",
            "adapter_version": "wp-cloud-escalation-review-adapter/v1",
            "cases": [completed_case],
        }
        self.assertTrue(self.scorer.score_suite(fixture, valid_results)["success"])

        invalid_provider = dict(valid_results, provider="unknown")
        with self.assertRaises(self.scorer.ScoringError):
            self.scorer.score_suite(fixture, invalid_provider)

        invalid_adapter = dict(valid_results, adapter_version="old-adapter")
        with self.assertRaises(self.scorer.ScoringError):
            self.scorer.score_suite(fixture, invalid_adapter)
        valid_results["cases"].append(completed_case)
        with self.assertRaises(self.scorer.ScoringError):
            self.scorer.score_suite(fixture, valid_results)


class PublicSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validate = load_script("validate")

    def test_repository_validation_passes(self) -> None:
        self.assertEqual([], self.validate.validate_repository(ROOT))

    def test_scanner_rejects_domain_address_and_identifier_shapes(self) -> None:
        domain = "sample" + "." + "com"
        address = ".".join(("203", "0", "113", "9"))
        opaque = "-".join(
            ("123e4567", "e89b", "12d3", "a456", "426614" + "174000")
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.txt").write_text(
                f"{domain}\n{address}\n{opaque}\n",
                encoding="utf-8",
            )
            errors = self.validate.scan_public_files(root)

        self.assertGreaterEqual(len(errors), 3)

    def test_scanner_rejects_broad_hosts_emails_and_authentication_material(self) -> None:
        host = "client" + "." + "co"
        second_host = "service" + "." + "ai"
        email = "person" + "@" + host
        authorization = "Author" + "ization: Bearer synthetic-credential-value"
        cookie = "Cook" + "ie: sessionid=synthetic-session-value"
        private_key = "-----BEGIN " + "PRIVATE KEY-----"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.txt").write_text(
                "\n".join(
                    (
                        f"https://{host}/status",
                        f"https://{second_host}/status",
                        email,
                        authorization,
                        cookie,
                        private_key,
                    )
                ),
                encoding="utf-8",
            )
            errors = self.validate.scan_public_files(root)

        self.assertGreaterEqual(len(errors), 6)

    def test_scanner_ignores_github_expression_context_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow = root / "workflow.yml"
            workflow.write_text(
                "env:\n  GH_TOKEN: ${{ github.token }}\n",
                encoding="utf-8",
            )

            self.assertEqual([], self.validate.scan_public_files(root))

    def test_scanner_rejects_existing_and_dangling_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            external = root.parent / f"{root.name}-external.txt"
            external.write_text("synthetic external content\n", encoding="utf-8")
            try:
                (root / "existing.md").symlink_to(external)
                (root / "dangling.md").symlink_to(root / "missing.md")
                errors = self.validate.scan_public_files(root)
            finally:
                external.unlink()

        self.assertEqual(2, sum("symlink" in error for error in errors))

    def test_scanner_allows_an_internal_marketplace_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("sample\n", encoding="utf-8")
            plugin_skills = root / "plugin" / "skills"
            plugin_skills.mkdir(parents=True)
            (plugin_skills / "sample").symlink_to(skill)

            self.assertEqual([], self.validate.scan_public_files(root))

    def test_tracked_evaluation_results_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = root / "evals" / "results" / "generated.json"
            result.parent.mkdir(parents=True)
            result.write_text("{}\n", encoding="utf-8")
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "add", "-f", "evals/results/generated.json"],
                cwd=root,
                check=True,
            )

            errors = self.validate.tracked_result_errors(root)

        self.assertEqual(
            ["tracked generated evaluation result: evals/results/generated.json"],
            errors,
        )

    def test_reference_to_reference_links_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            reference = package / "references" / "one.md"
            reference.parent.mkdir()
            reference.write_text("[Missing](two.md)\n", encoding="utf-8")

            errors = self.validate.relative_link_errors(package)

        self.assertEqual(
            ["broken runtime link: references/one.md -> two.md"],
            errors,
        )


if __name__ == "__main__":
    unittest.main()
