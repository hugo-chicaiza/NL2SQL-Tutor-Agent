# =========================================================
# app/core/sql_generator/validator.py
# =========================================================

import sqlparse

from sqlparse.tokens import DML


class SQLValidator:

    FORBIDDEN_KEYWORDS = [

        "DELETE",
        "DROP",
        "TRUNCATE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "GRANT",
        "REVOKE"

    ]

    def validate(
        self,
        sql: str
    ) -> str:

        if not sql:

            raise Exception(
                "Generated SQL is empty"
            )

        sql = sql.strip()

        self._validate_syntax(sql)

        self._validate_security(sql)

        sql = self._enforce_limit(sql)

        return sql

    # =====================================================
    # VALIDATIONS
    # =====================================================

    def _validate_syntax(
        self,
        sql: str
    ):

        parsed = sqlparse.parse(sql)

        if not parsed:

            raise Exception(
                "Invalid SQL syntax"
            )

    def _validate_security(
        self,
        sql: str
    ):

        sql_upper = sql.upper()

        for keyword in (
            self.FORBIDDEN_KEYWORDS
        ):

            if keyword in sql_upper:

                raise Exception(
                    f"Forbidden SQL operation "
                    f"detected: {keyword}"
                )

    def _enforce_limit(
        self,
        sql: str
    ) -> str:

        sql_upper = sql.upper()

        if (
            "SELECT" in sql_upper
            and "LIMIT" not in sql_upper
        ):

            sql += "\nLIMIT 100"

        return sql