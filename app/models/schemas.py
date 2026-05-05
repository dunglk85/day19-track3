from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from app.models.ontology import Ontology

class Entity(BaseModel):
    name: str = Field(..., description="The name of the entity")
    label: str = Field(..., description="The type/label of the entity (e.g., Company, Person)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties of the entity")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        if not Ontology.is_valid_label(v):
            # Fallback or strict validation? Let's be strict but allow some flexibility in casing
            # But ADD says PascalCase
            raise ValueError(f"Invalid entity label: {v}. Must be one of {Ontology.LABELS}")
        return v

class Relationship(BaseModel):
    source: str = Field(..., description="The name of the source entity")
    target: str = Field(..., description="The name of the target entity")
    type: str = Field(..., description="The type of the relationship (e.g., FOUNDED_BY)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties of the relationship")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if not Ontology.is_valid_relationship(v):
            raise ValueError(f"Invalid relationship type: {v}. Must be one of {Ontology.RELATIONSHIPS}")
        return v

class ExtractionResult(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
