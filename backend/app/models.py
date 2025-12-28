from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal, Annotated
from datetime import datetime, timezone
from bson import ObjectId

# Helper for ObjectId validation/serialization compatible with Pydantic v2
# Pydantic v2 handles ObjectId directly better with arbitrary_types_allowed
# but this custom type ensures validation and schema representation.
PyObjectId = Annotated[ObjectId, Field(validate_default=False)]

# --- Model for Meme Selection LLM Output ---
class MemeSelectionResponse(BaseModel):
    selected_memes: List[str] = Field(description="List of names of the most relevant ethical memes.")
    reasoning: Optional[str] = Field(default=None, description="Explanation for why these memes were selected.")

# --- Sub-models for Dimension Specific Attributes ---

class DeontologyAttributes(BaseModel):
    is_rule_based: Optional[bool] = None
    universalizability_test: Optional[str] = None
    respects_rational_agents: Optional[bool] = None
    focus_on_intent: Optional[bool] = None

class TeleologyAttributes(BaseModel):
    focus: Optional[str] = None
    utility_metric: Optional[str] = None
    scope: Optional[str] = None
    time_horizon: Optional[str] = None

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
    common_transmission_pathways: Optional[List[str]] = Field(default_factory=list)
    relevant_selection_pressures: Optional[List[str]] = Field(default_factory=list)

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

# --- Pydantic models for R2 analysis output validation ---

class ScoreEntry(BaseModel):
    score: int
    justification: str

class AnalysisResultModel(BaseModel):
    summary_text: str
    scores_json: Dict[str, ScoreEntry]

    model_config = {
        "extra": "ignore"  # ignore any additional keys
    }

# --- Agreements ---

AgreementStatus = Literal["draft", "proposed", "active", "rejected", "superseded", "expired"]
AgreementActionType = Literal["accept", "decline", "counter", "comment"]


class AgreementCreate(BaseModel):
    parties: Any
    terms: Dict[str, Any]
    status: AgreementStatus = "draft"
    model_id: Optional[str] = None
    model_version: Optional[str] = None


class AgreementActionRequest(BaseModel):
    action: AgreementActionType
    payload: Optional[Dict[str, Any]] = None
    actor_party_id: str
