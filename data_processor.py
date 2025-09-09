import pandas as pd
import json
import ast
from typing import Dict, List, Any


class DataProcessor:
    def __init__(self, candidates_file: str):
        self.candidates_file = candidates_file
        self.candidates_df = None
        self.job_description = None

    def load_candidates(self) -> pd.DataFrame:
        """Load and preprocess candidates data"""
        try:
            self.candidates_df = pd.read_excel(self.candidates_file)
            return self.candidates_df
        except Exception as e:
            return pd.DataFrame()

    def load_job_description(self, job_desc_file: str = None) -> str:
        """Load job description from file or create default"""
        try:
            if job_desc_file and os.path.exists(job_desc_file):
                with open(job_desc_file, "r", encoding="utf-8") as f:
                    self.job_description = f.read().strip()
            else:
                # Fallback to empty string so caller UI can populate
                self.job_description = ""
        except Exception:
            self.job_description = ""
        return self.job_description

    def parse_json_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse JSON fields in the dataframe"""
        json_columns = [
            "experience",
            "education",
            "skills",
            "topSkills",
            "currentPosition",
        ]

        for col in json_columns:
            if col in df.columns:
                df[f"{col}_parsed"] = df[col].apply(self._safe_parse_json)

        return df

    def _safe_parse_json(self, value):
        """Safely parse JSON values"""
        if pd.isna(value) or value == "":
            return []

        try:
            if isinstance(value, str):
                return json.loads(value)
            elif isinstance(value, list):
                return value
            else:
                return []
        except (json.JSONDecodeError, ValueError):
            try:
                return ast.literal_eval(value)
            except:
                return []

    def extract_candidate_features(self, candidate: Dict) -> Dict[str, Any]:
        """Extract relevant features from candidate data"""
        features = {
            "name": f"{candidate.get('firstName', '')} {candidate.get('lastName', '')}",
            "headline": candidate.get("headline", ""),
            "location": candidate.get("location", ""),
            "connections_count": candidate.get("connectionsCount", 0),
            "follower_count": candidate.get("followerCount", 0),
            "verified": candidate.get("verified", False),
            "about": candidate.get("about", ""),
            "experience": self._safe_parse_json(candidate.get("experience", [])),
            "skills": self._safe_parse_json(candidate.get("skills", [])),
            "top_skills": self._safe_parse_json(candidate.get("topSkills", [])),
            "education": self._safe_parse_json(candidate.get("education", [])),
            "certifications": self._safe_parse_json(
                candidate.get("certifications", [])
            ),
            "projects": self._safe_parse_json(candidate.get("projects", [])),
            "languages": self._safe_parse_json(candidate.get("languages", [])),
        }

        # Calculate derived features
        features["total_experience_years"] = self._calculate_experience_years(
            features["experience"]
        )
        features["skill_count"] = (
            len(features["skills"]) if isinstance(features["skills"], list) else 0
        )
        features["education_level"] = self._get_highest_education(features["education"])

        return features

    def _calculate_experience_years(self, experience: List) -> int:
        """Calculate total years of experience"""
        if not experience:
            return 0

        total_years = 0
        for exp in experience:
            if isinstance(exp, dict):
                # Extract duration from experience
                duration = exp.get("duration", "")
                if duration:
                    # Simple parsing - could be enhanced
                    years = self._extract_years_from_duration(duration)
                    total_years += years

        return total_years

    def _extract_years_from_duration(self, duration: str) -> int:
        """Extract years from duration string"""
        try:
            if "year" in duration.lower():
                # Extract number before 'year'
                import re

                match = re.search(r"(\d+)", duration)
                if match:
                    return int(match.group(1))
        except:
            pass
        return 0

    def _get_highest_education(self, education: List) -> str:
        """Get highest education level"""
        if not education:
            return "Unknown"

        education_levels = {
            "phd": 5,
            "doctorate": 5,
            "master": 4,
            "bachelor": 3,
            "associate": 2,
            "high school": 1,
        }

        highest_level = 0
        highest_degree = "Unknown"

        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree", "")
                if degree is None:
                    continue
                degree = str(degree).lower()
                for level_name, level_value in education_levels.items():
                    if level_name in degree and level_value > highest_level:
                        highest_level = level_value
                        highest_degree = edu.get("degree", "Unknown")

        return highest_degree

    def get_candidates_for_agent(self, agent_type: str, limit: int = 10) -> List[Dict]:
        """Get candidates filtered for specific agent type"""
        if self.candidates_df is None:
            self.load_candidates()

        # Parse JSON fields
        df = self.parse_json_fields(self.candidates_df.copy())

        # Convert to list of dictionaries
        candidates = []
        for _, row in df.head(limit).iterrows():
            candidate = self.extract_candidate_features(row.to_dict())
            candidates.append(candidate)

        return candidates


import os
