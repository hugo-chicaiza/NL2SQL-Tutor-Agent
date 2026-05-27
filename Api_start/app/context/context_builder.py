from app.models.context_models import (
    LLMContext,
    SchemaBlock,
    GraphBlock,
    SemanticBlock,
)


class ContextBuilderLLM:

    # =====================================================
    # BUILD FULL LLM CONTEXT
    # =====================================================

    @staticmethod
    def build(
        tables,
        columns,
        schema_graph,
        column_graph,
        semantic_context,
    ) -> LLMContext:

        # -------------------------------------------------
        # TABLE SEMANTICS
        # -------------------------------------------------

        table_semantics = {}

        for table in tables:

            semantic_match = next(

                (
                    s
                    for s in semantic_context.tables
                    if s.table_name == table.table_name
                ),

                None
            )

            table_semantics[table.table_name] = {

                "description":

                    semantic_match.business_meaning
                    if semantic_match
                    and semantic_match.business_meaning
                    else "",

                "domain_tags":

                    semantic_match.domain_tags
                    if semantic_match
                    else [],

                "importance_score":

                    semantic_match.importance_score
                    if semantic_match
                    else 0.0
            }

        # -------------------------------------------------
        # COLUMN SEMANTICS
        # -------------------------------------------------

        column_semantics = {}

        for table_name, cols in columns.items():

            column_semantics[table_name] = []

            for c in cols:

                semantic_match = next(

                    (
                        s
                        for s in semantic_context.columns
                        if (
                            s.table_name == table_name
                            and s.column_name == c.column_name
                        )
                    ),

                    None
                )

                column_semantics[
                    table_name
                ].append({

                    "column": c.column_name,

                    "description":

                        semantic_match.business_meaning
                        if semantic_match
                        and semantic_match.business_meaning
                        else "",

                    "semantic_type":

                        semantic_match.semantic_type
                        if semantic_match
                        else "",

                    "synonyms":

                        semantic_match.synonyms
                        if semantic_match
                        else []
                })

        # -------------------------------------------------
        # FINAL LLM CONTEXT
        # -------------------------------------------------

        return LLMContext(

            schema=SchemaBlock(

                tables=ContextBuilderLLM._build_schema(
                    tables,
                    columns
                )
            ),

            graph=GraphBlock(

                adjacency=schema_graph.adjacency,

                reverse_adjacency=(
                    schema_graph.reverse_adjacency
                ),

                edges=schema_graph.edges,
            ),

            semantics=SemanticBlock(

                tables=table_semantics,

                columns=column_semantics,
            ),

            joins=column_graph.join_clauses,
        )

    # =====================================================
    # SERIALIZATION FOR PROMPT
    # =====================================================

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

    # =====================================================
    # BUILD SCHEMA BLOCK
    # =====================================================

    @staticmethod
    def _build_schema(
        tables,
        columns
    ):

        schema_map = {

            f"{t.schema_name}.{t.table_name}": {

                "schema": t.schema_name,

                "table": t.table_name,

                "type": t.table_type,

                "columns": []
            }

            for t in tables
        }

        # -------------------------------------------------
        # BUILD COLUMNS
        # -------------------------------------------------

        for table_name, cols in columns.items():

            if not cols:
                continue

            # obtener schema desde primer column object
            schema_name = cols[0].schema_name

            table_key = (
                f"{schema_name}.{table_name}"
            )

            if table_key not in schema_map:
                continue

            for c in cols:

                col_name = (
                    getattr(
                        c,
                        "column_name",
                        None
                    )
                    or c.get(
                        "column_name"
                    )
                )

                col_type = (
                    getattr(
                        c,
                        "data_type",
                        None
                    )
                    or c.get(
                        "data_type"
                    )
                )

                nullable = getattr(
                    c,
                    "is_nullable",
                    None
                )

                pk = getattr(
                    c,
                    "is_primary_key",
                    None
                )

                fk = getattr(
                    c,
                    "is_foreign_key",
                    None
                )

                schema_map[
                    table_key
                ]["columns"].append({

                    "name": col_name,

                    "type": col_type,

                    "nullable": nullable,

                    "primary_key": pk,

                    "foreign_key": fk,
                })

        return schema_map