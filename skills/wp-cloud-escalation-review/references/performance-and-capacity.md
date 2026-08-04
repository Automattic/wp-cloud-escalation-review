# Performance and capacity

Use this reference when measured performance, workload cost, or a capacity
decision controls the next action. It returns findings to the router; it does
not assign readiness.

## Select this reference

Select it for latency, queueing, resource pressure, cache behavior, workload
shape, load-test safety, or a capacity or runtime configuration change.

Do not select it merely because a report mentions slowness, workers, a clone,
caching, migration, streaming, or an HTTP status. Route by the controlling
decision:

- Request identity or protection response: HTTP and automation.
- Pre-response connectivity: domains, network, and protocol access.
- WP Cloud Atomic API contract or managed job: WP Cloud Atomic API and managed
  operations.
- Sensitive compromise or disclosure: security handoffs.

Split separate incident, optimization, capability, and commercial questions.

## Decisive evidence

Use only facts that can change the decision:

- Affected workflow, method/path, or traffic slice and its observed effect.
- A bounded UTC window with Metrics, logs, and traces aligned to it.
- End-to-end time separated from queueing, PHP, database, external-call, and
  client time when available.
- Current capacity configuration and recorded runtime states.
- Saturation, backlog, failures, or latency from the same window.
- Auto Defensive Mode state and the exact request effect in that same
  site-specific window when it is part of the claim.
- Relevant cache layer, hit or miss result, and cache-abort reason.
- Workload rate, concurrency, retries, duplication, and cacheability.
- A baseline, denominator, or controlled comparison for aggregate claims.
- For a lasting or sized change: current and requested values, calculation,
  duration, success measure, review point, and rollback condition. A bounded
  diagnostic test may instead state why its step is safe and what result would
  distinguish.

A small repeatable test that contradicts configured platform behavior can be
enough. Do not demand a ceremonial checklist after the decisive fact is known.

A bounded diagnostic test may proceed when current traces show queueing,
remaining telemetry is available only to WP Cloud, and value, approval, scope,
duration, success measure, and rollback are present. Keep cause suspected and
state that access limit as a caveat.

If no evidence available to the reporter yet connects the symptom to the proposed
capacity control, ask for that smallest check before collecting change
controls. Impact alone does not justify the requested setting.

## Reporter-owned checks

- Review current documentation for capacity, cache, and runtime-state
  semantics.
- Inspect time-bounded Metrics, request logs, APM, PHP errors, cache data, and
  relevant application configuration.
- Identify expensive, duplicated, malformed, unexpected, or uncached request
  classes.
- Check queries and external calls when they could explain the measured delay.
- Reproduce the workflow or run a controlled comparison when safe.
- Record each performed check and what it showed.
- Narrow the report to the smallest unresolved WP Cloud boundary.

A healthy site with a general optimization request remains with the host or
site owner until the analysis identifies a specific platform constraint.

When exhaustion activates protection, determine whether an exempted request
would succeed, hit another limit, or add load. Separate capacity correction
from deciding how the affected traffic should be handled.

## When access is limited

Never require a tool the reporter cannot access. Ask what is available and use
the nearest reliable substitute.

When platform telemetry is available only to WP Cloud, provide exact sites,
UTC windows, affected methods, paths, callers or workflows, and the results the
reporter can see for matching. Missing platform-only data is an access limit,
not proof of a platform cause.
It also does not block a bounded handoff after the reporter has exhausted its
own layer.

## Challenge weak inferences

Challenge claims that:

- A quiet clone isolates hardware or pool behavior.
- Sequential client tests remove server-side contention.
- Another host is comparable without matching code, traffic, cache state,
  configuration, geography, and method.
- Low database time or an incomplete trace assigns all remaining time to
  infrastructure.
- Lifetime counters prove a current incident.
- A command timing isolates one operation when it boots the application too.
- More workers make one slow request faster or guarantee burst capacity.
- Page, object, edge, and static caches are interchangeable.
- A supported architecture supports every workload shape.
- `Root cause` is established without profiling the slow flow.
- A browser challenge alone proves Auto Defensive Mode caused the event.
- Letting an API or webhook request bypass protection means the origin can
  process it during worker exhaustion.

State separately what a comparison demonstrates and what it merely suggests.

## Risky changes

Reporter-executed or prescriptive capacity increases, pool moves,
resource-limit changes, cache bypasses, protection exceptions, and production
load tests need a verified target and environment, expected mechanism,
authorization, narrow scope and duration, safety limit, success measure, review
point, rollback trigger, and owner.

For a WP Cloud-owned assessment or adjustment request, require the observed
resource state, affected target and workflow, desired outcome, and narrow
scope. WP Cloud may own the exact mechanism, monitoring, review point, and
rollback.

More admitted concurrency can amplify expensive work. Cache changes need
correctness checks for personalized or stale content. A load test must state
what it measures and omits, its ceiling, abort condition, environment, and
review owner.

## Return to the router

Return one result: a supported platform contradiction or capacity decision;
the smallest useful reporter check; a condition resolved during testing; work
that remains with the application or another owner; or a bounded request for
matching in platform logs.

If evidence changes the controlling boundary, retain useful facts and replace
this reference. Do not stack references.
