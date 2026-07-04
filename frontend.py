import streamlit as st
from datetime import datetime

# Your LangGraph App
from main import app
from langchain_core.messages import HumanMessage

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("🤖 Multi-Agent AI")

    st.divider()

    thread_id = st.text_input(
        "Session ID",
        value="user_001"
    )

    st.selectbox(
        "LLM Model",
        [
            "Llama 3.3 70B",
            "GPT-4o",
            "Claude Sonnet",
            "Gemini 2.5 Pro"
        ]
    )

    st.divider()

    st.markdown("### Agents")

    st.success("✓ Flight Agent")
    st.success("✓ Hotel Agent")
    st.success("✓ Itinerary Agent")
    st.success("✓ Planner Agent")

    st.divider()

    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# -----------------------------
# Header
# -----------------------------
st.title("🌍 AI Travel Planner")

st.caption(
    "Plan complete trips using multiple AI agents powered by LangGraph."
)

st.divider()

# -----------------------------
# Input
# -----------------------------
query = st.text_area(
    "Describe your trip",
    height=140,
    placeholder="Example: Plan a 7-day Japan trip under ₹2 Lakhs."
)

col1, col2 = st.columns([1,4])

with col1:
    generate = st.button(
        "Generate",
        use_container_width=True
    )

# -----------------------------
# Generate
# -----------------------------
if generate:

    if query.strip() == "":
        st.warning("Please enter your travel request.")
        st.stop()

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    flight_result = ""
    hotel_result = ""
    itinerary = ""
    final_answer = ""
    llm_calls = 0

    progress = st.progress(0)

    status = st.empty()

    with st.spinner("Running AI Agents..."):

        for chunk in app.stream(
            {
                "messages": [HumanMessage(content=query)],
                "user_query": query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):

            for node, update in chunk.items():

                if node == "flight_agent":
                    status.info("✈ Flight Agent Finished")
                    flight_result = update.get(
                        "flight_results",
                        ""
                    )
                    progress.progress(25)

                elif node == "hotel_agent":
                    status.info("🏨 Hotel Agent Finished")
                    hotel_result = update.get(
                        "hotel_results",
                        ""
                    )
                    progress.progress(50)

                elif node == "itinerary_agent":
                    status.info("🗓 Itinerary Agent Finished")
                    itinerary = update.get(
                        "itinerary",
                        ""
                    )
                    progress.progress(75)

                elif node == "final_agent":

                    msgs = update.get("messages", [])

                    if msgs:
                        final_answer = msgs[-1].content

                    progress.progress(100)
                    status.success("✅ Planning Complete")

                llm_calls = update.get(
                    "llm_calls",
                    llm_calls
                )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("Agents", "4")

    c2.metric("LLM Calls", llm_calls)

    c3.metric("Status", "Success")

    st.divider()

    tabs = st.tabs(
        [
            "✈ Flights",
            "🏨 Hotels",
            "🗓 Itinerary",
            "🧠 Final Plan"
        ]
    )

    with tabs[0]:
        if flight_result:
            st.markdown(flight_result)
        else:
            st.info("No flight information.")

    with tabs[1]:
        if hotel_result:
            st.markdown(hotel_result)
        else:
            st.info("No hotel information.")

    with tabs[2]:
        if itinerary:
            st.markdown(itinerary)
        else:
            st.info("No itinerary generated.")

    with tabs[3]:
        st.markdown(final_answer)

    markdown = f"""
# AI Travel Plan

**Generated:** {datetime.now()}

## User Query

{query}

---

## Flights

{flight_result}

---

## Hotels

{hotel_result}

---

## Itinerary

{itinerary}

---

## Final Plan

{final_answer}

"""

    st.download_button(
        "📥 Download Markdown",
        markdown,
        file_name="travel_plan.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.session_state.history.append(
        {
            "query": query,
            "time": datetime.now().strftime("%H:%M")
        }
    )

# -----------------------------
# History
# -----------------------------
if st.session_state.history:

    st.divider()

    st.subheader("Recent Requests")

    for item in reversed(st.session_state.history[-5:]):
        st.write(f"🕒 {item['time']} — {item['query']}")