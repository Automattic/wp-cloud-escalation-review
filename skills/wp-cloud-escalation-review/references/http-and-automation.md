# HTTP and automation

Use this reference only when an HTTP response, a protection result, or an
automated caller controls the next decision. It returns findings to the router;
it does not assign readiness.

## Select this reference

Select it for an observed HTTP response, request filtering, a webhook, crawler,
monitor, build, or other automated HTTP traffic.

Do not select it for:

- DNS, TCP, TLS, SSH, SFTP, or another failure before an HTTP response.
- A direct WP Cloud Atomic API contract or managed job.
- Measured resource pressure, caching, or capacity when that controls the
  decision.
- A sensitive incident that requires containment or restricted disclosure.

Words such as `crawler`, `migration`, `webhook`, or a status code do not select
the reference by themselves. Split independent mechanisms first.

## Decisive evidence

Collect fields that change the decision:

- Current workflow, WP Cloud site ID, domain, and user-visible effect.
- When needed, an exact request tuple: UTC time, method, URL or path, status,
  source, full User-Agent, and correlation or vendor event ID.
- Response provenance: relevant headers, signature, renderer, origin
  visibility, and recorded protection reason.
- For an aggregate: bounded UTC window, affected count, denominator, request
  class, verified impact, and direct platform signal.
- For automation: normal and peak rate, concurrency, burst shape, retry and
  backoff behavior, duplicate work, cacheability, and request cost.
- A shareable link to the exact log view, dashboard view, or saved query when
  one exists. Always carry it into the handoff and state which count, request,
  or protection reason it supports. For counts, percentages, and rates, keep
  the absolute bounded interval and denominator in the handoff and preserve
  the same fixed interval in the link when possible. Do not block when the
  reporter has no shareable link.

Keep identity, authorization, legitimacy, risk, and cost separate.

An aggregate can replace event times only with absolute UTC bounds, one request
class, a denominator, verified impact, and a direct controlling signal.
Otherwise require an event. Keep sample and population distinct: “three 429s
in a 500-request sample from 6,000 total requests.”

A current event, full User-Agent, method, path, verified workflow, and matching
platform reason can support narrow review without IP, headers, body, or vendor
ID. Require extras only for correlation, provenance, legitimacy, or risky
scope. Do not require registry or vendor-list research when the event suffices.

## Reporter-owned checks

- For a broad failure or routing claim with a known site and time window, check
  the single-site dashboard or equivalent summary first. Quantify affected
  requests, paths or request class, denominator, and the direct reason any
  request reached another server before narrowing to one raw event.
- Reproduce safely when reproducibility controls the decision. Never label a
  log search as reproduction. Do not demand a fresh reproduction when a recent
  bounded event and durable controlling signal already support a
  receiver-owned review.
- Match the same event across reporter-visible layers only when that result can
  change the route, owner, or action.
- Inspect the response and application logs before assigning a generic status
  to the platform edge.
- Check site tools, proxies, and CDNs only when they could produce the result.
- Separate status codes, interactive requests, crawlers, webhooks, monitors,
  and builds unless evidence connects them.
- For automation, test a bounded reduction in concurrency, volume, duplicate
  work, retries, or query cost when resource impact is plausible.
- Confirm stable caller identity. Correct misleading identities when controlled;
  otherwise record the weakness and narrow the request.
- Map each site, caller, source, method, path, and event. Do not transfer an
  identity or legitimacy conclusion across providers or request classes.
- After partial changes, identify failing status, request class, and protection
  reason before readjusting. Continued failure does not prove the original
  mechanism persists.

Skip plugin, domain, and application checklists once direct evidence
already identifies the controlling platform condition.

Nearby SSH activity, a host-label change, or another timestamped operation is
context, not a migration or cause. Do not make an unproven host-move theory the
frame for the next check.

## When access is limited

Do not require receiver-only logs. Provide a compact lookup tuple: site, UTC
time, method or path, status, source, User-Agent, workflow, response
characteristics, and origin observation.

Absence from origin logs narrows the boundary but does not prove where a
response was generated. State the access limit and ask WP Cloud only for the
correlation the reporter cannot perform.

An empty `rate_limit_reason` does not locate the layer. Use renderer, signature,
headers, body, origin visibility, and direct protection state. `renderer=php`
means WordPress produced the response. A proxy change invalidates a
single-variable comparison.

For Auto Defensive Mode, match state and request on the same site and UTC
window. A browser challenge alone is insufficient. If resource exhaustion
controls, replace this reference with performance.

## Challenge weak inferences

Challenge claims that:

- A status code or client error identifies the producing layer.
- An IP, provider, User-Agent, endpoint, or fingerprint proves legitimacy.
- Customer authorization proves low request cost.
- One missing origin event proves an edge block.
- A version label, vendor article, or earlier exception proves vulnerability,
  remediation, or current cause.
- Success after several changes proves which change worked.
- Supported architecture means unlimited rate, concurrency, retries, or cost.
- A few failures without a denominator establish broad impact.
- Several statuses or workloads from one vendor share a cause.
- Every automated request or API path is legitimate.
- An empty limit reason identifies an edge response.
- A proxy or CDN change proves that another platform control stopped.

## Risky changes

For a reporter-executed or prescriptive protection change, add control, request
class, target, environment, duration, abuse and availability risk, blast
radius, success condition, rollback owner, and trigger.

For WP Cloud-owned review, require target, evidenced condition, impact, desired
behavior, and what must remain protected. WP Cloud owns the implementation
controls.

Prefer the smallest evidenced change. Business importance affects priority,
not cause or safe scope.

Do not turn review or unobserved future risk into an exception; that is a
different decision.

## Return to the router

Return one result: evidence complete; smallest reporter blocker; receiver-only
correlation with a lookup tuple; corrected owner; resolved; or unverified
post-change result.

If a likely site-code cause and a successful fix already settle ownership and
leave no WP Cloud work, keep the cause qualified and stop. Do not require a
three-stage log chain solely to make the explanation more certain.

If the controlling boundary changes, retain the useful record and replace this
reference. Do not stack references. After a change, record what changed, when,
the observed result, and the remaining scope.
