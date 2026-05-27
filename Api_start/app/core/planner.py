# =========================================================
# app/core/sql_generator/planner.py
# =========================================================

import re

from typing import Dict, Any


class QueryPlanner:

    AGGREGATION_PATTERNS = {
        "count": [
            "count",
            "how many",
            "cantidad",
            "numero de"
        ],
        "sum": [
            "sum",
            "total"
        ],
        "avg": [
            "average",
            "avg",
            "promedio"
        ],
        "max": [
            "highest",
            "largest",
            "maximum",
            "max"
        ],
        "min": [
            "lowest",
            "minimum",
            "min"
        ]
    }

    ORDER_PATTERNS = {
        "DESC": [
            "top",
            "highest",
            "largest",
            "most",
            "best"
        ],
        "ASC": [
            "lowest",
            "smallest",
            "least",
            "worst"
        ]
    }

    TIME_PATTERNS = [
        "today",
        "yesterday",
        "week",
        "month",
        "year",
        "daily",
        "weekly",
        "monthly"
    ]

    LIMIT_REGEX = r"\btop\s+(\d+)\b"

    def build_plan(
        self,
        question: str
    ) -> Dict[str, Any]:

        question_clean = (
            question
            .lower()
            .strip()
        )

        aggregation = self._detect_aggregation(
            question_clean
        )

        ordering = self._detect_ordering(
            question_clean
        )

        limit = self._detect_limit(
            question_clean
        )

        time_context = (
            self._detect_time_context(
                question_clean
            )
        )

        requires_group_by = (
            aggregation is not None
        )

        return {

            "intent": self._detect_intent(
                aggregation
            ),

            "aggregation": aggregation,

            "ordering": ordering,

            "limit": limit,

            "time_context": time_context,

            "requires_group_by": (
                requires_group_by
            ),

            "question": question
        }

    # =====================================================
    # INTERNAL METHODS
    # =====================================================

    def _detect_intent(
        self,
        aggregation
    ) -> str:

        if aggregation:
            return "aggregation"

        return "select"

    def _detect_aggregation(
        self,
        question: str
    ):

        for agg_type, patterns in (
            self.AGGREGATION_PATTERNS.items()
        ):

            for pattern in patterns:

                if pattern in question:
                    return agg_type

        return None

    def _detect_ordering(
        self,
        question: str
    ):

        for direction, patterns in (
            self.ORDER_PATTERNS.items()
        ):

            for pattern in patterns:

                if pattern in question:

                    return {
                        "direction": direction,
                        "reason": pattern
                    }

        return None

    def _detect_time_context(
        self,
        question: str
    ):

        for pattern in self.TIME_PATTERNS:

            if pattern in question:
                return pattern

        return None

    def _detect_limit(
        self,
        question: str
    ) -> int:

        match = re.search(
            self.LIMIT_REGEX,
            question
        )

        if match:
            return int(match.group(1))

        return 100