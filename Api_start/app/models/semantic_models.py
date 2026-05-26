from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TableSemanticInfo(BaseModel):
    table_name: str

    business_meaning: Optional[str] = None

    domain_tags: List[str] = Field(default_factory=list)

    importance_score: float = 0.0

    sample_queries: List[str] = Field(default_factory=list)

    approved: bool = False

    confidence_score: float = 0.0

    generated_by: Optional[str] = None

    review_notes: Optional[str] = None

    last_updated: Optional[datetime] = None


class ColumnSemanticInfo(BaseModel):
    table_name: str

    column_name: str

    semantic_type: Optional[str] = None

    business_meaning: Optional[str] = None

    synonyms: List[str] = Field(default_factory=list)

    example_values: List[str] = Field(default_factory=list)

    approved: bool = False

    confidence_score: float = 0.0

    generated_by: Optional[str] = None

    review_notes: Optional[str] = None

    last_updated: Optional[datetime] = None


class SchemaSemanticMap(BaseModel):
    tables: List[TableSemanticInfo] = Field(default_factory=list)

    columns: List[ColumnSemanticInfo] = Field(default_factory=list)