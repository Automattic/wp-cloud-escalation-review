# WP Cloud documentation routing

Check current reporter-available documentation before calling a symptom
undocumented. Record `checked`, `unavailable`, or `not_applicable`; never imply
inaccessible material was reviewed.

Do not research documentation until currentness and the remaining WP Cloud
decision or action are known. If no WP Cloud work remains, use
`not_applicable` and stop. General documentation can explain a published
mechanism, but it cannot prove that a specific request followed that mechanism.
Do not use a general failover page to replace direct event evidence or to
relabel an event-specific retry.

## Public documentation

Start with the published [WP Cloud documentation](https://wp.cloud/docs/)
for concepts, procedures, troubleshooting, scope, and terminology. Use the
site's navigation or search to find the relevant issue category. For a
symptom, start with the [Troubleshooting](https://wp.cloud/docs/troubleshooting/)
section. Then use the matching area, such as
[Edge](https://wp.cloud/docs/edge/), [Security](https://wp.cloud/docs/security/),
[Performance](https://wp.cloud/docs/performance/),
[Site access](https://wp.cloud/docs/site-access/), or
[API & automation](https://wp.cloud/docs/api-automation/). Never preload the
full corpus. Consult the [public source repository](https://github.com/Automattic/wp-cloud-docs)
only when source context or publication status is needed.

When a draft carries a general question about how the platform works, chooses,
or behaves, check here first. A documented answer goes back to the reporter or
customer, not into the escalation. An undocumented general question is a
separate information request, not part of an incident handoff.

1. Select one published guide that can change route, validation, ownership, or
   action. Use a catalog or machine-readable index when available; do not
   require one to browse the published docs.
2. For ambiguous terminology, use the public glossary or the most specific
   matching page; follow its link for procedures or limits.
3. Read the article outline, then relevant section. Open one related article
   only when necessary.
4. Record the page title, public URL, relevant heading, and finding. Preserve
   any stated review or publication limitation. Paraphrase; quote only the
   shortest decision-bearing phrase.

Read only the selected page or its offered Markdown and necessary navigation.
Do not clone a documentation repository for one lookup.

Use the relevant published procedure for behavior and troubleshooting.
Glossary can clarify terms, not replace canonical procedure. Treat explicitly
review-needed or unclear material as a limitation; do not assume unpublished
catalog metadata exists on a published page.

When more reporter work remains, state only what the selected section changes
and link the page. Never dump search results, frontmatter, glossary, or
unrelated sections.

Record:

```text
WP Cloud docs: checked | unavailable | not_applicable
Document: <public URL and heading, or none>
Glossary term: <term or none>
Finding: <answer, correction, narrowing, or limitation>
```

Every selected technical case with remaining WP Cloud work gets this
applicability check. When the reporter states a specific documentation finding
and you cannot open the page, record `unavailable`, attribute the finding to
the reporter, and keep any link given. It does not block an otherwise ready
escalation. Ask for the smallest current source only when no finding was
supplied and the documentation could change scope, ownership, or action.

## WP Cloud Atomic API documentation

For direct WP Cloud Atomic API work, validate the exact contract with the
current [WP Cloud Atomic API reference](https://wp.cloud/docs/api/):

1. route through the [API index](https://wp.cloud/docs/api/llms.txt);
2. read one endpoint Markdown file;
3. use agent guide or `openapi.json` only for API-wide rules or exact schema.

Validate method, path, identifiers, parameters, body, responses, errors,
access, and async job behavior. Never request an API key. Use sanitized
requests/responses.

Record status, endpoint page, and correction, mismatch, or access limit.
Documentation proves contract, not endpoint access. Use `not_applicable` for
WordPress REST API, GraphQL, and ordinary browser traffic.

## Source authority

- Public WP Cloud documentation: platform behavior, procedure,
  troubleshooting, terminology, and published support scope.
- Endpoint/OpenAPI: public WP Cloud Atomic API contract.
- Glossary: disambiguation, not sole proof of procedure/limits.

Historical examples never override current docs. Preserve unclear,
inaccessible, or apparently incorrect documentation as a limitation. Add a
public link to copy-ready text only when the receiver needs it.

A request to improve public documentation belongs to the documentation owner
and issue tracker, not a WP Cloud platform escalation. State that route without
an escalation draft unless the reporter explicitly asks for separate issue
copy.
