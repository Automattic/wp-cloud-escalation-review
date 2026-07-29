# Agent guidance

Keep this repository public-safe and focused on escalation review.

- Preserve the product boundary: this skill reviews escalation readiness and
  drafts; it is not a general WP Cloud support or investigation tool.
- Use synthetic examples and public sources only.
- Use the public term **WP Cloud Atomic API**.
- Never add real domains, usernames, customer or client names, site or account
  IDs, IP addresses, internal links, private provenance, or copied support
  cases.
- Never add authentication material, secrets, private transcripts, or
  generated evaluation results.
- Keep the installable package self-contained and lightweight.
- Keep the Codex manifest, Claude manifest, and Claude marketplace versions in
  sync. Keep both marketplace entries pointed at the repository root.
- Keep `skills/wp-cloud-escalation-review/` canonical. Generated plugin
  archives must copy it exactly rather than introducing a second source.
- Update `skills/wp-cloud-escalation-review/agents/openai.yaml` when the
  skill's name, description, or invocation identity changes.

After changes, run:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/build_plugin.py --check
```

For substantial core-skill changes, also run:

```bash
python3 scripts/evaluate.py development --dry-run
python3 scripts/evaluate.py development
```

Run `python3 scripts/evaluate.py regression` before a release or after a
wide-ranging behavior change. Model evaluations are opt-in and do not run in
CI.
