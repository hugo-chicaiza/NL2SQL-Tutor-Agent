# app/core/sql_generator.py

import json
import time
import logging

from dataclasses import dataclass
from typing import Dict, List, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.llm.gemini import (
    GeminiLLMProvider
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
# MAIN SQL GENERATOR
# =========================================================

class SQLGenerator:

    def __init__(
        self,
        db_session: AsyncSession,
        context: LLMContext
    ):

        # -------------------------------------------------
        # LLM PROVIDER
        # -------------------------------------------------

        #self.llm = GeminiLLMProvider()
        self.llm = OpenRouterLLMProvider()

        # -------------------------------------------------
        # LOCAL COMPONENTS
        # -------------------------------------------------

        self.planner = QueryPlanner()

        self.prompt_builder = PromptBuilder()

        self.validator = SQLValidator()

        self.executor = SQLExecutor(
            db_session=db_session
        )

        self.context_retriever = (
            ContextRetriever()
        )

        # -------------------------------------------------
        # PREBUILT LLM CONTEXT
        # -------------------------------------------------

        self.context = context

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    async def generate(
        self,
        question: str
    ) -> SQLGenerationResponse:

        pipeline_start = time.time()

        logger.info(
            f"Starting NL2SQL generation "
            f"for: {question}"
        )

        # -------------------------------------------------
        # 1. LOCAL PLANNER
        # -------------------------------------------------

        plan = self.planner.build_plan(
            question
        )

        logger.info(
            f"Execution plan generated: "
            f"{plan}"
        )



        # -------------------------------------------------
        # 2. RETRIEVE CONTEXT
        # -------------------------------------------------

        retrieved_context = (
            self.context_retriever.retrieve(
                question=question,
                plan=plan,
                llm_context=self.context
            )
        )

        relevant_context = (
            PromptModulator.build_context_text(
                retrieved_context
            )
        )

        logger.info(
            "Relevant context retrieved"
        )

        # -------------------------------------------------
        # 3. BUILD PROMPT
        # -------------------------------------------------

        prompt = (
            self.prompt_builder.build_prompt(
                question=question,
                relevant_context=relevant_context,
                plan=plan
            )
        )

        logger.info(
            "Prompt generated successfully"
        )

        # -------------------------------------------------
        # 4. SINGLE LLM CALL
        # -------------------------------------------------

        llm_response = await (
            self._generate_sql_and_reasoning(
                prompt
            )
        )

        sql = llm_response["sql"]

        explanation = (
            llm_response["explanation"]
        )

        llm_time = (
            llm_response["llm_time"]
        )

        logger.info(
            "SQL generated successfully"
        )

        # -------------------------------------------------
        # 5. VALIDATE SQL
        # -------------------------------------------------

        validated_sql = (
            self.validator.validate(
                sql
            )
        )

        logger.info(
            "SQL validation completed"
        )

        # -------------------------------------------------
        # 6. EXECUTE SQL
        # -------------------------------------------------

        rows, execution_time = await (
            self.executor.execute(
                validated_sql
            )
        )

        logger.info(
            f"Query executed in "
            f"{execution_time}s"
        )

        total_pipeline_time = round(
            time.time() - pipeline_start,
            3
        )

        logger.info(
            f"Pipeline completed in "
            f"{total_pipeline_time}s"
        )

        # -------------------------------------------------
        # 7. FINAL RESPONSE
        # -------------------------------------------------

        return SQLGenerationResponse(

            question=question,

            sql=validated_sql,

            explanation=explanation,

            rows=rows,

            execution_time=execution_time,

            plan=plan,

            relevant_context=relevant_context,

            llm_time=llm_time
        )

    # =====================================================
    # SINGLE OPTIMIZED LLM CALL
    # =====================================================

    async def _generate_sql_and_reasoning(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        llm_start = time.time()

        response = await self.llm.generate(
            prompt
        )

        raw_text = response.strip()

        # -------------------------------------------------
        # CLEAN MARKDOWN
        # -------------------------------------------------

        raw_text = raw_text.replace(
            "```json",
            ""
        )

        raw_text = raw_text.replace(
            "```",
            ""
        )

        raw_text = raw_text.strip()

        # -------------------------------------------------
        # PARSE JSON RESPONSE
        # -------------------------------------------------

        try:

            data = json.loads(
                raw_text
            )

        except Exception as e:

            logger.error(
                f"Failed parsing LLM JSON: "
                f"{str(e)}"
            )

            logger.error(
                f"Raw LLM response: "
                f"{raw_text}"
            )

            raise Exception(
                "LLM returned invalid JSON"
            )

        # -------------------------------------------------
        # VALIDATE RESPONSE STRUCTURE
        # -------------------------------------------------

        if "sql" not in data:

            raise Exception(
                "LLM response missing "
                "'sql'"
            )

        if "explanation" not in data:

            raise Exception(
                "LLM response missing "
                "'explanation'"
            )

        llm_time = round(
            time.time() - llm_start,
            3
        )

        return {

            "sql": data["sql"].strip(),

            "explanation": (
                data["explanation"].strip()
            ),

            "llm_time": llm_time
        }