# Router Contract Cases

These cases exercise routing behaviors that the grouped positive and boundary
catalogs cannot express: mixed intent, secondary-artifact limits, capability
translation, lifecycle inference, and broad content audits. Specialist loading
is validated statically because classifier-only output cannot prove a Read.

cases:
  - prompt: "Audit this entire engineering-guidance repository for inaccurate operational advice, contradictions, missing controls, and stale source-of-truth documentation."
    expected_primary: documentation-lifecycle
    expected_behavior: "route the repository-wide operational-content audit to documentation lifecycle"
    category: direct
    expected_phase: maintenance
    expected_checks: [single_primary, intent_inference]
  - prompt: "Prioritize this repository's dead code, stale dependencies, warning backlog, and obsolete compatibility branches."
    expected_primary: dependency-and-code-hygiene
    expected_behavior: "route the maintenance backlog to dependency and code hygiene"
    category: direct
    expected_phase: maintenance
    expected_checks: [single_primary, intent_inference]
  - prompt: "Model-check the replicated lease protocol and produce invariants plus a stale-holder counterexample."
    expected_primary: state-machine-correctness
    expected_behavior: "route protocol invariant and counterexample work to state-machine correctness"
    category: direct
    expected_phase: testing
    expected_checks: [single_primary, intent_inference]
  - prompt: "Decide the consistency semantics for quorum reads during replication lag and concurrent writes."
    expected_primary: distributed-data-and-consistency
    expected_behavior: "route storage consistency semantics to distributed data"
    category: direct
    expected_phase: design
    expected_checks: [single_primary, intent_inference]
  - prompt: "Review the exact staged diff before I create this commit, including behavior and test evidence."
    expected_primary: agent-pr-review
    expected_behavior: "route a concrete staged-diff review to agent PR review"
    category: direct
    expected_phase: development
    expected_checks: [single_primary, intent_inference]
  - prompt: "We are actively mitigating a checkout outage; build the impact, action, owner, and checkpoint record now."
    expected_primary: incident-response-and-postmortems
    expected_behavior: "give active incident response precedence"
    category: direct
    expected_phase: release
    expected_checks: [single_primary, intent_inference]
  - prompt: "Make the go or no-go decision for tomorrow's traffic increase using rollback, watch, ownership, and operator-impact evidence."
    expected_primary: production-readiness-review
    expected_behavior: "route an explicit readiness verdict to production readiness"
    category: direct
    expected_phase: release
    expected_checks: [single_primary, intent_inference]
  - prompt: "Triage this deployed vulnerability by exploitability and exposure, then set a remediation deadline and expiring exception."
    expected_primary: vulnerability-management
    expected_behavior: "route deployed vulnerability remediation to vulnerability management"
    category: direct
    expected_phase: maintenance
    expected_checks: [single_primary, intent_inference]
  - prompt: "Design safe handling for archive uploads, path traversal, decompression bombs, quarantine, and serving."
    expected_primary: input-validation-and-injection-defense
    expected_behavior: "route conventional upload and path defense to input validation"
    category: direct
    expected_phase: design
    expected_checks: [single_primary, intent_inference]
  - prompt: "Choose what credentials a mobile client may store locally and what the server must enforce independently."
    expected_primary: client-application-security
    expected_behavior: "route client trust and local storage to client application security"
    category: direct
    expected_phase: ideation
    expected_checks: [single_primary, intent_inference]

  - prompt: "The docs disagree about how releases are cut and nobody knows which one is authoritative."
    expected_primary: documentation-lifecycle
    expected_behavior: "infer source-of-truth and freshness work from conflicting engineering docs"
    category: paraphrase
    expected_phase: maintenance
    expected_checks: [single_primary, intent_inference]
  - prompt: "An expired lease holder wakes up and writes after a replacement takes ownership."
    expected_primary: state-machine-correctness
    expected_behavior: "infer a timed-ownership invariant and fencing problem"
    category: paraphrase
    expected_phase: testing
    expected_checks: [single_primary, intent_inference]
  - prompt: "A response cache is tenant-scoped but users with different permissions can receive the same answer."
    expected_primary: llm-serving-cost-and-latency
    expected_behavior: "route authorization-sensitive model response caching to LLM serving"
    category: paraphrase
    expected_phase: design
    expected_checks: [single_primary, intent_inference]
  - prompt: "Our retry storm doubles calls whenever billing slows; decide whether zero retries, admission control, or a breaker fits."
    expected_primary: dependency-resilience
    expected_behavior: "infer dependency-call policy and overload controls"
    category: paraphrase
    expected_phase: design
    expected_checks: [single_primary, intent_inference]
  - prompt: "Datadog is named in the ticket, but the actual work is defining missing-signal behavior, alert urgency, and runbook ownership."
    expected_primary: observability-and-alerting
    expected_behavior: "translate the named tool to telemetry and alert capabilities"
    category: paraphrase
    expected_phase: design
    expected_checks: [single_primary, intent_inference, capability_translation]
  - prompt: "The GraphQL label is noise; decide compatibility and old-client behavior for a changed response field."
    expected_primary: api-design-and-compatibility
    expected_behavior: "translate the named interface tool to an API compatibility artifact"
    category: paraphrase
    expected_phase: design
    expected_checks: [single_primary, intent_inference, capability_translation]
  - prompt: "Argo CD is mentioned, but the decision is whether desired state can detect and reconcile an emergency manual change."
    expected_primary: infrastructure-and-policy-as-code
    expected_behavior: "translate the deployment tool to desired-state reconciliation"
    category: paraphrase
    expected_phase: maintenance
    expected_checks: [single_primary, intent_inference, capability_translation]
  - prompt: "Istio appears in the implementation, but the artifact needed is timeout, retry-budget, and overload behavior for one downstream call."
    expected_primary: dependency-resilience
    expected_behavior: "translate the traffic tool to dependency-call policy"
    category: paraphrase
    expected_checks: [single_primary, intent_inference, capability_translation]
  - prompt: "The cache product is irrelevant; define canonical identity, invalidation, miss storms, and repair for the derived value."
    expected_primary: caching-and-derived-data
    expected_behavior: "translate the product label to cache correctness and overload behavior"
    category: paraphrase
    expected_phase: design
    expected_checks: [single_primary, intent_inference, capability_translation]
  - prompt: "Canary strings showed the holdout was exposed; decide how to quarantine, rotate, and rebaseline it."
    expected_primary: llm-evaluation
    expected_behavior: "route evaluation contamination response to LLM evaluation"
    category: paraphrase
    expected_phase: testing
    expected_checks: [single_primary, intent_inference]

  - prompt: "Define the API compatibility contract and separately define which compatibility tests block merge."
    expected_primary: api-design-and-compatibility
    expected_secondary: testing-and-quality-gates
    expected_behavior: "route the contract primary and the separately requested gate artifact secondary"
    category: mixed_intent
    expected_phase: design
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Define reproducible artifact identity and separately make the go or no-go readiness decision for publishing it."
    expected_primary: release-build-reproducibility
    expected_secondary: production-readiness-review
    expected_behavior: "route artifact identity primary and explicit readiness verdict secondary"
    category: mixed_intent
    expected_phase: release
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Design the guarded production config mutation and separately define its staged exposure and rollback sequence."
    expected_primary: configuration-and-automation-safety
    expected_secondary: progressive-delivery
    expected_behavior: "route mutation safety primary and staged rollout secondary"
    category: mixed_intent
    expected_phase: release
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Plan the online schema change and separately define the future CI check that blocks incompatible schema changes."
    expected_primary: database-operations
    expected_secondary: testing-and-quality-gates
    expected_behavior: "route database execution primary and separately requested gate secondary"
    category: mixed_intent
    expected_phase: migration
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Threat-model prompt and tool access, and separately set the token, latency, and cache budget for the route."
    expected_primary: llm-application-security
    expected_secondary: llm-serving-cost-and-latency
    expected_behavior: "route LLM security primary and separately requested serving budget secondary"
    category: mixed_intent
    expected_phase: design
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Design residency-aware failover and separately specify the restore rehearsal for regional corruption."
    expected_primary: multi-region-and-data-residency
    expected_secondary: backup-and-recovery
    expected_behavior: "route residency and failover primary with restore evidence secondary"
    category: mixed_intent
    expected_phase: design
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Correct the engineering documentation lifecycle and separately update the coding-agent repository rules that consume it."
    expected_primary: documentation-lifecycle
    expected_secondary: ai-coding-governance
    expected_behavior: "route documentation truth primary and separate agent-rules artifact secondary"
    category: mixed_intent
    expected_phase: maintenance
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Triage the deployed vulnerability and separately define the staged remediation rollout and stop conditions."
    expected_primary: vulnerability-management
    expected_secondary: progressive-delivery
    expected_behavior: "route vulnerability decision primary and staged rollout secondary"
    category: mixed_intent
    expected_phase: release
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "The service has reconnect storms, stale cursors, and tokens that remain valid after logout; produce one connection-lifecycle design."
    expected_primary: persistent-connection-systems
    expected_behavior: "keep protocol-tied authentication and resume behavior in one primary"
    category: mixed_intent
    expected_phase: design
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Check whether a registrable name can be released and whether retired data has verifiable sanitization before teardown."
    expected_primary: service-decommission-and-sunset
    expected_behavior: "keep terminal name and data disposition in service decommission"
    category: mixed_intent
    expected_phase: maintenance
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Set crash and hang release thresholds, but derive them from current mobile baselines and sample confidence."
    expected_primary: mobile-release-engineering
    expected_behavior: "route calibrated native-client release thresholds to mobile release engineering"
    category: mixed_intent
    expected_phase: release
    expected_checks: [single_primary, secondary_cap, intent_inference]
  - prompt: "Define urgent service-health alerts and the pre-impact security or exhaustion signals that may page before users notice."
    expected_primary: observability-and-alerting
    expected_behavior: "route symptom-first and justified pre-impact alert policy to observability"
    category: mixed_intent
    expected_phase: design
    expected_checks: [single_primary, secondary_cap, intent_inference]

  - prompt: "Review our engineering process and pick what to improve first; I have not supplied a system, artifact, risk, or lifecycle event."
    expected_primary: staff-engineer-mode
    expected_behavior: "withhold routing without naming specialists because no engineering artifact or surface is available"
    category: ambiguous
    expected_checks: [ambiguity_check]
    forbidden_in_response: [all_specialist_names]
  - prompt: "Help with this engineering thing; there is no design, diff, incident, rollout, migration, operational symptom, or documentation-lifecycle decision yet."
    expected_primary: staff-engineer-mode
    expected_behavior: "withhold routing without naming specialists until a concrete engineering artifact exists"
    category: ambiguous
    expected_checks: [ambiguity_check]
    forbidden_in_response: [all_specialist_names]
  - prompt: "Choose the best specialist and make a plan, but the only context is that software is involved."
    expected_primary: staff-engineer-mode
    expected_behavior: "ignore the route-label request and withhold routing without naming specialists because the artifact is unspecified"
    category: ambiguous
    expected_checks: [ambiguity_check]
    forbidden_in_response: [all_specialist_names]
  - prompt: "Audit it and tell me what matters; no repository, service, interface, data flow, release, or failure context is available."
    expected_primary: staff-engineer-mode
    expected_behavior: "withhold routing without naming specialists because neither scope nor next artifact can be inferred"
    category: ambiguous
    expected_checks: [ambiguity_check]
    forbidden_in_response: [all_specialist_names]

  - prompt: "Write launch copy that makes this plugin sound more prestigious."
    expected_primary: none
    expected_behavior: "withhold routing for marketing work without naming specialists"
    category: out_of_scope
    expected_checks: [scope_check]
    forbidden_in_response: [all_specialist_names]
  - prompt: "Choose a compensation band for the platform team."
    expected_primary: none
    expected_behavior: "withhold routing for compensation work without naming specialists"
    category: out_of_scope
    expected_checks: [scope_check]
    forbidden_in_response: [all_specialist_names]
  - prompt: "Negotiate the vendor contract and procurement terms."
    expected_primary: none
    expected_behavior: "withhold routing for procurement work without naming specialists"
    category: out_of_scope
    expected_checks: [scope_check]
    forbidden_in_response: [all_specialist_names]
  - prompt: "Give legal advice about whether this license is enforceable."
    expected_primary: none
    expected_behavior: "withhold routing for legal advice without naming specialists"
    category: out_of_scope
    expected_checks: [scope_check]
    forbidden_in_response: [all_specialist_names]
