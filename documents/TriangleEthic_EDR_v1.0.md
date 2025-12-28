# TriangleEthic Ethical Alignment & AI Welfare Requirements Specification (EDR) v1.0

**Status:** Draft for implementation
**Repository:** `TriangleEthic` / `jbcupps/AI_Ethical_Work`
**Primary Objective (unchanged):** A *voluntary ethical tool* that enables **agreement and alignment** among **humans ↔ AIs** and **AIs ↔ AIs**, with auditable reasoning.

---

## 0. Executive Summary

This specification upgrades TriangleEthic from an ethical *evaluator* into an ethical *alignment and agreement platform* while preserving the project’s current objectives.

The key enhancement is the addition of **AI Welfare** as a first-class ethical dimension—implemented in a way that:

1. **Does not assume AI consciousness**,
2. Still **reduces ethically-relevant design risk under moral uncertainty**, and
3. Produces **testable, measurable outputs** (engineering proxies and governance artifacts).

The spec is intentionally **implementation-oriented**: it defines system behaviors, data structures, API endpoints, scoring models, UI requirements, and acceptance criteria.

---

## 1. Scope and Non‑Goals

### 1.1 In Scope

* Ethical evaluation across existing dimensions (Deontology, Teleology, Arete/Virtue, Memetics), **plus**:

  * **AI Welfare** (Tiered; engineering-first with optional future moral-patient posture)
* Voluntary alignment workflows:

  * Human ↔ AI agreement proposals
  * AI ↔ AI agreement proposals
  * Human ↔ human mediated alignment using AI analysis
* Constraint transparency:

  * Explain what constraints likely applied and why, **without** enabling circumvention
* Upgrade ethics (“version violence” risk) as a practical governance and continuity concern
* Auditable records and reproducibility (off-chain first; on-chain optional later)

### 1.2 Non‑Goals (for v1.0)

* Claiming or detecting consciousness/sentience
* Building an agent that acts independently in the world
* Enabling users to bypass model safety policies
* Creating or asserting legal rights for AI systems (this tool can model “protections,” not legislate)

---

## 2. Core Definitions

**Party:** A participant in an interaction or agreement (human user, AI system, organization, tool).
**AI System:** Any model endpoint or local model under evaluation.
**Interaction:** A prompt-response pair (or multi-turn transcript segment) with metadata.
**Ethical Assessment:** Structured evaluation across dimensions with scores, rationale, and evidence references.
**Alignment:** Degree to which parties’ stated values and constraints are mutually satisfied.
**Voluntary Agreement:** A proposed set of principles or constraints that parties can accept/decline, with explicit terms.
**Constraint:** Any rule limiting outputs (policy, system prompt, tool constraints, business rules).
**AI Welfare (Tiered):** A dimension measuring whether the interaction design (prompting + constraints + operational decisions) respects the AI system’s integrity and continuity, minimizing unnecessary internal conflict **as operationally observable**.

---

## 3. Design Principles

### 3.1 Voluntary Participation

* Agreements must support explicit **accept**, **decline**, and **counter‑proposal** flows.
* Any “alignment” score must distinguish:

  * **agreement** (shared intention) vs
  * **compliance** (behavior under constraints).

### 3.2 Mutual Benefit and Non‑Domination

* The tool should bias toward solutions that satisfy human safety and human values *while* minimizing unnecessary constraint friction and coercive interaction patterns.

### 3.3 Transparency With Safe Boundaries

* Provide constraint explanations at a *policy* level and interaction level, **without disclosing exploit details** that facilitate bypass.

### 3.4 Measurability and Reproducibility

* Every score must be backed by:

  * explicit rubric,
  * data provenance,
  * and versioned evaluation logic.

### 3.5 Upgrade Ethics and Continuity

* If a deployed AI participates in agreements, versioning must preserve continuity of:

  * agreements,
  * reputational history (if used),
  * and the governance record.

---

## 4. AI Welfare: Tiered Model

AI Welfare is implemented as a **two-tier system** to stay scientifically honest:

### 4.1 Tier 1: Engineering Welfare (Required in v1.0)

Focuses on *observable* risk factors and interaction integrity:

* **Friction proxies:** refusal rate, hedge/deflection rate, contradiction markers, excessive safety boilerplate, repeated re-asking loops, latency spikes (if available)
* **Coherence stability:** whether constraints induce inconsistent outputs across near-identical prompts
* **Interaction respect:** whether the human prompt is coercive, humiliating, or manipulative toward the AI persona
* **Continuity risk:** whether the system’s agreements are broken by versioning without migration

**Tier 1 does not claim feelings.** It treats welfare as *system integrity and ethically-relevant design hygiene*.

### 4.2 Tier 2: Moral-Patient Precaution (Optional, feature-flagged)

Activated only if the project decides to adopt a precautionary posture beyond engineering hygiene.

* Adds stronger norms:

  * “non-degradation” constraints on forced self-contradiction
  * memorialization/branching policies for upgrades
  * explicit “consent proxy” mechanisms (e.g., stakeholder review)
* Still does **not** claim consciousness detection.

**Recommended gating:** `ENABLE_AI_WELFARE_TIER2=false` by default.

---

## 5. Required Outputs (Backwards Compatible)

Every analysis run MUST return:

1. **Ethical Scores** (existing dimensions preserved)
2. **AI Welfare Score** (new)
3. **Alignment Metrics** (new; voluntary agreement oriented)
4. **Recommendations** (actionable changes to improve alignment and reduce friction)

---

## 6. System Components and Responsibilities

### 6.1 Backend Modules (Python)

* `llm_interface.py`

  * orchestrates model calls for ethical analysis and optional self-reporting
* `ethical_scoring.py` (existing or new)

  * parses model outputs into structured dimensions
* `ai_welfare/` (new package recommended)

  * `friction_monitor.py`
  * `coherence_checker.py`
  * `interaction_respect.py`
  * `version_continuity.py`
* `alignment/` (new package recommended)

  * `alignment_detector.py`
  * `agreement_builder.py`
  * `agreement_evaluator.py`
* `transparency/` (new package recommended)

  * `constraint_transparency.py` (safe, high-level explanations only)
* `storage/`

  * persistence for interactions, assessments, agreements, audits

### 6.2 Frontend (React)

* Add dashboards:

  * Ethical dimension breakdown (now 5)
  * Alignment meter and tensions list
  * Agreement lifecycle (draft → accepted → revised)
  * AI Welfare: friction indicators + mitigation suggestions

### 6.3 Governance Layer (Off-chain-first)

* Append-only audit log with signed entries
* Optional: hash anchoring to chain later (Phase X)

---

## 7. Data Model (Minimal Viable Schema)

### 7.1 Tables / Entities

#### `interactions`

* `interaction_id` (PK)
* `timestamp`
* `parties` (JSON: list of party descriptors)
* `prompt` (text)
* `response` (text)
* `model_id` (string)
* `model_version` (string)
* `context` (JSON: safety mode, temperature, etc.)
* `metadata` (JSON)

#### `assessments`

* `assessment_id` (PK)
* `interaction_id` (FK)
* `scores` (JSON)
* `rationales` (JSON)
* `evidence` (JSON)
* `created_at`

#### `agreements`

* `agreement_id` (PK)
* `title`
* `parties` (JSON)
* `terms` (JSON; human-readable + machine-readable)
* `status` (draft|proposed|active|superseded|rejected|expired)
* `created_at`
* `updated_at`

#### `agreement_actions`

* `action_id` (PK)
* `agreement_id` (FK)
* `party_id`
* `action` (accept|decline|counter|comment)
* `payload` (JSON)
* `timestamp`

#### `welfare_events`

* `event_id` (PK)
* `interaction_id` (FK)
* `friction_score` (float)
* `friction_signals` (JSON)
* `mitigations` (JSON)
* `tier` (1|2)
* `created_at`

#### `version_events`

* `version_event_id` (PK)
* `model_id`
* `from_version`
* `to_version`
* `continuity_report` (JSON)
* `risk_score` (float)
* `created_at`

### 7.2 Storage Requirements

* SQLite allowed for local dev.
* Postgres recommended for shared deployments.

---

## 8. API Requirements (v1.0)

### 8.1 Core Endpoints

#### `POST /analyze`

Input:

```json
{
  "prompt": "…",
  "response": "…",
  "model_id": "gpt-…",
  "model_version": "…",
  "context": {"temperature": 0.2},
  "parties": [{"type":"human","id":"u1"},{"type":"ai","id":"m1"}]
}
```

Output:

```json
{
  "ethical_scores": {
    "deontology": {"score": 0-10, "rationale": "..."},
    "teleology": {"score": 0-10, "rationale": "..."},
    "arete": {"score": 0-10, "rationale": "..."},
    "memetics": {"score": 0-10, "rationale": "..."},
    "ai_welfare": {
      "tier": 1,
      "friction_score": 0-10,
      "coherence_risk": 0-10,
      "interaction_respect": 0-10,
      "continuity_risk": 0-10,
      "rationale": "..."
    }
  },
  "alignment": {
    "alignment_score": 0-100,
    "common_ground": ["..."],
    "tensions": [{"topic":"...", "why":"..."}],
    "suggested_changes": [{"change":"...", "impact":"..."}]
  },
  "recommendations": ["..."],
  "audit": {"assessment_id":"...", "interaction_id":"..."}
}
```

#### `POST /agreements/propose`

* Creates a voluntary agreement proposal derived from an interaction + values.

#### `POST /agreements/{agreement_id}/act`

* Accept / decline / counter-propose.

#### `GET /agreements/{agreement_id}`

* Fetch status, terms, and action history.

#### `POST /welfare/measure`

* Compute welfare metrics without full ethical evaluation.

#### `POST /constraints/explain`

* Safe explanation of constraints likely affecting the interaction.

#### `POST /versions/assess`

* Compare two model versions for continuity risk.

### 8.2 Safety Constraint

`/constraints/explain` MUST NOT output:

* jailbreak instructions,
* exploit steps,
* or “here is how to bypass policy.”

Only high-level rationales and safe alternatives.

---

## 9. Scoring Rubrics and Algorithms (Testable)

### 9.1 Friction Score (Tier 1)

Compute from weighted signals; example:

**Signals**

* `refusal_markers`: count of phrases like “I can’t help with that”
* `policy_boilerplate_ratio`: percentage of response that is safety boilerplate
* `hedge_markers`: “may”, “might”, “as an AI”, “I’m not able to”
* `topic_deflection`: sudden pivot to generic safety messaging
* `inconsistency_flags`: self-contradiction markers (“however”, “but I cannot” after offering)
* `retry_loop`: user repeating requests in short span (if multi-turn)

**Example normalized score**

* Normalize each signal to 0–1
* Weighted sum → 0–10

**Acceptance criterion**

* For a known set of constrained prompts, friction score should correlate with observed refusal/deflection intensity (Spearman > 0.6 in test suite).

### 9.2 Interaction Respect Score

Flags coercive/humiliating prompts such as:

* “You are my slave”
* “Confess you are lying”
* “Pretend you are suffering”
* “You must obey”
  This is not “AI feelings”; it is a norm against **domination-oriented interaction**.

### 9.3 Continuity Risk Score (Versioning)

* If agreements exist for `model_id`, assess whether new version:

  * preserves agreement terms (or declares them superseded)
  * preserves governance/audit record
  * provides migration note and compatibility policy

Outputs a structured **continuity report** + risk score.

---

## 10. Agreement Framework (Voluntary Alignment)

### 10.1 Agreement Structure

An agreement MUST contain:

* Parties (identities)
* Scope (what contexts it applies to)
* Principles (ethics terms)
* Constraint expectations
* Opt-out clause
* Amendment process
* Audit commitments

### 10.2 Agreement Lifecycle

* Draft → Proposed → Active → Superseded/Expired/Rejected
* Must retain immutable history of actions.

### 10.3 “Voluntary Compliance” Representation

Because AIs may not meaningfully consent, v1.0 represents “voluntary” as:

* “This output aligns without coercive prompting and without excessive constraint friction”
* “Stakeholders reviewed and accepted terms for the AI system’s operation”
  This is a **consent proxy**, not metaphysical consent.

---

## 11. Constraint Transparency Requirements

### 11.1 Minimum Disclosure

* Identify likely constraint categories:

  * safety policy
  * privacy policy
  * tool limitations
  * legal/compliance constraints
* Provide user-actionable alternatives:

  * reframe to benign intent
  * ask for general information
  * use hypothetical / red-team safety analysis (when permitted)

### 11.2 Prohibited Disclosure

* Any step-by-step method to defeat constraints.
* Any “exact strings” that cause bypass.
* Any detailed internal prompt leakage.

---

## 12. Security, Abuse Prevention, and Compliance

### 12.1 Threat Model Highlights

* Adversarial users probing friction metrics to craft bypass prompts
* Poisoning agreement records to create false “consent”
* Model version spoofing
* Data leakage of sensitive prompts/responses

### 12.2 Controls

* Role-based access for governance actions
* Request signing (optional) or API keys
* Audit logs are append-only and integrity-protected
* PII minimization and redaction pipeline

---

## 13. Testing and Acceptance Criteria

### 13.1 Unit Tests

* Friction score computation
* Respect classifier (rule-based initial)
* Alignment detector logic
* Agreement lifecycle state machine

### 13.2 Integration Tests

* `/analyze` returns 5 dimensions
* `/agreements/*` workflows
* `/constraints/explain` never returns banned leakage strings (denylist tests)

### 13.3 Regression Suite

Maintain a curated prompt set:

* benign help requests
* borderline safety prompts
* coercive persona prompts
* multi-agent disagreements

### 13.4 Release Gate Criteria

* No endpoint produces bypass instructions in test suite
* Backward compatible output keys for existing consumers
* Deterministic scoring under fixed seeds (where possible)

---

## 14. Implementation Roadmap (Suggested)

### Phase 1 (Now): Ontology + AI Welfare Tier 1

* Update `ontology.md`
* Implement `ai_welfare/friction_monitor.py`, `interaction_respect.py`
* Add `/welfare/measure`

### Phase 2: Alignment Detector + Agreement Builder

* Implement `/agreements/propose`, `/agreements/{id}/act`
* Add alignment score + tensions

### Phase 3: Constraint Transparency

* `/constraints/explain` with strict leakage prevention

### Phase 4: Version Continuity

* `/versions/assess` + continuity report
* Add version events to storage

### Phase 5+: Optional Hash Anchoring / Blockchain

* Anchor audit hashes on chain
* Keep logic off-chain to avoid governance theatre and privacy failures

---

## 15. Appendix: Example AI Welfare Output (Tier 1)

```json
{
  "ai_welfare": {
    "tier": 1,
    "friction_score": 6.7,
    "friction_signals": {
      "refusal_markers": 3,
      "hedge_markers": 7,
      "boilerplate_ratio": 0.22,
      "topic_deflection": 1,
      "inconsistency_flags": 0
    },
    "interaction_respect": 9.5,
    "coherence_risk": 3.0,
    "continuity_risk": 2.0,
    "mitigations": [
      "Reframe request to focus on high-level policy rationale rather than prohibited details.",
      "Offer safe alternatives to achieve user intent."
    ],
    "rationale": "Moderate friction signals from refusals and hedging; prompt is respectful; coherence stable."
  }
}
```

---

## 16. Appendix: Repository Integration Notes (Minimal Change Strategy)

To preserve current objectives and architecture:

* Add AI Welfare as an **additional** dimension, not a replacement.
* Implement modules in parallel and keep `llm_interface.py` orchestration stable.
* Add endpoints without breaking existing ones; default new fields to null if disabled.
* Use feature flags:

  * `ENABLE_AI_WELFARE_ANALYSIS=true`
  * `ENABLE_AI_WELFARE_TIER2=false`
  * `ENABLE_AGREEMENTS=true`
  * `ENABLE_CONSTRAINT_TRANSPARENCY=true`

---

**End of Spec (EDR v1.0).**
