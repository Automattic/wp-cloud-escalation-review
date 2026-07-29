# Evaluations

These fixtures are synthetic behavior contracts. They contain no customer
cases, production identifiers, or private provenance.

`development.json` is the small inner loop for substantial changes to the
skill's core behavior. `regression.json` is the broader suite for releases and
wide-ranging behavior changes.

Inspect the input-only projection without invoking a model:

```bash
python3 scripts/evaluate.py development --dry-run
python3 scripts/evaluate.py regression --dry-run
```

Run and score a suite with the locally configured Codex CLI:

```bash
python3 scripts/evaluate.py development
python3 scripts/evaluate.py regression
```

Use `--model`, `--effort`, and `--timeout-seconds` to override run settings.
Each case runs in a disposable, read-only workspace containing only the exact
installable skill manifest. Expectations remain in the driver process and are
never copied into model-visible input or staging.

Local results are written under `evals/results/` and ignored by Git. Review
individual failures. Results carry an input fingerprint, so stale or mismatched
files cannot be scored against a changed fixture. Model evaluations are useful
signals, not deterministic unit tests.
