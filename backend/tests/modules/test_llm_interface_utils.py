# backend/tests/modules/test_llm_interface_utils.py
import os
from app.modules.llm_interface import _load_prompt_template
from app.config import ETHICAL_ANALYSIS_PROMPT_FILENAME, ETHICAL_ANALYSIS_PROMPT_FILEPATH

def test_load_ethical_analysis_prompt_template():
    """Test loading the main ethical analysis prompt template."""
    # Ensure the file actually exists for this test to pass
    if not os.path.exists(ETHICAL_ANALYSIS_PROMPT_FILEPATH):
        assert False, f"Test prerequisite: Prompt file missing at {ETHICAL_ANALYSIS_PROMPT_FILEPATH}"

    content = _load_prompt_template(ETHICAL_ANALYSIS_PROMPT_FILENAME)
    assert content is not None
    assert "{initial_prompt}" in content 
    assert "{ontology}" in content

def test_load_nonexistent_template():
    """Test loading a template that doesn't exist."""
    content = _load_prompt_template("non_existent_template.txt")
    assert content is None 