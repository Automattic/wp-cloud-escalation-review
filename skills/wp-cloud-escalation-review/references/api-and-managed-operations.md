# WP Cloud Atomic API and managed operations

Use this for a direct WP Cloud Atomic API contract, managed job, WP-Cron
lifecycle, platform runtime hook, managed configuration, or missing API
capability. It returns findings to the router, not readiness.

## Select this reference

Select it for:

- A direct WP Cloud Atomic API request or response.
- An accepted operation's managed-job state or failed stage.
- WP-Cron or scheduled work when state, persistence, retry, duplication, or a
  platform hook controls the question.
- A platform callback or MU-plugin behavior whose runtime context matters.
- A non-capacity configuration value controlled by the WP Cloud Atomic API or
  a managed operation.
- A missing platform primitive or API capability.

Do not select it merely for cloning, migration, WordPress REST, webhooks,
domains, or SSH. REST and webhooks are HTTP. Route connectivity, performance,
capacity, and incidents to their boundaries. Split independent issues first.

## Check the current contract

Follow [documentation routing](documentation-routing.md) for the smallest
current contract and record whether it was checked or unavailable.

Check method, path, identifiers, parameters, encoding, documented response,
errors, access expectations, and asynchronous job behavior. Never request or
repeat an API key or Authorization header.

A call that violates the current contract returns to the reporter for
correction. A sanitized, contract-valid call whose result contradicts the
documentation can support escalation.

When a contract error establishes correction, retain the status, shortest
response, and correction.

If current docs lack the claimed contract, keep it unvalidated and ask for its
source. Use `forwarded_claims_unvalidated`, not `request_contract_not_met`.

## Decisive evidence

For a direct API request:

- Method and path.
- Site, client, operation, request, or correlation IDs.
- Sanitized request body and relevant non-secret headers.
- Exact UTC time, status, and response.
- Documented expectation and observed mismatch.

For a managed job:

- Site and job IDs.
- Submission or acceptance time.
- Current state and when it was last checked.
- Failed stage, exact exception, and useful stack boundary.
- Source and destination IDs when applicable.
- Repeat result or proof that the failure is current.
- User effect and narrow owner action requested.

For configuration, include field, current and requested values, read method,
owner, and safe retry result.

For WP-Cron or scheduled work, include:

- Site, hook or job identity, and absolute UTC event time.
- Prior state, attempted transition, returned error, and resulting state.
- Expected and actual next run, work result, state, or absence.
- Retry behavior and whether the same event remained pending.
- The observable missed, late, duplicate, or otherwise incorrect work.
- Runtime context: CLI, HTTP request, cron spawn, worker, or another executor.

Start with the work result, not callback attribution. Validate one expected
execution and its observable result: a sync that did not arrive, an entry that
was not purged, a recurring event that was not created, or another missed,
late, duplicate, or incorrect outcome. A warning without failed work is not a
platform incident.

Keep warnings, persistence, retry, duplicate prevention, missed work, and
impact separate. Retain an asserted sequence as linked claims and prove each
transition. A combined hook list does not map every hook to every error.
Treat arrows, causal labels, and explanations added beside log lines as
reporter analysis, not raw log output.

For a capability gap, include workflow, workaround, missing primitive, desired
scope, and interface limit. Separate control from observability.

A direct platform exception can justify a short report. Do not add generic
troubleshooting to make it look substantial.

Do not require every possible lookup field. The Atomic Site ID for every
affected site, a bounded range, and a distinctive operation stage and error can
be sufficient without an exact second or a literal job ID. For multiple sites
with the same operation,
failure, impact, owner, and requested decision, keep one mapped handoff when
separate posts are unnecessary.

## Reporter-owned checks

- Validate the call against the current endpoint contract.
- Sanitize and repeat one representative request when safe.
- Poll or re-read asynchronous job state.
- Read configuration values instead of inferring them from usage or an error
  label.
- Inspect owned scheduling, queues, authorization, retries, and error handling.
- Prevent or identify duplicate and concurrent operations.
- Compare the expected and actual next execution or state for one representative
  scheduled event.
- Test the failing runtime. Source inspection and CLI success do not reproduce
  conditional HTTP, cron, or worker callbacks.
- Correct reporter-owned configuration and retry when safe.
- Confirm that the condition still exists.

Using WP Cloud primitives does not make an integrator-built workflow WP
Cloud-owned.

Inspect available logs, PHP or MU-plugin code, cron state, and application
outcomes before asking WP Cloud to interpret ordinary WordPress behavior.
Callback registration proves only that a callback was registered in the
inspected runtime. It does not prove which callback returned a value during
another execution or that the result was incorrect.

Treat `wp eval` as arbitrary PHP execution that bootstraps WordPress, not as a
harmless read command. Prefer existing logs, purpose-built WP-CLI commands, and
code inspection. If an exact diagnostic command is necessary, follow the
command-safety rules in `SKILL.md` and avoid dumping whole callback or runtime
objects.

## When access is limited

Record unavailable documentation or tooling honestly. Ask only for the
smallest item the reporter can obtain.

When platform logs are unavailable to the reporter, preserve site, job or
request ID, UTC time, stage or endpoint, and result. This can support a narrow
handoff.

An emergency may waive waiting for docs, not safety or ownership gates.

## Challenge weak inferences

Challenge claims that:

- API acceptance proves job completion.
- A familiar error proves the same cause or remedy.
- Current usage is the controlling configured quota.
- Overlapping jobs cannot create a race.
- User-facing `stuck` text is as strong as the failed stage.
- Polished or precise analysis validates causality.
- A workaround for one record is a safe general deletion rule.
- Historical behavior overrides the current contract.
- Similar environments have matching configuration and orchestration.
- A cron warning proves the scheduled work was missed.
- A registered callback proves it returned false or behaved incorrectly.
- Several hooks or plugins prove one shared cause.
- A historical failed-job count belongs to the suspected filter or write
  failure without event-level correlation.
- A `could_not_set` write failure left the exact state later rejected by
  duplicate prevention without tracing that event.

## Risky changes

Destructive, quota, configuration, cross-site, and repeated production changes
need target, environment, authority, dependencies, idempotency, blast radius,
success check, duration, and rollback.

## Return to the router

Return one result: resolved correction; untested owned orchestration; valid
contract mismatch; repeated managed-stage failure; stale condition; capability
decision; one broken scheduled lifecycle; warnings without failed work; or
changed boundary.

Retain useful facts when changing boundaries. Replace this reference; do not
stack it with another.
