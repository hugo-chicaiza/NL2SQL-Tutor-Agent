from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from app.models.schema_models import (
    RelationshipInfo
)


@dataclass
class ColumnGraph:

    join_map: Dict[
        str,
        Dict[str, Dict[str, str]]
    ]

    reverse_map: Dict[
        str,
        List[dict]
    ]

    join_clauses: List[str]

    edges: List[dict]


class ColumnGraphBuilder:

    @staticmethod
    def build(
        relationships: List[RelationshipInfo]
    ) -> ColumnGraph:

        join_map = defaultdict(dict)

        reverse_map = defaultdict(list)

        join_clauses = []

        edges = []

        for rel in relationships:

            src_table = (
                f"{rel.source_schema}."
                f"{rel.source_table}"
            )

            tgt_table = (
                f"{rel.target_schema}."
                f"{rel.target_table}"
            )

            src_col = rel.source_column

            tgt_col = rel.target_column

            # =========================================
            # FORWARD JOIN MAP
            # =========================================

            join_map[
                src_table
            ][tgt_table] = {

                "source_column":
                    src_col,

                "target_column":
                    tgt_col
            }

            # =========================================
            # REVERSE LOOKUP
            # =========================================

            reverse_map[
                tgt_table
            ].append({

                "source_table":
                    src_table,

                "source_column":
                    src_col,

                "target_column":
                    tgt_col
            })

            # =========================================
            # SQL READY JOIN
            # =========================================

            join_clauses.append(

                f"{src_table}.{src_col} = "
                f"{tgt_table}.{tgt_col}"
            )

            # =========================================
            # NORMALIZED EDGE
            # =========================================

            edges.append({

                "source_table":
                    src_table,

                "target_table":
                    tgt_table,

                "source_column":
                    src_col,

                "target_column":
                    tgt_col,

                "constraint":
                    rel.constraint_name,

                "join":

                    f"{src_table}.{src_col} = "
                    f"{tgt_table}.{tgt_col}"
            })

        return ColumnGraph(

            join_map=dict(join_map),

            reverse_map=dict(reverse_map),

            join_clauses=join_clauses,

            edges=edges,
        )