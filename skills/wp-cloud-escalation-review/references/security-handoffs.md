# Security handoffs

Use this reference only when containment, sensitive incident handling, or
authorized disclosure controls the next action. It returns findings to the
router; it does not assign readiness.

## Select this reference

Select it for a suspected vulnerability, compromise, identity abuse, or
credential exposure that needs containment, evidence preservation, or a
restricted route.

Do not select it for an ordinary WAF response, virtual-patch event, security
plugin symptom, or protocol login failure unless evidence establishes a
sensitive incident. Split independent security and availability issues.

## Contain and preserve

Containment takes priority over a perfect report. When safe and permitted,
preserve hashes, sanitized paths, ownership, UTC times, relevant logs, and
artifact metadata before removal. Record every containment or cleanup action
and distinguish evidence collected before it from results seen afterward.

Urgency does not authorize a broad exception, disabled control, destructive
action, or unbounded production change.

## Decisive evidence

Collect only applicable facts:

- First known, latest, and representative UTC times.
- Atomic Site ID for every affected site, domains, accounts, and confirmed
  scope.
- Current state: active, contained, cleaned, recurring, or not reproducible.
- Observed unauthorized behavior, separate from the suspected access path.
- Sanitized artifact metadata and preserved log sources.
- Scanner or investigation method, run time, and result.
- Containment actions and observed post-action result.
- Exact WP Cloud evidence, correlation, or boundary decision requested.

## Reporter-owned checks

Record completed, incomplete, and inaccessible checks across applicable
identity layers: WordPress administrators, reset and mail evidence, active
sessions, application credentials, SSH or SFTP, provider-console access,
email security, and verified 2FA state.

Do not call cleanup, rotation, session invalidation, or scanner coverage
complete without evidence.

## Minimum disclosure

Use the current approved public security process for vulnerability material,
not a routine support request. Do not invent or expose a non-public route.

Apply the shared secret rule before records, tools, challenge inputs, traces,
or output. Never ask for authentication material. Preserve useful domains,
Atomic Site IDs, account labels, UTC times, hashes, public keys, customer
context, and sanitized logs.

In a mixed artifact, remove only the unsafe value and retain the useful shape
with a typed marker. Keep exploit payloads and sensitive reproduction material
out of ordinary channels. Share only what the authorized receiver needs.

If actual authentication material was supplied, sanitizing it does not complete
containment. Return `Reporter action required` without copy-ready text until
revocation or rotation and affected-session review are confirmed.
While containment remains open, route it as `reporter /
reporter_investigation / restricted_security / restricted_durable`.

Authentication material takes precedence over protocol troubleshooting. Do not
load a domain, SSH, or SFTP reference merely because the unsafe artifact came
from a connection attempt.

## When access is limited

Do not demand logs the reporter cannot access. Provide the smallest lookup
packet:
site or account, UTC window, sanitized artifact identity, observed behavior,
and reporter-owned results.

An active containment handoff can proceed without waiting for unavailable
documentation. Secret, authorization, route, current-state, and change-safety
checks still apply.

## Challenge weak inferences

Challenge claims that:

- A browser, device, User-Agent, payload condition, or alert identifies the
  access vector.
- An account-change notice proves SSH, a specific actor, or a platform cause.
- Similar symptoms across sites prove one platform mechanism.
- Missing logs, matched precedent, successful cleanup, or one clean scan proves
  cause or complete eradication.

## Risky changes

Protection changes, session termination, credential rotation, deletion, and
production investigation need the exact target, authorization, preserved
evidence, blast radius, downstream effect, success check, review point,
rollback or recovery plan, and owner.

Prefer a narrow diagnostic or containment action. Preserve evidence first.

## Return to the router

Return one result: reporter-owned containment remains; an authorized security
route is required; no WP Cloud action remains; bounded matching in platform
logs is needed; or the technical boundary changed.

If HTTP protection, protocol access, or a managed operation becomes
controlling, retain the record and replace this reference. Do not stack
references. Any potentially ready result returns to the main workflow for the
private challenge before drafting.
