# Escalation writing style

Write the shortest self-contained handoff that lets the receiver act without
reconstructing reporter work. Keep evidence, impact, controls, constraints,
uncertainty, and requested decision. The router owns readiness and safety.

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
