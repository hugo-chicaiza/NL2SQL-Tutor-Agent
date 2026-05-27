from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List

from app.models.schema_models import RelationshipInfo


@dataclass
class SchemaGraph:
    """
    Graph representation of database schema (TABLE LEVEL).
    This is NOT SQL. This is for LLM reasoning and routing.
    """

    adjacency: Dict[str, List[str]]
    reverse_adjacency: Dict[str, List[str]]
    edges: List[dict]  # normalized for LLM + API compatibility

    def get_neighbors(self, table: str) -> List[str]:
        return self.adjacency.get(table, [])

    def get_reverse_neighbors(self, table: str) -> List[str]:
        return self.reverse_adjacency.get(table, [])

    def has_path(self, start: str, end: str) -> bool:
        return bool(self.shortest_path(start, end))

    def shortest_path(self, start: str, end: str) -> List[str]:
        """
        BFS shortest path between tables.
        Useful for join planning.
        """

        if start == end:
            return [start]

        queue = deque([[start]])
        visited = set()

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node in visited:
                continue

            visited.add(node)

            for neighbor in self.adjacency.get(node, []):
                new_path = path + [neighbor]

                if neighbor == end:
                    return new_path

                queue.append(new_path)

        return []

    def detect_self_joins(self) -> List[str]:
        """
        Returns tables that reference themselves.
        """
        return [
            src
            for src, targets in self.adjacency.items()
            if src in targets
        ]


class SchemaGraphBuilder:

    @staticmethod
    def build(
        relationships: List[RelationshipInfo]
    ) -> SchemaGraph:

        adjacency = defaultdict(set)

        reverse_adjacency = defaultdict(set)

        edges = []

        for rel in relationships:

            src = (
                f"{rel.source_schema}."
                f"{rel.source_table}"
            )

            tgt = (
                f"{rel.target_schema}."
                f"{rel.target_table}"
            )

            adjacency[src].add(tgt)

            adjacency[tgt].add(src)

            reverse_adjacency[tgt].add(src)

            edges.append({

                "source_table": src,

                "target_table": tgt,

                "source_column":
                    rel.source_column,

                "target_column":
                    rel.target_column,

                "constraint":
                    rel.constraint_name,
            })

        return SchemaGraph(

            adjacency={
                k: list(v)
                for k, v in adjacency.items()
            },

            reverse_adjacency={
                k: list(v)
                for k, v in reverse_adjacency.items()
            },

            edges=edges,
        )