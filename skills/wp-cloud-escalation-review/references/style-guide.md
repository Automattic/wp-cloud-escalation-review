# Escalation writing style

Apply this guide before every user-visible response: questions, progress,
blockers, outcomes, caveats, and copy-ready drafts.

Write the shortest self-contained handoff that lets the recipient act without
reconstructing the reporter's work. Preserve necessary evidence, context,
uncertainty, impact, safety, and the requested decision.

## Speak plainly

Lead with what the reporter should do or what WP Cloud needs to decide. Use
direct verbs, familiar words, and clear subjects. Explain a material gap
without blame.

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

Prefer “check the dashboards and logs available to you,” “this is a likely
cause, but it is not confirmed,” “match this request with the platform logs,”
and “there is nothing left for WP Cloud to answer.”

Name a dashboard only when access is known. Otherwise offer useful examples
such as a host or Grafana dashboard, company panel, nginx or PHP logs, or
metrics from the WP Cloud Atomic API.

## Make questions useful

State what the supplied evidence already changed, then ask all currently known
questions that can change scope, ownership, certainty, safety, routing, or the
requested action. Group them into one focused turn. Several short questions
are better than a serial interrogation.

Do not ask for a field because a template contains it. Explain briefly why a
check matters and how to perform it when useful. Do not repeat a disputed claim
as fact in the question, quotation, or recap. Say its scope or cause is not yet
supported.

Do not respond to an undefined cause with a list of every possible log and
metric. Ask for the smallest grouped set that can choose the route. When a
blocker is clear, ask for the correction without describing the future rewrite
or repeating claims that will be removed.

Treat time as a lookup aid. Keep an adequate event time or bounded range and
time zone. Ask for greater precision only when WP Cloud cannot find the event
from the existing range and request, trace, job, or other identifier.

Once ownership and action are settled, remove unneeded proof requests. Do not
tell the reporter that extra logs would increase confidence when collecting
them would not change the result.

## Draft from verified meaning

Before editing, identify:

- selected issue or justified bundle;
- mapped sites and current state;
- observed versus expected result;
- impact and blocked goal;
- strongest sufficient evidence and useful negative results;
- remaining uncertainty or access limit; and
- one primary WP Cloud outcome.

Draft from that record, not source paragraphs. Every sentence must help the
recipient understand issue, scope, evidence, certainty, impact, ownership,
safety, lookup, or action.

Preserve decision-bearing meaning once. Do not preserve source order, duplicate
wording, exhaustive history, generic explanation, ornamental precision, or
speculation. Keep versions, code locations, trace frames, workarounds, and
history only when they change the decision.

## Open with the handoff

Lead with the verified problem, scope, impact, and request. Do not begin with
the review process, evidence taxonomy, a generic summary, or a long technical
explanation.

Use the smallest helpful structure. A normal post often needs only a useful
title, two to four short paragraphs or a few meaningful bullets, the requested
action, and an evidence artifact when justified. Do not force headings or a
template.

For code-backed platform work, present:

1. affected site or mapped sites, current impact, and workaround;
2. the shortest supported trigger-to-failure explanation;
3. what was inspected or tested and the important limitation;
4. one primary WP Cloud outcome, with only related secondary questions; and
5. a trace, code excerpt, or evidence link when it helps verification.

## Remove AI and code-review padding

Cut throat-clearing, importance theater, corporate filler, causal certainty,
recap endings, canned thanks, rhetorical questions, dramatic fragments,
decorative headings, generic tutorials, repeated framing, and conclusions
repeated after each section.

When evidence narrows a broad source claim, write only the measured scope. Do
not quote or name the rejected broader claim in the correction.

Also challenge these patterns:

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
- implementation prescriptions before the desired platform outcome; and
- several questions competing as separate primary asks.

These are review signals, not word bans. Keep exact technical language and
control-flow detail when the recipient needs it to verify or change behavior.

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
State its meaning once.

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
before implementation ideas. Keep a code suggestion, version question, or
workaround only when it directly affects the same decision.

## Compress and finish

A normal single-issue draft should usually be about 200–350 narrative words.
More than about 450 narrative words triggers another private compression pass.
Longer text is allowed when mapped sites, a justified issue bundle, safety, or
necessary explanation materially helps the recipient. Justified artifacts are
outside the narrative target.

Before returning copy, confirm:

1. The opening matches the selected issue and measured scope.
2. Every claim matches its evidence and certainty.
3. Important context and limitations survive.
4. The ask belongs to WP Cloud and fits the evidence.
5. Each conclusion and important code location appears once.
6. The artifact and narrative do not duplicate each other.
7. The text ends after the last concrete action or question.
8. No internal framework term or recognizable AI padding remains.
9. No claim rejected during review appears again, even in an instruction to
   remove or replace it.
