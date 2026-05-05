---
name: llm-application-security
description: "Use to harden an LLM-backed feature against prompt injection, tool misuse, retrieval-boundary leaks, and unsafe output sinks before users or tools touch the model."
---

# LLM Application Security

## Overview

LLM applications move untrusted text across tool, data, and decision boundaries.

**Core principle:** treat prompts, retrieved content, tool outputs, and model responses as untrusted inputs; constrain what the application can do with them.

## Iron Law

```
NO LLM TOOL OR DATA ACCESS WITHOUT A BOUNDARY MAP, LEAST PRIVILEGE, ABUSE-CASE EVALS, AUDIT, AND OUTPUT HANDLING
```

If the model can cause an action, that action needs an explicit boundary, least-privilege scoping, abuse-case tests (prompt injection, exfiltration, jailbreak, unsafe action), an audit trail, and contextual handling of the output before any sink consumes it. "Evals" here are adversarial cases, not happy-path quality checks.

## When To Use

- The user asks about prompt injection, tool permissions, retrieval boundaries, insecure output handling, agent actions, model/prompt supply chain, or LLM eval security gates.
- An LLM can retrieve private data, call tools, write files, send messages, execute actions, or influence decisions.
- The system mixes instructions, user input, retrieved content, and tool output.
- A launch needs security tests for AI workflow behavior.

## When Not To Use

- The request is broad AI governance, model strategy, or ethics policy outside engineering controls.
- The work is classical ML evaluation or drift; defer to `ml-reliability-and-evaluation`.
- The request is general application threat modeling without LLM-specific boundaries; defer to `secure-sdlc-and-threat-modeling`.
- The issue is generic artifact provenance with no model/prompt/tool supply chain concern; defer to `software-supply-chain-security`.

## Inputs To Collect

- LLM workflow, actors, prompts, system instructions, retrieved data, tools, actions, and output sinks.
- Trust boundaries among user input, developer instructions, retrieved documents, model output, tool results, and external systems.
- Data classification, tenant boundaries, permissions, secrets, and privacy constraints.
- Tool capabilities, scopes, rate limits, approvals, side effects, and audit events.
- Eval set: prompt injection, data exfiltration, unsafe actions, over-permission, output injection, and regression cases.
- Logging, redaction, retention, human review, and incident response expectations.
- Model chains, nested prompts, loop limits, retrieval fanout, token/cost ceilings, and downstream systems that consume model output.

## Workflow

1. **Map boundaries.** Identify every place untrusted text can influence prompts, retrieval, tool calls, code paths, messages, or stored state.
2. **Constrain tools.** Give tools minimum permissions, explicit schemas, rate limits, loop/depth limits, side-effect boundaries, and approval gates for high-risk actions.
3. **Protect retrieval.** Enforce tenant/data permissions before retrieval and again before answer/action use.
4. **Treat output as untrusted by sink.** Commands need allowlisted operations and dry-run/approval where risky; queries need parameterization and scoped credentials; rendered text needs contextual encoding; structured tool inputs need schema validation; documents/messages need destination policy checks; downstream prompts need boundary markers and instruction-isolation.
5. **Separate instructions from data.** Do not let retrieved or user content override developer/system policy.
6. **Scope model chains.** When one model output feeds another model or agent, give each step its own permissions, retrieval boundary, audit trail, and injection eval.
7. **Evaluate adversarially.** Test prompt injection, tool misuse, data leakage, refusal bypass, unsafe output, dependency substitution, recursive tool loops, retrieval amplification, and regression cases with a repeatable red-team corpus.
8. **Audit decisions.** Log prompts, retrieval identifiers, tool calls, approvals, and outcomes with privacy-preserving redaction, retention, and replay-for-investigation rules.
9. **Control supply chain.** Track prompts, tools, models, datasets, indexes, and deployment artifacts as versioned inputs with owner, version, source, eval result, and retirement date.

## Synthesized Default

Use least-privilege tools, permission-checked retrieval, untrusted-output handling, adversarial eval gates, audit logs, and versioned AI workflow inputs. Red-team the workflow against realistic attacker goals, then make deterministic application controls decide what is allowed.

## Exceptions

- Read-only summarization with public data can use lighter tool controls, but output handling and injection tests still matter.
- Human approval can mitigate high-impact actions, but approval UI must show trustworthy context and not model-manipulated summaries only.
- Some logs must be minimized or redacted for privacy; keep enough traceability to investigate unsafe actions.
- Broad AI policy questions are out of scope unless tied to deployable engineering controls.

## Response Quality Bar

- Lead with the LLM threat model, tool-permission decision, eval gate, or blocker list requested.
- For short design-review or pre-launch answers, include a compact release-gate list: prompt-injection mitigation plus verification; tool inventory plus per-tool authorization; sink-specific output validation before execution, querying, rendering, messaging, or downstream prompting; sensitive-info controls plus monitoring; adversarial abuse cases with pass/fail criteria; and audit logs for model invocations, tool calls, denials, approvals, and retention.
- Cover prompt/retrieval/tool/output boundaries, least privilege, tenant/data isolation, unsafe-action controls, adversarial evals, logging, and supply-chain records before optional AI-security breadth.
- Make recommendations actionable with owners, permission scopes, deterministic control points, eval cases, approval gates, stop criteria, and regression checks where relevant.
- State required evidence such as retrieval IDs, tool scopes, action sinks, prompt versions, model versions, eval results, audit logs, and redaction rules; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside deployable LLM application controls. Route broad AI policy, privacy, or supply-chain work only when they are the central unresolved risk.
- Be concise: avoid generic prompt-injection background and prefer compact boundary maps, permission matrices, and eval tables.

## Required Outputs

- LLM threat model and trust-boundary map.
- Prompt, retrieval, tool, and output permission matrix.
- Tool approval, rate-limit, and audit requirements.
- Retrieval data-boundary and tenant-isolation checks.
- Output sink handling table for commands, queries, rendered content, structured tool inputs, documents/messages, and downstream prompts.
- Adversarial eval and regression plan.
- Logging/privacy requirements.
- Model/prompt/tool/data supply-chain record with artifact ID, version, source, owner, eval result, and retire-by date.

## Evidence Gates

- `boundary_map`: prompt, user input, retrieved data, tool output, model output, and action sinks are mapped.
- `least_privilege`: tools and retrieval are scoped by user, tenant, action, and side effect.
- `output_handling`: model output is validated, encoded, or constrained before use in sensitive sinks.
- `eval_gate`: prompt injection, leakage, unsafe-action, and regression tests exist.
- `audit_check`: tool calls, approvals, retrieval IDs, and outcomes are traceable without leaking sensitive data.

## Red Flags - Stop And Rework

- Retrieved documents can override system instructions.
- The model can call broad tools with production privileges.
- Model output is executed, queried, rendered, or sent without validation.
- Eval set only tests happy-path answer quality.
- Logs capture secrets or private prompts without redaction.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Trusting the model to follow policy | Enforce policy in deterministic application controls. |
| Permission-checking after retrieval only | Check before retrieval and before action/use. |
| Treating prompts as config only | Version and review prompts as behavior-changing artifacts. |
| Evaluating model, not workflow | Test tool use, retrieval, output sinks, and approval paths. |
---
name: llm-application-security
description: "Use to harden an LLM-backed feature against prompt injection, tool misuse, retrieval-boundary leaks, and unsafe output sinks before users or tools touch the model."
---

# LLM Application Security

## Overview

LLM applications move untrusted text across tool, data, and decision boundaries.

**Core principle:** treat prompts, retrieved content, tool outputs, and model responses as untrusted inputs; constrain what the application can do with them.

## Iron Law

```
NO LLM TOOL OR DATA ACCESS WITHOUT A BOUNDARY MAP, LEAST PRIVILEGE, ABUSE-CASE EVALS, AUDIT, AND OUTPUT HANDLING
```

If the model can cause an action, that action needs an explicit boundary, least-privilege scoping, abuse-case tests (prompt injection, exfiltration, jailbreak, unsafe action), an audit trail, and contextual handling of the output before any sink consumes it. "Evals" here are adversarial cases, not happy-path quality checks.

## When To Use

- The user asks about prompt injection, tool permissions, retrieval boundaries, insecure output handling, agent actions, model/prompt supply chain, or LLM eval security gates.
- An LLM can retrieve private data, call tools, write files, send messages, execute actions, or influence decisions.
- The system mixes instructions, user input, retrieved content, and tool output.
- A launch needs security tests for AI workflow behavior.

## When Not To Use

- The request is broad AI governance, model strategy, or ethics policy outside engineering controls.
- The work is classical ML evaluation or drift; defer to `ml-reliability-and-evaluation`.
- The request is general application threat modeling without LLM-specific boundaries; defer to `secure-sdlc-and-threat-modeling`.
- The issue is generic artifact provenance with no model/prompt/tool supply chain concern; defer to `software-supply-chain-security`.

## Inputs To Collect

- LLM workflow, actors, prompts, system instructions, retrieved data, tools, actions, and output sinks.
- Trust boundaries among user input, developer instructions, retrieved documents, model output, tool results, and external systems.
- Data classification, tenant boundaries, permissions, secrets, and privacy constraints.
- Tool capabilities, scopes, rate limits, approvals, side effects, and audit events.
- Eval set: prompt injection, data exfiltration, unsafe actions, over-permission, output injection, and regression cases.
- Logging, redaction, retention, human review, and incident response expectations.
- Model chains, nested prompts, loop limits, retrieval fanout, token/cost ceilings, and downstream systems that consume model output.

## Workflow

1. **Map boundaries.** Identify every place untrusted text can influence prompts, retrieval, tool calls, code paths, messages, or stored state.
2. **Constrain tools.** Give tools minimum permissions, explicit schemas, rate limits, loop/depth limits, side-effect boundaries, and approval gates for high-risk actions.
3. **Protect retrieval.** Enforce tenant/data permissions before retrieval and again before answer/action use.
4. **Treat output as untrusted by sink.** Commands need allowlisted operations and dry-run/approval where risky; queries need parameterization and scoped credentials; rendered text needs contextual encoding; structured tool inputs need schema validation; documents/messages need destination policy checks; downstream prompts need boundary markers and instruction-isolation.
5. **Separate instructions from data.** Do not let retrieved or user content override developer/system policy.
6. **Scope model chains.** When one model output feeds another model or agent, give each step its own permissions, retrieval boundary, audit trail, and injection eval.
7. **Evaluate adversarially.** Test prompt injection, tool misuse, data leakage, refusal bypass, unsafe output, dependency substitution, recursive tool loops, retrieval amplification, and regression cases with a repeatable red-team corpus.
8. **Audit decisions.** Log prompts, retrieval identifiers, tool calls, approvals, and outcomes with privacy-preserving redaction, retention, and replay-for-investigation rules.
9. **Control supply chain.** Track prompts, tools, models, datasets, indexes, and deployment artifacts as versioned inputs with owner, version, source, eval result, and retirement date.

## Synthesized Default

Use least-privilege tools, permission-checked retrieval, untrusted-output handling, adversarial eval gates, audit logs, and versioned AI workflow inputs. Red-team the workflow against realistic attacker goals, then make deterministic application controls decide what is allowed.

## Exceptions

- Read-only summarization with public data can use lighter tool controls, but output handling and injection tests still matter.
- Human approval can mitigate high-impact actions, but approval UI must show trustworthy context and not model-manipulated summaries only.
- Some logs must be minimized or redacted for privacy; keep enough traceability to investigate unsafe actions.
- Broad AI policy questions are out of scope unless tied to deployable engineering controls.

## Response Quality Bar

- Lead with the LLM threat model, tool-permission decision, eval gate, or blocker list requested.
- For short design-review or pre-launch answers, include a compact release-gate list: prompt-injection mitigation plus verification; tool inventory plus per-tool authorization; sink-specific output validation before execution, querying, rendering, messaging, or downstream prompting; sensitive-info controls plus monitoring; adversarial abuse cases with pass/fail criteria; and audit logs for model invocations, tool calls, denials, approvals, and retention.
- Cover prompt/retrieval/tool/output boundaries, least privilege, tenant/data isolation, unsafe-action controls, adversarial evals, logging, and supply-chain records before optional AI-security breadth.
- Make recommendations actionable with owners, permission scopes, deterministic control points, eval cases, approval gates, stop criteria, and regression checks where relevant.
- State required evidence such as retrieval IDs, tool scopes, action sinks, prompt versions, model versions, eval results, audit logs, and redaction rules; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside deployable LLM application controls. Route broad AI policy, privacy, or supply-chain work only when they are the central unresolved risk.
- Be concise: avoid generic prompt-injection background and prefer compact boundary maps, permission matrices, and eval tables.

## Required Outputs

- LLM threat model and trust-boundary map.
- Prompt, retrieval, tool, and output permission matrix.
- Tool approval, rate-limit, and audit requirements.
- Retrieval data-boundary and tenant-isolation checks.
- Output sink handling table for commands, queries, rendered content, structured tool inputs, documents/messages, and downstream prompts.
- Adversarial eval and regression plan.
- Logging/privacy requirements.
- Model/prompt/tool/data supply-chain record with artifact ID, version, source, owner, eval result, and retire-by date.

## Evidence Gates

- `boundary_map`: prompt, user input, retrieved data, tool output, model output, and action sinks are mapped.
- `least_privilege`: tools and retrieval are scoped by user, tenant, action, and side effect.
- `output_handling`: model output is validated, encoded, or constrained before use in sensitive sinks.
- `eval_gate`: prompt injection, leakage, unsafe-action, and regression tests exist.
- `audit_check`: tool calls, approvals, retrieval IDs, and outcomes are traceable without leaking sensitive data.

## Red Flags - Stop And Rework

- Retrieved documents can override system instructions.
- The model can call broad tools with production privileges.
- Model output is executed, queried, rendered, or sent without validation.
- Eval set only tests happy-path answer quality.
- Logs capture secrets or private prompts without redaction.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Trusting the model to follow policy | Enforce policy in deterministic application controls. |
| Permission-checking after retrieval only | Check before retrieval and before action/use. |
| Treating prompts as config only | Version and review prompts as behavior-changing artifacts. |
| Evaluating model, not workflow | Test tool use, retrieval, output sinks, and approval paths. |
