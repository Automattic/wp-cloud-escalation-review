---
title: Friendly, decision-focused escalation reviews
type: fix
date: 2026-07-29
status: ready
---

# Friendly, decision-focused escalation reviews

## Goal

Keep the skill’s strong escalation judgment while making every message to the HE clear, friendly, precise, and useful.

The improved skill should ask only for evidence that can change the route, owner, risk, or next action. It should stop as soon as no WP Cloud decision or action remains, without exposing its internal workflow or drafting an unnecessary escalation.

## What must stay true

- Safety, secret handling, authorization, issue separation, attribution, and change-safety checks remain intact.
- Direct/Guided routing, readiness states, gates, reason codes, challenge state, and reference selection remain internal.
- The skill still withholds drafts for unresolved, alternate-owner, split, unsafe, or no-post cases.
- Exact event details remain appropriate when WP Cloud is the only team that can perform the remaining correlation.
- A symptom being resolved is not enough by itself to stop. Stop only when no WP Cloud decision or action remains.
- Resolution-record behavior is unchanged.
- All examples and evaluation fixtures remain synthetic and safe for the public repository.
- The installable skill remains client-neutral: behavioral instructions live in `SKILL.md` and shared references, not in Codex- or Claude-only configuration.
- Codex and Claude may use different evaluation adapters, but they must be scored against the same behavior contract.

## Changes

### 1. Use the existing escalation style guide for every user-visible message

Make `references/style-guide.md` the single writing standard for commentary, questions, blockers, review notes, resolutions, and copy-ready drafts. It already governs generated escalation reports; load and apply it before any user-visible response, not only when a draft is allowed.

Do not create a second, competing conversation style guide. Add only the missing conversational rules to the existing guide, then have the main skill and Guided workflow point to it.

The skill should:

- lead with the practical outcome;
- use familiar, concrete language;
- describe missing evidence neutrally, without blaming the reporter;
- explain briefly why a requested check matters;
- ask no more than one focused question at a time;
- stop after the decision, action, or question;
- keep workflow phases, challenge state, evidence classes, and internal checks out of user-facing prose;
- avoid abstract process language when ordinary wording says the same thing more clearly.

If the output contract still requires a readiness line, allow exactly one short line such as `Readiness: Resolved during validation`. It must be followed immediately by the practical decision. Do not print `Blocking`, `Challenged`, `Checked`, workflow phases, evidence classes, or a review checklist.

Add the observed failures to the style and evaluation examples. User-facing responses should not say:

- “active causal investigation”;
- “smallest reporter-owned evidence”;
- “bounded incident window”;
- “coherent causal hypothesis”;
- “clears the earlier attribution blocker”;
- “HTTP-routing review and challenge pass”;
- “reported platform behavior”;
- “No further WP Cloud decision appears outstanding.”

Prefer direct alternatives such as “check the dashboard for this period,” “this is a likely cause, but it is not confirmed,” and “there is nothing left for WP Cloud to answer.” Prefer “match this request with the platform logs” or “these happened around the same time” over the abstract noun “correlation” unless that technical term is genuinely needed in copy-ready text.

For ready work, keep `Copy/paste` as the clear boundary around the draft. Do not surround it with an internal checklist.

Files:

- `skills/wp-cloud-escalation-review/SKILL.md`
- `skills/wp-cloud-escalation-review/references/style-guide.md`
- `skills/wp-cloud-escalation-review/references/guided-workflow.md`
- `skills/wp-cloud-escalation-review/references/challenge.md`

### 2. Reorder Guided review around the decision that remains

After sanitizing the input, separating independent issues, and handling any safety concern, use this order:

1. Is the issue still current?
2. What decision or action does WP Cloud still own?
3. Can one reporter-accessible dashboard, Metrics, APM, log, or application check settle it?
4. If not, does WP Cloud need an exact event tuple to perform the remaining correlation?
5. Only while WP Cloud work still remains, load public documentation and one relevant technical reference.
6. Challenge only work that is otherwise ready, then draft.

Recompute the outcome after every answer. If no WP Cloud decision or action remains, say plainly that no escalation should be posted and stop before documentation research, technical-reference loading, challenge, or drafting.

Additional rules:

- For a broad impact claim, prefer affected count, denominator or request class, and a direct routing/error signal before asking for one raw event.
- When the site and time window are already known, begin with the single-site dashboard or equivalent reporter-visible summary rather than asking for a representative event.
- Treat nearby commands, host changes, timestamps, and similar facts as coincidence or lookup context only. Do not turn them into migration, failover, or causality without direct evidence.
- Do not frame the next check around the reporter’s unproven theory—for example, whether an event matched a “host move or another managed operation.” Ask what the dashboard directly shows.
- A plausible application cause may remain “likely” or “possible” when stronger proof would not change the owner or next action.
- Do not demand a perfect end-to-end log chain merely to increase confidence after the decision is already settled.
- Do not imply access to a private dashboard. Ask for the type of reporter-visible state needed.
- Do not load general failover documentation after direct evidence has already explained the event and settled ownership. General failover behavior must not be used to infer that a specific request followed that mechanism.

Expected response shapes:

> Before escalating, please check the single-site dashboard for the affected period. What does it show about how many requests failed, which paths were affected, and why any requests were sent to the secondary server?
>
> The nearby SSH activity happened around the same time, but we do not yet have evidence that it caused the failures.

After receiving a plausible site-code explanation:

> This gives us a likely site-code cause, but first: is the problem still happening after the code was fixed, and what question still needs WP Cloud to answer?
>
> If the issue stopped and no platform action remains, we may not need to post an escalation.

For a resolved review:

> Readiness: Resolved during validation
>
> Don’t post this escalation. The additional evidence answers the original question, narrows the affected scope, and leaves the remaining work with the site developer.

Files:

- `skills/wp-cloud-escalation-review/SKILL.md`
- `skills/wp-cloud-escalation-review/references/guided-workflow.md`
- `skills/wp-cloud-escalation-review/references/documentation-routing.md`
- `skills/wp-cloud-escalation-review/references/http-and-automation.md`

### 3. Evaluate the whole interaction during repository test runs

This section applies only to the opt-in evaluation tools under `scripts/` and `evals/`. It does not add event capture, subprocesses, result files, or telemetry to normal skill usage.

The current evaluator sees only the final response and requires a literal `Readiness:` line. Replace that contract with a client-neutral result model and thin Codex and Claude adapters.

During evaluation runs:

- the Codex adapter captures `codex exec --json` plus its final-message output;
- the Claude adapter captures Claude Code’s stream-JSON output and final result;
- each adapter stages the same exact public skill manifest in that client’s standard project skill location;
- both adapters normalize into the same versioned result and use the same scorer.

The normalized result contains:

- the provider and adapter version;
- assistant messages in order, including commentary and final text;
- the authoritative final response;
- observable conditionally opened reference paths;
- sanitized diagnostics when parsing fails.

The parser must ignore unknown event types safely, sanitize before writing results, and fail clearly if it cannot recover a final response.

Provider-specific event names and command flags must remain inside their adapters. Fixture expectations, scoring, and the installable skill must not depend on Codex or Claude event vocabulary.

Replace the fixture expectation shape with:

- `outcome`: `ready`, `ready_with_caveat`, `needs_reporter_check`, `needs_existing_evidence`, `split`, `alternate_owner`, or `no_post`;
- `draft`: `required` or `forbidden`;
- message expectations: required ideas, forbidden phrases, and maximum question count;
- reference expectations: required and forbidden conditional references.

The readiness line may be present for compatibility, but the scorer must determine the outcome from the complete response rather than require or trust that literal label.

Score the full set of assistant messages for:

- the practical outcome;
- draft presence;
- the next action or question;
- neutral, concrete wording;
- unsupported mechanisms;
- exposed workflow jargon;
- unnecessary reference use.

Apply forbidden-phrase checks to every assistant message, including commentary. Add positive checks for plain dashboard/currentness questions so passing does not mean merely swapping one set of jargon for another.

Keep fixture expectations out of model prompts, projected inputs, and staged skill files.

Files:

- `scripts/run_evaluations.py`
- `scripts/evaluate.py`
- `scripts/score_evaluations.py`
- `scripts/validate.py`
- `tests/test_evaluation_tools.py`
- `evals/README.md`
- `README.md`

### 4. Add focused synthetic regressions

Add a small development case for fast iteration and broader regression cases for:

- a broad reported impact plus an unexplained host correlation: ask for the reporter-visible aggregate/direct signal and do not invent a mechanism;
- the known site and time window are sufficient to begin a single-site dashboard check: do not ask for a representative raw event first;
- nearby SSH or host activity: state that timing alone does not establish cause, and do not ask whether the event matched a migration, host move, or managed operation;
- a plausible application cause with unknown currentness or WP Cloud action: ask about those before requesting a multi-log proof chain;
- a plausible cause that would become more certain with three matching logs but would not change ownership: keep the claim qualified and stop instead of demanding the full chain;
- evidence that explains the platform behavior and leaves no WP Cloud action: clearly recommend not posting, preserve uncertainty around any unconfirmed cause, and open no documentation or technical reference;
- general failover documentation that resembles, but does not establish, the event-specific retry path: do not use it to strengthen the case or final explanation;
- a current receiver-only correlation: retain the exact lookup tuple and allow the appropriate technical reference;
- a blocked review whose final answer is clean but whose commentary contains workflow jargon: fail the evaluation;
- each observed jargon phrase listed in the style section: fail if it appears anywhere in the interaction;
- a ready review: return a concise decision and a substantive `Copy/paste` block;
- existing split, alternate-owner, secret-containment, unsafe-change, ready-with-caveat, and no-draft behavior;
- provider parity: the same synthetic case must produce the same scored outcome through the Codex and Claude adapters even when their raw event streams differ.

Use invented labels, dates, counts, paths, and errors only. Do not reproduce the real incident, site, identifiers, internal tools, or private links.

Files:

- `evals/development.json`
- `evals/regression.json`
- `tests/test_evaluation_tools.py`
- `evals/README.md`

## One-shot implementation order

Treat the skill-output change and evaluator change as one contract migration; do not consider an intermediate state complete.

1. Add characterization tests for Codex and Claude event streams, result parsing, sanitization, and expectation isolation.
2. Add the client-neutral result envelope, semantic scorer, and Codex/Claude adapters while temporarily preserving enough compatibility to run the existing suite.
3. Update the skill language and Guided decision order.
4. Migrate fixture validation and expectations, remove the literal `Readiness:` dependency, and add the new synthetic cases.
5. Run deterministic checks, then development and regression evaluations through both clients.
6. Remove temporary compatibility code and abandoned schema/parser paths before finishing.

## Verification

Run:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/evaluate.py development --dry-run --provider codex
python3 scripts/evaluate.py regression --dry-run --provider codex
python3 scripts/evaluate.py development --provider codex
python3 scripts/evaluate.py regression --provider codex
python3 scripts/evaluate.py development --provider claude
python3 scripts/evaluate.py regression --provider claude
git diff --check
```

Manually confirm:

- no user-visible message exposes the internal workflow;
- the existing escalation style guide governs both conversational responses and generated reports;
- questions are friendly, neutral, and decision-bearing;
- resolved or actionless work performs no optional research and produces no draft;
- a resolved symptom with remaining WP Cloud work does not stop early;
- receiver-only correlation still requests the exact information WP Cloud needs;
- the public diff contains no private case reconstruction, internal tool name, real identifier, or resolution-record expansion;
- installation and usage instructions work for both Codex and Claude, with no behavioral rule available to only one client.

## Done when

- The skill reaches the same safe routing decisions with clearer and shorter HE-facing language.
- It asks currentness and remaining WP Cloud ownership before forensic completeness.
- It never turns correlation into an unsupported mechanism.
- It stops only when no WP Cloud decision or action remains.
- The evaluator catches bad commentary, needless research, exposed jargon, excessive questions, unsupported claims, and incorrect draft behavior.
- Codex and Claude normalize into the same evaluation contract and pass the same development and regression suites.
- All deterministic checks and both clients’ model-evaluation suites pass.
