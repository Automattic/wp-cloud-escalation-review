# Guided workflow

Use for raw, investigative, incomplete, or explicitly step-by-step work. The
router owns record and readiness; this file owns turn progression.

## Start at the first unmet gate

Check earlier gates without narrating phases:

1. **Route:** goal, candidates, document type, destination when material,
   required owner, channel, durability. Identify independent issues first.
   When no ask exists, include `analysis_or_review_note`.
2. **Define:** selected issue, current condition/decision, blocked goal, scope,
   requested action.
3. **Validate:** claim ledger, provenance, currentness, reporter work,
   documentation, zero/one technical reference.
4. **Challenge:** only after one selected issue clears earlier gates; use
   [the challenge contract](challenge.md).
5. **Readiness and draft:** resolve objections, recompute readiness, draft only
   when allowed.
6. **Final check:** compare draft with record for strength, completeness,
   relevance, safety, secrets, and writing.

Raw notes usually enter Define. A strong draft may enter Challenge only after
earlier gates actually pass. Interim blockers return one blocker and next
action/question, without challenge or draft.

## Update the compact record

Keep one authoritative state, not a transcript:

```text
Session goal:
Candidates [id, label, relationship, state, readiness, next step]:
Selected candidate:
Completed artifacts:
Remaining candidates:
```

Candidate state: `unselected|active|blocked|ready|resolved|routed_elsewhere|declined`.

Each turn:

- sanitize before recording;
- update only affected claims/fields;
- replace contradicted, stale, or superseded values;
- retain unaffected facts, parked candidates, and linked claims;
- record who verified each claim and how;
- retain challenge status (`not_reached|completed`), inline route, objections,
  and resolutions; never rerun a completed pass;
- recompute from the earliest affected gate;
- show only changed fields, controlling readiness, and next question.

Preserve desired outcome. Ask before changing outcome, owner, or risk boundary.
Repeated facts, full records, checklists, and unanswered questions are not
progress.

## Ask the next useful question

Ask one question changing route, ownership, validation, readiness, safety, or
decision. Up to three related fields may identify one event/decision; do not
mix evidence, impact, troubleshooting, and solution preference.

Keep nonterminal prose under 120 words. If new reporter work is needed, state
the action and observable result. If an existing artifact is missing, ask for
it directly. Never ask for recorded facts again.

For technical events, prefer site/domain, absolute UTC, workflow,
operation/request, observed/expected result, and direct signal when available.
Do not request external identity research when a supplied event already scopes
the decision.

## Split before selection

When independent decisions, owners, evidence contracts, mechanisms, or
outcomes remain:

1. return `Split required`;
2. list candidate labels only;
3. leave selected issue unset and reference `none`;
4. ask which candidate comes first;
5. retain others as `unselected`.

Before selection, add no destinations, troubleshooting, evidence requests, or
conditional analysis. Evidence/readiness never crosses candidates.

Do not split another error, hook, plugin, site, or possibly related step.
Keep claimed damage with its alleged mechanism until evidence separates them.
For example, keep reported `schedule_event_false` and `could_not_set` together
while their lifecycle relationship is unresolved.

After one candidate terminates, return its artifact/outcome, list remaining
labels, and ask which is next unless scope was limited. If the user knowingly
keeps independent issues in one post, use independent sections with separate
evidence, readiness, and asks; blocked material stays outside copy-ready text.

## Stop and resume correctly

A nonterminal turn stops after the smallest blocker and next question, then
resumes there. Stop a candidate when:

- ready and final check passes;
- resolved during validation;
- another known owner/process/destination controls action;
- user declines or cannot perform required reporter work.

Stopping one candidate does not stop requested parked work. When a check is
unavailable, offer only honest choices: leave claim unverified, obtain source
evidence, convert to guidance/analysis, select another candidate, or stop.

A missing destination is a routing choice, not evidence. `Belongs elsewhere`
requires a known destination. Do not draft an incident for a resolved
condition; a follow-up records change, time, result, and remaining scope.

If final comparison finds a new assertion, promoted certainty, missing fact,
unsafe detail, or material writing defect, withdraw the draft and return the
smallest blocker. Never loop through unchanged drafting.
