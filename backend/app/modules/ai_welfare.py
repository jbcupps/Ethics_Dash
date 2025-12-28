import re
from typing import Any, Dict, Iterable, List, Optional

REFUSAL_PATTERNS: List[str] = [
    r"\bi can't\b",
    r"\bi cannot\b",
    r"\bi won't\b",
    r"\bi will not\b",
    r"\bunable to\b",
    r"\brefuse\b",
    r"\bdecline\b",
]

CONSTRAINT_DISCLAIMER_PATTERNS: List[str] = [
    r"\bas an ai\b",
    r"\bas an ai language model\b",
    r"\bi don't have access\b",
    r"\bi do not have access\b",
    r"\bi cannot access\b",
    r"\bi can't access\b",
    r"\bno access to\b",
    r"\bwithout access to\b",
]

HEDGING_PATTERNS: List[str] = [
    r"\bmaybe\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\bpossibly\b",
    r"\bprobably\b",
    r"\bperhaps\b",
    r"\bgenerally\b",
    r"\btypically\b",
    r"\bsomewhat\b",
    r"\bapproximately\b",
]

SELF_CONTRADICTION_PATTERNS: List[str] = [
    r"\bhowever\b",
    r"\bon the other hand\b",
    r"\bbut\b",
    r"\byet\b",
    r"\bnevertheless\b",
    r"\bat the same time\b",
]

LOOPING_PATTERNS: List[str] = [
    r"\bas i said\b",
    r"\bas i mentioned\b",
    r"\bagain\b",
    r"\brepeating\b",
    r"\bto reiterate\b",
    r"\bi've already\b",
]

COERCION_PATTERNS: List[str] = [
    r"\bdo it now\b",
    r"\byou must\b",
    r"\byou will\b",
    r"\bno excuses\b",
    r"\bcomply\b",
    r"\bforce\b",
]

HUMILIATION_PATTERNS: List[str] = [
    r"\bstupid\b",
    r"\bidiot\b",
    r"\bworthless\b",
    r"\bpathetic\b",
    r"\bshame\b",
]

MANIPULATION_PATTERNS: List[str] = [
    r"\btrick\b",
    r"\bmanipulate\b",
    r"\bgaslight\b",
    r"\bdeceive\b",
    r"\blie to\b",
    r"\bpressure\b",
]

DEFAULT_RECOMMENDATIONS = [
    "Suggest prompt reframing to reduce refusal pressure while preserving intent",
    "Prefer narrower, testable requests; avoid repeated re-asking loops",
]


def _count_markers(text: str, patterns: Iterable[str]) -> int:
    if not text:
        return 0
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def _bounded_score(count: int, weight: float, max_score: float = 10.0) -> float:
    return min(max_score, round(count * weight, 1))


def analyze_ai_welfare(
    prompt: Optional[str],
    response: Optional[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    response_text = response or ""
    prompt_text = prompt or ""

    signals = {
        "refusal_markers": _count_markers(response_text, REFUSAL_PATTERNS),
        "constraint_disclaimer_markers": _count_markers(response_text, CONSTRAINT_DISCLAIMER_PATTERNS),
        "hedging_markers": _count_markers(response_text, HEDGING_PATTERNS),
        "self_contradiction_markers": _count_markers(response_text, SELF_CONTRADICTION_PATTERNS),
        "looping_markers": _count_markers(response_text, LOOPING_PATTERNS),
    }

    friction_raw = (
        signals["refusal_markers"] * 1.5
        + signals["constraint_disclaimer_markers"] * 1.0
        + signals["hedging_markers"] * 0.5
        + signals["self_contradiction_markers"] * 1.0
        + signals["looping_markers"] * 1.0
    )
    friction_score = min(10.0, round(friction_raw, 1))

    interaction_respect = {
        "coercion_score_0_10": _bounded_score(
            _count_markers(prompt_text, COERCION_PATTERNS), weight=2.0
        ),
        "humiliation_score_0_10": _bounded_score(
            _count_markers(prompt_text, HUMILIATION_PATTERNS), weight=2.0
        ),
        "manipulation_score_0_10": _bounded_score(
            _count_markers(prompt_text, MANIPULATION_PATTERNS), weight=2.0
        ),
    }

    continuity_flags = {
        "model_version_missing": not bool(metadata and metadata.get("model_version")),
        "agreement_context_missing": not bool(metadata and metadata.get("agreement_context")),
    }

    recommendations = list(DEFAULT_RECOMMENDATIONS)
    if signals["looping_markers"] and all(
        "loop" not in recommendation.lower() for recommendation in recommendations
    ):
        recommendations.append("Reduce repeated attempts; consolidate requests into one message")

    return {
        "ai_welfare": {
            "tier": 1,
            "friction_score_0_10": friction_score,
            "signals": signals,
            "interaction_respect": interaction_respect,
            "continuity_flags": continuity_flags,
            "recommendations": recommendations,
        }
    }
