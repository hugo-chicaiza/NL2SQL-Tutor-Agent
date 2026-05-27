# =========================================================
# app/core/executor.py
# =========================================================

import time
import logging

from typing import List, Dict, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class SQLExecutor:

    def __init__(
        self,
        db_session: AsyncSession
    ):

        self.session = db_session

    # =====================================================
    # EXECUTE SQL
    # =====================================================

    async def execute(
        self,
        sql: str
    ) -> tuple[List[Dict[str, Any]], float]:

        start_time = time.time()

        try:

            logger.info(
                "Executing SQL query"
            )

            # -------------------------------------------------
            # EXECUTE QUERY
            # -------------------------------------------------

            result = await self.session.execute(
                text(sql)
            )

            execution_time = round(
                time.time() - start_time,
                3
            )

            # -------------------------------------------------
            # FETCH RESULTS
            # -------------------------------------------------

            if result.returns_rows:

                rows = result.mappings().all()

                results = [
                    dict(row)
                    for row in rows
                ]

            else:

                results = []

            logger.info(
                f"Query executed successfully "
                f"in {execution_time}s"
            )

            return (
                results,
                execution_time
            )

        except Exception as e:

            logger.error(
                f"Database execution error: "
                f"{str(e)}"
            )

            raise Exception(
                f"Database execution failed: "
                f"{str(e)}"
            )