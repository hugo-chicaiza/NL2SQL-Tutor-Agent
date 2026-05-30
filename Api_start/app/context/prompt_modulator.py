from typing import Dict, Any


class PromptModulator:

    """
    Converts structured DB context into
    compact LLM-friendly DSL format.
    """

    @staticmethod
    def build_context_text(
        context: Dict[str, Any]
    ) -> str:

        schema = context.get("schema", {})
        relationships = context.get("relationships", [])
        joins = context.get("joins", [])
        semantic_tables = context.get("semantic_tables", {})

        lines = []

        # -------------------------------------------------
        # TABLES (COMPACT DSL)
        # -------------------------------------------------

        for table_name, table_data in schema.items():

            short_desc = semantic_tables.get(table_name, {}).get("description", "")

            lines.append(f"\nTABLE: {table_name}")
            if short_desc:
                lines.append(f"-- {short_desc[:100]}")

            for col in table_data.get("columns", []):

                name = col.get("name")
                ctype = col.get("type", "")
                pk = " PK" if col.get("primary_key") else ""
                fk = " FK" if col.get("foreign_key") else ""

                lines.append(f"- {name} ({ctype}){pk}{fk}")

        # -------------------------------------------------
        # RELATIONS (COMPRESSED)
        # -------------------------------------------------

        lines.append("\nRELATIONS:")

        for r in relationships[:10]:
            lines.append(
                f"- {r['source_table']}.{r['source_column']} → "
                f"{r['target_table']}.{r['target_column']}"
            )

        # -------------------------------------------------
        # JOINS (DIRECTLY USABLE)
        # -------------------------------------------------

        lines.append("\nJOINS:")

        for j in joins[:10]:
            lines.append(f"- {j}")

        return "\n".join(lines)