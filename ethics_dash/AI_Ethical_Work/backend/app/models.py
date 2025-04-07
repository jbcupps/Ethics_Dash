from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
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
    ethical_dimension: List[Literal["Deontology", "Teleology", "Virtue Ethics", "Memetics"]]
    source_concept: str
    keywords: List[str] = Field(default_factory=list)
    variations: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    # Allow string names or ObjectIds for related memes - validation might need refinement
    related_memes: List[Union[PyObjectId, str]] = Field(default_factory=list)
    dimension_specific_attributes: Optional[DimensionSpecificAttributes] = None

class EthicalMemeCreate(EthicalMemeBase):
    # No additional fields needed for creation beyond the base
    pass

class EthicalMemeUpdate(BaseModel):
    # All fields are optional for updates
    name: Optional[str] = None
    description: Optional[str] = None
    ethical_dimension: Optional[List[Literal["Deontology", "Teleology", "Virtue Ethics", "Memetics"]]] = None
    source_concept: Optional[str] = None
    keywords: Optional[List[str]] = None
    variations: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    related_memes: Optional[List[Union[PyObjectId, str]]] = None
    dimension_specific_attributes: Optional[DimensionSpecificAttributes] = None
    # Metadata is handled separately during update

class EthicalMemeInDB(EthicalMemeBase):
    id: PyObjectId = Field(alias="_id") # Map MongoDB's _id to Pydantic's id
    metadata: MemeMetadata

    class Config:
        populate_by_name = True # Allow using alias "_id"
        json_encoders = {ObjectId: str} # Ensure ObjectId is serialized as str
        from_attributes = True # Necessary for ORM mode (if used, good practice anyway) 