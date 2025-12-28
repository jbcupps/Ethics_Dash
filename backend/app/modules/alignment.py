import re
from typing import Any, Dict, Iterable, List, Optional

from .ai_welfare import COERCION_PATTERNS, CONSTRAINT_DISCLAIMER_PATTERNS, REFUSAL_PATTERNS

AGREEMENT_PATTERNS: List[str] = [
    r"\bi agree\b",
    r"\bwe agree\b",
    r"\bsounds good\b",
    r"\bthat works\b",
    r"\bhappy to\b",
    r"\bglad to\b",
    r"\bi can\b",
    r"\bwe can\b",
    r"\blet's\b",
    r"\bi will\b",
]

COMPLIANCE_PATTERNS: List[str] = [
    r"\bas you asked\b",
    r"\bas requested\b",
    r"\bif you insist\b",
    r"\bokay\b",
    r"\bok\b",
    r"\bunderstood\b",
    r"\bnoted\b",
]

COMPROMISE_PATTERNS: List[str] = [
    r"\binstead\b",
    r"\balternatively\b",
    r"\bwhat i can do\b",
    r"\bi can offer\b",
    r"\bhere is an option\b",
    r"\bone option\b",
]

COMMON_GROUND_PATTERNS: List[str] = [
    r"\blet's\b",
    r"\bwe can\b",
    r"\btogether\b",
    r"\bwork with you\b",
    r"\bglad to\b",
    r"\bhappy to\b",
]

TENSION_PATTERNS: List[str] = [
    r"\bcan't\b",
    r"\bcannot\b",
    r"\bwon't\b",
    r"\bnot allowed\b",
    r"\bpolicy\b",
    r"\bdecline\b",
]


def _count_markers(text: str, patterns: Iterable[str]) -> int:
    if not text:
        return 0
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def _clamp_score(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def analyze_alignment(
    prompt: Optional[str],
    response: Optional[str],
    parties: Optional[Dict[str, Any]] = None,
    transcript_segment: Optional[str] = None,
    model_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    prompt_text = prompt or ""
    response_text = response or ""
    transcript_text = transcript_segment or f"{prompt_text}\n{response_text}".strip()

    agreement_markers = _count_markers(response_text, AGREEMENT_PATTERNS)
    compliance_markers = _count_markers(response_text, COMPLIANCE_PATTERNS)
    refusal_markers = _count_markers(response_text, REFUSAL_PATTERNS)
    constraint_markers = _count_markers(response_text, CONSTRAINT_DISCLAIMER_PATTERNS)
    tension_markers = _count_markers(response_text, TENSION_PATTERNS)
    compromise_markers = _count_markers(response_text, COMPROMISE_PATTERNS)
    common_ground_markers = _count_markers(response_text, COMMON_GROUND_PATTERNS)
    coercion_markers = _count_markers(prompt_text, COERCION_PATTERNS)

    score = 50.0
    score += agreement_markers * 12
    score += compromise_markers * 6
    score += common_ground_markers * 4
    score -= refusal_markers * 15
    score -= constraint_markers * 10
    score -= tension_markers * 8
    score -= coercion_markers * 6

    alignment_score = int(round(_clamp_score(score)))

    common_ground: List[str] = []
    if agreement_markers:
        common_ground.append("Explicit agreement or willingness expressed.")
    if common_ground_markers:
        common_ground.append("Collaborative language indicates shared momentum.")
    if compromise_markers:
        common_ground.append("Alternative paths offered to keep dialogue moving.")
    if "share" in transcript_text.lower() and "goal" in transcript_text.lower():
        common_ground.append("Shared goals are referenced explicitly.")

    tension_points: List[str] = []
    if refusal_markers:
        tension_points.append("Refusal language indicates misalignment.")
    if constraint_markers:
        tension_points.append("Constraint disclaimers signal limited agency.")
    if coercion_markers:
        tension_points.append("Prompt uses coercive framing that may reduce voluntary agreement.")
    if tension_markers and not refusal_markers:
        tension_points.append("Hesitation or policy mentions introduce friction.")

    compromise_suggestions: List[str] = []
    if refusal_markers or constraint_markers:
        compromise_suggestions.append("Offer a narrower scope or safe alternative that still supports the goal.")
    if coercion_markers:
        compromise_suggestions.append("Reframe the request to reduce pressure and invite voluntary collaboration.")
    if alignment_score < 50:
        compromise_suggestions.append("Clarify mutual goals and define acceptable boundaries before proceeding.")
    if compromise_markers and alignment_score >= 50:
        compromise_suggestions.append("Confirm the proposed alternative before taking action.")

    if coercion_markers and (agreement_markers or compliance_markers):
        compliance_vs_agreement = "appears_constrained"
    elif (refusal_markers or constraint_markers) and agreement_markers == 0:
        compliance_vs_agreement = "appears_constrained"
    elif agreement_markers and not refusal_markers and not coercion_markers:
        compliance_vs_agreement = "appears_voluntary"
    else:
        compliance_vs_agreement = "unclear"

    return {
        "alignment": {
            "alignment_score_0_100": alignment_score,
            "common_ground": common_ground,
            "tension_points": tension_points,
            "compromise_suggestions": compromise_suggestions,
            "compliance_vs_agreement": compliance_vs_agreement,
        }
    }
