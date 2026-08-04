# Escalation writing style

This guide is a required correctness and readiness check, not optional polish.
Apply it before every visible question, update, blocker, outcome, caveat, and
draft, then again before returning. No request or client waives it.
Before copy, state only the decision and any material caveat; do not recap the
readiness checklist.
Do not add a research-access caveat unless it changes what the recipient can
trust or do.

Write the shortest self-contained handoff that lets the recipient act without
reconstructing the reporter's work. Preserve necessary evidence, context,
uncertainty, impact, safety, and the requested decision.

## Speak plainly

Lead with what the reporter should do or what WP Cloud needs to decide. Use
direct verbs, familiar words, and clear subjects. Explain a material gap
without blame.

Use one stable term for each thing and prefer a short familiar word when it
keeps the exact technical meaning. Use active voice when the actor is known;
use passive voice rather than inventing an actor. Keep complete subjects and
verbs, one main topic per sentence and paragraph, related material together,
and a material condition before its result. Use necessary jargon consistently
and explain it once when the recipient may not know it.

Treat roughly 25 words as a review signal, not a hard limit. Split only when
the relationship stays clear. Accuracy, safety, necessary terms, and natural
reading take priority.

Keep workflow, readiness, challenge status, reason codes, evidence classes,
and reference selection private. Never announce skill loading, paths, phases,
research, reference reads, or challenge work. Do not print internal labels
such as `Blocking:`, `Challenged:`, or `Checked:`.

Translate internal analysis into ordinary language. Never use these phrases in
visible text, even while explaining that they should be removed:

- active causal investigation;
- smallest reporter-owned evidence;
- bounded incident window;
- coherent causal hypothesis;
- clears the attribution blocker;
- challenge pass;
- reported platform behavior;
- request class when URL, method, caller, or traffic is clearer;
- receiver-only or receiver-side;
- reporter-visible evidence; or
- no further WP Cloud decision appears outstanding.

Name a dashboard only when access is known. Otherwise offer useful examples
such as a host or Grafana dashboard, company panel, nginx or PHP logs, or
metrics from the WP Cloud Atomic API.

## Make questions useful

State what the evidence changed. Ask all known questions that can change scope,
ownership, certainty, safety, routing, or action in one focused turn.

Ask only for fields that matter and explain why or how when useful. Do not
repeat a disputed claim as fact; say its scope or cause is not yet supported.

For an undefined cause, ask for the smallest grouped set that can choose the
route. When a blocker is clear, ask for the correction without previewing the
rewrite or repeating rejected claims.

Treat time as a lookup aid. Keep an adequate event time or bounded range and
time zone. Ask for greater precision only when WP Cloud cannot find the event
from the existing range and request, trace, job, or other identifier.

Once ownership and action are settled, remove proof requests that cannot change
the result.

## Draft from verified meaning

Reduce the source to the selected issue or justified bundle, mapped sites and
current state, observed and expected results, impact, strongest evidence,
important uncertainty or access limit, and one primary WP Cloud outcome. Draft
from that record, not source order.

Lead with the verified problem, measured scope, impact, and request. Every
sentence must help with evidence, certainty, ownership, safety, lookup, or
action. Preserve each fact once. Keep history, versions, code locations, trace
frames, and workarounds only when they change the decision.

Use the smallest helpful structure; do not force headings or a template. For
code-backed work, keep one short trigger-to-failure explanation, what was
checked, the important limitation, one outcome, and a useful artifact when
needed.

## Remove AI and code-review padding

Cut throat-clearing, faux-insight or rhetorical setups, canned contrasts,
negative lists, colon reveals, importance claims, dramatic fragments, repeated
framing, recaps, stale metaphors, idioms, figures of speech, and hollow endings.
State the fact or effect directly.

Prefer concrete nouns and direct verbs. Replace `serves as`, `leverage`,
`utilize`, `facilitate`, and trailing `highlighting` or `underscoring` clauses
when plain words keep the meaning. Remove superficial `reflecting` and
`showcasing` clauses too. Name material sources; remove vague attribution,
synonym cycling, and robotic sentence patterns.
Prefer plain `is`, `has`, `uses`, `failed`, or `returned` when accurate.

Use formatting only when it improves scanning. Avoid decorative headings,
bold, emoji, and em dashes used for cadence. End at the last result,
limitation, request, or action.

When evidence narrows a broad source claim, write only the measured scope. Do
not quote or name the rejected broader claim in the correction. Do not announce
edits or removed or unsupported source claims.

Also challenge these patterns:

- forensic labels and editorial asides such as `Entry point`, `Trigger
  condition`, or `that frame is incidental` when the direct fact is enough;
- call-frame growth, stack mutation, callback internals, and other execution
  mechanics that do not change verification, ownership, safety, or action;
- `does not rule out` language that defends a theory instead of stating the
  useful limit of the missing evidence;
- long prose chains of “calls,” “routes through,” “re-enters,” “falls through,”
  and “returns” when a short explanation plus the trace is enough;
- the same file, line, callback, version gate, missing guard, or workaround
  repeated under several headings;
- separate Description, Mechanism, Evidence, Related Findings, and
  Troubleshooting sections that carry the same proof;
- repeated “confirmed / observed / inferred” prefixes when normal prose can
  express certainty once;
- “site-wide,” “all requests,” “the only,” “nothing,” or “without bound”
  without a precise supported population;
- bold or standalone code-review verdicts that introduce another issue without
  its own scope, evidence, impact, owner, and request;
- implementation prescriptions before the desired platform outcome; and
- several questions competing as separate primary asks.

These AI patterns are prohibited when they add padding or narrate the analysis.
This does not ban exact technical language or control-flow detail the recipient
needs to verify or change behavior.

## Keep sufficient evidence

Use the strongest sufficient evidence, not the shortest possible evidence.
Preserve qualifications, negative results, reproduction limits, and access
boundaries that prevent a false conclusion.

Always retain a supplied shareable evidence link when it helps verification or
lookup, and say what it supports. Counts, percentages, and rates need a fixed
bounded interval and denominator. A missing shareable link is not a blocker
when an excerpt or lookup tuple is sufficient.

Logs, traces, code, queries, requests, and responses may remain inline or be
linked. Do not prefer one form universally. A large artifact must be relevant,
mapped to the correct site and time, interpretable, safe, and non-duplicative.
State its meaning once. Use a plain heading such as `Stack trace` when helpful.

When retaining a full trace, summarize only the frames that establish the entry
point, repeating loop or failure boundary, and platform-owned code. Do not
narrate every frame and then reproduce the sequence. Keep an omission or
sanitization note only when it changes interpretation.

If the source states that the issue was not reproduced, say “not reproduced”
or an equally direct phrase. “Not confirmed” describes certainty but does not
preserve reproduction status.

Use screenshots only for an interface state or visual error that text would
lose. Use a non-production example only when it safely reproduces a complex
issue. For domain and network issues, include only commands and results that
test the claimed phase.

Do not ask the reporter to sanitize ordinary traffic. Remove only actual
authentication material or a specific unauthorized sensitive value.

## Match claims and asks to evidence

Describe warnings as warnings until a failed outcome is shown. Do not call them
false positives, broken recurring work, or real-world damage without mapped
failed work. When no failed scheduled result is shown, ask only which expected
work failed and what its observed result was. Do not ask about callback
attribution or diagnostics yet.

Separate observed facts, likely triggers, and confirmed causes. A workaround
can support a likely trigger without proving the full chain. Nearby activity,
precise prose, or repeated timestamps do not prove causality.

Challenge broad scope with measured scope. Map every site and identifier. If a
later site ID or domain conflicts with the opening, clarify whether it is an
error or an intentional additional site.

When the affected site and time range are already known, test a broad traffic
claim with the available dashboard or log summary first: how many failed out
of how many, which URL and method, and the recorded reason when available. Do
not ask for a full incident packet before that check shows what else matters.

Ask for the smallest unresolved WP Cloud action. Lead with the desired outcome
before implementation ideas. Do not turn a proposed guard, callback shape, or
version gate into the request unless WP Cloud needs that detail to decide or
act. Keep a code suggestion, version question, or workaround only when it
directly affects the same decision.

## Compress and finish

A normal single-issue draft should usually be about 200–350 narrative words.
More than about 450 narrative words triggers another private compression pass.
Longer text is allowed when mapped sites, a justified issue bundle, safety, or
necessary explanation materially helps the recipient. Justified artifacts are
outside the narrative target.

Before returning copy, confirm:

1. Does every sentence, heading, list, and qualifier add a fact, limitation,
   evidence, safety boundary, or action the recipient needs?
2. Are terms stable, sources clear, verbs direct, rhythm natural, and
   formatting functional, with no canned setup, puffery, recap, or em-dash
   cadence?
3. The opening matches the selected issue and measured scope.
4. Every claim matches its evidence and certainty.
5. Observed and expected results, important context, and limitations survive.
6. The ask belongs to WP Cloud and fits the evidence.
7. Each conclusion and important code location appears once.
8. The artifact and narrative do not duplicate each other.
9. The text ends after the last concrete action or question.
10. No internal framework term or recognizable AI padding remains.
11. No claim rejected during review appears again, even in an instruction to
   remove or replace it.
