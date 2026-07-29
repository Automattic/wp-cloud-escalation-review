# WP Cloud documentation routing

Check current reporter-available documentation before calling a symptom
undocumented. Record `checked`, `unavailable`, or `not_applicable`; never imply
inaccessible material was reviewed.

## Public documentation

Use the [public WP Cloud documentation repository](https://github.com/Automattic/wp-cloud-docs)
for concepts, procedures, troubleshooting, scope, and terminology. Never
preload the full corpus.

1. Search the public catalog or `llms.txt`. Select one document that can change
   route, validation, ownership, or action.
2. For ambiguous terminology, use the public glossary or the most specific
   matching page; follow its link for procedures or limits.
3. Read the article outline, then relevant section. Open one related article
   only when necessary.
4. Record key, public path, heading, catalog status, and finding. Paraphrase;
   quote only the shortest decision-bearing phrase.

Fetch only the catalog and targeted Markdown. Do not clone a documentation
repository for one lookup.

Prefer an approved, technically validated article for behavior/procedure.
Glossary can clarify terms, not replace canonical procedure. Treat
review-needed or unclear material as a limitation.

In Guided, state what the selected section says, why it changes investigation,
and link the page. Never dump search results, frontmatter, glossary, or
unrelated sections.

Record:

```text
WP Cloud docs: checked | unavailable | not_applicable
Document: <key and heading, or none>
Glossary term: <term or none>
Finding: <answer, correction, narrowing, or limitation>
```

Every selected technical case gets this applicability check. If relevant
documentation is unavailable, say so and ask for the smallest current source
that could change scope, ownership, or action.

## WP Cloud Atomic API documentation

For direct WP Cloud Atomic API work, validate the exact contract with the
current [WP Cloud Atomic API reference](https://wp.cloud/docs/api/):

1. route through `llms.txt`;
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
