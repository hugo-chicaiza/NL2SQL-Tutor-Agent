from dataclasses import dataclass
from typing import Dict, List, Any


# =========================
# SCHEMA BLOCK
# =========================
@dataclass
class SchemaBlock:
    tables: Dict[str, Any]


# =========================
# GRAPH BLOCK
# =========================
@dataclass
class GraphBlock:
    adjacency: Dict[str, List[str]]
    reverse_adjacency: Dict[str, List[str]]
    edges: List[dict]


# =========================
# SEMANTIC BLOCK
# =========================
@dataclass
class SemanticBlock:
    tables: Dict[str, Any]
    columns: Dict[str, Any]


# =========================
# FINAL LLM CONTEXT
# =========================
@dataclass
class LLMContext:
    schema: SchemaBlock
    graph: GraphBlock
    semantics: SemanticBlock
    joins: List[str]