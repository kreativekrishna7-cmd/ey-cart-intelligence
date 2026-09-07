import json
from typing import Any

from agent.foundry import (
    project_client,
    MODEL_DEPLOYMENT,
)

from agent.prompts import SYSTEM_INSTRUCTIONS

from agent.tools import (
    get_ey_cart_kpis,
    get_ey_cart_revenue_trend,
    get_ey_cart_top_products,
    get_ey_cart_categories,
    compare_ey_cart_periods,
    run_ey_cart_sql,
)


class EYCartAgent:

    def __init__(self):

        self.client = (
            project_client.get_openai_client()
        )

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTIONS,
            }
        ]

    def get_tools(self) -> list[dict]:

        return [

            {
                "type": "function",
                "function": {
                    "name": "get_ey_cart_kpis",
                    "description": (
                        "Get executive KPIs for EY CART "
                        "for a specified date range. "
                        "Use for revenue, profit, margin, "
                        "orders, units, customers and AOV."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": (
                                    "Start date in YYYY-MM-DD format."
                                ),
                            },
                            "end_date": {
                                "type": "string",
                                "description": (
                                    "End date in YYYY-MM-DD format."
                                ),
                            },
                        },
                        "required": [
                            "start_date",
                            "end_date",
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "get_ey_cart_revenue_trend",
                    "description": (
                        "Get monthly revenue trend for "
                        "a specified period."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                            },
                            "end_date": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "start_date",
                            "end_date",
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "get_ey_cart_top_products",
                    "description": (
                        "Get top EY CART products by "
                        "revenue, profit, units sold "
                        "or orders."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                            },
                            "end_date": {
                                "type": "string",
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 50,
                            },
                            "metric": {
                                "type": "string",
                                "enum": [
                                    "revenue",
                                    "profit",
                                    "units_sold",
                                    "orders",
                                ],
                            },
                        },
                        "required": [
                            "start_date",
                            "end_date",
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "get_ey_cart_categories",
                    "description": (
                        "Get EY CART performance by "
                        "product category."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                            },
                            "end_date": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "start_date",
                            "end_date",
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "compare_ey_cart_periods",
                    "description": (
                        "Compare two EY CART date ranges "
                        "and calculate KPI changes."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "current_start": {
                                "type": "string",
                            },
                            "current_end": {
                                "type": "string",
                            },
                            "previous_start": {
                                "type": "string",
                            },
                            "previous_end": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "current_start",
                            "current_end",
                            "previous_start",
                            "previous_end",
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "run_ey_cart_sql",
                    "description": (
                        "Execute a safe, read-only SQL "
                        "query against the EY CART "
                        "PostgreSQL database. "
                        "Use for ad-hoc analytical questions."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": (
                                    "A SELECT or WITH SQL "
                                    "query using only EY CART tables."
                                ),
                            }
                        },
                        "required": [
                            "sql"
                        ],
                    },
                },
            },
        ]

    def execute_tool(
        self,
        name: str,
        arguments: dict,
    ) -> Any:

        if name == "get_ey_cart_kpis":

            return get_ey_cart_kpis(
                **arguments
            )

        if name == "get_ey_cart_revenue_trend":

            return get_ey_cart_revenue_trend(
                **arguments
            )

        if name == "get_ey_cart_top_products":

            return get_ey_cart_top_products(
                **arguments
            )

        if name == "get_ey_cart_categories":

            return get_ey_cart_categories(
                **arguments
            )

        if name == "compare_ey_cart_periods":

            return compare_ey_cart_periods(
                **arguments
            )

        if name == "run_ey_cart_sql":

            return run_ey_cart_sql(
                **arguments
            )

        raise ValueError(
            f"Unknown tool requested: {name}"
        )

    def ask(
        self,
        user_message: str,
    ) -> str:

        self.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        max_iterations = 8

        for _ in range(max_iterations):

            response = (
                self.client.chat.completions.create(
                    model=MODEL_DEPLOYMENT,
                    messages=self.messages,
                    tools=self.get_tools(),
                    tool_choice="auto",
                )
            )

            assistant_message = (
                response.choices[0].message
            )

            self.messages.append(
                assistant_message
            )

            if not assistant_message.tool_calls:

                return (
                    assistant_message.content
                    or "I could not generate a response."
                )

            for tool_call in (
                assistant_message.tool_calls
            ):

                tool_name = (
                    tool_call.function.name
                )

                raw_arguments = (
                    tool_call.function.arguments
                )

                arguments = json.loads(
                    raw_arguments
                )

                try:

                    result = self.execute_tool(
                        tool_name,
                        arguments,
                    )

                    tool_result = {
                        "success": True,
                        "data": result,
                    }

                except Exception as exc:

                    tool_result = {
                        "success": False,
                        "error": str(exc),
                    }

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            tool_result,
                            default=str,
                        ),
                    }
                )

        return (
            "I was unable to complete the analysis "
            "within the allowed number of steps."
        )


_agent = EYCartAgent()


def chat(
    user_message: str,
) -> str:

    return _agent.ask(
        user_message
    )
