
import streamlit as st

from recommender import recommend


st.set_page_config(
    page_title="Smart Listing Finder",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Smart Listing Finder")
st.write(
    "Find the right space for your needs using natural language. "
    "Describe your budget, location, capacity, and preferred features."
)

st.divider()

EXAMPLES = [
    "Find a meeting room in Pune under 1500 for 8 people with a projector",
    "I need a coworking space in Mumbai",
    "Find a podcast studio in Delhi with microphones",
    "Find an event venue in Bengaluru for 100 people with parking",
    "Find a photo studio in Chennai under 3000",
]

st.subheader("Describe what you're looking for")

selected_example = st.selectbox(
    "Or choose an example query",
    ["Write my own query"] + EXAMPLES,
)

default_query = (
    "" if selected_example == "Write my own query"
    else selected_example
)

query = st.text_area(
    "Your requirements",
    value=default_query,
    placeholder=(
        "Example: Find a meeting room in Pune under 1500 "
        "for 8 people with a projector"
    ),
    height=100,
)

search_clicked = st.button(
    "Find Recommendations",
    type="primary",
    use_container_width=True,
)

if search_clicked:
    if not query.strip():
        st.warning("Please enter your requirements first.")
    else:
        with st.spinner("Finding suitable listings..."):
            try:
                response = recommend(query)

                st.subheader("Your results")

                if response["status"] == "clarification":
                    st.info(response["message"])

                elif response["status"] == "no_matches":
                    st.warning(response["message"])

                else:
                    st.success(response["message"])

                    requirements = response["requirements"]

                    with st.expander("See interpreted requirements"):
                        st.write(
                            "City:",
                            requirements["city"] or "Any",
                        )
                        st.write(
                            "Category:",
                            requirements["category"] or "Any",
                        )
                        st.write(
                            "Maximum budget:",
                            (
                                f"₹{requirements['max_price']}/hour"
                                if requirements["max_price"] is not None
                                else "Not specified"
                            ),
                        )
                        st.write(
                            "Minimum capacity:",
                            (
                                f"{requirements['min_capacity']} people"
                                if requirements["min_capacity"] is not None
                                else "Not specified"
                            ),
                        )
                        st.write(
                            "Required features:",
                            ", ".join(
                                requirements["required_features"]
                            ) or "None specified",
                        )

                    for index, listing in enumerate(
                        response["results"], start=1
                    ):
                        with st.container(border=True):
                            st.markdown(
                                f"### {index}. {listing['name']}"
                            )

                            col1, col2, col3 = st.columns(3)

                            col1.metric(
                                "Price per hour",
                                f"₹{listing['price_per_hour']:,}",
                            )
                            col2.metric(
                                "Rating",
                                f"{listing['rating']}/5 ⭐",
                            )
                            col3.metric(
                                "Capacity",
                                f"{listing['capacity']} people",
                            )

                            st.write(
                                f"**Location:** {listing['city']}"
                            )
                            st.write(
                                f"**Category:** {listing['category'].title()}"
                            )
                            st.write(
                                "**Features:** "
                                + listing["features"].replace("|", ", ")
                            )

                            st.write("**Why this was recommended:**")
                            for reason in listing["reasons"]:
                                st.markdown(f"- {reason}")

            except Exception as error:
                st.error(
                    "Something went wrong while finding "
                    "recommendations. Please check the terminal "
                    "for details."
                )
                st.exception(error)

st.divider()

st.caption(
    "Prototype powered by Python, Pandas, rule-based query parsing, "
    "and transparent ranking. Sample listings are synthetic data."
)
