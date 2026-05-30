# =========================================================
# app/core/sql_generator.py
# =========================================================

import json
import time
import logging

from dataclasses import dataclass

from typing import (
    Dict,
    List,
    Any,
    Optional,
    Set
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.llm.openrouter import (
    OpenRouterLLMProvider
)

from app.models.context_models import (
    LLMContext
)

from app.core.planner import (
    QueryPlanner
)

from app.core.prompt_builder import (
    PromptBuilder
)

from app.core.validator import (
    SQLValidator
)

from app.core.executor import (
    SQLExecutor
)

from app.context.retriever import (
    ContextRetriever
)

from app.context.semantic_retriever import (
    SemanticRetriever
)

from app.context.prompt_modulator import (
    PromptModulator
)

logger = logging.getLogger(__name__)


# =========================================================
# RESPONSE MODEL
# =========================================================

@dataclass
class SQLGenerationResponse:

    question: str

    sql: str

    explanation: str

    rows: List[Dict[str, Any]]

    execution_time: float

    plan: Dict[str, Any]

    relevant_context: Dict[str, Any]

    llm_time: float


# =========================================================
# SQL GENERATOR
# =========================================================

class SQLGenerator:

    def __init__(
        self,
        db_session: AsyncSession,
        context: LLMContext,
        semantic_retriever: Optional[
            SemanticRetriever
        ] = None
    ):

        self.llm = (
            OpenRouterLLMProvider()
        )

        self.planner = (
            QueryPlanner()
        )

        self.prompt_builder = (
            PromptBuilder()
        )

        self.validator = (
            SQLValidator()
        )

        self.executor = (
            SQLExecutor(
                db_session=db_session
            )
        )

        self.context_retriever = (
            ContextRetriever()
        )

        self.semantic_retriever = (
            semantic_retriever
        )

        self.context = context

    # =====================================================
    # MAIN ENTRY
    # =====================================================

    async def generate(
        self,
        question: str
    ) -> SQLGenerationResponse:

        pipeline_start = time.time()

        logger.info(
            f"NL2SQL request: {question}"
        )

        # =================================================
        # 1. PLAN
        # =================================================

        plan = (
            self.planner.build_plan(
                question
            )
        )

        logger.info(
            f"Plan generated: {plan}"
        )

        # =================================================
        # 2. SEMANTIC RETRIEVAL
        # =================================================

        semantic_candidates: Optional[
            Set[str]
        ] = None

        if self.semantic_retriever:

            try:

                if (
                    self.semantic_retriever
                    .is_ready()
                ):

                    semantic_candidates = (
                        self.semantic_retriever
                        .retrieve(question)
                    )

                    logger.info(
                        f"Semantic candidates: "
                        f"{semantic_candidates}"
                    )

            except Exception as e:

                logger.warning(
                    f"Semantic retrieval failed: "
                    f"{str(e)}"
                )

                semantic_candidates = None

        # =================================================
        # 3. CONTEXT RETRIEVAL
        # =================================================

        retrieved_context = (

            self.context_retriever
            .retrieve(

                question=question,

                plan=plan,

                llm_context=self.context,

                semantic_candidates=
                    semantic_candidates
            )
        )

        logger.info(
            "Context retrieved"
        )

        # =================================================
        # 4. CONTEXT MODULATION
        # =================================================

        modulated_context = (

            PromptModulator
            .build_context_text(
                retrieved_context
            )
        )

        # =================================================
        # 5. BUILD PROMPT
        # =================================================

        prompt = (

            self.prompt_builder
            .build_prompt(

                question=question,

                relevant_context=
                    modulated_context,

                plan=plan
            )
        )

        logger.info(
            "Prompt built"
        )

        # =================================================
        # 6. GENERATE SQL
        # =================================================

        llm_response = await (
            self._generate_sql(
                prompt
            )
        )

        sql = self._format_sql(
            llm_response["sql"]
        )

        explanation = (
            llm_response[
                "explanation"
            ]
        )

        llm_time = (
            llm_response[
                "llm_time"
            ]
        )

        # =================================================
        # 7. VALIDATE SQL
        # =================================================

        validated_sql = (

            self.validator.validate(
                sql
            )
        )

        logger.info(
            "SQL validated"
        )

        # =================================================
        # 8. EXECUTE
        # =================================================

        rows, execution_time = await (

            self.executor.execute(
                validated_sql
            )
        )

        logger.info(
            f"Rows returned: "
            f"{len(rows)}"
        )

        total_time = round(
            time.time() -
            pipeline_start,
            3
        )

        logger.info(
            f"Pipeline completed "
            f"in {total_time}s"
        )

        return SQLGenerationResponse(

            question=question,

            sql=validated_sql,

            explanation=explanation,

            rows=rows,

            execution_time=
                execution_time,

            plan=plan,

            relevant_context=
                modulated_context,

            llm_time=llm_time
        )

    # =====================================================
    # LLM CALL
    # =====================================================

    async def _generate_sql(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        start_time = time.time()

        response = await (
            self.llm.generate(
                prompt
            )
        )

        raw = response.strip()

        raw = raw.replace(
            "```json",
            ""
        )

        raw = raw.replace(
            "```",
            ""
        )

        raw = raw.strip()

        try:

            data = json.loads(
                raw
            )

        except Exception as e:

            logger.error(
                f"JSON parsing error: "
                f"{str(e)}"
            )

            logger.error(raw)

            raise Exception(
                "LLM returned invalid JSON"
            )

        if "sql" not in data:

            raise Exception(
                "Missing sql field"
            )

        if "explanation" not in data:

            raise Exception(
                "Missing explanation field"
            )

        llm_time = round(
            time.time() -
            start_time,
            3
        )

        return {

            "sql":
                data["sql"].strip(),

            "explanation":
                data[
                    "explanation"
                ].strip(),

            "llm_time":
                llm_time
        }

    # =====================================================
    # SQL FORMATTER
    # =====================================================

    def _format_sql(self, sql: str) -> str:

        if not sql:
            return sql

        sql = sql.strip()

        # ❌ remove trailing semicolon safely
        sql = sql.rstrip(";")

        # ❌ FIX: remove accidental semicolon before LIMIT (CRITICAL BUG)
        sql = sql.replace(";\nLIMIT", "\nLIMIT")
        sql = sql.replace("; LIMIT", "\nLIMIT")

        # 🔧 basic formatting (safe version)
        keywords = [
            "SELECT",
            "FROM",
            "WHERE",
            "JOIN",
            "INNER JOIN",
            "LEFT JOIN",
            "RIGHT JOIN",
            "GROUP BY",
            "ORDER BY",
            "HAVING",
            "LIMIT"
        ]

        formatted = sql

        for keyword in keywords:
            formatted = formatted.replace(keyword, f"\n{keyword}")

        lines = [
            line.strip()
            for line in formatted.split("\n")
            if line.strip()
        ]

        return "\n".join(lines)