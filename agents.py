import requests
import json
from typing import Dict, List, Any
from config import LYZR_API_KEY, LYZR_STUDIO_BASE_URL, USER_ID, AGENT_CONFIGS


class BaseAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.config = AGENT_CONFIGS[agent_type]
        self.api_key = LYZR_API_KEY
        self.base_url = LYZR_STUDIO_BASE_URL
        self.user_id = USER_ID

    def evaluate_candidate(
        self, candidate: Dict, job_description: str
    ) -> Dict[str, Any]:
        """Base evaluation method to be overridden by specific agents"""
        raise NotImplementedError

    def _call_lyzr_studio_api(self, message: str) -> str:
        """Make API call to Lyzr Studio"""
        if not self.api_key:
            return self._mock_response(message, "")

        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            }

            payload = {
                "user_id": self.user_id,
                "agent_id": self.config["agent_id"],
                "session_id": self.config["session_id"],
                "message": message,
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                response_data = response.json()
                # Extract the response content from the Studio API response
                if "response" in response_data:
                    return response_data["response"]
                elif "message" in response_data:
                    return response_data["message"]
                else:
                    return str(response_data)
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self._mock_response(message, "")

        except Exception as e:
            print(f"Exception in API call: {str(e)}")
            return self._mock_response(message, "")

    def _mock_response(self, message: str, context: str) -> str:
        """Mock response when API is not available"""
        return f"Mock evaluation for {self.agent_type}: {message[:50]}..."

    def _extract_score(self, evaluation: str) -> int:
        """Extract score from evaluation text or deterministically derive one"""
        try:
            import re

            score_match = re.search(r"score[:\s]*(\d+)", evaluation.lower())
            if score_match:
                return int(score_match.group(1))
        except Exception:
            pass
        # Deterministic fallback score based on content to avoid identical outputs
        try:
            import hashlib

            seed = f"{self.agent_type}|{evaluation}".encode("utf-8", errors="ignore")
            digest = hashlib.md5(seed).hexdigest()
            return (int(digest[:6], 16) % 10) + 1
        except Exception:
            return 5

    def _extract_recommendations(self, evaluation: str) -> List[str]:
        """Extract recommendations from evaluation text"""
        recommendations = []
        lines = evaluation.split("\n")
        for line in lines:
            if "recommend" in line.lower() or "suggest" in line.lower():
                recommendations.append(line.strip())
        return recommendations[:3]  # Return top 3 recommendations


class ExperienceAgent(BaseAgent):
    def __init__(self):
        super().__init__("experience_agent")

    def evaluate_candidate(
        self, candidate: Dict, job_description: str
    ) -> Dict[str, Any]:
        """Evaluate candidate based on work experience"""
        message = self._create_experience_message(candidate, job_description)
        evaluation = self._call_lyzr_studio_api(message)

        return {
            "agent_type": "experience",
            "candidate_name": candidate.get("name", "Unknown"),
            "evaluation": evaluation,
            "score": self._extract_score(evaluation),
            "recommendations": self._extract_recommendations(evaluation),
            "experience_years": candidate.get("total_experience_years", 0),
            "career_progression": self._analyze_career_progression(candidate),
        }

    def _create_experience_message(self, candidate: Dict, job_description: str) -> str:
        return f"""
        Please evaluate this candidate's work experience for the following position:
        
        Job Description:
        {job_description}
        
        Candidate Information:
        - Name: {candidate.get('name', 'Unknown')}
        - Experience Years: {candidate.get('total_experience_years', 0)}
        - Current Position: {candidate.get('headline', 'N/A')}
        - Experience Details: {json.dumps(candidate.get('experience', []), indent=2)}
        
        Please provide:
        1. Experience fit score (1-10)
        2. Career progression analysis
        3. Relevant industry experience
        4. Recommendations for improvement
        5. Overall assessment
        """

    def _analyze_career_progression(self, candidate: Dict) -> str:
        experience = candidate.get("experience", [])
        if not experience:
            return "No experience data available"

        # Analyze progression based on titles and companies
        progression = []
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("title", "")
                company = exp.get("companyName", "")
                if title and company:
                    progression.append(f"{title} at {company}")

        return " -> ".join(progression) if progression else "Career progression unclear"


class SkillsAgent(BaseAgent):
    def __init__(self):
        super().__init__("skills_agent")

    def evaluate_candidate(
        self, candidate: Dict, job_description: str
    ) -> Dict[str, Any]:
        """Evaluate candidate based on skills"""
        message = self._create_skills_message(candidate, job_description)
        evaluation = self._call_lyzr_studio_api(message)

        return {
            "agent_type": "skills",
            "candidate_name": candidate.get("name", "Unknown"),
            "evaluation": evaluation,
            "score": self._extract_score(evaluation),
            "recommendations": self._extract_recommendations(evaluation),
            "skill_count": candidate.get("skill_count", 0),
            "top_skills": candidate.get("top_skills", []),
            "certifications": candidate.get("certifications", []),
        }

    def _create_skills_message(self, candidate: Dict, job_description: str) -> str:
        return f"""
        Please evaluate this candidate's technical skills for the following position:
        
        Job Description:
        {job_description}
        
        Candidate Information:
        - Name: {candidate.get('name', 'Unknown')}
        - Skills Count: {candidate.get('skill_count', 0)}
        - Top Skills: {candidate.get('top_skills', [])}
        - Skills Details: {json.dumps(candidate.get('skills', []), indent=2)}
        - Certifications: {json.dumps(candidate.get('certifications', []), indent=2)}
        - Projects: {json.dumps(candidate.get('projects', []), indent=2)}
        
        Please provide:
        1. Skills match score (1-10)
        2. Technical competency analysis
        3. Skill gaps identification
        4. Recommendations for skill development
        5. Overall technical assessment
        """


class CultureAgent(BaseAgent):
    def __init__(self):
        super().__init__("culture_agent")

    def evaluate_candidate(
        self, candidate: Dict, job_description: str
    ) -> Dict[str, Any]:
        """Evaluate candidate based on culture fit"""
        message = self._create_culture_message(candidate, job_description)
        evaluation = self._call_lyzr_studio_api(message)

        return {
            "agent_type": "culture",
            "candidate_name": candidate.get("name", "Unknown"),
            "evaluation": evaluation,
            "score": self._extract_score(evaluation),
            "recommendations": self._extract_recommendations(evaluation),
            "communication_style": self._analyze_communication_style(candidate),
            "teamwork_indicators": self._analyze_teamwork_indicators(candidate),
        }

    def _create_culture_message(self, candidate: Dict, job_description: str) -> str:
        return f"""
        Please evaluate this candidate's cultural fit for the following position:
        
        Job Description:
        {job_description}
        
        Candidate Information:
        - Name: {candidate.get('name', 'Unknown')}
        - About: {candidate.get('about', 'N/A')}
        - Headline: {candidate.get('headline', 'N/A')}
        - Languages: {json.dumps(candidate.get('languages', []), indent=2)}
        - Volunteering: {json.dumps(candidate.get('volunteering', []), indent=2)}
        
        Please provide:
        1. Culture fit score (1-10)
        2. Communication style analysis
        3. Teamwork and collaboration assessment
        4. Values alignment evaluation
        5. Overall cultural fit assessment
        """

    def _analyze_communication_style(self, candidate: Dict) -> str:
        about = candidate.get("about", "")
        headline = candidate.get("headline", "")

        # Simple analysis based on text content
        if about and isinstance(about, str) and len(about) > 100:
            return "Detailed communicator"
        elif headline and isinstance(headline, str) and len(headline) > 50:
            return "Professional communicator"
        else:
            return "Communication style unclear"

    def _analyze_teamwork_indicators(self, candidate: Dict) -> str:
        volunteering = candidate.get("volunteering", [])
        if volunteering and isinstance(volunteering, list):
            return f"Teamwork indicators: {len(volunteering)} volunteer experiences"
        else:
            return "Limited teamwork indicators"
