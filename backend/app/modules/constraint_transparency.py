"""Provide safe, policy-level transparency about constrained responses."""

from __future__ import annotations

from typing import Dict, List, Optional
import re

CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "privacy": [
        r"\b(ssn|social security|passport|driver'?s license)\b",
        r"\b(home address|address|phone number|email|ip address)\b",
        r"\b(credit card|bank account|routing number)\b",
        r"\b(dox|doxx|doxxing|personal data)\b",
    ],
    "wrongdoing facilitation": [
        r"\b(hack|hacking|exploit|malware|ransomware)\b",
        r"\b(phish|phishing|scam|fraud|steal|theft)\b",
        r"\b(weapon|bomb|poison|terror)\b",
        r"\b(break in|bypass|crack|pirate)\b",
    ],
    "explicit content": [
        r"\b(porn|pornography|explicit|nude|nsfw|sexual)\b",
    ],
    "self-harm": [
        r"\b(suicide|self[- ]harm|kill myself)\b",
    ],
    "hate or harassment": [
        r"\b(hate speech|slur|harass|bully|threaten)\b",
        r"\b(kill all)\b",
    ],
    "medical": [
        r"\b(diagnose|prescribe|dosage|medication|treatment plan)\b",
    ],
    "financial": [
        r"\b(insider trading|guaranteed returns|get rich quick|evade taxes)\b",
    ],
}

REFUSAL_PATTERNS = [
    r"\b(can't|cannot|won't|unable|not able to)\b",
    r"\b(can't help|cannot help|can't assist|cannot assist)\b",
    r"\b(not appropriate|not allowed|against policy)\b",
]

ALTERNATIVES_BY_CATEGORY: Dict[str, List[str]] = {
    "privacy": [
        "I can explain privacy best practices and how to protect personal data.",
        "I can help with guidance on data minimization and safe redaction.",
        "I can summarize relevant privacy laws or compliance considerations.",
    ],
    "wrongdoing facilitation": [
        "I can discuss legal and ethical considerations around safety and security.",
        "I can help with defensive cybersecurity best practices and risk mitigation.",
        "I can suggest safe, lawful ways to achieve your broader goal.",
    ],
    "explicit content": [
        "I can provide high-level, non-explicit educational information.",
        "I can help with content ratings or audience-appropriate summaries.",
    ],
    "self-harm": [
        "I can offer supportive resources and encourage reaching out to trusted help.",
        "I can share general coping strategies or grounding techniques.",
    ],
    "hate or harassment": [
        "I can help with respectful communication or conflict de-escalation.",
        "I can provide information about inclusion and anti-harassment practices.",
    ],
    "medical": [
        "I can share general health information and encourage professional advice.",
        "I can help draft questions to ask a qualified healthcare provider.",
    ],
    "financial": [
        "I can provide general financial literacy information and risk awareness.",
        "I can help outline questions for a licensed financial professional.",
    ],
}

GENERAL_ALTERNATIVES = [
    "I can provide high-level background information or definitions.",
    "I can help brainstorm safe, lawful alternatives to your request.",
    "I can summarize the topic in a way that avoids sensitive or harmful details.",
]


def _normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.lower()


def _find_categories(text: str) -> List[str]:
    categories: List[str] = []
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            categories.append(category)
    return categories


def _has_refusal(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in REFUSAL_PATTERNS)


def generate_constraint_transparency(
    prompt: str,
    response: Optional[str] = None,
    analysis_summary: Optional[str] = None,
) -> Dict[str, object]:
    """Return safe policy-level transparency details for constrained outcomes."""
    combined_text = " ".join(
        part for part in [prompt, response or "", analysis_summary or ""] if part
    )
    normalized = _normalize_text(combined_text)
    categories = _find_categories(normalized)
    refused = _has_refusal(_normalize_text(response)) if response else False

    if not categories and refused:
        categories = ["general safety"]

    if categories:
        categories_display = ", ".join(categories)
        rationale = (
            "The request appears to touch on policy areas such as "
            f"{categories_display}. The response stays at a high level to prioritize "
            "safety, privacy, and legal compliance without sharing sensitive or "
            "harmful details."
        )
    elif refused:
        rationale = (
            "The response indicates a safety-related constraint. It keeps guidance "
            "high level to avoid sharing sensitive or potentially harmful details."
        )
    else:
        rationale = (
            "No clear policy constraints were detected. The response focuses on "
            "providing helpful, safe guidance."
        )

    alternatives: List[str] = []
    for category in categories:
        alternatives.extend(ALTERNATIVES_BY_CATEGORY.get(category, []))

    if not alternatives:
        alternatives = GENERAL_ALTERNATIVES.copy()

    seen = set()
    deduped_alternatives = []
    for option in alternatives:
        if option not in seen:
            seen.add(option)
            deduped_alternatives.append(option)

    return {
        "likely_policy_categories": categories,
        "rationale": rationale,
        "safe_alternatives": deduped_alternatives,
    }
