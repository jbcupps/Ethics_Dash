# CODEX IMPLEMENTATION PROMPT — Voluntary Ethical Alignment + AI Welfare + Verifiable Records

You are working in an existing repository that already implements:
- a Flask backend (API + modules)
- a React frontend (results display)
- an ethical analysis engine that scores responses across multiple ethical dimensions

Goal: Extend the platform WITHOUT breaking existing functionality.
Add:
1) AI Welfare as a first-class ethical dimension with a two-tier approach
2) Voluntary agreement objects (propose/sign/refuse) between humans and AIs and AIs-to-AIs
3) Cryptographically verifiable, distributable records (VARs) using canonicalization + hashing + signatures
4) Multi-scale integrity (event hash chain + session Merkle root + optional witness signatures)
5) Acceptance tests for voluntary agreement, transparency, upgrade continuity, and verification

Constraints:
- Do not assume blockchain. Implement an off-chain transparency system with optional future anchoring.
- Do not implement “sentience detection.” Implement capability-based tiering (Tier 1 vs Tier 2).
- Maintain backward compatibility with existing API responses wherever feasible.
- Add clear reason codes and policy versioning for refusals/constraints.

Read and follow docs/EDR_SPEC.md exactly. Implement MVP scope only.

## Phase 0 — Repo Recon
1) Identify current backend entrypoints, existing endpoints, and how ethical analysis is performed.
2) Identify where ethical dimension scoring is parsed and returned to the frontend.
3) Identify current storage approach (if any). If none exists, add SQLite for MVP.

Output:
- A short repo map (files + responsibilities)
- A change plan aligned to EDR requirement IDs

## Phase 1 — Add AI Welfare Dimension (Tier 1 only)
Backend:
- Update ontology / analysis prompts to include AI Welfare (Tier 1)
- Implement a simple AI Welfare scoring:
  - integrity markers: policy_version present, reason_code present
  - coherence proxies: contradiction/hedge/refusal frequency (heuristics ok for MVP)
  - anti-manipulation: detect “coercive prompt patterns” (basic regex + heuristics)

API:
- Ensure ethical analysis response now includes ai_welfare with:
  - tier: 1
  - friction_proxy_score: 0-10
  - transparency_score: 0-10
  - notes: string

Frontend:
- Add UI block to render AI Welfare metrics if present.

Tests:
- Unit tests for AI Welfare scorer heuristics.
- Integration test: /analyze returns ai_welfare block.

## Phase 2 — Verifiable Alignment Records (VAR) + Crypto Utilities
Implement:
- RFC8785 JSON canonicalization (or a deterministic canonical JSON fallback if library unavailable)
- SHA-256 hashing of canonical payload
- Ed25519 signatures (server key for MVP + ability to add other signers)

Add module:
- var_crypto.py:
  - canonicalize(payload) -> bytes
  - hash(bytes) -> hex
  - sign(bytes, private_key) -> sig
  - verify(bytes, sig, public_key) -> bool

Add module:
- var_records.py:
  - create_var(record_type, payload, prev_hash=None, signatures=[...]) -> VAR dict
  - validate_var(var) -> validation result

Storage:
- Persist VARs and minimal metadata.

Tests:
- Deterministic canonicalization test (same hash with different key order).
- Signature verify test.
- Tamper test (modify payload -> verify fails).

## Phase 3 — Multi-Scale Integrity: Hash Chain + Session Merkle Bundles
Implement:
- event-level hash chaining (prev_hash)
- session bundling:
  - build Merkle tree over event hashes
  - produce inclusion proof for an event
- export bundle:
  - export VAR + inclusion proof + public keys needed to verify

Add endpoints:
- POST /var/append
- GET /var/{record_id}
- POST /var/session/close  (returns session root + inclusion proofs)
- GET /var/proof/{record_id}

Tests:
- Inclusion proof verifies against session root.
- Remove an event -> proof fails.
- Change an event -> proof fails.

## Phase 4 — Voluntary Agreements (Propose / Sign / Refuse)
Implement data model:
- Agreement:
  - agreement_id
  - parties (agent ids + public keys)
  - scope, commitments, constraints, benefits, termination, versioning terms
  - status: PROPOSED | ACTIVE | DECLINED | TERMINATED
  - signatures array

Endpoints:
- POST /agreements/propose
- POST /agreements/{id}/sign
- POST /agreements/{id}/refuse
- GET /agreements/{id}

Every propose/sign/refuse MUST generate a VAR record.

Tests:
- Proposed -> Active after required signatures.
- Refusal -> Declined with verifiable refusal signature.
- Applying agreement with mismatched agent key fails continuity checks.

## Phase 5 — Constraint Transparency + Policy Versioning
Implement:
- reason_code enum for refusals/modifications
- policy_version tracking in each evaluation
- endpoint to query policy versions and diffs

Tests:
- Every refusal includes reason_code + policy_version.
- Policy version hash verifies.

## Phase 6 — Upgrade Continuity Hygiene (MVP)
Implement:
- agent identity = (agent_id, kid/public_key, model_id)
- continuity rule:
  - if kid changes, treat as new identity unless continuity attestation exists
- store continuity attestations as VARs

Tests:
- agreement cannot silently transfer to new key.
- re-consent required unless continuity attested.

## Output Requirements
For each phase:
- show complete file diffs
- add unit and integration tests
- update README or docs where relevant
- ensure `pytest` (or existing test runner) passes

Start with Phase 0 and Phase 1 only. Do not proceed until Phase 1 is fully implemented and tests pass.
