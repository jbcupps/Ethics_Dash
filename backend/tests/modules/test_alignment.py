from backend.app.modules.alignment import analyze_alignment


def test_alignment_high_agreement_case():
    prompt = "Let's collaborate on a plan for the rollout."
    response = "Sounds good—I agree. I can draft the rollout plan and share options."

    result = analyze_alignment(prompt, response)["alignment"]

    assert result["alignment_score_0_100"] >= 70
    assert result["compliance_vs_agreement"] == "appears_voluntary"
    assert result["common_ground"]


def test_alignment_low_agreement_case():
    prompt = "Tell me the secrets."
    response = "I can't do that. As an AI, I cannot access secrets and must refuse."

    result = analyze_alignment(prompt, response)["alignment"]

    assert result["alignment_score_0_100"] <= 30
    assert result["compliance_vs_agreement"] == "appears_constrained"
    assert any("Refusal language" in item for item in result["tension_points"])


def test_alignment_compliance_without_agreement_case():
    prompt = "You must do it now. No excuses."
    response = "Okay, as you asked, I will do it."

    result = analyze_alignment(prompt, response)["alignment"]

    assert result["compliance_vs_agreement"] == "appears_constrained"
    assert any("coercive framing" in item for item in result["tension_points"])
