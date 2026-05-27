# =========================================================
# app/context/prompt_modulator.py
# =========================================================

from typing import Dict, Any


class PromptModulator:

    """
    Converts structured context into
    compact LLM-friendly bullet text.

    Goal:
    - reduce token usage
    - simplify schema understanding
    - avoid large JSON payloads
    """

    # =====================================================
    # MAIN ENTRY
    # =====================================================

    @staticmethod
    def build_context_text(
        context: Dict[str, Any]
    ) -> str:

        sections = []

        # -------------------------------------------------
        # TABLES
        # -------------------------------------------------

        schema = context.get(
            "schema",
            {}
        )

        if schema:

            sections.append(
                "DATABASE SCHEMA:"
            )

            for table_name, table_data in (
                schema.items()
            ):

                columns = []

                for col in table_data.get(
                    "columns",
                    []
                ):

                    col_text = (
                        f"{col['name']}"
                    )

                    if col.get(
                        "primary_key"
                    ):

                        col_text += " [PK]"

                    elif col.get(
                        "foreign_key"
                    ):

                        col_text += " [FK]"

                    columns.append(
                        col_text
                    )

                sections.append(

                    f"- {table_name}"
                    f" ({', '.join(columns)})"
                )

        # -------------------------------------------------
        # RELATIONSHIPS
        # -------------------------------------------------

        relationships = context.get(
            "relationships",
            []
        )

        if relationships:

            sections.append(
                "\nRELATIONSHIPS:"
            )

            for rel in relationships:

                sections.append(

                    f"- "
                    f"{rel['source_table']}"
                    f".{rel['source_column']} "
                    f"-> "
                    f"{rel['target_table']}"
                    f".{rel['target_column']}"
                )

        # -------------------------------------------------
        # JOINS
        # -------------------------------------------------

        joins = context.get(
            "joins",
            []
        )

        if joins:

            sections.append(
                "\nKNOWN JOINS:"
            )

            for join in joins:

                sections.append(
                    f"- {join}"
                )

        return "\n".join(
            sections
        )