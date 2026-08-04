# Domains, network, and protocol access

Use this reference when the first failed phase is DNS, destination selection,
network or TCP reachability, TLS, SSH, SFTP, or another protocol boundary
before an HTTP response. It returns findings to the router; it does not assign
readiness.

## Select this reference

Locate the first failed phase:

1. DNS name and record resolution.
2. Selected destination, route, NAT, or TCP connection.
3. TLS handshake, certificate, and name match.
4. Protocol negotiation and authentication, including SSH or SFTP.
5. Application or HTTP behavior after the connection succeeds.

Select this reference for phases 1–4. Once a valid HTTP response controls the
decision, use HTTP and automation. Use another reference when a direct WP Cloud
Atomic API contract, measured capacity condition, or sensitive incident
controls the next action.

Split independent domain, network, certificate, and login failures.

## Decisive evidence

Preserve the smallest phase-specific packet:

- WP Cloud site ID, domain or host, intended destination, source network, and
  exact UTC window.
- DNS: queried name and type, resolver, answer, authoritative result, TTL, and
  propagation result.
- Domain or certificate workflow, when applicable: current platform status,
  exact authorization or eligibility error, relevant A, AAAA, CAA, DNSSEC,
  proxy, or delegation state, and the result of the documented retry.
- Domain verification, when applicable: required TXT name and value, observed
  answer, propagation result, verification attempt, and current collision or
  ownership state without disclosing another client.
- Network: resolved address, destination port, source context, TCP result,
  route or traceroute result, and repeat pattern.
- TLS: requested name, resolved destination, certificate subject and issuer,
  validity, chain or name error, SNI, and handshake result.
- SSH or SFTP: host, port, username or account label when safe, client and
  version, authentication method name, verbose sanitized output, and server
  fingerprint or public-key details when relevant.
- The exact first failure and a successful control from the same source when
  available.

Preserve domains, site IDs, IP addresses, account labels, public keys, logs,
and protocol output when useful. Remove passwords, private keys, tokens, and
session material under the shared secret rule.

## Reporter-owned checks

- Confirm the tested hostname, destination, port, protocol, and environment.
- Check public and authoritative DNS rather than infer propagation from one
  local cache.
- Run `curl`, a TCP test, `ping`, or `traceroute` only when that tool tests the
  claimed phase. Record command, source, UTC time, and result.
- Inspect certificate and SNI behavior for the exact hostname.
- For SSH or SFTP, run a verbose client attempt with secrets removed; check
  client configuration, key selection, username, host key, authentication
  method, retries, and connection limits.
- Compare a working source or protocol only when the changed variable is known.
- Re-test after correcting reporter-owned DNS, proxy, firewall, credential
  selection, or client configuration.
- Complete the documented domain, certificate, or TXT verification workflow
  before escalating a state that the reporter can correct or retry.

An HTTP health check is not a ping. A successful HTTP request does not prove
SSH works, and HTTP logs do not explain a pre-HTTP failure.

## When access is limited

Do not require routing, firewall, or authentication logs that the reporter
cannot access. Provide the receiver a correlation tuple: site or account,
hostname, source and destination, port, protocol, exact UTC window, first
failed phase, sanitized client output, and repeat pattern.

A direct test from a container may still use NAT, proxying, shared egress, or a
different route. State what the source actually was. Missing receiver logs is
not evidence that the platform blocked the connection.

For a domain already associated elsewhere, never disclose another client's
identity or bypass ownership verification. Provide the domain, current
verification result, and the authorized action requested.

## Challenge weak inferences

Challenge claims that:

- `Ping failed` proves an edge outage or dropped customer traffic.
- One resolver proves global DNS propagation.
- A certificate warning proves failed provisioning rather than wrong
  destination, stale DNS, proxying, or name mismatch.
- A working HTTP request proves network and protocol access generally.
- Missing application logs prove an edge or firewall block.
- A password-reset or account email proves SSH access.
- A direct test bypassed every proxy or NAT layer.
- A second site or network is equivalent without matching the route and
  protocol variables.

## Risky changes

DNS changes, certificate replacement, firewall or allowlist changes, session
termination, and authentication changes need the exact target, authorization,
current and requested state, affected names or users, propagation or session
effect, success check, review point, and rollback trigger.

Preserve evidence before terminating sessions or changing credentials. Prefer
a narrow diagnostic test to a broad production bypass.

## Return to the router

Return one result: reporter-owned correction resolved the issue; another
network or service owner controls the next step; documentation answers the
question; a named evidence blocker prevents phase attribution; or an exact
platform-only condition remains with a sufficient correlation tuple. Treat a
complete tuple plus a demonstrated platform-log access limit as a
non-blocking caveat, not unfinished reporter work.

When a current authoritative check succeeds and the symptom is gone, return
`Resolved during validation` with technical reference `none`.

If the first failed phase changes, keep the record and replace this reference.
Do not stack references.
