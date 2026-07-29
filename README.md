# WP Cloud Escalation Review Skill

WP Cloud Escalation Review is an Agent Skill for checking whether a possible
WP Cloud escalation is ready to send and for improving the final draft. It
reviews evidence, ownership, routing, safety, and writing quality.

The skill starts after someone already has a possible escalation, review
request, or draft. It can suggest public documentation and reporter-owned
checks, including checks against the WP Cloud Atomic API. It is not a general
WP Cloud support, troubleshooting, or issue-resolution tool, and it does not
include private support history or internal Automattic access.

## Why this skill exists

AI can produce a long, technical-looking explanation quickly. If a reporter
forwards that material without validating and editing it, the receiving team
inherits extra work. It must identify the concrete problem, separate supplied
claims from verified facts, repeat reporter-owned troubleshooting, and remove
irrelevant detail.

This avoidable transfer of work is the cognitive AI tax.

Do not impose a cognitive AI tax on others. Eliminate it or pay it yourself.

Four principles guide the review:

1. Treat confidence as presentation, not evidence. Verify factual claims
   against the source, logs, dashboards, or tools. Mark an unverified claim as
   reported or suspected, or remove it.
2. Make every detail earn its reading cost. Dense, nested analysis is harder
   to audit and gives unchecked claims more places to hide. Keep details that
   change validation, scope, routing, risk, or the requested action.
3. Own everything you send. Do not send a draft you have not read. You should
   be able to explain its claims and answer follow-up questions. AI can produce
   a first pass, but the sender remains responsible for the result.
4. Write for the next person to act. Lead with the request, then summarize the
   verified work and the remaining blocker. Correct errors as soon as you
   discover them.

The receiving team may still need to investigate the unresolved platform
problem. That investigation should start at the WP Cloud boundary, without
first reconstructing the report or auditing an unreviewed research dump.

## Install and use

Ask Codex, Claude, or another AI assistant that supports Agent Skills to
install the skill from this repository:

```text
Install the WP Cloud Escalation Review skill from https://github.com/Automattic/wp-cloud-escalation-review
```

Invoke `$wp-cloud-escalation-review` in Codex or
`/wp-cloud-escalation-review` in Claude with the escalation material you want
reviewed. Include the facts and evidence that are safe and necessary for the
review, but do not include authentication material. The behavior is defined in
the shared `SKILL.md` and references; provider-specific metadata does not carry
separate review rules.

## Repository contents

- `skills/wp-cloud-escalation-review/` contains the installable skill and its
  public references.
- `evals/` contains synthetic development and regression cases.
- `scripts/` contains repository validation and opt-in behavior-evaluation
  tools.
- `tests/` verifies the public package and evaluation workflow.

The repository intentionally excludes real customer cases, client names,
internal links, private provenance, transcripts, and evaluation results.

## Contribute

Keep changes focused on escalation review. Use synthetic examples and public
sources, then run the deterministic checks:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
```

For a substantial change to core skill behavior, first inspect the projected
development cases without invoking a model:

```bash
python3 scripts/evaluate.py development --dry-run --provider codex
```

Then run the opt-in development evaluation through either supported client:

```bash
python3 scripts/evaluate.py development --provider codex
python3 scripts/evaluate.py development --provider claude
```

Run the broader opt-in regression evaluation before a release or after a
wide-ranging behavior change:

```bash
python3 scripts/evaluate.py regression --provider codex
python3 scripts/evaluate.py regression --provider claude
```

Model evaluations use the selected locally configured CLI, may incur cost, and
do not run in CI. Event capture and result files exist only in this opt-in test
harness; normal skill use adds no telemetry. Both adapters normalize into the
same scoring contract. Generated results are local artifacts and are not
committed.

## License

The skill, tools, tests, and documentation are licensed under
GPL-2.0-or-later. See [LICENSE](LICENSE).
