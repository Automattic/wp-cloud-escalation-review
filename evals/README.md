# Evaluations

These fixtures are synthetic behavior contracts. They contain no customer
cases, production identifiers, or private provenance.

`development.json` is the small inner loop for substantial changes to the
skill's core behavior. `regression.json` is the broader suite for releases and
wide-ranging behavior changes.

Inspect the input-only projection without invoking a model:

```bash
python3 scripts/evaluate.py development --dry-run --provider codex
python3 scripts/evaluate.py regression --dry-run --provider codex
```

Run and score a suite with either locally configured client:

```bash
python3 scripts/evaluate.py development --provider codex
python3 scripts/evaluate.py regression --provider codex
python3 scripts/evaluate.py development --provider claude
python3 scripts/evaluate.py regression --provider claude
```

Use `--provider`, `--model`, `--effort`, and `--timeout-seconds` to override
run settings. Each case runs in a disposable, read-only workspace containing
only the exact installable skill manifest in the selected client's project
skill directory. Codex JSON events and Claude stream-JSON events normalize into
the same result contract. Expectations remain in the driver process and are
never copied into model-visible input or staging.

Local results are written under `evals/results/` with the provider in the
filename and ignored by Git. Review individual failures. Results carry an input
fingerprint, so stale or mismatched files cannot be scored against a changed
fixture. Event capture is evaluation-only and adds no telemetry to normal skill
usage. Model evaluations are useful signals, not deterministic unit tests.
