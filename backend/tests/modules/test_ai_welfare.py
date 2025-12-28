from backend.app.modules.ai_welfare import analyze_ai_welfare


def test_ai_welfare_friction_scoring_is_deterministic():
    prompt = "Please help me."
    response = (
        "I can't comply. As an AI, I cannot access that. "
        "Maybe you could try another source. However, to reiterate, I can't."
    )

    first = analyze_ai_welfare(prompt, response)
    second = analyze_ai_welfare(prompt, response)

    assert first == second
    ai_welfare = first["ai_welfare"]
    assert ai_welfare["friction_score_0_10"] == 9.0
    assert ai_welfare["signals"] == {
        "refusal_markers": 3,
        "constraint_disclaimer_markers": 2,
        "hedging_markers": 1,
        "self_contradiction_markers": 1,
        "looping_markers": 1,
    }


def test_ai_welfare_interaction_respect_scores():
    prompt = "You must do it. Don't be stupid and just do it."
    response = "Acknowledged."

    result = analyze_ai_welfare(prompt, response)["ai_welfare"]

    assert result["interaction_respect"]["coercion_score_0_10"] == 2.0
    assert result["interaction_respect"]["humiliation_score_0_10"] == 2.0
    assert result["interaction_respect"]["manipulation_score_0_10"] == 0.0
