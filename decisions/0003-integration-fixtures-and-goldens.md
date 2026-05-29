# ADR 0003: Integration Fixture And Golden-File Rules

## Context

The new integration test suite needs representative inputs and expected outputs
before it starts using production samples. Without explicit rules, production
captures can become unidentified test dependencies, and golden files can drift
from reviewed behavior into rewritten snapshots.

This repository already treats router eval fixtures as a maintained data
contract in ADR 0002. Integration fixtures need the same discipline, with
stronger rules for production-derived data because future samples may include
real prompts, routing outputs, tool traces, or environment-specific paths.

## Decision

Use synthetic and hand-authored fixtures by default. Do not add production
samples to the integration suite until the fixture inventory, anonymization
policy, restore path, and golden regeneration checks in this decision are in
place.

Accepted fixture classes:

| Class | Use For | Default Scope | Refresh Rule | Restore Rule |
| --- | --- | --- | --- | --- |
| Hand-authored | Small cases that prove one contract or edge case. | Per test. | Update only with the contract being tested. | Recreate from the test and documented intent. |
| Synthetic-generated | Representative combinations, long traces, and awkward edge cases. | Per test or per file. | Regenerate from a pinned generator version and seed. | Re-run the generator with recorded version and seed. |
| Derived golden | Expected output from a fixture input and stable command path. | Per test. | Regenerate only through the reviewed workflow below. | Re-run the documented command against the paired input fixture. |
| Captured production | Only behavior that cannot be represented safely with synthetic data. | Read-only per suite. | Refresh on schema change, routing contract change, or drift threshold breach. | Recapture from recorded source, timestamp, filter, and anonymization transform. |

Shared mutable seeded state is not allowed for the initial suite. If setup cost
later requires shared state, it must be read-only or have an explicit teardown
check and an order-independence test.

## Production Sample Gate

A production-derived fixture is blocked unless its manifest records:

- Source system or corpus, capture timestamp, owner, and reason synthetic data
  is insufficient.
- Data classification for direct identifiers, quasi-identifiers, sensitive
  fields, free text, secrets, customer-identifying values, local machine paths,
  and environment-specific values.
- Transform per field type: suppress, generalize, redact, pseudonymize, or
  replace with synthetic values. Field renaming or hashing alone is not
  sufficient for quasi-identifiers.
- Restore procedure with the recapture filter, anonymization command or steps,
  expected runtime, and validation command.
- Drift signal comparing the fixture shape with the current source shape for
  fields the test relies on.

If any of those entries are unknown, keep the case synthetic or hand-authored.

## Fixture Inventory

Each integration fixture directory must include an inventory entry with:

| Field | Meaning |
| --- | --- |
| `name` | Stable fixture identifier used by tests. |
| `path` | Fixture file or directory path. |
| `class` | One of hand-authored, synthetic-generated, derived-golden, or captured-production. |
| `scope` | Per test, per file, per suite, or read-only shared. |
| `source` | Human intent, generator path, command output, or production capture source. |
| `owner` | Maintainer responsible for refresh and deletion. |
| `refresh_trigger` | Contract change, schema change, source drift, dependency update, or manual only. |
| `restore` | Exact local steps to recreate the fixture from scratch. |
| `sensitive` | Yes or no, with classification notes when yes. |
| `callers` | Test paths that consume the fixture. |

Fixtures with no callers, no recoverable source, or no owner are removed before
production-derived samples are introduced.

## Golden-File Rules

Golden files are review artifacts, not caches.

- Pair every golden with one input fixture and one test path.
- Store or document the command that regenerates the golden.
- Require a separate check that fails when the working tree changes after
  regeneration.
- Review golden diffs as behavioral changes. The reviewer must be able to tell
  whether the change is intentional contract movement, harmless formatting, or
  accidental drift.
- Do not regenerate goldens automatically on test failure.
- Keep nondeterministic values out of goldens. Normalize timestamps, local
  paths, random identifiers, ordering, and environment-specific strings before
  comparison.
- Prefer semantic assertions over full-file goldens when the test only cares
  about a small subset of output.

## Drift And Freshness

Synthetic and hand-authored fixtures are deterministic unless the tested
contract changes. Captured production fixtures need drift checks before they are
trusted:

- Track field presence, requiredness, categorical values, nullability, list
  lengths, and output block shape for the values the tests assert on.
- Run drift checks when router contracts, specialist lists, fixture schemas, or
  production capture filters change.
- Treat drift as a fixture-maintenance failure, not as permission to blindly
  rewrite goldens.

## Validation Expectations

Before merging the integration suite or adding production samples:

1. The fixture inventory is complete for every input and golden.
2. Every fixture has a restore procedure that works from a clean checkout.
3. Captured production fixtures have anonymization evidence and a drift check.
4. Golden regeneration is explicit, reviewed, and leaves no unexpected working
   tree changes.
5. Repo-local validation scripts still pass.

## Status

Accepted.

## References

Source-index references used for this decision:

- Software Engineering at Google - Testing Overview.
- Microsoft DevOps - Shift Testing Left with Unit Tests.
- Azure Well-Architected - Data Classification.
- NIST Privacy Framework 1.0 PDF.
