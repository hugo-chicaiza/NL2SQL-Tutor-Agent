from app.models.context_models import (
    LLMContext,
    SchemaBlock,
    GraphBlock,
    SemanticBlock,
)


class ContextBuilderLLM:

    @staticmethod
    def build(
        tables,
        columns,
        schema_graph,
        column_graph,
        semantic_context,
    ) -> LLMContext:

        return LLMContext(
            schema=SchemaBlock(
                tables=ContextBuilderLLM._build_schema(tables, columns)
            ),

            graph=GraphBlock(
                adjacency=schema_graph.adjacency,
                reverse_adjacency=schema_graph.reverse_adjacency,
                edges=schema_graph.edges,
            ),

            semantics=SemanticBlock(
                tables={
                    t.table_name: {
                        "description": semantic_context.tables.get(
                            t.table_name, {}
                        ).get("description", "")
                    }
                    for t in tables
                },

                columns={
                    table: [
                        {
                            "column": c.column_name,
                            "description": semantic_context.columns
                            .get(table, {})
                            .get(c.column_name, "")
                        }
                        for c in cols
                    ]
                    for table, cols in columns.items()
                },
            ),

            joins=column_graph.join_clauses,
        )

    @staticmethod
    def _build_schema(tables, columns):

        schema_map = {
            t.table_name: {
                "type": t.table_type,
                "columns": []
            }
            for t in tables
        }

        for table_name, cols in columns.items():

            # safety check
            if table_name not in schema_map:
                continue

            for c in cols:

                # soporta ColumnInfo o dict (robustez)
                col_name = getattr(c, "column_name", None) or c.get("column_name")
                col_type = getattr(c, "data_type", None) or c.get("data_type")
                nullable = getattr(c, "is_nullable", None)
                pk = getattr(c, "is_primary_key", None)
                fk = getattr(c, "is_foreign_key", None)

                schema_map[table_name]["columns"].append({
                    "name": col_name,
                    "type": col_type,
                    "nullable": nullable,
                    "primary_key": pk,
                    "foreign_key": fk,
                })

        return schema_map