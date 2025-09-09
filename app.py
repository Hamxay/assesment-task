import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from multi_agent_system import MultiAgentSystem
from config import UI_CONFIG, DATA_CONFIG
import json
import os

# Page configuration
st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["initial_sidebar_state"],
)

# Custom CSS for better UI
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .agent-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "multi_agent_system" not in st.session_state:
    st.session_state.multi_agent_system = MultiAgentSystem()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "evaluations_completed" not in st.session_state:
    st.session_state.evaluations_completed = False
if "current_step" not in st.session_state:
    st.session_state.current_step = "setup"


def main():
    # Header
    st.markdown(
        '<h1 class="main-header">🎯 AI Talent Recruiter</h1>', unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("🤖 AI Agents")
        st.markdown(
            """
        **Experience Agent**: Evaluates work experience and career progression
        **Skills Agent**: Assesses technical skills and certifications  
        **Culture Agent**: Analyzes cultural fit and soft skills
        """
        )

        st.header("📊 Quick Stats")
        if st.session_state.evaluations_completed:
            summary = (
                st.session_state.multi_agent_system.create_agent_performance_summary()
            )
            if summary:
                st.metric("Total Candidates", summary["total_candidates"])
                st.metric("Avg Overall Score", summary["average_scores"]["overall"])

        st.header("⚙️ Settings")
        candidate_limit = st.slider("Number of candidates to evaluate", 5, 50, 10)
        st.session_state.candidate_limit = candidate_limit

        if st.button("🔄 Reset System"):
            st.session_state.multi_agent_system = MultiAgentSystem()
            st.session_state.chat_history = []
            st.session_state.evaluations_completed = False
            st.session_state.current_step = "setup"
            st.rerun()

    # Main content area
    if st.session_state.current_step == "setup":
        setup_phase()
    elif st.session_state.current_step == "evaluation":
        evaluation_phase()
    elif st.session_state.current_step == "results":
        results_phase()
    elif st.session_state.current_step == "chat":
        chat_phase()


def setup_phase():
    st.header("🚀 Setup Phase")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Enter or modify the job description:",
            value=st.session_state.multi_agent_system.data_processor.load_job_description(
                DATA_CONFIG["job_description_file"]
            ),
            height=300,
        )

        if st.button("💾 Save Job Description"):
            # Save job description to file
            try:
                with open("job_description.txt", "w", encoding="utf-8") as f:
                    f.write(job_description)
                st.success("Job description saved!")
            except Exception as e:
                st.error(f"Error saving job description: {e}")

    with col2:
        st.subheader("📊 Candidate Data")
        if os.path.exists(DATA_CONFIG["candidates_file"]):
            df = pd.read_excel(DATA_CONFIG["candidates_file"])
            st.metric("Total Candidates", len(df))
            st.metric("Available Fields", len(df.columns))

            st.subheader("📈 Data Preview")
            st.dataframe(df.head(5))
        else:
            st.error("Candidates file not found!")

    st.markdown("---")

    if st.button("🎯 Start Evaluation Process"):
        st.session_state.multi_agent_system.load_data()
        st.session_state.current_step = "evaluation"
        st.rerun()


def evaluation_phase():
    st.header("🔍 Evaluation Phase")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🤖 AI Agent Evaluation")

        if not st.session_state.evaluations_completed:
            if st.button("🚀 Start AI Evaluation"):
                with st.spinner("Loading data..."):
                    st.session_state.multi_agent_system.load_data()

                # Get candidate limit from sidebar
                candidate_limit = st.session_state.get("candidate_limit", 10)

                # Run evaluation
                evaluations = st.session_state.multi_agent_system.evaluate_candidates(
                    candidate_limit
                )
                st.session_state.evaluations_completed = True
                st.session_state.current_step = "results"
                st.rerun()
        else:
            st.success("✅ Evaluation completed!")
            if st.button("📊 View Results"):
                st.session_state.current_step = "results"
                st.rerun()

    with col2:
        st.subheader("🎯 Agent Status")

        agents = [
            ("Experience Agent", "🔍", "Analyzing work history..."),
            ("Skills Agent", "⚡", "Assessing technical skills..."),
            ("Culture Agent", "🤝", "Evaluating cultural fit..."),
        ]

        for name, icon, status in agents:
            st.markdown(
                f"""
            <div class="agent-card">
                <h4>{icon} {name}</h4>
                <p>{status}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


def results_phase():
    st.header("📊 Results & Analysis")

    if not st.session_state.evaluations_completed:
        st.warning("Please complete evaluation first!")
        return

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Overview", "👥 Top Candidates", "🤖 Agent Analysis", "💬 Interactive Chat"]
    )

    with tab1:
        show_overview()

    with tab2:
        show_top_candidates()

    with tab3:
        show_agent_analysis()

    with tab4:
        if st.button("💬 Start Interactive Chat"):
            st.session_state.current_step = "chat"
            st.rerun()


def show_overview():
    st.subheader("📈 Evaluation Overview")

    # Summary statistics
    summary = st.session_state.multi_agent_system.create_agent_performance_summary()

    if summary:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Candidates", summary["total_candidates"])
        with col2:
            st.metric("Avg Experience Score", summary["average_scores"]["experience"])
        with col3:
            st.metric("Avg Skills Score", summary["average_scores"]["skills"])
        with col4:
            st.metric("Avg Culture Score", summary["average_scores"]["culture"])

        # Score comparison chart
        st.subheader("📊 Score Comparison")
        fig = st.session_state.multi_agent_system.create_score_comparison_chart()
        st.plotly_chart(fig, use_container_width=True)

        # Score distributions
        st.subheader("📋 Score Distributions")
        distributions = summary["score_distributions"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Excellent (8-10)", distributions["overall"]["excellent"])
        with col2:
            st.metric("Good (6-8)", distributions["overall"]["good"])
        with col3:
            st.metric("Average (4-6)", distributions["overall"]["average"])
        with col4:
            st.metric("Below Average (<4)", distributions["overall"]["below_average"])


def show_top_candidates():
    st.subheader("👥 Top Candidates")

    top_candidates = st.session_state.multi_agent_system.get_top_candidates(10)

    for i, candidate_data in enumerate(top_candidates):
        candidate = candidate_data["candidate"]
        evaluations = candidate_data["evaluations"]
        overall_score = candidate_data["overall_score"]

        # Determine score color
        if overall_score >= 8:
            score_class = "score-high"
        elif overall_score >= 6:
            score_class = "score-medium"
        else:
            score_class = "score-low"

        with st.expander(
            f"#{i+1} {candidate.get('name', 'Unknown')} - Score: {overall_score}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Headline:** {candidate.get('headline', 'N/A')}")
                st.write(f"**Location:** {candidate.get('location', 'N/A')}")
                st.write(
                    f"**Experience:** {candidate.get('total_experience_years', 0)} years"
                )
                st.write(f"**Skills:** {candidate.get('skill_count', 0)} skills")

            with col2:
                st.write(
                    f"**Experience Score:** {evaluations['experience'].get('score', 5)}"
                )
                st.write(f"**Skills Score:** {evaluations['skills'].get('score', 5)}")
                st.write(f"**Culture Score:** {evaluations['culture'].get('score', 5)}")
                st.write(
                    f"**Overall Score:** <span class='{score_class}'>{overall_score}</span>",
                    unsafe_allow_html=True,
                )

            st.subheader("💡 Recommendations")
            for rec in candidate_data["recommendations"][:3]:
                st.write(f"• {rec}")


def show_agent_analysis():
    st.subheader("🤖 Agent Performance Analysis")

    summary = st.session_state.multi_agent_system.create_agent_performance_summary()

    if summary:
        # Agent comparison
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Average Scores by Agent")
            avg_scores = summary["average_scores"]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=["Experience", "Skills", "Culture", "Overall"],
                        y=[
                            avg_scores["experience"],
                            avg_scores["skills"],
                            avg_scores["culture"],
                            avg_scores["overall"],
                        ],
                        marker_color=["lightblue", "lightgreen", "lightcoral", "red"],
                    )
                ]
            )
            fig.update_layout(title="Agent Performance Comparison")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📋 Score Distributions")
            distributions = summary["score_distributions"]

            for agent_type in ["experience", "skills", "culture"]:
                dist = distributions[agent_type]
                st.write(f"**{agent_type.title()} Agent:**")
                st.write(
                    f"Excellent: {dist['excellent']}, Good: {dist['good']}, Average: {dist['average']}, Below: {dist['below_average']}"
                )


def chat_phase():
    st.header("💬 Interactive Chat with AI Agents")

    st.markdown(
        """
    **Chat with our AI agents to get detailed insights about candidates, ask questions, 
    and receive personalized recommendations for your hiring process.**
    """
    )

    # Chat interface
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="chat-message agent-message">
                    <strong>AI Agent:</strong> {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Chat input
    user_input = st.text_input("Ask a question about candidates or hiring process:")

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("💬 Send"):
            if user_input:
                process_chat_message(user_input)
                st.rerun()

    with col2:
        if st.button("🔙 Back to Results"):
            st.session_state.current_step = "results"
            st.rerun()


def process_chat_message(message: str):
    """Process user chat message and generate AI response"""
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": message})

    # Generate AI response based on message content
    response = generate_ai_response(message)

    # Add AI response to history
    st.session_state.chat_history.append({"role": "assistant", "content": response})


def generate_ai_response(message: str) -> str:
    """Generate AI response based on user message"""
    message_lower = message.lower()

    if "top candidate" in message_lower or "best candidate" in message_lower:
        top_candidates = st.session_state.multi_agent_system.get_top_candidates(3)
        response = "Here are the top 3 candidates:\n\n"
        for i, candidate_data in enumerate(top_candidates):
            candidate = candidate_data["candidate"]
            score = candidate_data["overall_score"]
            response += (
                f"{i+1}. **{candidate.get('name', 'Unknown')}** - Score: {score}\n"
            )
            response += f"   {candidate.get('headline', 'N/A')}\n\n"
        return response

    elif "experience" in message_lower:
        return """I can help you analyze candidate experience! Here are some insights:
        
        • **Experience Agent** evaluates work history, career progression, and industry relevance
        • **Key factors**: Years of experience, job stability, career growth
        • **Recommendations**: Look for candidates with relevant industry experience and steady career progression
        
        Would you like me to show you candidates with specific experience criteria?"""

    elif "skills" in message_lower:
        return """Let me tell you about skills evaluation:
        
        • **Skills Agent** assesses technical competencies, certifications, and project experience
        • **Key factors**: Technical skills match, certifications, hands-on projects
        • **Recommendations**: Focus on candidates with relevant technical skills and continuous learning
        
        Would you like to see candidates with specific skill requirements?"""

    elif "culture" in message_lower or "fit" in message_lower:
        return """Here's what I know about cultural fit:
        
        • **Culture Agent** evaluates communication style, teamwork, and values alignment
        • **Key factors**: Communication patterns, volunteer work, language skills
        • **Recommendations**: Look for candidates who demonstrate collaboration and cultural awareness
        
        Would you like me to analyze cultural fit for specific candidates?"""

    elif "recommend" in message_lower or "suggestion" in message_lower:
        return """Based on the evaluation results, here are my recommendations:
        
        1. **Shortlist top 5-10 candidates** for initial screening
        2. **Focus on candidates with balanced scores** across all three dimensions
        3. **Consider experience requirements** - prioritize candidates with relevant industry experience
        4. **Look for skill gaps** that can be addressed through training
        5. **Assess cultural fit** through behavioral interviews
        
        Would you like me to help you create a specific shortlist?"""

    else:
        return """I'm here to help you with your hiring process! I can:
        
        • Show you top candidates
        • Explain evaluation criteria
        • Provide hiring recommendations
        • Analyze specific candidate profiles
        • Help with interview planning
        
        Just ask me anything about the candidates or hiring process!"""


if __name__ == "__main__":
    main()
