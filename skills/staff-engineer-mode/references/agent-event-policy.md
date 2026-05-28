# Agent Event Policy

Use this policy when the host agent exposes command or tool hooks, and as
router guidance when it does not.

## Events

- `before_commit`: before creating or amending a commit, load
  `agent-pr-review`, review the exact staged diff, then record a local receipt
  for that staged diff.
- `before_release`: before tags, version bumps, hosted release records, package builds,
  artifact publication, or promotion, load `release-build-reproducibility` and
  check pinned inputs, artifact identity, promotion path, and rollback
  traceability.

## Enforcement

Receipts live under the repository's git metadata, not in the working tree. They
bind to the staged diff for commit events and to the current source revision plus
staged diff for release events. If the artifact changes after review, the agent
must rerun the matching specialist before retrying the action.

On receipt-enforced hosts, the specialist review and the receipt are separate
steps. After a clean commit review, record the commit receipt before the first
commit attempt; a review message alone does not satisfy the hook.

The review requirement gates agent awareness, not user authority. A clean review
can record a normal receipt. A review with unresolved gaps can still record an
override receipt when the user explicitly accepts the findings and asks to
proceed.

Hosts without command-interception hooks still follow the same policy through
router and specialist triggers. A commit attempt is a concrete change-set review
request. A release, tag, version, package, artifact, or promotion attempt is a
release-engineering request.
