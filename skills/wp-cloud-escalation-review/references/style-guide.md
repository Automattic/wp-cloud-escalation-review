# Escalation writing style

Write the shortest self-contained handoff that lets the receiver act without
reconstructing reporter work. Keep evidence, impact, controls, constraints,
uncertainty, and requested decision. The router owns readiness and safety.

## Use this style for every response

Apply this guide to commentary, questions, blockers, outcomes, and review notes,
not only the final escalation draft.

Lead with what the HE should do or decide. Use direct verbs and familiar words.
Describe an evidence gap without blaming the reporter, explain why the check
matters, ask one focused question, and stop.

Keep routing, readiness, challenge status, reason codes, evidence classes, and
reference selection private. Do not announce skill loading, Direct or Guided
paths, documentation research, reference reads, or challenge work. If
compatibility requires a `Readiness:` line, use one short line and immediately
state the practical decision. Do not print `Blocking:`, `Challenged:`,
`Checked:`, phase names, or a review checklist.

Translate internal analysis into ordinary language. Avoid phrases such as
“active causal investigation,” “smallest reporter-owned evidence,” “bounded
incident window,” “coherent causal hypothesis,” “clears the earlier
attribution blocker,” “HTTP-routing review and challenge pass,” “reported
platform behavior,” and “No further WP Cloud decision appears outstanding.”
Prefer “check the dashboards and logs you can access for this period,” “this is
a likely cause, but it is not confirmed,” and “there is nothing left for WP
Cloud to answer.”

Do not name an internal dashboard unless the reporter is known to have access.
When access is unknown, refer to “the dashboards and logs available to you.”
Offer examples such as a host or Grafana dashboard, company panel, nginx or PHP
logs, or metrics from the WP Cloud Atomic API only when they help the reader
find an equivalent.

Prefer “match this request with the platform logs” or “these happened around
the same time” over the abstract noun “correlation” when either is accurate.
Ask “which URL and HTTP method failed?” instead of “what request class was
affected?” Say “information only WP Cloud can access” instead of
“receiver-side visibility.” Keep technical terminology only when the HE or
receiver needs it. Do not use “request class,” “receiver-side,”
“receiver-only,” or “reporter-visible evidence” in any user-facing response.

Treat time as a lookup aid, not a ritual. Keep an adequate bounded window.
Quietly normalize a known time zone. Ask for a more exact time only when no
existing request, trace, or job ID can identify the event WP Cloud must find.

Once ownership and action are settled, remove unneeded proof requests from the
response. Do not explain that extra logs would increase confidence when the
reader does not need to collect them.

Show progress between questions. State the useful conclusion from the latest
answer, then ask only for the next check that could change the decision. Do not
turn missing fields or conflicting customer reports into an interrogation.
Test a disputed claim without repeating it as though it were true.

Describe warnings as warnings until an observable failure is established.
Prefer “What scheduled work did not happen?” over questions about which
callback returned a value. Do not call warnings “damage,” “false positives,” or
“broken recurring work” without a mapped failed result. Challenge the exact
claims “false positive,” “breaking recurring cron,” and “real-world damage”
when no failed outcome supports them.

## Draft from the record

Inventory the selected issue before editing:

- observed condition or requested decision;
- affected scope and blocked goal;
- verified basis, including useful negative results;
- remaining uncertainty;
- requested outcome at the WP Cloud boundary.

Draft from this inventory, not source paragraphs. Every sentence must establish
issue, scope, evidence, uncertainty, impact, risk, ownership, or action.

Mark facts, negative findings, conditions, warnings, decisions, risks,
mitigations, and actions as protected anchors. Preserve each anchor's actor,
scope, negation, attribution, certainty, condition, consequence, and force.
Preserve useful directness, candor, and deliberate roughness.

Keep exact errors, identifiers, UTC times, request details, commands,
measurements, and uncertainty only when they change the decision.

## Open with the handoff

Incident: observed condition, scope, verified basis, request.

> Site `<site-id>` returned HTTP 429 for the vendor webhook. We reproduced two
> failures at `<UTC times>` and observed `<limit-reason>`. Can WP Cloud review
> these events and confirm the recorded protection result?

Capability/policy: requested change, current limit, verified need, decision.

> We request `<capability>` for `<scope>`. The workaround takes `<measured
> effort>`. Can WP Cloud decide whether to prioritize the change?

Never invent an outage, site, timestamp, or request. Title must match record
scope and certainty. Avoid unsupported `platform bug`, `false positive`,
`root cause`, or `pool issue`.

## Match ask to evidence

Ask for the smallest unresolved WP Cloud action:

- interpret platform-only state;
- correlate exact receiver-only events;
- review a narrow protection change after traffic/risk identification;
- correct platform-managed behavior contradicting repeatable tests;
- inspect an exact managed job stage;
- decide on a missing capability.

Do not ask WP Cloud to perform first reproduction, inspect reporter-visible
evidence, extract facts from a memo, optimize a healthy site without a platform
question, or validate unrelated issues.

State outcome and decision before remedies. Retain evidence-backed candidate
controls only when they expose different safety, availability, or durability
tradeoffs; name demonstrated limits without prescribing WP Cloud's mechanism.
Do not append an unrequested change option to correlation/review.

## Keep decision-bearing detail

One direct platform error, bounded aggregate, or protection reason may already
establish action. Do not add ceremonial timestamps, URLs, plugin checks, or
generic troubleshooting.

Use more detail only when it changes the decision:

- shortest ordered trace establishing impact;
- minimal stack boundary;
- controlled comparison and held variables;
- multi-site pattern with denominator;
- turning-point timeline showing recurrence, control effect, owner routing, or
  ruled-out layers;
- success, review, rollback controls for executable change.

Keep decisive excerpts. Link large artifacts, state what they prove, and retain
enough detail that the receiver need not reopen them to understand the claim.
Precision is not relevance. Remove unrelated hashes, counts, classifier fields,
comparison sites, and history.

Always include a supplied, shareable link to the relevant logs, dashboard view,
or saved query. For traffic and rate-limit claims, link the exact view or query
that supports the count or protection reason and say what it shows. A count,
percentage, or “per day” claim must name its absolute bounded interval and
denominator. Preserve the same fixed interval in whatever log, saved-search,
dashboard, or evidence link is available; do not rely on a drifting “last 24
hours” view. If the reporter cannot share a link, keep a short excerpt or
lookup details instead; the missing link is not a blocker. Do not ask the
reporter to sanitize ordinary traffic details. Remove only actual
authentication material or a specific sensitive personal or financial value.

For scheduled work, prefer one mapped hook/error example plus runtime limit.
Remove diagnostic installation history, raw filter inventories, and extra
hooks unless they change action.

## Edit source material, not shape

Customer, vendor, and generated analysis are evidence. Preserve facts and
useful caveats, not structure or confidence:

- separate supplied claims from reporter validation;
- merge repeated conclusions;
- remove generic explanations and advocacy;
- remove untested causes/remedies;
- keep reporter conclusion and remaining question.

Remove instructional brackets, unused headings, empty fields, unchecked
checklists, and editorial notes. Add headings/bullets only for navigation,
parallel scanning, safety, or a real procedure. Long source does not justify
long review.

## Remove AI-style padding

Review observable patterns, not authorship. Cut throat-clearing, importance
theater, causal certainty, corporate filler, repeated framing, recap endings,
canned thanks, rhetorical questions, dramatic fragments, metaphorical closers,
emoji headings, decorative bold, and full-report blockquotes.

Remove generic explanations of HTTP, DNS, caching, webhooks, fingerprints,
workers, or security controls. Preserve exact quotations, errors, product
names, and necessary terminology.

Sentences over 25 words are review signals, not failures. Prefer clear
subjects, direct verbs, familiar words, and one main statement. Break these
preferences before making text false, incomplete, unsafe, or flat.

## Present major-change value

When prioritization needs it, retain only decision-changing facts: validated
demand, affected customers/sites/workflows, authorized revenue/value, support
volume, workaround cost, deadline/commitment, churn risk, expected benefit, and
broader demand. Business value changes priority, never cause or safety.

Executable production changes also need target/environment, current/requested
state, authorization, duration/review point, blast radius, success measure,
rollback owner, and trigger. Prioritization proposals need no invented
implementation controls.

## Match the destination

A durable standalone technical record needs available decision-bearing title,
issue/decision, evidence, UTC lookup tuple, durable link, impact mechanism,
tested controls, constraints, negative findings, scope, and ask.

A same-issue reply adds only new evidence, correction, answer, or result.
Changed issue/decision gets a linked durable record.

Compact chat works only when one owner can close one immediate action without
persisting evidence, authorization, decision, or outcome. Urgent coordination
may begin there; lasting facts still need durable backfill.

Keep only audience-facing caveats inside copy-ready text. Keep review metadata
and editorial notes outside. When independent issues knowingly share a post,
give each separate evidence, readiness, and ask.

## Record outcomes

After change/resolution, record what changed, when, observed result, tested
scope, and remaining limitation. Use UTC when correlation matters. Never write
only `fixed`, `resolved`, or `working now`.

## Editing check

Before returning copy-ready text:

1. Title/opening match selected issue.
2. Every claim matches evidence and uncertainty.
3. Decisive details survive; irrelevant precision does not.
4. Ask belongs to WP Cloud and fits proof.
5. Each conclusion appears once.
6. Business value stays separate from cause.
7. Destination preserves needed context.
8. Text ends after last concrete action/question.
9. Every decision-bearing record item survives directly or equivalently.
10. An in-order source sweep preserves every protected anchor.
11. No unsupported relationship, consensus, sequence, heading, list, recap, or
    structural symmetry was added.
