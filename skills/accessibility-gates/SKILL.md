---
name: accessibility-gates
description: "Use to set release gates on user-facing flows for keyboard, screen-reader, focus, contrast, and assistive-technology behavior — anything from a single critical journey on a small site to a full conformance program."
---

# Accessibility Conformance Gates

## Overview

Accessibility is a release quality property, not a post-launch polish pass.

**Core principle:** gate critical user journeys on semantic structure, keyboard access, focus behavior, visual contrast, assistive-technology behavior, and regression evidence.

## Iron Law

```
NO CRITICAL USER FLOW SHIPS WITHOUT A NAMED CONFORMANCE LEVEL, ASSISTIVE-TECH TEST EVIDENCE, AND A REGRESSION GATE
```

Pick the conformance level explicitly (for most public web work, WCAG 2.x AA is the named target). Run the critical flow with at least one assistive-technology path before release. Add a regression gate so the same defect cannot recur silently. For a solo developer or tiny team, "evidence" is your own keyboard-only and screen-reader walkthrough recorded once per release; the discipline is that the walkthrough happened, not that a separate accessibility team ran it.

## When To Use

- The user asks about accessibility, conformance, assistive-technology support, keyboard navigation, focus order, contrast, labels, or release gates for user-facing flows.
- A UI change affects forms, navigation, dialogs, errors, media, dynamic updates, or critical journeys.
- Automated checks and manual checks need to be combined into a release decision.
- A regression blocks users from perceiving, operating, or understanding the interface.

## When Not To Use

- The main issue is loading speed, responsiveness, visual stability, or runtime errors; defer to `web-release-gates`.
- The main issue is native crash, startup, offline, or app-store rollout risk; defer to `mobile-release-engineering`.
- The request is brand design or marketing copy without accessibility engineering risk.
- The work is a legal policy discussion without concrete engineering gates.

## Inputs To Collect

- Critical journeys, user surfaces, target conformance level, supported input modes, and assistive technologies.
- Changed components, labels, roles, focus behavior, keyboard paths, error handling, contrast, and dynamic content.
- Existing automated checks, manual test scripts, defect history, and release-blocking rules.
- Exceptions, owner, expiry, severity, affected users, and compensating path.
- Telemetry or support signals for accessibility regressions where available.

## Workflow

1. **Define the target.** State the conformance expectation and critical journeys before evaluating details.
2. **Map the journey.** Identify every step, control, message, focus transition, and error state a user must complete.
3. **Check semantics and names.** Ensure controls expose meaningful structure, labels, state, and relationships.
4. **Verify operation.** Test keyboard-only and assistive-technology paths for completion, not just component snapshots.
5. **Check perception.** Review contrast, text resizing, motion, timing, media alternatives, and status updates where relevant.
6. **Combine evidence.** Use automated checks for broad regressions and manual checks for interaction quality.
7. **Gate release.** Block critical journey failures; track lower-risk defects with owner, severity, expiry, and retest date.
8. **Prevent recurrence.** Add component tests, examples, lint rules, or review checks for repeated failure patterns.

## Synthesized Default

Gate critical journeys with a named conformance target, automated checks, manual assistive-technology scripts, keyboard completion tests, dated exceptions with a named owner (which can be you for solo work), and regression tests for known defects. Accessibility evidence should be part of launch readiness for user-facing changes.

## Exceptions

- Internal tools may use a narrower journey set only when the affected user group and alternative path are explicit.
- Emergency fixes can ship with a tracked accessibility exception only when delaying is riskier and a repair owner/date exists.
- Automated checks are not enough for complex interactions; manual verification remains required for critical flows.

## Response Quality Bar

- Lead with the accessibility release decision, blocker list, conformance gap, or test plan requested.
- Cover target, critical journeys, semantics, keyboard behavior, focus, assistive-technology checks, contrast, exceptions, and regression gates before optional design advice.
- Name one concrete assistive-technology path for at least one critical journey, such as NVDA, VoiceOver, JAWS, TalkBack, Dragon, or switch control, with a pass/fail criterion for completing that journey.
- Make recommendations actionable with owners, severity, blocking status, retest steps, and release criteria where relevant.
- State required evidence such as journey list, automated results, manual scripts, screenshots or recordings, defect history, and exception records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them, explicitly requested tool-specific guidance, or a named assistive technology is needed for test evidence.
- Stay inside accessibility engineering. Route performance, mobile rollout, or broad legal policy only when those are central.
- Be concise: prefer journey-based gate tables over broad accessibility lectures.

## Required Outputs

- Accessibility conformance target and journey inventory.
- Release gate matrix: automated checks, manual checks, blocking status, and owner.
- Critical journey manual test script.
- Exception register with severity, expiry, compensating path, and retest.
- Regression-prevention plan for recurring defects.
- Follow-up routes for performance or mobile-specific release risk where needed.

## Evidence Gates

- `target_defined`: conformance expectation and critical journeys are named.
- `journey_complete`: users can complete critical flows through supported input and assistive paths.
- `mixed_testing`: automated and manual evidence are both used where interaction quality matters.
- `exception_owner`: every exception has severity, owner, expiry, and compensating path.
- `regression_gate`: known failures have tests or review gates to prevent recurrence.

## Red Flags - Stop And Rework

- Automated checks pass, but nobody tested the critical journey.
- Focus is trapped, lost, or moves unpredictably.
- Controls have visible labels but no reliable accessible names.
- Error messages are visible but not announced or associated with fields.
- Accessibility exceptions have no owner or repair date.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Component-only checks | Test complete user journeys. |
| Automation as proof | Add manual interaction verification. |
| Treating all defects alike | Block critical journey failures first. |
| Exceptions without expiry | Require owner, compensating path, and retest. |
---
name: accessibility-gates
description: "Use to set release gates on user-facing flows for keyboard, screen-reader, focus, contrast, and assistive-technology behavior — anything from a single critical journey on a small site to a full conformance program."
---

# Accessibility Conformance Gates

## Overview

Accessibility is a release quality property, not a post-launch polish pass.

**Core principle:** gate critical user journeys on semantic structure, keyboard access, focus behavior, visual contrast, assistive-technology behavior, and regression evidence.

## Iron Law

```
NO CRITICAL USER FLOW SHIPS WITHOUT A NAMED CONFORMANCE LEVEL, ASSISTIVE-TECH TEST EVIDENCE, AND A REGRESSION GATE
```

Pick the conformance level explicitly (for most public web work, WCAG 2.x AA is the named target). Run the critical flow with at least one assistive-technology path before release. Add a regression gate so the same defect cannot recur silently. For a solo developer or tiny team, "evidence" is your own keyboard-only and screen-reader walkthrough recorded once per release; the discipline is that the walkthrough happened, not that a separate accessibility team ran it.

## When To Use

- The user asks about accessibility, conformance, assistive-technology support, keyboard navigation, focus order, contrast, labels, or release gates for user-facing flows.
- A UI change affects forms, navigation, dialogs, errors, media, dynamic updates, or critical journeys.
- Automated checks and manual checks need to be combined into a release decision.
- A regression blocks users from perceiving, operating, or understanding the interface.

## When Not To Use

- The main issue is loading speed, responsiveness, visual stability, or runtime errors; defer to `web-release-gates`.
- The main issue is native crash, startup, offline, or app-store rollout risk; defer to `mobile-release-engineering`.
- The request is brand design or marketing copy without accessibility engineering risk.
- The work is a legal policy discussion without concrete engineering gates.

## Inputs To Collect

- Critical journeys, user surfaces, target conformance level, supported input modes, and assistive technologies.
- Changed components, labels, roles, focus behavior, keyboard paths, error handling, contrast, and dynamic content.
- Existing automated checks, manual test scripts, defect history, and release-blocking rules.
- Exceptions, owner, expiry, severity, affected users, and compensating path.
- Telemetry or support signals for accessibility regressions where available.

## Workflow

1. **Define the target.** State the conformance expectation and critical journeys before evaluating details.
2. **Map the journey.** Identify every step, control, message, focus transition, and error state a user must complete.
3. **Check semantics and names.** Ensure controls expose meaningful structure, labels, state, and relationships.
4. **Verify operation.** Test keyboard-only and assistive-technology paths for completion, not just component snapshots.
5. **Check perception.** Review contrast, text resizing, motion, timing, media alternatives, and status updates where relevant.
6. **Combine evidence.** Use automated checks for broad regressions and manual checks for interaction quality.
7. **Gate release.** Block critical journey failures; track lower-risk defects with owner, severity, expiry, and retest date.
8. **Prevent recurrence.** Add component tests, examples, lint rules, or review checks for repeated failure patterns.

## Synthesized Default

Gate critical journeys with a named conformance target, automated checks, manual assistive-technology scripts, keyboard completion tests, dated exceptions with a named owner (which can be you for solo work), and regression tests for known defects. Accessibility evidence should be part of launch readiness for user-facing changes.

## Exceptions

- Internal tools may use a narrower journey set only when the affected user group and alternative path are explicit.
- Emergency fixes can ship with a tracked accessibility exception only when delaying is riskier and a repair owner/date exists.
- Automated checks are not enough for complex interactions; manual verification remains required for critical flows.

## Response Quality Bar

- Lead with the accessibility release decision, blocker list, conformance gap, or test plan requested.
- Cover target, critical journeys, semantics, keyboard behavior, focus, assistive-technology checks, contrast, exceptions, and regression gates before optional design advice.
- Name one concrete assistive-technology path for at least one critical journey, such as NVDA, VoiceOver, JAWS, TalkBack, Dragon, or switch control, with a pass/fail criterion for completing that journey.
- Make recommendations actionable with owners, severity, blocking status, retest steps, and release criteria where relevant.
- State required evidence such as journey list, automated results, manual scripts, screenshots or recordings, defect history, and exception records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them, explicitly requested tool-specific guidance, or a named assistive technology is needed for test evidence.
- Stay inside accessibility engineering. Route performance, mobile rollout, or broad legal policy only when those are central.
- Be concise: prefer journey-based gate tables over broad accessibility lectures.

## Required Outputs

- Accessibility conformance target and journey inventory.
- Release gate matrix: automated checks, manual checks, blocking status, and owner.
- Critical journey manual test script.
- Exception register with severity, expiry, compensating path, and retest.
- Regression-prevention plan for recurring defects.
- Follow-up routes for performance or mobile-specific release risk where needed.

## Evidence Gates

- `target_defined`: conformance expectation and critical journeys are named.
- `journey_complete`: users can complete critical flows through supported input and assistive paths.
- `mixed_testing`: automated and manual evidence are both used where interaction quality matters.
- `exception_owner`: every exception has severity, owner, expiry, and compensating path.
- `regression_gate`: known failures have tests or review gates to prevent recurrence.

## Red Flags - Stop And Rework

- Automated checks pass, but nobody tested the critical journey.
- Focus is trapped, lost, or moves unpredictably.
- Controls have visible labels but no reliable accessible names.
- Error messages are visible but not announced or associated with fields.
- Accessibility exceptions have no owner or repair date.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Component-only checks | Test complete user journeys. |
| Automation as proof | Add manual interaction verification. |
| Treating all defects alike | Block critical journey failures first. |
| Exceptions without expiry | Require owner, compensating path, and retest. |
