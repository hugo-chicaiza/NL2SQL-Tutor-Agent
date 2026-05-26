from typing import List, Optional

from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    schema_name: str
    table_name: str

    table_type: Optional[str] = None
    table_comment: Optional[str] = None

    table_category: Optional[str] = None


class ColumnInfo(BaseModel):
    schema_name: str
    table_name: str

    column_name: str
    ordinal_position: int

    data_type: str

    is_nullable: bool = True

    default_value: Optional[str] = None

    max_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None

    is_primary_key: bool = False
    is_foreign_key: bool = False

    foreign_table_name: Optional[str] = None
    foreign_column_name: Optional[str] = None

    column_comment: Optional[str] = None


class PrimaryKeyInfo(BaseModel):
    schema_name: str

    table_name: str
    column_name: str

    constraint_name: str


class ForeignKeyInfo(BaseModel):
    constraint_name: str
    constraint_type: Optional[str] = "FOREIGN KEY"

    source_schema: str
    source_table: str
    source_column: str

    target_schema: str
    target_table: str
    target_column: str


class RelationshipInfo(BaseModel):
    relationship_type: str = "many-to-one"

    source_schema: str
    source_table: str
    source_column: str

    target_schema: str
    target_table: str
    target_column: str

    constraint_name: Optional[str] = None


class IndexInfo(BaseModel):
    schema_name: str

    table_name: str
    index_name: str

    columns: List[str] = Field(default_factory=list)

    is_unique: bool = False

    index_type: Optional[str] = None


class SchemaStats(BaseModel):
    total_tables: int = 0
    total_columns: int = 0
    total_relationships: int = 0
    total_indexes: int = 0