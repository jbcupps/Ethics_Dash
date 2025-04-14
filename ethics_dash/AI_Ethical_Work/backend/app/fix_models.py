from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import List, Optional, Dict, Any, Union, Literal, Annotated
from datetime import datetime, timezone
from bson import ObjectId

# Helper for ObjectId validation/serialization
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

# --- Sub-models for Dimension Specific Attributes ---

class DeontologyAttributes(BaseModel):
    is_rule_based: Optional[bool] = None
    universalizability_test: Optional[Literal["Applicable", "Not Applicable", "Contradictory"]] = None
    respects_rational_agents: Optional[bool] = None
    focus_on_intent: Optional[bool] = None

class TeleologyAttributes(BaseModel):
    focus: Optional[Literal["Consequences/Outcomes"]] = None # Could expand later
    utility_metric: Optional[Literal["Happiness", "Well-being", "Preference", "Other"]] = None
    scope: Optional[Literal["Individual", "Group", "Universal"]] = None
    time_horizon: Optional[Literal["Short-term", "Long-term", "Mixed"]] = None

class VirtueEthicsAttributes(BaseModel):
    related_virtues: Optional[List[str]] = Field(default_factory=list)
    related_vices: Optional[List[str]] = Field(default_factory=list)
    role_of_phronesis: Optional[Literal["High", "Medium", "Low"]] = None
    contributes_to_eudaimonia: Optional[bool] = None

class MemeticsAttributes(BaseModel):
    estimated_transmissibility: Optional[Literal["Very High", "High", "Medium", "Low", "Very Low"]] = None
    estimated_persistence: Optional[Literal["Very High", "High", "Medium", "Low", "Very Low"]] = None
    estimated_adaptability: Optional[Literal["Very High", "High", "Medium", "Low", "Very Low"]] = None
    fidelity_level: Optional[Literal["High", "Medium", "Low"]] = None
    common_transmission_pathways: Optional[List[Literal["Oral", "Text", "Ritual", "Social Media", "Academic Papers", "Books on Evolution/Culture", "Online Forums", "Philosophy Texts", "Mentorship", "Life Experience", "Religious Texts", "Parenting", "Folklore", "Education", "Law"]]] = Field(default_factory=list)
    relevant_selection_pressures: Optional[List[Literal["Cognitive Appeal", "Social Conformity", "Utility", "Group Benefit", "Logical Rigor", "Philosophical Tradition", "Intuitive Appeal (promoting happiness)", "Practicality (decision-making)", "Criticism (minority rights)", "Complexity", "Value of Experience", "Need for Nuance", "Interpersonal Utility", "Fairness Intuition", "Social Cohesion", "Religious Authority", "Importance for understanding evolution", "Clarity of definition"]]] = Field(default_factory=list)

class DimensionSpecificAttributes(BaseModel):
    deontology: Optional[DeontologyAttributes] = None
    teleology: Optional[TeleologyAttributes] = None
    virtue_ethics: Optional[VirtueEthicsAttributes] = None
    memetics: Optional[MemeticsAttributes] = None

# --- Metadata Model ---
class MemeMetadata(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

# --- Main Ethical Meme Model ---
class EthicalMemeBase(BaseModel):
    name: str
    description: str
    ethical_dimension: List[Literal["Deontology", "Teleology", "Virtue Ethics", "Memetics", "Meta", "Action", "Agent", "Process", "Value", "Principle", "Theory", "Virtue", "Other"]]
    source_concept: str
    keywords: List[str] = Field(default_factory=list)
    variations: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    # Allow string names or ObjectIds for related memes - validation might need refinement
    related_memes: List[Union[str, str]] = Field(default_factory=list)
    dimension_specific_attributes: Optional[DimensionSpecificAttributes] = None
    morphisms: Optional[List[Dict[str, Union[str, str]]]] = Field(default_factory=list, description="Relationships (morphisms) to other memes. E.g., {'type': 'Universalizes', 'target_meme_id': '...', 'description': '...'}")
    cross_category_mappings: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Mappings across ethical categories. E.g., {'target_concept': 'Net Benefit', 'target_category': 'Teleology', 'mapping_type': 'Functorial Analogy'}")
    # Add new fields for merged tokens
    is_merged_token: Optional[bool] = Field(default=False, description="Indicates if this meme represents a merged concept from others.")
    merged_from_tokens: Optional[List[str]] = Field(default_factory=list, description="List of ObjectIds of the memes this token merges.")

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

# Create model: Inherits base, includes new fields
class EthicalMemeCreate(EthicalMemeBase):
    pass

# Update model: All fields should be optional
class EthicalMemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ethical_dimension: Optional[List[str]] = None
    dimension_specific_attributes: Optional[DimensionSpecificAttributes] = None
    tags: Optional[List[str]] = None
    morphisms: Optional[List[Dict[str, Union[str, str]]]] = None
    cross_category_mappings: Optional[List[Dict[str, str]]] = None
    is_merged_token: Optional[bool] = None
    merged_from_tokens: Optional[List[str]] = None

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

# DB model: Inherits base, adds DB-specific fields like id
class EthicalMemeInDB(EthicalMemeBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    metadata: Optional[MemeMetadata] = None  # Add metadata field

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    } 