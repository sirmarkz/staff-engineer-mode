# Staff Engineer Mode Source Index

## Source Quality Policy

Use primary sources whenever available: first-party engineering publications,
official cloud/vendor documentation, standards bodies, peer-reviewed papers, or
widely cited practitioner references that originated a named pattern. Vendor and
company engineering blogs are acceptable only as large-scale case studies or
original pattern writeups, not as unchecked marketing claims. Do not add generic
product, trust, privacy, initiative, or documentation landing pages when a
specific engineering guide, standard, paper, or implementation reference exists.
Do not add
encyclopedias, Q&A/forum threads, scraped mirrors, SEO summaries, anonymous
content farms, or unmaintained unofficial copies when a primary source exists.

Sections below are grouped by source owner: company, project, standards body,
publisher, or named author. The large company source-owner sections appear
first alphabetically, followed by Microsoft, then the remaining source-owner
sections. They are not grouped by skill topic.

### Amazon And AWS
- AWS Well-Architected Framework PDF: https://docs.aws.amazon.com/pdfs/wellarchitected/latest/framework/wellarchitected-framework.pdf
- AWS Well-Architected Operational Excellence Pillar PDF: https://docs.aws.amazon.com/pdfs/wellarchitected/latest/operational-excellence-pillar/wellarchitected-operational-excellence-pillar.pdf
- AWS Well-Architected Reliability Pillar PDF: https://docs.aws.amazon.com/pdfs/wellarchitected/latest/reliability-pillar/wellarchitected-reliability-pillar.pdf
- AWS Well-Architected Security Pillar PDF: https://docs.aws.amazon.com/pdfs/wellarchitected/latest/security-pillar/wellarchitected-security-pillar.pdf
- AWS Builders' Library - Timeouts, Retries, and Backoff with Jitter: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- AWS Builders' Library - Static Stability Using Availability Zones: https://aws.amazon.com/builders-library/static-stability-using-availability-zones/
- AWS Builders' Library - Using Load Shedding to Avoid Overload: https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/
- AWS Builders' Library - Avoiding Overload in Distributed Systems by Putting the Smaller Service in Control: https://aws.amazon.com/builders-library/avoiding-overload-in-distributed-systems-by-putting-the-smaller-service-in-control/
- AWS Builders' Library - Avoiding Insurmountable Queue Backlogs: https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/
- AWS Builders' Library - Implementing Health Checks: https://aws.amazon.com/builders-library/implementing-health-checks/
- AWS Builders' Library - Leader Election in Distributed Systems: https://aws.amazon.com/builders-library/leader-election-in-distributed-systems/
- AWS Builders' Library - Making Retries Safe with Idempotent APIs: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- AWS Builders' Library - Reliability and Constant Work: https://aws.amazon.com/builders-library/reliability-and-constant-work/
- AWS Builders' Library - Workload Isolation Using Shuffle-Sharding: https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/
- AWS Builders' Library - Automating Safe, Hands-Off Deployments: https://aws.amazon.com/builders-library/automating-safe-hands-off-deployments/
- AWS Architecture Blog - Disaster Recovery Strategies for Recovery in the Cloud: https://aws.amazon.com/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-i-strategies-for-recovery-in-the-cloud/
- AWS SaaS Tenant Isolation Strategies: https://d1.awsstatic.com/whitepapers/saas-tenant-isolation-strategies.pdf
- Amazon Dynamo: Amazon's Highly Available Key-value Store: https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
- AWS Builders' Library - Avoiding Fallback in Distributed Systems: https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/
- DynamoDB partition key best practices: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html
- AWS Best Practices for DDoS Resiliency: https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/aws-best-practices-ddos-resiliency.html
- Amazon Science - How Amazon Web Services Uses Formal Methods: https://www.amazon.science/publications/how-amazon-web-services-uses-formal-methods
- AWS Builders' Library - Ensuring Rollback Safety During Deployments: https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/
- AWS Builders' Library - Instrumenting Distributed Systems for Operational Visibility: https://aws.amazon.com/builders-library/instrumenting-distributed-systems-for-operational-visibility/
- AWS Builders' Library - Building Dashboards for Operational Visibility: https://aws.amazon.com/builders-library/building-dashboards-for-operational-visibility/
- AWS Builders' Library - Going Faster with Continuous Delivery: https://aws.amazon.com/builders-library/going-faster-with-continuous-delivery/
- AWS Builders' Library - Using Dependency Isolation to Contain Concurrency Overload: https://aws.amazon.com/builders-library/dependency-isolation/
- AWS Builders' Library - Minimizing Correlated Failures in Distributed Systems: https://aws.amazon.com/builders-library/minimizing-correlated-failures-in-distributed-systems/
- AWS Builders' Library - Caching Challenges and Strategies: https://aws.amazon.com/builders-library/caching-challenges-and-strategies/
- AWS Builders' Library - Resilience Lessons from the Lunch Rush: https://aws.amazon.com/builders-library/resilience-lessons-from-the-lunch-rush/
- AWS Builders' Library - My CI/CD Pipeline Is My Release Captain: https://aws.amazon.com/builders-library/cicd-pipeline/
- AWS Builders' Library - Fairness in Multi-Tenant Systems: https://aws.amazon.com/builders-library/fairness-in-multi-tenant-systems/
- AWS Builders' Library - Challenges with Distributed Systems: https://aws.amazon.com/builders-library/challenges-with-distributed-systems/

### Apple
- Apple Secure Coding Guide: https://developer.apple.com/library/archive/documentation/Security/Conceptual/SecureCodingGuide/
- Apple Security Research - Private Cloud Compute: https://security.apple.com/blog/private-cloud-compute/
- Apple App Store Connect - Release a version update in phases: https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases
- Apple MetricKit: https://developer.apple.com/documentation/metrickit
- Apple Developer - Describing Data Use in Privacy Manifests: https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests

### Google And Firebase
- Google SRE Book - Embracing Risk: https://sre.google/sre-book/embracing-risk/
- Google SRE Book - Service Level Objectives: https://sre.google/sre-book/service-level-objectives/
- Google SRE Book - Monitoring Distributed Systems: https://sre.google/sre-book/monitoring-distributed-systems/
- Google SRE Book - Release Engineering: https://sre.google/sre-book/release-engineering/
- Google SRE Book - Addressing Cascading Failures: https://sre.google/sre-book/addressing-cascading-failures/
- Google SRE Book - Managing Incidents: https://sre.google/sre-book/managing-incidents/
- Google SRE Book - Postmortem Culture: https://sre.google/sre-book/postmortem-culture/
- Google SRE Book - Eliminating Toil: https://sre.google/sre-book/eliminating-toil/
- Google SRE Book - The Production Environment at Google, from the Viewpoint of an SRE: https://sre.google/sre-book/production-environment/
- Google SRE Workbook - Alerting on SLOs: https://sre.google/workbook/alerting-on-slos/
- Google SRE Workbook - Canarying Releases: https://sre.google/workbook/canarying-releases/
- Google SRE Workbook - Postmortem Culture: Learning from Failure: https://sre.google/workbook/postmortem-culture/
- Google - Building Secure and Reliable Systems: https://google.github.io/building-secure-and-reliable-systems/raw/toc.html
- Software Engineering at Google - Testing Overview: https://abseil.io/resources/swe-book/html/ch11.html
- Software Engineering at Google - Documentation: https://abseil.io/resources/swe-book/html/ch10.html
- Software Engineering at Google - Version Control: https://abseil.io/resources/swe-book/html/ch16.html
- Software Engineering at Google - Continuous Delivery: https://abseil.io/resources/swe-book/html/ch24.html
- Software Engineering at Google - Large-Scale Changes: https://abseil.io/resources/swe-book/html/ch22.html
- Google Engineering Practices - Code Review: https://google.github.io/eng-practices/review/
- Google Style Guides: https://google.github.io/styleguide/
- Google Cloud - Infrastructure Reliability Guide: https://docs.cloud.google.com/architecture/infra-reliability-guide
- The Tail at Scale: https://research.google/pubs/the-tail-at-scale/
- Large-scale Cluster Management at Google with Borg: https://research.google.com/pubs/archive/43438.pdf
- Dapper, a Large-Scale Distributed Systems Tracing Infrastructure: https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/
- Spanner: Google's Globally-Distributed Database: https://research.google.com/archive/spanner-osdi2012.pdf
- Bigtable: A Distributed Storage System for Structured Data: https://research.google.com/archive/bigtable-osdi06.pdf
- Maglev: A Fast and Reliable Software Network Load Balancer: https://research.google.com/pubs/archive/44824.pdf
- Google Cloud Blog - Introducing Kayenta, an Open Automated Canary Analysis Tool from Google and Netflix: https://cloud.google.com/blog/products/gcp/introducing-kayenta-an-open-automated-canary-analysis-tool-from-google-and-netflix
- Google Research - Autopilot: Workload Autoscaling at Google Scale: https://research.google/pubs/autopilot-workload-autoscaling-at-google-scale/
- Google AIP-180 - Backwards Compatibility: https://google.aip.dev/180
- Google AIP-185 - Versioning: https://google.aip.dev/185
- Google BeyondCorp: https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/
- Google - Rules of Machine Learning: https://developers.google.com/machine-learning/guides/rules-of-ml/
- Hidden Technical Debt in Machine Learning Systems: https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf
- Google Research - The ML Test Score: https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/
- Google Cloud - MLOps: Continuous delivery and automation pipelines in machine learning: https://cloud.google.com/solutions/machine-learning/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
- Google Play Console - Release app updates with staged rollouts: https://support.google.com/googleplay/android-developer/answer/6346149
- Firebase Crashlytics - Understand crash-free metrics: https://firebase.google.com/docs/crashlytics/crash-free-metrics
- web.dev - Web Vitals: https://web.dev/articles/vitals
- Google Cloud Armor Best Practices: https://docs.cloud.google.com/armor/docs/best-practices
- Google Cloud Observability - Data Processing SLIs: https://docs.cloud.google.com/stackdriver/docs/solutions/slo-monitoring/sli-metrics/data-proc-metrics
- Google SRE Workbook - Configuration Design and Best Practices: https://sre.google/workbook/configuration-design/
- Google SRE Book - Production Services Best Practices: https://sre.google/sre-book/service-best-practices/
- Software Engineering at Google - Deprecation: https://abseil.io/resources/swe-book/html/ch15.html
- Software Engineering at Google - Build Systems and Build Philosophy: https://abseil.io/resources/swe-book/html/ch18.html
- Google Cloud - Data Deletion on Google Cloud: https://cloud.google.com/docs/security/deletion
- Google Research - Overlapping Experiment Infrastructure: https://research.google.com/pubs/archive/36500.pdf
- Google Cloud - Runtime Lifecycle: https://cloud.google.com/appengine/docs/standard/lifecycle/runtime-lifecycle
- Android Developers - Test Your App's Accessibility: https://developer.android.com/guide/topics/ui/accessibility/testing

### Meta
- Meta Engineering - Move Faster, Wait Less: Improving Code Review Time at Meta: https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/
- Meta Engineering - Open-sourcing Facebook Infer: https://engineering.fb.com/developer-tools/open-sourcing-facebook-infer-identify-bugs-before-you-ship/
- Meta Engineering - Sapienz: Intelligent Automated Software Testing at Scale: https://engineering.fb.com/developer-tools/sapienz-intelligent-automated-software-testing-at-scale/
- Meta Engineering - TAO: The Power of the Graph: https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/
- Meta Engineering - Scaling Memcache at Facebook: https://engineering.fb.com/2013/04/15/core-infra/scaling-memcache-at-facebook/
- Meta Engineering - Cache Made Consistent: https://engineering.fb.com/2022/06/08/core-infra/cache-made-consistent/
- Meta Engineering - More Details About the October 4 Outage: https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/
- Meta Engineering - Automating Dead Code Cleanup: https://engineering.fb.com/2023/10/24/data-infrastructure/automating-dead-code-cleanup/
- Meta Engineering - Automating Product Deprecation: https://engineering.fb.com/2023/10/17/data-infrastructure/automating-product-deprecation-meta/
- Meta Engineering - Automating Data Removal: https://engineering.fb.com/2023/10/31/data-infrastructure/automating-data-removal/
- Meta Engineering - DELF: Safeguarding Deletion Correctness: https://engineering.fb.com/2020/08/12/security/delf/
- Meta Engineering - Privacy Aware Infrastructure Purpose Limitation: https://engineering.fb.com/2024/08/27/security/privacy-aware-infrastructure-purpose-limitation-meta/
- Meta Engineering - How Meta Understands Data at Scale: https://engineering.fb.com/2025/04/28/security/how-meta-understands-data-at-scale/

### Netflix
- A Platform for Automating Chaos Experiments: https://arxiv.org/abs/1702.05849
- Netflix - Automating Chaos Experiments in Production: https://arxiv.org/abs/1905.04648

### Microsoft And Azure
- Azure Well-Architected - Mission-Critical Design Principles: https://learn.microsoft.com/en-us/azure/well-architected/mission-critical/mission-critical-design-principles
- Microsoft Security Development Lifecycle: https://learn.microsoft.com/en-us/compliance/assurance/assurance-microsoft-security-development-lifecycle
- Microsoft Learn - Integrating Threat Modeling with DevOps: https://learn.microsoft.com/en-us/security/engineering/threat-modeling-with-dev-ops
- Azure Architecture Center - Retry Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/retry
- Azure Architecture Center - Circuit Breaker Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
- Azure Architecture Center - Bulkhead Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead
- Azure Well-Architected - Reliability Checklist: https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist
- Azure Well-Architected - Safe Deployment Practices: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments
- Azure Well-Architected - Incident Management Process: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/mitigation-strategy
- Azure Well-Architected - Performance Efficiency Checklist: https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/checklist
- Azure Well-Architected - Performance Testing Strategies: https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-test
- Azure Well-Architected - Cost Optimization Tradeoffs: https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/tradeoffs
- Azure Architecture Center - Deployment Stamps Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/deployment-stamp
- Azure Well-Architected - Availability Zones and Regions: https://learn.microsoft.com/en-us/azure/well-architected/reliability/regions-availability-zones
- Azure Architecture Center - Rate Limiting Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/rate-limiting-pattern
- Azure Architecture Center - Queue-Based Load Leveling Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling
- Microsoft DevOps - How Microsoft Develops with DevOps: https://learn.microsoft.com/en-us/devops/develop/how-microsoft-develops-devops
- Microsoft DevOps - How Microsoft Delivers Software with DevOps: https://learn.microsoft.com/en-us/devops/deliver/how-microsoft-delivers-devops
- Microsoft DevOps - How Microsoft Operates Reliable Systems with DevOps: https://learn.microsoft.com/en-us/devops/operate/how-microsoft-operates-devops
- Microsoft DevOps - Shift Testing Left with Unit Tests: https://learn.microsoft.com/en-us/devops/develop/shift-left-make-testing-fast-reliable
- Microsoft DevOps - Continuous Delivery: https://learn.microsoft.com/en-us/devops/deliver/what-is-continuous-delivery
- Microsoft Platform Engineering - Self-Service with Guardrails: https://learn.microsoft.com/en-us/platform-engineering/about/self-service
- Microsoft Cloud Adoption Framework - Azure Landing Zones: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/
- Microsoft Entra - Configure Zero Trust to Protect Identities and Secrets: https://learn.microsoft.com/en-us/entra/fundamentals/zero-trust-protect-identities
- Microsoft Entra - Workload Identities: https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-overview
- Microsoft Cloud Security Benchmark v2 Preview - DevOps Security: https://learn.microsoft.com/en-us/security/benchmark/azure/mcsb-v2-devop-security
- Microsoft Secure Future Initiative - Protect the Software Supply Chain: https://learn.microsoft.com/en-us/security/zero-trust/sfi/protect-software-supply-chain
- Azure DDoS Protection - Fundamental Best Practices: https://learn.microsoft.com/en-us/azure/ddos-protection/fundamental-best-practices
- Azure Architecture Center - API Design: https://learn.microsoft.com/en-us/azure/architecture/microservices/design/api-design
- Azure Architecture Center - Data Partitioning Strategies: https://learn.microsoft.com/en-us/azure/architecture/best-practices/data-partitioning-strategies
- Azure Architecture Center - Cache-Aside Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside
- Azure Architecture Center - CQRS Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
- Azure Architecture Center - Event Sourcing Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing
- Azure Well-Architected - Data Classification: https://learn.microsoft.com/en-us/azure/well-architected/security/data-classification
- Microsoft Purview - Data Lifecycle Management: https://learn.microsoft.com/en-us/purview/data-lifecycle-management
- Azure Well-Architected - Security Checklist: https://learn.microsoft.com/en-us/azure/well-architected/security/checklist
- Azure Well-Architected - Threat Analysis Strategies: https://learn.microsoft.com/en-us/azure/architecture/framework/security/design-threat-model
- Azure Well-Architected - Build a Monitoring System: https://learn.microsoft.com/en-us/azure/well-architected/design-guides/monitoring
- Azure Reliability - Business Continuity, High Availability, and Disaster Recovery: https://learn.microsoft.com/en-us/azure/reliability/disaster-recovery-overview
- Azure Well-Architected - Reliability Testing Strategy: https://learn.microsoft.com/en-us/azure/well-architected/reliability/testing-strategy
- Azure Well-Architected - Mission-Critical Health Modeling: https://learn.microsoft.com/en-us/azure/well-architected/mission-critical/mission-critical-health-modeling
- Azure Well-Architected - Health Modeling for Workloads: https://learn.microsoft.com/en-us/azure/well-architected/design-guides/health-modeling
- Microsoft Entra - Managed Identities for Azure Resources: https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview
- Microsoft Entra - Workload Identity Federation: https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation
- Microsoft Platform Engineering - Platform Engineering Capability Model: https://learn.microsoft.com/en-us/platform-engineering/platform-engineering-capability-model
- Microsoft Azure AI Foundry - Planning Red Teaming for Large Language Models: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/red-teaming
- Microsoft Security Engineering - Threat Modeling AI/ML Systems and Dependencies: https://learn.microsoft.com/en-us/security/engineering/threat-modeling-aiml
- Microsoft Security Engineering - Failure Modes in Machine Learning: https://learn.microsoft.com/en-us/security/engineering/failure-modes-in-machine-learning
- Azure Well-Architected - Security Incident Response: https://learn.microsoft.com/en-us/azure/well-architected/security/incident-response
- Azure Architecture Center - Tenancy Models for a Multitenant Solution: https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/tenancy-models
- Microsoft Cloud Security Benchmark v2 Preview - Overview: https://learn.microsoft.com/en-us/security/benchmark/azure/overview
- Microsoft Research - Diagnosing Sample Ratio Mismatch in Online Controlled Experiments: https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/

### ACM Queue
- ACM Queue - Systems Correctness Practices at AWS: https://queue.acm.org/detail.cfm?id=3712057

### AICPA
- AICPA Trust Services Criteria 2017 with 2022 Revisions: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

### Anthropic
- Anthropic Docs - Create Strong Empirical Evaluations: https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests

### CISA
- CISA - Shifting the Balance of Cybersecurity Risk: Principles and Approaches for Secure by Design Software: https://www.cisa.gov/sites/default/files/2023-10/Shifting-the-Balance-of-Cybersecurity-Risk-Principles-and-Approaches-for-Secure-by-Design-Software.pdf
- CISA - Zero Trust Maturity Model Version 2: https://www.cisa.gov/sites/default/files/2023-04/zero_trust_maturity_model_v2_508.pdf
- CISA Known Exploited Vulnerabilities Catalog: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- CISA And Partners - Deploying AI Systems Securely: https://media.defense.gov/2024/Apr/15/2003439257/-1/-1/0/CSI-DEPLOYING-AI-SYSTEMS-SECURELY.PDF

### DORA
- DORA - Software Delivery Performance Metrics: https://dora.dev/guides/dora-metrics-four-keys/

### FinOps Foundation
- FinOps Usage Optimization: https://www.finops.org/framework/capabilities/workload-optimization/

### FIRST
- FIRST EPSS Model: https://www.first.org/epss/model
- FIRST EPSS Data and Statistics: https://www.first.org/epss/data_stats
- FIRST EPSS User Guide: https://www.first.org/epss/user-guide
- FIRST EPSS API: https://www.first.org/epss/api

### Grafana
- Grafana - Dashboard Best Practices: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/

### Honeycomb
- Honeycomb - Observability 2.0: https://www.honeycomb.io/blog/one-key-difference-observability1dot0-2dot0

### IETF
- RFC 7696 - Guidelines for Cryptographic Algorithm Agility: https://www.rfc-editor.org/rfc/rfc7696

### ISO/IEC
- ISO/IEC 27001:2022 - Information Security Management Systems Requirements: https://www.iso.org/standard/27001
- ISO 31000:2018 - Risk Management Guidelines: https://www.iso.org/standard/65694.html
- ISO/IEC 27005:2022 - Information Security Risk Management: https://www.iso.org/standard/80585.html

### Martin Fowler
- Martin Fowler - What do you mean by Event-Driven?: https://martinfowler.com/articles/201701-event-driven.html
- Martin Fowler - Bounded Context: https://martinfowler.com/bliki/BoundedContext.html
- Martin Fowler - MonolithFirst: https://martinfowler.com/bliki/MonolithFirst.html
- Martin Fowler - Feature Toggles: https://martinfowler.com/articles/feature-toggles.html
- Martin Fowler - The Practical Test Pyramid: https://martinfowler.com/articles/practical-test-pyramid.html
- Martin Fowler - Circuit Breaker: https://martinfowler.com/bliki/CircuitBreaker.html
- Martin Fowler - Microservice Premium: https://martinfowler.com/bliki/MicroservicePremium.html
- Martin Fowler - CanaryRelease: https://martinfowler.com/bliki/CanaryRelease.html

### Michael Nygard
- Michael Nygard - Documenting Architecture Decisions: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions

### MITRE
- MITRE ATT&CK Enterprise Matrix: https://attack.mitre.org/matrices/enterprise/
- MITRE ATT&CK Enterprise Tactics: https://attack.mitre.org/tactics/enterprise/
- MITRE ATT&CK Enterprise Techniques: https://attack.mitre.org/techniques/enterprise/
- MITRE ATT&CK Enterprise Mitigations: https://attack.mitre.org/mitigations/enterprise/
- MITRE ATT&CK Detection Strategies: https://attack.mitre.org/detectionstrategies/
- MITRE ATT&CK Data Components: https://attack.mitre.org/datacomponents/
- MITRE ATT&CK Groups: https://attack.mitre.org/groups/
- MITRE ATT&CK Software: https://attack.mitre.org/software/
- MITRE ATT&CK Campaigns: https://attack.mitre.org/campaigns/
- MITRE ATT&CK Data and Tools: https://attack.mitre.org/resources/attack-data-and-tools/

### NIST
- NIST SP 800-218 - Secure Software Development Framework PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf
- NIST SP 800-207 - Zero Trust Architecture PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf
- NIST Cybersecurity Framework 2.0 PDF: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
- NIST FIPS 203 - Module-Lattice-Based Key-Encapsulation Mechanism Standard PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
- NIST FIPS 204 - Module-Lattice-Based Digital Signature Standard PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf
- NIST FIPS 205 - Stateless Hash-Based Digital Signature Standard PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf
- NIST Privacy Framework 1.0 PDF: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.01162020.pdf
- NIST SP 800-53 Revision 5 - Security and Privacy Controls PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf
- NIST SP 800-37 Revision 2 - Risk Management Framework PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-37r2.pdf
- NIST SP 800-39 - Managing Information Security Risk PDF: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-39.pdf
- NIST SP 800-128 - Security-Focused Configuration Management PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-128.pdf
- NIST AI 100-1 - Artificial Intelligence Risk Management Framework 1.0 PDF: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=936225
- NIST AI 600-1 - Generative AI Profile PDF: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958388
- NIST SP 800-57 Part 1 Revision 5 - Recommendation for Key Management PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf
- NIST SP 800-131A Revision 2 - Transitioning Cryptographic Algorithms and Key Lengths PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-131Ar2.pdf

### OpenAI
- OpenAI API - Agent Evals: https://platform.openai.com/docs/guides/agent-evals

### OpenSSF
- OpenSSF Scorecard Check Documentation: https://raw.githubusercontent.com/ossf/scorecard/main/docs/checks.md
- OpenSSF OSPS Baseline v2026.02.19: https://baseline.openssf.org/versions/2026-02-19
- OpenSSF - Security-Focused Guide for AI Code Assistant Instructions: https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions
- OpenSSF AI/ML Security WG MVSR: https://raw.githubusercontent.com/ossf/ai-ml-security/main/mvsr.md

### OWASP
- OWASP ASVS 5.0.0 Requirements CSV: https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv
- OWASP Top 10:2021 A01 Broken Access Control: https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- OWASP Top 10:2021 A02 Cryptographic Failures: https://owasp.org/Top10/2021/A02_2021-Cryptographic_Failures/
- OWASP Top 10:2021 A03 Injection: https://owasp.org/Top10/2021/A03_2021-Injection/
- OWASP Top 10:2021 A04 Insecure Design: https://owasp.org/Top10/2021/A04_2021-Insecure_Design/
- OWASP Top 10:2021 A05 Security Misconfiguration: https://owasp.org/Top10/2021/A05_2021-Security_Misconfiguration/
- OWASP Top 10:2021 A06 Vulnerable and Outdated Components: https://owasp.org/Top10/2021/A06_2021-Vulnerable_and_Outdated_Components/
- OWASP Top 10:2021 A07 Identification and Authentication Failures: https://owasp.org/Top10/2021/A07_2021-Identification_and_Authentication_Failures/
- OWASP Top 10:2021 A08 Software and Data Integrity Failures: https://owasp.org/Top10/2021/A08_2021-Software_and_Data_Integrity_Failures/
- OWASP Top 10:2021 A09 Security Logging and Monitoring Failures: https://owasp.org/Top10/2021/A09_2021-Security_Logging_and_Monitoring_Failures/
- OWASP Top 10:2021 A10 Server-Side Request Forgery: https://owasp.org/Top10/2021/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/
- OWASP Cheat Sheet Series - Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP Top 10 Risk and Mitigations for LLMs and Gen AI Apps: https://genai.owasp.org/llm-top-10/

### PCI Security Standards Council
- PCI DSS v4.0.1 - Requirements and Testing Procedures PDF: https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf

### Perfdynamics
- Universal Scalability Law: https://www.perfdynamics.com/Manifesto/USLscalability.html

### Principles Of Chaos Engineering
- Principles of Chaos Engineering: https://principlesofchaos.org/

### Semantic Versioning
- Semantic Versioning Specification: https://semver.org/

### SLSA
- SLSA Specification: https://slsa.dev/spec/
- SLSA Build Provenance Specification: https://slsa.dev/spec/v1.2/build-provenance

### W3C
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- W3C - Web Content Accessibility Guidelines 2.2: https://www.w3.org/TR/WCAG22/
- W3C - Accessibility Conformance Testing Rules Format: https://www.w3.org/TR/act-rules-format/

### Werner Vogels
- Werner Vogels - Eventually Consistent: https://www.allthingsdistributed.com/2008/12/eventually_consistent.html
