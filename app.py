import re

import streamlit as st

from agent.chat import chat

from visualization.charts import (
    monthly_revenue,
    yearly_revenue_profit,
    category_revenue,
    top_products,
)

from visualization.chart_selector import (
    detect_visualization,
)


st.set_page_config(
    page_title="EY CART BOT",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .stChatMessage {
        border-radius: 12px;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">🛒 EY CART BOT</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered ecommerce analytics and management assistant"
    "</div>",
    unsafe_allow_html=True,
)


if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:

    st.header("EY CART")

    st.caption(
        "Ask questions about your ecommerce data."
    )

    st.divider()

    st.subheader("Try asking")

    example_questions = [
        "What is our total revenue in 2026?",
        "Compare revenue and profit between 2025 and 2026.",
        "Show monthly revenue trend for 2026.",
        "Show revenue contribution by category.",
        "What are the top 10 products by revenue?",
        "Give me an executive summary for 2026.",
        "Prepare a management report for 2026.",
    ]

    for question in example_questions:
        st.caption(f"• {question}")

    st.divider()

    if st.button(
        "Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


def extract_years(text: str) -> list[int]:
    """
    Extract 4-digit years from the user's question.
    """

    years = re.findall(
        r"\b(20\d{2})\b",
        text,
    )

    return sorted(
        set(int(year) for year in years)
    )


def get_year_range(year: int):
    """
    Return start/end dates for a year.
    """

    return (
        f"{year}-01-01",
        f"{year + 1}-01-01",
    )


def render_visualization(question: str):
    """
    Determine whether the user's question benefits
    from a visualization and render the appropriate chart.
    """

    visualization_type = detect_visualization(
        question
    )

    years = extract_years(question)

    if visualization_type == "line":

        if years:

            year = years[-1]

        else:

            year = 2026

        start_date, end_date = get_year_range(
            year
        )

        fig = monthly_revenue(
            start_date,
            end_date,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"revenue_trend_{year}_{len(st.session_state.messages)}",
            )

        return


    if visualization_type == "comparison":

        if len(years) >= 2:

            year_1 = years[0]
            year_2 = years[1]

        else:

            year_1 = 2025
            year_2 = 2026

        start_1, end_1 = get_year_range(
            year_1
        )

        start_2, end_2 = get_year_range(
            year_2
        )

        fig = yearly_revenue_profit(
            start_1,
            end_1,
            start_2,
            end_2,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=(
                    f"comparison_"
                    f"{year_1}_{year_2}_"
                    f"{len(st.session_state.messages)}"
                ),
            )

        return


    if visualization_type == "pie":

        if years:

            year = years[-1]

        else:

            year = 2026

        start_date, end_date = get_year_range(
            year
        )

        fig = category_revenue(
            start_date,
            end_date,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=(
                    f"category_revenue_"
                    f"{year}_"
                    f"{len(st.session_state.messages)}"
                ),
            )

        return


    if visualization_type == "products":

        if years:

            year = years[-1]

        else:

            year = 2026

        start_date, end_date = get_year_range(
            year
        )

        fig = top_products(
            start_date,
            end_date,
            10,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=(
                    f"top_products_"
                    f"{year}_"
                    f"{len(st.session_state.messages)}"
                ),
            )

        return


for message in st.session_state.messages:

    role = message["role"]

    with st.chat_message(role):

        st.markdown(
            message["content"]
        )

        if role == "user":

            message_index = (
                st.session_state.messages.index(
                    message
                )
            )

            if (
                message_index + 1
                < len(st.session_state.messages)
            ):

                pass


user_input = st.chat_input(
    "Ask EY CART anything..."
)


if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_input
        )


    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing EY CART data..."
        ):

            try:

                response = chat(
                    user_input
                )

                st.markdown(
                    response
                )

                try:

                    render_visualization(
                        user_input
                    )

                except Exception as chart_error:

                    st.caption(
                        "Visualization unavailable "
                        f"for this query: {chart_error}"
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

            except Exception as exc:

                error_message = (
                    "I couldn't complete the analysis.\n\n"
                    f"**Error:** `{exc}`"
                )

                st.error(
                    error_message
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
