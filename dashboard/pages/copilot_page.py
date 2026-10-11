"""AI Operations Copilot Page for Medical Operations Intelligence."""
import streamlit as st
from copilot.query_engine import OperationalQueryEngine
from copilot.insights_engine import InsightsEngine


def render_copilot(db, filters):
    st.title("💬 AI Operations Copilot & Executive Assistant")
    st.markdown("Ask natural language questions about hospital operations, bed capacity, revenue, claim denials, or request automated executive briefings.")

    facility_id = filters.get("facility")

    try:
        query_engine = OperationalQueryEngine(db)
        insights_engine = InsightsEngine(db)

        # Tabs for Copilot functions
        tab_qa, tab_insights = st.tabs(["💬 Natural Language Q&A", "📄 Automated Executive Briefings"])

        with tab_qa:
            st.subheader("Ask the Operational Assistant")
            
            # Quick Question Presets
            st.markdown("**Sample Questions:**")
            col_q1, col_q2, col_q3 = st.columns(3)
            with col_q1:
                q1 = "What is the average waiting time in Emergency?"
                if st.button(q1):
                    st.session_state["copilot_query"] = q1
            with col_q2:
                q2 = "Show total revenue and claim denial rate"
                if st.button(q2):
                    st.session_state["copilot_query"] = q2
            with col_q3:
                q3 = "Which doctor handled the most appointments?"
                if st.button(q3):
                    st.session_state["copilot_query"] = q3

            user_query = st.text_input(
                "Enter your question:",
                value=st.session_state.get("copilot_query", ""),
                placeholder="e.g. How many beds are occupied at Central Hospital?"
            )

            if st.button("🚀 Process Query", type="primary"):
                if user_query:
                    with st.spinner("Analyzing MongoDB collections & generating operational intelligence..."):
                        response = query_engine.process_query(user_query, facility_id=facility_id)
                        
                        st.markdown("### 🤖 Copilot Response")
                        st.write(response.get("answer", "No answer could be generated."))
                        
                        if "data" in response and response["data"]:
                            st.markdown("#### 📊 Retrieved Data")
                            st.json(response["data"])
                else:
                    st.warning("Please enter a question.")

        with tab_insights:
            st.subheader("Automated Daily Executive Insights")
            if st.button("✨ Generate Daily Executive Briefing", type="primary"):
                with st.spinner("Compiling operational metrics, predictions, and anomaly logs..."):
                    briefing = insights_engine.generate_daily_briefing(facility_id=facility_id)
                    st.markdown("### 📋 Executive Briefing")
                    st.write(briefing.get("briefing", "Briefing generated."))
                    
                    st.markdown("#### 💡 Strategic Recommendations")
                    for rec in briefing.get("recommendations", []):
                        st.info(f"• {rec}")

    except Exception as e:
        st.error(f"Error loading Copilot Assistant: {e}")
