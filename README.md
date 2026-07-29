# WP Cloud Escalation Review

WP Cloud Escalation Review is an Agent Skill for checking whether a possible
WP Cloud escalation is ready to send and for improving the final draft. It
reviews evidence, ownership, routing, safety, and writing quality.

The skill starts after someone already has a possible escalation, review
request, or draft. It can suggest public documentation and reporter-owned
checks, including checks against the WP Cloud Atomic API. It is not a general
WP Cloud support, troubleshooting, or issue-resolution tool, and it does not
include private support history or internal Automattic access.

## Install and use

Copy or link `skills/wp-cloud-escalation-review/` into your agent's skills
directory. The package is self-contained.

Invoke `wp-cloud-escalation-review` with the escalation material you want
reviewed. Include the facts and evidence that are safe and necessary for the
review, but do not include authentication material.

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
python3 scripts/evaluate.py development --dry-run
```

Then run the opt-in development evaluation:

```bash
python3 scripts/evaluate.py development
```

Run the broader opt-in regression evaluation before a release or after a
wide-ranging behavior change:

```bash
python3 scripts/evaluate.py regression
```

Model evaluations use the locally configured Codex CLI, may incur cost, and do
not run in CI. Generated results are local artifacts and are not committed.

## License

The skill, tools, tests, and documentation are licensed under
GPL-2.0-or-later. See [LICENSE](LICENSE).
