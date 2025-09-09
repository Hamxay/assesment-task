import os
from dotenv import load_dotenv

load_dotenv()

# Lyzr Studio API Configuration
LYZR_API_KEY = "sk-default-I0SEUWVC3kE1VisOjzBnNVr2G3nph1oM"
LYZR_STUDIO_BASE_URL = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
USER_ID = "dev.hamza341@gmail.com"

# Agent Configuration with Studio IDs
AGENT_CONFIGS = {
    "experience_agent": {
        "name": "Experience Filter Agent",
        "description": "Specializes in evaluating candidates based on work experience, job history, and career progression",
        "agent_id": "68beb0a78a8eb0a43d847f3c",
        "session_id": "68beb0a78a8eb0a43d847f3c-bvm5biip669",
        "criteria": [
            "years_of_experience",
            "relevant_industry",
            "career_progression",
            "job_stability",
        ],
    },
    "skills_agent": {
        "name": "Skills Assessment Agent",
        "description": "Analyzes technical skills, certifications, and competencies",
        "agent_id": "68beb0d68a8eb0a43d847f40",
        "session_id": "68beb0d68a8eb0a43d847f40-ad83easriqw",
        "criteria": ["technical_skills", "certifications", "projects", "languages"],
    },
    "culture_agent": {
        "name": "Culture Fit Agent",
        "description": "Evaluates cultural alignment, soft skills, and team compatibility",
        "agent_id": "68beb2b9cc9c7b45bbcc39c0",
        "session_id": "68beb2b9cc9c7b45bbcc39c0-0d4oneo6nnb",
        "criteria": [
            "communication_style",
            "values_alignment",
            "teamwork",
            "adaptability",
        ],
    },
}

# UI Configuration
UI_CONFIG = {
    "page_title": "AI Talent Recruiter",
    "page_icon": "🎯",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Data Configuration
DATA_CONFIG = {
    "candidates_file": "Candidates Sheet.xlsx",
    "job_description_file": "job_description.txt",
}
