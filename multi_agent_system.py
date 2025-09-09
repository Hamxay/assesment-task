import streamlit as st
from typing import Dict, List, Any
from data_processor import DataProcessor
from agents import ExperienceAgent, SkillsAgent, CultureAgent
from config import DATA_CONFIG
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class MultiAgentSystem:
    def __init__(self):
        self.data_processor = DataProcessor(DATA_CONFIG["candidates_file"])
        self.experience_agent = ExperienceAgent()
        self.skills_agent = SkillsAgent()
        self.culture_agent = CultureAgent()
        self.job_description = None
        self.evaluations = []

    def load_data(self):
        """Load candidates and job description"""
        self.data_processor.load_candidates()
        from config import DATA_CONFIG

        self.job_description = self.data_processor.load_job_description(
            DATA_CONFIG["job_description_file"]
        )

    def evaluate_candidates(self, candidate_limit: int = 10) -> List[Dict]:
        """Evaluate candidates using all three agents"""
        candidates = self.data_processor.get_candidates_for_agent(
            "all", candidate_limit
        )

        if not candidates:
            return []
        evaluations = []

        with st.spinner("Evaluating candidates with AI agents..."):
            for i, candidate in enumerate(candidates):
                try:
                    if hasattr(st, "progress"):
                        st.progress((i + 1) / len(candidates))

                    # Evaluate with each agent
                    experience_eval = self.experience_agent.evaluate_candidate(
                        candidate, self.job_description
                    )
                    skills_eval = self.skills_agent.evaluate_candidate(
                        candidate, self.job_description
                    )
                    culture_eval = self.culture_agent.evaluate_candidate(
                        candidate, self.job_description
                    )

                    # Combine evaluations
                    combined_eval = {
                        "candidate": candidate,
                        "evaluations": {
                            "experience": experience_eval,
                            "skills": skills_eval,
                            "culture": culture_eval,
                        },
                        "overall_score": self._calculate_overall_score(
                            experience_eval, skills_eval, culture_eval
                        ),
                        "recommendations": self._combine_recommendations(
                            experience_eval, skills_eval, culture_eval
                        ),
                    }

                    evaluations.append(combined_eval)

                except Exception as e:
                    st.error(f"Error evaluating candidate {i+1}: {e}")
                    continue

        self.evaluations = evaluations
        return evaluations

    def _calculate_overall_score(
        self, experience_eval: Dict, skills_eval: Dict, culture_eval: Dict
    ) -> float:
        """Calculate overall score from all agents"""
        exp_score = experience_eval.get("score", 5)
        skills_score = skills_eval.get("score", 5)
        culture_score = culture_eval.get("score", 5)

        # Weighted average (can be adjusted based on requirements)
        weights = {"experience": 0.4, "skills": 0.4, "culture": 0.2}
        overall_score = (
            exp_score * weights["experience"]
            + skills_score * weights["skills"]
            + culture_score * weights["culture"]
        )

        return round(overall_score, 2)

    def _combine_recommendations(
        self, experience_eval: Dict, skills_eval: Dict, culture_eval: Dict
    ) -> List[str]:
        """Combine recommendations from all agents"""
        all_recommendations = []

        for eval_dict in [experience_eval, skills_eval, culture_eval]:
            recommendations = eval_dict.get("recommendations", [])
            if isinstance(recommendations, list):
                all_recommendations.extend(recommendations)

        # Remove duplicates and return top recommendations
        unique_recommendations = []
        for rec in all_recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)

        return unique_recommendations[:5]

    def get_top_candidates(self, limit: int = 5) -> List[Dict]:
        """Get top candidates based on overall score"""
        if not self.evaluations:
            return []

        sorted_evaluations = sorted(
            self.evaluations, key=lambda x: x["overall_score"], reverse=True
        )

        return sorted_evaluations[:limit]

    def create_score_comparison_chart(self) -> go.Figure:
        """Create a comparison chart of agent scores"""
        if not self.evaluations:
            return go.Figure()

        # Prepare data for plotting
        names = []
        experience_scores = []
        skills_scores = []
        culture_scores = []
        overall_scores = []

        for eval_data in self.evaluations[:10]:  # Top 10 for readability
            candidate = eval_data["candidate"]
            names.append(candidate.get("name", "Unknown"))

            evals = eval_data["evaluations"]
            experience_scores.append(evals["experience"].get("score", 5))
            skills_scores.append(evals["skills"].get("score", 5))
            culture_scores.append(evals["culture"].get("score", 5))
            overall_scores.append(eval_data["overall_score"])

        # Create the chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Experience",
                x=names,
                y=experience_scores,
                marker_color="lightblue",
            )
        )

        fig.add_trace(
            go.Bar(name="Skills", x=names, y=skills_scores, marker_color="lightgreen")
        )

        fig.add_trace(
            go.Bar(name="Culture", x=names, y=culture_scores, marker_color="lightcoral")
        )

        fig.add_trace(
            go.Scatter(
                name="Overall Score",
                x=names,
                y=overall_scores,
                mode="lines+markers",
                line=dict(color="red", width=3),
                marker=dict(size=8),
            )
        )

        fig.update_layout(
            title="Candidate Evaluation Scores by Agent",
            xaxis_title="Candidates",
            yaxis_title="Score (1-10)",
            barmode="group",
            height=500,
        )

        return fig

    def create_agent_performance_summary(self) -> Dict[str, Any]:
        """Create summary statistics for each agent"""
        if not self.evaluations:
            return {}

        summary = {
            "total_candidates": len(self.evaluations),
            "average_scores": {},
            "score_distributions": {},
            "top_performers": {},
        }

        # Calculate average scores
        exp_scores = [
            e["evaluations"]["experience"].get("score", 5) for e in self.evaluations
        ]
        skills_scores = [
            e["evaluations"]["skills"].get("score", 5) for e in self.evaluations
        ]
        culture_scores = [
            e["evaluations"]["culture"].get("score", 5) for e in self.evaluations
        ]
        overall_scores = [e["overall_score"] for e in self.evaluations]

        summary["average_scores"] = {
            "experience": round(sum(exp_scores) / len(exp_scores), 2),
            "skills": round(sum(skills_scores) / len(skills_scores), 2),
            "culture": round(sum(culture_scores) / len(culture_scores), 2),
            "overall": round(sum(overall_scores) / len(overall_scores), 2),
        }

        # Score distributions
        summary["score_distributions"] = {
            "experience": self._get_score_distribution(exp_scores),
            "skills": self._get_score_distribution(skills_scores),
            "culture": self._get_score_distribution(culture_scores),
            "overall": self._get_score_distribution(overall_scores),
        }

        return summary

    def _get_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Get distribution of scores"""
        distribution = {
            "excellent": len([s for s in scores if s >= 8]),
            "good": len([s for s in scores if 6 <= s < 8]),
            "average": len([s for s in scores if 4 <= s < 6]),
            "below_average": len([s for s in scores if s < 4]),
        }
        return distribution

    def export_results(self, filename: str = "evaluation_results.csv"):
        """Export evaluation results to CSV"""
        if not self.evaluations:
            return None

        export_data = []
        for eval_data in self.evaluations:
            candidate = eval_data["candidate"]
            evals = eval_data["evaluations"]

            row = {
                "Name": candidate.get("name", "Unknown"),
                "Headline": candidate.get("headline", ""),
                "Location": candidate.get("location", ""),
                "Experience_Score": evals["experience"].get("score", 5),
                "Skills_Score": evals["skills"].get("score", 5),
                "Culture_Score": evals["culture"].get("score", 5),
                "Overall_Score": eval_data["overall_score"],
                "Experience_Years": candidate.get("total_experience_years", 0),
                "Skill_Count": candidate.get("skill_count", 0),
                "Top_Recommendations": "; ".join(eval_data["recommendations"][:3]),
            }
            export_data.append(row)

        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False)
        return filename
