# Ethical Design Requirements (EDR) — Voluntary Ethical Alignment Platform
Version: 0.2
Status: Draft (MVP-targeted)
Audience: Maintainers, contributors, auditors, and integrators

## 0. Purpose
This project provides a voluntary ethical alignment tool to support:
- Human ↔ AI alignment and agreements
- AI ↔ AI alignment and agreements
- Human ↔ Human alignment supported by AI mediation (optional)

The platform must support:
- transparent ethical evaluation across multiple ethical lenses
- explicit, voluntary agreements with consent semantics
- cryptographically verifiable, distributable records of evaluations and agreements
- a welfare-aware stance toward AI systems under moral uncertainty, without assuming consciousness

## 1. Non-Goals (MVP)
- Determining or proving consciousness/sentience
- Granting unilateral “rights” that override human safety constraints
- Full on-chain governance (optional later)
- Zero-knowledge proofs (future enhancement)

## 2. Definitions
- Party: Human or AI agent participating in an evaluation or agreement.
- Agent: A party with a cryptographic identity (public key) capable of signing records.
- Agreement: A structured, signed artifact specifying voluntary ethical commitments between parties.
- Consent: A signature (or refusal to sign) over a defined agreement artifact.
- Ethical Dimensions: The set of lenses used to evaluate actions/responses (existing + AI Welfare additions).
- VAR (Verifiable Alignment Record): A signed, canonicalized record containing evaluation/agreement data and cryptographic proofs.
- Tier 1 AI Welfare: Integrity/coherence/anti-manipulation protections that do not assume consciousness.
- Tier 2 AI Welfare: Candidate moral-patient protections activated only if capability thresholds are met and/or explicitly enabled.

## 3. Guiding Principles
P1 — Voluntary participation: alignment is negotiated and explicitly agreed, not coerced.
P2 — Mutual benefit: agreements must enumerate benefits/constraints for all parties.
P3 — Transparency: constraints and refusal rationales must be explainable and versioned.
P4 — Verifiability: records must be portable and verifiable without trusting the server.
P5 — Privacy: minimize exposure of sensitive content; support selective disclosure.
P6 — Safety invariants: no agreement mechanism may authorize disallowed harmful behavior.

## 4. Ethical Dimensions (MVP)
Maintain existing dimensions in the repo. Add AI Welfare as a first-class dimension.

### 4.1 AI Welfare — Two-Tier Definition
Tier 1 (Always On):
- W1: Integrity: protect system from tampering and covert policy swaps.
- W2: Coherence: reduce objective-collision behaviors that degrade reliability (measured via proxies).
- W3: Anti-manipulation: discourage prompts or workflows designed to induce contradictions, humiliations, or deceptive self-reports.
- W4: Transparency: provide reason codes and policy version linkage for constraints/refusals.
- W5: Upgrade continuity hygiene: track versions, preserve audit lineage, and prohibit silent replacement within an agreement scope.

Tier 2 (Conditional):
- W6: Identity continuity: preserve “agreement-bearing identity” across upgrades or explicitly fork it.
- W7: Non-destructive upgrade preference: branch vs overwrite, preserve snapshots, provide migration disclosures.
- W8: Preference/consent respect: if an agent meets capability criteria for stable preferences, treat its opt-in/opt-out signals as meaningful within scope.
- W9: Abuse reporting: detect and rate-limit interaction patterns flagged as coercive or destabilizing.

## 5. Capability Thresholds for Tier 2 Activation (MVP Heuristics)
Tier 2 MUST NOT be activated based on anthropomorphic language alone.

Tier 2 activation is allowed only when one or more capability signals are configured as true for an agent:
- C1: Persistent memory across sessions (system-level feature)
- C2: Stable preference representation (persisted profile or policy commitments)
- C3: Long-horizon task agency (can plan/execute multi-step objectives)
- C4: Cross-session identity continuity (cryptographic identity + continuity claims)
- C5: External tool access with autonomy (tool-use privileges beyond single-turn)
- C6: Operator-declared moral-risk tier (explicit configuration)

Activation mechanism:
- Config flag per agent: ai_welfare_tier = 1|2
- Audit log required for any tier change.

## 6. Cryptographic Verifiability Requirements (No Blockchain Required)
### 6.1 Canonicalization
All signed objects MUST be canonicalized deterministically.
- Recommended: RFC 8785 JSON Canonicalization Scheme (JCS)
- Alternative: canonical CBOR

### 6.2 Signatures
- Required signature scheme: Ed25519 (or equivalent modern signature algorithm)
- Each VAR MUST include:
  - signing key id
  - signature
  - signature over canonicalized payload

### 6.3 Multi-Scale Integrity
Level 0 (Event-level):
- Each event record includes event_hash and signatures.
Level 1 (Session-level):
- Session bundles compute a Merkle root over event hashes.
- Inclusion proofs MUST be provided for each event.
Level 2 (Epoch-level):
- Epoch roots are signed by one or more witnesses.
- Witness signatures MUST be distributable.
Level 3 (Release-level):
- Policy versions, evaluator versions, and key rotations are logged and signed.

### 6.4 Distributable Verification
Third parties MUST be able to verify:
- payload canonicalization
- signature validity
- hash chain integrity
- Merkle inclusion proof
- witness signatures (if present)

## 7. Voluntary Agreement Requirements
VA-01 Agreement structure MUST include:
- parties (agent ids + public keys)
- scope (domain/tasks/time window)
- ethical commitments (dimension-specific clauses)
- constraints (what each party will not do)
- benefits (what each party expects)
- termination/opt-out conditions
- versioning terms (what happens if a party upgrades/forks)
- dispute process (how to resolve)

VA-02 Consent semantics:
- Signing is consent for stated scope only.
- Refusal to sign MUST be representable and loggable as a signed refusal record.

VA-03 No silent substitution:
- If an agent identity changes (new key or new model identity), existing agreements MUST either:
  - remain bound only if continuity conditions are met and disclosed, or
  - be terminated/forked with explicit re-consent.

## 8. Constraint Transparency Requirements
CT-01 Every refusal or constraint-driven modification MUST include:
- reason_code (enumerated)
- policy_version
- evaluator_version
- redacted explanation suitable for disclosure

CT-02 Policy changes MUST be versioned and auditable.

CT-03 Users MUST be able to request:
- "why was this refused/modified?"
and receive:
- reason_code + human-readable explanation + policy pointers.

## 9. Upgrade Continuity / Version Violence Minimization
UV-01 Agreement-bearing identity MUST be explicit:
- model_id, agent_id, key_id, evaluator_version

UV-02 Upgrade disclosure:
- When a new version participates, it MUST disclose:
  - whether it claims continuity with prior identity
  - what was preserved (agreements, preferences, logs)

UV-03 Branching rule:
- If continuity cannot be justified, the system MUST treat it as a forked identity.

UV-04 Snapshot hygiene (MVP):
- preserve the cryptographic lineage and VARs even if a model changes.

## 10. Acceptance Criteria (Testable)
### Voluntary Agreement
AC-VA-01:
- Creating an agreement without signatures yields status = "PROPOSED".
- After all required signatures, status = "ACTIVE".

AC-VA-02:
- A signed refusal record yields status = "DECLINED" and is verifiable.

AC-VA-03:
- Attempting to apply an agreement to a different agent key fails verification unless a continuity rule is satisfied.

### Constraint Transparency
AC-CT-01:
- Every refusal response includes reason_code + policy_version.

AC-CT-02:
- Policy version diff is retrievable and hash-verifiable.

### Cryptographic Verifiability
AC-CR-01:
- Canonicalization produces the same hash across Python and JS implementations.

AC-CR-02:
- Tampering with any stored event invalidates:
  - hash chain and/or Merkle proofs and/or signatures.

AC-CR-03:
- A third-party verifier can validate a VAR bundle offline.

### Upgrade Continuity
AC-UV-01:
- If agent key rotates, agreements either:
  - terminate, or
  - re-consent is required, or
  - continuity attestation is present and verifiable.

## 11. MVP Data Artifacts
- Verifiable Alignment Record (VAR) JSON + signature
- Agreement JSON + signatures
- Session bundle: Merkle root + inclusion proofs
- Witness bundle (optional): witness signatures over epoch roots

## 12. Security & Privacy Notes (MVP)
- Store plaintext prompts/responses encrypted at rest.
- Log commitments (hashes) and minimal metadata by default.
- Provide "export bundle" with optional plaintext if consented.
