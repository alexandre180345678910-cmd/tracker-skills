# Contract compatibility

Use for public/internal APIs, OpenAPI, GraphQL, protobuf, events, webhooks, SDKs, shared schemas, and persisted data formats.

- Inventory producers, consumers, versions, ownership, and compatibility window.
- Establish a checked-in baseline and run a semantic diff. Treat removed/renamed fields, tighter validation, changed nullability/type/defaults, enum narrowing, route/status/auth changes, event ordering, and protobuf field-number reuse as potential breaks.
- Prefer additive evolution. Define versioning, deprecation notice, migration path, telemetry for old consumers, and removal criteria.
- Test provider conformance plus representative consumers. Use consumer-driven contracts where independent deployment makes them valuable; never let generated mocks become the only truth.
- For events and stored data, verify forward/backward readers, replay/idempotency, schema registry rules, dual-read/write period, and rollback.

Block release on an unapproved breaking change, an unverifiable consumer impact, or a migration that cannot coexist safely across rollout versions.
