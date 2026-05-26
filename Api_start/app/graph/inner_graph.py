from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from app.models.schema_models import RelationshipInfo


@dataclass
class ColumnGraph:
    """
    Column-level graph for SQL JOIN generation.
    This is the SQL execution layer for the LLM.
    """

    join_map: Dict[str, Dict[str, Dict[str, str]]]
    reverse_map: Dict[str, List[dict]]
    join_clauses: List[str]
    edges: List[dict]


class ColumnGraphBuilder:

    @staticmethod
    def build(relationships: List[RelationshipInfo]) -> ColumnGraph:

        join_map = defaultdict(dict)
        reverse_map = defaultdict(list)
        join_clauses = []
        edges = []

        for rel in relationships:

            src_table = rel.source_table
            src_col = rel.source_column

            tgt_table = rel.target_table
            tgt_col = rel.target_column

            # 1. Forward join map
            join_map[src_table][tgt_table] = {
                "source_column": src_col,
                "target_column": tgt_col
            }

            # 2. Reverse lookup
            reverse_map[tgt_table].append({
                "source_table": src_table,
                "source_column": src_col,
                "target_column": tgt_col
            })

            # 3. SQL-ready join clause
            join_clauses.append(
                f"{src_table}.{src_col} = {tgt_table}.{tgt_col}"
            )

            # 4. normalized edge (future semantic + MCP ready)
            edges.append({
                "source_table": src_table,
                "target_table": tgt_table,
                "source_column": src_col,
                "target_column": tgt_col,
                "constraint": rel.constraint_name,
                "join": f"{src_table}.{src_col} = {tgt_table}.{tgt_col}"
            })

        return ColumnGraph(
            join_map=dict(join_map),
            reverse_map=dict(reverse_map),
            join_clauses=join_clauses,
            edges=edges,
        )