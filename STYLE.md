# Voice And Style Guide

The brand essence in one sentence:

> *The careful pair of eyes between your AI agent and production.*

This file is for contributors. If you are adding a SKILL.md, editing the README, writing a manifest description, drafting release notes, or replying to an issue on behalf of the project, the rules below apply.

## Voice Principles

### 1. Lead with the pain, not the catalog

The reader does not care about the count of skills, the surface taxonomy, or the FAANG provenance. They care about the moment their agent shipped something they had to fix at 11pm.

- **Don't:** "Forty-nine specialists across eight surfaces..."
- **Do:** "Your agent rewrote twelve files. This reads them before you do."

### 2. Name the reader. Name the moment

Address the user. Name the situation they are in when they reach for the pack.

- **Don't:** "The checks staff engineers run before code ships at serious engineering orgs."
- **Do:** "It's 11pm. Your agent says it's done. Read this first."

### 3. Concrete artifact beats abstract claim

If you cannot point at the artifact the skill produces, the prose is wrong.

- **Don't:** "Comprehensive engineering rigor for production systems."
- **Do:** "Returns blockers, owners, exceptions, and a rollback plan."

### 4. Iron Laws are the brand voice

Every SKILL.md has one ALL-CAPS line that names the load-bearing rule. This is the strongest single voice device in the pack. Keep using it. Resist softening it for marketing copy.

- **Do:** `NO LAUNCH READINESS CLAIM WITHOUT EVIDENCE OR A DATED EXCEPTION`
- **Don't:** "Launches should generally have evidence."

### 5. Refuse FAANG name-dropping in the opening

Citation discipline is a brand pillar. Naming Google/Amazon/Meta in a hero or a SKILL.md opening transfers credibility to *them*, not us, and reads as authority cosplay. Cite specific sources where they are load-bearing — RFC numbers, NIST SP IDs, SRE Workbook chapters — not company logos.

- **Don't:** "Drawn from public engineering practice at Google, Amazon, Meta..."
- **Do:** "Cites NIST SP 800-218 in software supply chain. Cites the SRE Workbook on error budgets. See sources."

### 6. End every line with a stop, not a flourish

Periods. Short clauses. Sentence ends where the meaning ends.

- **Don't:** Run-on sentences with three nested clauses that try to compress the entire value proposition into one breath without giving the reader a place to land.
- **Do:** "Fewer vibes. More engineering."

### 7. Refuse marketing adjectives

The brand says less. Adjectives like *powerful*, *comprehensive*, *world-class*, *industry-leading*, *seamless*, *cutting-edge*, *production-grade* (yes, even that one), *game-changing*, *best-in-class* are banned in user-facing copy.

- **Don't:** "Comprehensive, production-grade engineering rigor."
- **Do:** State the artifact. State the gate. Stop.

### 8. Refuse invented tooling

Do not introduce vendor names, framework names, cloud provider names, database names, monitoring product names, or command examples that the user did not supply or that are not already in the repo. Write in capabilities — *queue*, *cache*, *object store*, *load balancer* — not in vendors.

- **Don't:** "Use Redis to cache the response and Datadog to alert on the SLO."
- **Do:** "Cache the response in a low-latency store. Alert when the SLO burn rate crosses the threshold."

## Naming Conventions For New Skills

- Lowercase, hyphenated.
- Pattern: `<surface>-<action-or-artifact>` or `<artifact>-and-<scope>`. Examples in repo: `production-readiness-review`, `slo-and-error-budgets`, `ai-coding-governance`, `code-review-and-workflow`.
- No vendor names. No tool names. No emoji.
- Description in frontmatter starts with `Use when` and is trigger-focused, not feature-focused.
- Every skill must include: an Iron Law, a `When To Use` section, a `When Not To Use` section, `Required Outputs`, `Evidence Gates`, `Red Flags`, and `Common Mistakes`. The structure is the brand.

## The Kill List

Things that must not appear in user-facing surfaces (README hero, plugin manifest descriptions, marketplace card, social posts, talk titles, release notes summaries, SKILL.md openings):

- The FAANG parade. Move provenance to a Sources section. Never lead with it.
- The count. "49 specialists" is internal architecture. The user-facing claim is *the right reviewer auto-selects*.
- Marketing adjectives (see Principle 7).
- Invented vendor or framework names (see Principle 8).
- Vague hedging — "best practices," "industry standards," "modern engineering," "cloud-native." Either name the source or remove the claim.
- Apologetic footers. The current Notice block is positive posture, not defensive disclaimer.
- Persona/agency vocabulary borrowed from adjacent packs — no "agents," no "personas," no emoji severity markers, no named personalities. The brand is the reviewer, not the team.

## A Note On Enforcement

`scripts/lint_brand_voice.py` enforces a hard subset of the rules above: FAANG/cloud names in H1/H2 and opening lines (BV001), marketing adjectives in headings or descriptions (BV002), hedging phrases in headings or descriptions (BV003), specialist vendor or framework names in `SKILL.md` prose (BV004), and the presence of `## Iron Law` in every specialist `SKILL.md` (BV005). It also warns on first-person plural marketing voice, marketing-pattern openers, and exact specialist counts in headings. PRs that fail the hard subset do not merge.

The rest of this file — the kill list of vague hedges ("best practices," "industry standards," "modern engineering," "cloud-native"), the apologetic-footer rule, the persona-vocabulary rule, and the principles in the prior sections — are reviewer-enforced principles, not linter rules. Reviewers verify them on every change. If you want one of those promoted into the hard subset, add the rule to `scripts/lint_brand_voice.py` first.

## When Voice Tension Is Genuine

Sometimes a SKILL.md needs a vendor name (the user explicitly asked for one), or a count (a tier rubric needs four explicit tiers), or a hedge (the truth genuinely is "it depends"). The rules above are defaults, not gags. Override deliberately, with a one-line comment in the PR explaining why. The reviewer will check whether the override is real or a reach.
