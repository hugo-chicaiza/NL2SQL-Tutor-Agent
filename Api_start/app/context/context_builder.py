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

        schema_block = (
            ContextBuilderLLM._build_schema(
                tables=tables,
                columns=columns
            )
        )

        table_semantics = (
            ContextBuilderLLM._build_table_semantics(
                tables=tables,
                semantic_context=semantic_context
            )
        )

        column_semantics = (
            ContextBuilderLLM._build_column_semantics(
                columns=columns,
                semantic_context=semantic_context
            )
        )

        return LLMContext(

            schema=SchemaBlock(
                tables=schema_block
            ),

            graph=GraphBlock(
                adjacency=schema_graph.adjacency,
                reverse_adjacency=schema_graph.reverse_adjacency,
                edges=schema_graph.edges,
            ),

            semantics=SemanticBlock(
                tables=table_semantics,
                columns=column_semantics,
            ),

            joins=column_graph.join_clauses,
        )

    @staticmethod
    def to_prompt_context(
        llm_context: LLMContext
    ) -> dict:

        return {

            "schema":
                llm_context.schema.tables,

            "relationships":
                llm_context.graph.edges,

            "semantic_tables":
                llm_context.semantics.tables,

            "semantic_columns":
                llm_context.semantics.columns,

            "joins":
                llm_context.joins,
        }

    @staticmethod
    def _build_table_semantics(
        tables,
        semantic_context,
    ):

        semantic_lookup = {

            s.table_name: s
            for s in semantic_context.tables
        }

        result = {}

        for table in tables:

            full_name = (
                f"{table.schema_name}."
                f"{table.table_name}"
            )

            semantic = semantic_lookup.get(
                table.table_name
            )

            result[full_name] = {

                "description":
                    semantic.business_meaning
                    if semantic and semantic.business_meaning
                    else "",

                "domain_tags":
                    semantic.domain_tags
                    if semantic
                    else [],

                "importance_score":
                    semantic.importance_score
                    if semantic
                    else 0.0,
            }

        return result

    @staticmethod
    def _build_column_semantics(
        columns,
        semantic_context,
    ):

        semantic_lookup = {

            (
                s.table_name,
                s.column_name
            ): s

            for s in semantic_context.columns
        }

        result = {}

        for table_name, cols in columns.items():

            if not cols:
                continue

            schema_name = cols[0].schema_name

            full_table_name = (
                f"{schema_name}.{table_name}"
            )

            result[full_table_name] = []

            for col in cols:

                semantic = semantic_lookup.get(
                    (
                        table_name,
                        col.column_name
                    )
                )

                result[
                    full_table_name
                ].append({

                    "column":
                        col.column_name,

                    "description":
                        semantic.business_meaning
                        if semantic
                        and semantic.business_meaning
                        else "",

                    "semantic_type":
                        semantic.semantic_type
                        if semantic
                        else "",

                    "synonyms":
                        semantic.synonyms
                        if semantic
                        else [],
                })

        return result

    @staticmethod
    def _build_schema(
        tables,
        columns,
    ):

        schema_map = {}

        for table in tables:

            full_name = (
                f"{table.schema_name}."
                f"{table.table_name}"
            )

            schema_map[full_name] = {

                "schema":
                    table.schema_name,

                "table":
                    table.table_name,

                "type":
                    table.table_type,

                "columns": []
            }

        for table_name, cols in columns.items():

            if not cols:
                continue

            schema_name = cols[0].schema_name

            full_table_name = (
                f"{schema_name}.{table_name}"
            )

            if full_table_name not in schema_map:
                continue

            for col in cols:

                schema_map[
                    full_table_name
                ]["columns"].append({

                    "name":
                        col.column_name,

                    "type":
                        col.data_type,

                    "nullable":
                        col.is_nullable,

                    "primary_key":
                        col.is_primary_key,

                    "foreign_key":
                        col.is_foreign_key,

                    "foreign_table":
                        col.foreign_table_name,

                    "foreign_column":
                        col.foreign_column_name,
                })

        return schema_map