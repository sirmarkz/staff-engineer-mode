# ADR 0002: Router Eval Fixture Data Contract

## Context

The router eval fixtures under
`skills/staff-engineer-mode/references/router-eval-set.yaml` and
`skills/staff-engineer-mode/references/router-phase-eval-set.yaml` are shared
data. Fixture authors produce case records. Validation scripts, eval runners,
sample-prompt evaluators, and reviewers consume those records to verify routing
behavior.

The current shape is a top-level `cases:` list. Each case is a mapping written
in the restricted YAML subset parsed by the repo scripts: two-space list items,
four-space case fields, scalar strings, and inline string lists.

## Decision

Treat router eval cases as a maintained data contract. Do not change field
meaning, requiredness, parse format, or compatibility expectations without first
updating producer rules, consumer rules, validators, representative fixtures,
and any affected tests.

The contract for the shared shape is:

| Field | Meaning | Required | Validity Rule | Sensitive |
| --- | --- | --- | --- | --- |
| `prompt` | User request used as the routing input. | Yes | Non-empty string. | No |
| `expected_primary` | Expected primary routing result. | Yes | Specialist slug, `staff-engineer-mode` for ambiguous no-route, or `none` for out-of-scope. | No |
| `expected_behavior` | Human-readable reason the case exists. | Yes | Non-empty string; ambiguous no-route cases must state that specialists are withheld. | No |
| `category` | Fixture coverage class. | Yes | Existing categories include `direct`, `paraphrase`, `mixed_intent`, and `out_of_scope`; `ambiguous` is allowed only where validators require no-route handling. | No |
| `expected_checks` | Contract checks the runner should enforce. | Yes | Non-empty inline list of known check names. | No |
| `expected_secondary` | Expected secondary routing result for a separate artifact. | No | Specialist slug; requires `secondary_cap` in `expected_checks`. | No |
| `forbidden_in_response` | Names or aliases that must not appear in low-confidence or out-of-scope responses. | Conditional | Required for `ambiguous` and `out_of_scope` categories; inline list of specialist slugs or `all_specialist_names`. | No |
| `expected_phase` | Expected lifecycle phase for phase-focused fixtures. | Conditional | Required only when the phase fixture needs phase coverage for routed cases. | No |

## Producers

Fixture authors must preserve the current parseable subset:

- Add cases as entries under `cases:` with the existing indentation style.
- Use quoted strings for prompts and behavior when punctuation could be
  misread by the parser.
- Use inline lists for `expected_checks` and `forbidden_in_response`.
- Use only known specialist slugs, `staff-engineer-mode`, or `none` in
  routing-result fields.
- Add or update validation before relying on a new field, category, check name,
  phase, or sentinel value.

## Consumers

Consumers must read the shape as a contract, not as incidental YAML:

- `scripts/validate_router_eval.py` is the release-blocking compatibility gate
  for fixture shape and coverage.
- `scripts/run_router_eval.py` scores responses against the main fixture and
  must ignore absent optional fields unless a declared check requires them.
- `scripts/run_sample_prompt_router_eval.py` may synthesize compatible cases
  from docs, but generated cases must still use the same field meanings.
- Tests that construct in-memory cases must match the same required fields and
  compatibility rules as file-backed fixtures.

## Compatibility Rules

| Change | Class | Rule |
| --- | --- | --- |
| Add a new case using existing fields and values. | Compatible | Allowed when validation passes and coverage remains balanced. |
| Edit `prompt` or `expected_behavior` without changing the expected route semantics. | Compatible | Allowed when the case still exercises the same behavior. |
| Add `expected_secondary` to a case. | Conditional | Requires `secondary_cap`, validates the secondary slug, and may affect secondary-case coverage counts. |
| Add `forbidden_in_response` to a low-confidence or out-of-scope case. | Compatible | Allowed when values are known slugs or `all_specialist_names`. |
| Add an optional field consumed by no current script. | Conditional | Allowed only if existing consumers tolerate it and the field is documented here before use. |
| Add a new `expected_checks` value. | Breaking until supported | Update validators, runners, tests, and representative fixtures in the same change. |
| Add a new category, phase, or sentinel route value. | Breaking until supported | Update validation constants, scoring behavior, docs, and tests before using it broadly. |
| Rename a field or change requiredness. | Breaking | Requires a migration path or simultaneous consumer updates. |
| Change `expected_primary`, `expected_secondary`, or `expected_phase` meaning. | Breaking | Treat as a contract change even if the field type is unchanged. |
| Change indentation, list style, or quoting rules beyond the parser subset. | Breaking | Replace or harden every parser before changing fixture format. |
| Remove a field from existing cases. | Breaking unless optional | Confirm every consumer handles absence and validators encode the new rule. |

## Validation And Consumer Tests

Before changing this shape:

1. Run `python3 scripts/validate_router_eval.py`.
2. Run tests that cover the fixture parser and scorer.
3. If field semantics changed, add focused tests in the relevant consumer before
   updating broad fixtures.
4. If categories, phases, checks, or sentinel values changed, update validation
   constants and failure messages in the same change.

## Deprecation And Migration

Prefer additive evolution. For a breaking shape change, use one of these paths:

- Dual-read old and new fields until every consumer has migrated, then remove
  the old field in a later change.
- Convert the fixture format mechanically only after the parser, validators,
  tests, and sample consumers accept the new format.
- Keep old sentinel values accepted until fixture history and generated sample
  cases no longer depend on them.

Removal is allowed only after `rg` finds no producer or consumer references to
the deprecated field, check, category, phase, or sentinel value, and the
repo-local validation suite passes.
