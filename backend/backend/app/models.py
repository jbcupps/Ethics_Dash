from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import List, Optional, Dict, Any, Union, Literal, Annotated
from datetime import datetime, timezone
from bson import ObjectId

# Helper for ObjectId validation/serialization compatible with Pydantic v2
# Pydantic v2 handles ObjectId directly better with arbitrary_types_allowed
# but this custom type ensures validation and schema representation.
PyObjectId = Annotated[ObjectId, Field(validate_default=False)]

# Define ethical dimensions as Literals for type hinting and validation
EthicalDimension = Literal["Deontology", "Teleology", "Areteology", "Memetics"]

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
    ethical_dimension: List[str]
    source_concept: str
    keywords: List[str] = Field(default_factory=list)
    variations: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    related_memes: List[Union[PyObjectId, str]] = Field(default_factory=list)
    dimension_specific_attributes: Optional[DimensionSpecificAttributes] = None
    morphisms: Optional[List[Dict[str, Union[str, PyObjectId]]]] = Field(default_factory=list, description="Relationships (morphisms) to other memes. E.g., {'type': 'Universalizes', 'target_meme_id': '...', 'description': '...'}")
    cross_category_mappings: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Mappings across ethical categories. E.g., {'target_concept': 'Net Benefit', 'target_category': 'Teleology', 'mapping_type': 'Functorial Analogy'}")
    is_merged_token: Optional[bool] = Field(default=False, description="Indicates if this meme represents a merged concept from others.")
    merged_from_tokens: Optional[List[PyObjectId]] = Field(default_factory=list, description="List of ObjectIds of the memes this token merges.")
    metadata: MemeMetadata

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True, # Needed for ObjectId
        "json_encoders": {ObjectId: str} # Used by model_dump_json
    }

# Create model: Inherits base
class EthicalMemeCreate(EthicalMemeBase):
    # Exclude metadata on creation, it will be added by the API
    metadata: Optional[MemeMetadata] = Field(default=None, exclude=True)
    pass

# Update model: All fields should be optional
class EthicalMemeUpdate(BaseModel):
    # Make all fields from Base optional, exclude metadata as it's handled separately
    name: Optional[str] = None
    description: Optional[str] = None
    ethical_dimension: Optional[List[str]] = None
    source_concept: Optional[str] = None
    keywords: Optional[List[str]] = None
    variations: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    related_memes: Optional[List[Union[PyObjectId, str]]] = None
    dimension_specific_attributes: Optional[DimensionSpecificAttributes] = None
    morphisms: Optional[List[Dict[str, Union[str, PyObjectId]]]] = None
    cross_category_mappings: Optional[List[Dict[str, str]]] = None
    is_merged_token: Optional[bool] = None
    merged_from_tokens: Optional[List[PyObjectId]] = None
    # metadata is not directly updatable via this model

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

# DB model: Represents data fetched from DB including _id
class EthicalMemeInDB(EthicalMemeBase):
    # Use Field with alias for '_id'
    id: PyObjectId = Field(alias="_id")

    # Inherits model_config from Base, including metadata handling
    # No need to redefine model_config unless overriding Base

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    } 