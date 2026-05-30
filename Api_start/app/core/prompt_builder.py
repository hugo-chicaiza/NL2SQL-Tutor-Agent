# =========================================================
# app/core/prompt_builder.py
# =========================================================

import json

from typing import Dict, Any


class PromptBuilder:

    """
    Builds the final NL2SQL prompt.

    Responsibilities:
    - inject filtered schema
    - inject semantic metadata
    - inject planner hints
    - enforce output format
    """

    @staticmethod
    def build_prompt(
        question: str,
        relevant_context: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> str:

        context_json = json.dumps(
            relevant_context,
            indent=2,
            ensure_ascii=False
        )

        plan_json = json.dumps(
            plan,
            indent=2,
            ensure_ascii=False
        )

        return f"""
You are a senior PostgreSQL query generation engine.

Your objective is to generate a valid PostgreSQL query using ONLY the provided context.

========================================================
DATABASE CONTEXT
========================================================

{context_json}

========================================================
USER QUESTION
========================================================

{question}

========================================================
QUERY PLAN
========================================================

{plan_json}

========================================================
MANDATORY RULES
========================================================

1. Use ONLY tables present in DATABASE CONTEXT.

2. Use ONLY columns present in DATABASE CONTEXT.

3. Use ONLY relationships and joins present in DATABASE CONTEXT.

4. NEVER invent:
   - tables
   - columns
   - aliases
   - joins

5. Generate PostgreSQL syntax only.

6. NEVER generate:
   - INSERT
   - UPDATE
   - DELETE
   - DROP
   - ALTER
   - TRUNCATE
   - CREATE

7. Use explicit JOIN clauses.

8. Avoid SELECT *.

9. Use aggregation only when required.

10. Respect planner hints.

11. Add LIMIT when appropriate.

12. If multiple joins exist,
    prefer joins listed in the "joins" section.

13. Return executable SQL.

========================================================
OUTPUT FORMAT
========================================================

Return ONLY valid JSON.

{{
  "sql": "SELECT ...",
  "explanation": "Explain how the query answers the question."
}}

DO NOT RETURN MARKDOWN.
DO NOT USE ```json.
DO NOT ADD EXTRA TEXT.
"""