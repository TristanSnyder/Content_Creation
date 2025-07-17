"""Brand Consistency Agent for voice analysis and optimization."""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from src.data.models import ContentType, Platform
from src.rag.chains import EcoTechRAGChains
from src.rag.mock_llm import MockLLMClient
from src.vector_db.chroma_client import ChromaVectorDB
from src.data.demo_data import get_brand_guidelines

logger = logging.getLogger(__name__)


class BrandConsistencyAgent:
    """Specialized agent for brand voice analysis and consistency optimization."""
    
    def __init__(
        self, 
        rag_chains: EcoTechRAGChains,
        vector_db: ChromaVectorDB,
        mock_llm: MockLLMClient
    ):
        """Initialize brand consistency agent.
        
        Args:
            rag_chains: EcoTech RAG chains for analysis
            vector_db: Vector database for brand voice examples
            mock_llm: Mock LLM for analysis
        """
        self.rag_chains = rag_chains
        self.vector_db = vector_db
        self.llm = mock_llm
        self.brand_guidelines = get_brand_guidelines()
        
        # Brand voice patterns and scoring
        self.voice_patterns = self._load_voice_patterns()
        self.scoring_weights = self._load_scoring_weights()
        
        logger.info("BrandConsistencyAgent initialized with voice patterns and guidelines")
    
    def analyze_brand_voice(self, content: str) -> Dict[str, Any]:
        """Analyze content for comprehensive brand voice consistency.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detailed brand voice analysis
        """
        try:
            logger.info("Performing comprehensive brand voice analysis")
            
            # Use vector database for embedding-based analysis
            vector_analysis = self.vector_db.brand_voice_analysis(
                content=content,
                collection_name="brand_voice_examples"
            )
            
            # Perform rule-based analysis
            rule_based_analysis = self._analyze_voice_rules(content)
            
            # Combine analyses
            combined_analysis = self._combine_analyses(vector_analysis, rule_based_analysis)
            
            # Generate detailed recommendations
            recommendations = self._generate_recommendations(combined_analysis, content)
            
            # Create comprehensive analysis result
            analysis_result = {
                "content_analyzed": content[:200] + "..." if len(content) > 200 else content,
                "overall_score": combined_analysis["overall_score"],
                "confidence": combined_analysis["confidence"],
                "dimension_scores": combined_analysis["dimension_scores"],
                "strengths": combined_analysis["strengths"],
                "improvement_areas": combined_analysis["improvement_areas"],
                "recommendations": recommendations,
                "similar_examples": vector_analysis.get("similar_examples", []),
                "analysis_timestamp": datetime.now().isoformat(),
                "voice_pattern_matches": rule_based_analysis["pattern_matches"]
            }
            
            logger.info(f"Brand voice analysis completed with score: {combined_analysis['overall_score']:.3f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Brand voice analysis failed: {e}")
            return {
                "content_analyzed": content[:100] + "...",
                "overall_score": 0.0,
                "confidence": 0.0,
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def score_consistency(
        self, 
        content: str, 
        reference_content: List[str]
    ) -> float:
        """Score content consistency against reference examples.
        
        Args:
            content: Content to score
            reference_content: Reference content for comparison
            
        Returns:
            Consistency score (0-1)
        """
        try:
            # Analyze target content
            target_analysis = self.analyze_brand_voice(content)
            target_score = target_analysis.get("overall_score", 0.0)
            
            # Analyze reference content
            reference_scores = []
            for ref_content in reference_content:
                ref_analysis = self.analyze_brand_voice(ref_content)
                reference_scores.append(ref_analysis.get("overall_score", 0.0))
            
            if not reference_scores:
                return target_score
            
            # Calculate consistency as inverse of variance from reference average
            ref_avg = sum(reference_scores) / len(reference_scores)
            consistency = 1.0 - abs(target_score - ref_avg)
            
            return max(0.0, min(1.0, consistency))
            
        except Exception as e:
            logger.error(f"Consistency scoring failed: {e}")
            return 0.0
    
    def optimize_voice_alignment(
        self, 
        content: str,
        target_score: float = 0.9
    ) -> Dict[str, Any]:
        """Provide specific recommendations to improve brand voice alignment.
        
        Args:
            content: Content to optimize
            target_score: Target brand voice score
            
        Returns:
            Optimization recommendations
        """
        try:
            # Analyze current state
            current_analysis = self.analyze_brand_voice(content)
            current_score = current_analysis.get("overall_score", 0.0)
            
            if current_score >= target_score:
                return {
                    "optimization_needed": False,
                    "current_score": current_score,
                    "target_score": target_score,
                    "message": "Content already meets target brand voice score"
                }
            
            # Identify specific optimization areas
            dimension_scores = current_analysis.get("dimension_scores", {})
            improvement_areas = current_analysis.get("improvement_areas", [])
            
            # Generate prioritized recommendations
            recommendations = self._generate_optimization_recommendations(
                content, current_score, target_score, dimension_scores, improvement_areas
            )
            
            return {
                "optimization_needed": True,
                "current_score": current_score,
                "target_score": target_score,
                "score_gap": target_score - current_score,
                "priority_areas": list(dimension_scores.keys())[:3],
                "recommendations": recommendations,
                "estimated_effort": self._estimate_optimization_effort(current_score, target_score),
                "expected_impact": self._estimate_impact(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Voice alignment optimization failed: {e}")
            return {
                "optimization_needed": True,
                "error": str(e),
                "current_score": 0.0,
                "target_score": target_score
            }
    
    def track_voice_drift(
        self, 
        content_samples: List[Tuple[str, datetime]],
        window_days: int = 30
    ) -> Dict[str, Any]:
        """Track brand voice consistency over time.
        
        Args:
            content_samples: List of (content, timestamp) tuples
            window_days: Analysis window in days
            
        Returns:
            Voice drift analysis
        """
        try:
            # Sort samples by timestamp
            sorted_samples = sorted(content_samples, key=lambda x: x[1])
            
            # Analyze each sample
            voice_scores = []
            for content, timestamp in sorted_samples:
                analysis = self.analyze_brand_voice(content)
                voice_scores.append({
                    "timestamp": timestamp.isoformat(),
                    "score": analysis.get("overall_score", 0.0),
                    "content_preview": content[:100] + "..."
                })
            
            # Calculate drift metrics
            if len(voice_scores) < 2:
                return {"error": "Need at least 2 content samples for drift analysis"}
            
            scores = [item["score"] for item in voice_scores]
            recent_avg = sum(scores[-3:]) / min(3, len(scores))
            overall_avg = sum(scores) / len(scores)
            
            # Determine drift direction and magnitude
            drift_magnitude = recent_avg - overall_avg
            drift_direction = "improving" if drift_magnitude > 0.05 else "declining" if drift_magnitude < -0.05 else "stable"
            
            return {
                "sample_count": len(voice_scores),
                "overall_average": overall_avg,
                "recent_average": recent_avg,
                "drift_magnitude": drift_magnitude,
                "drift_direction": drift_direction,
                "score_trend": voice_scores,
                "recommendations": self._generate_drift_recommendations(drift_direction, drift_magnitude),
                "analysis_window_days": window_days
            }
            
        except Exception as e:
            logger.error(f"Voice drift tracking failed: {e}")
            return {"error": str(e)}
    
    def _analyze_voice_rules(self, content: str) -> Dict[str, Any]:
        """Perform rule-based brand voice analysis.
        
        Args:
            content: Content to analyze
            
        Returns:
            Rule-based analysis results
        """
        content_lower = content.lower()
        
        # Check preferred terms usage
        preferred_terms_found = [
            term for term in self.brand_guidelines.preferred_terms
            if term.lower() in content_lower
        ]
        
        # Check avoided terms usage
        avoided_terms_found = [
            term for term in self.brand_guidelines.avoid_terms
            if term.lower() in content_lower
        ]
        
        # Analyze tone indicators
        tone_indicators = {
            "professional": self._check_professional_tone(content),
            "solution_focused": self._check_solution_focus(content),
            "optimistic": self._check_optimistic_tone(content),
            "data_driven": self._check_data_driven(content),
            "accessible": self._check_accessibility(content)
        }
        
        # Calculate rule-based score
        rule_score = self._calculate_rule_score(
            preferred_terms_found, avoided_terms_found, tone_indicators
        )
        
        return {
            "rule_based_score": rule_score,
            "preferred_terms_found": preferred_terms_found,
            "avoided_terms_found": avoided_terms_found,
            "tone_indicators": tone_indicators,
            "pattern_matches": self._identify_pattern_matches(content)
        }
    
    def _check_professional_tone(self, content: str) -> float:
        """Check for professional tone indicators."""
        professional_indicators = [
            "analysis", "research", "data", "study", "report", "proven", 
            "demonstrated", "evidence", "implementation", "strategy"
        ]
        casual_indicators = [
            "awesome", "amazing", "super", "totally", "really cool", "epic"
        ]
        
        content_lower = content.lower()
        professional_count = sum(1 for term in professional_indicators if term in content_lower)
        casual_count = sum(1 for term in casual_indicators if term in content_lower)
        
        if professional_count == 0 and casual_count == 0:
            return 0.7  # Neutral
        
        professional_ratio = professional_count / (professional_count + casual_count + 1)
        return min(1.0, professional_ratio * 1.2)
    
    def _check_solution_focus(self, content: str) -> float:
        """Check for solution-focused messaging."""
        solution_indicators = [
            "solution", "solve", "address", "improve", "optimize", "reduce",
            "increase", "enhance", "achieve", "deliver", "implement", "strategy"
        ]
        
        content_lower = content.lower()
        solution_count = sum(1 for term in solution_indicators if term in content_lower)
        
        # Normalize by content length
        words = len(content.split())
        solution_density = solution_count / max(words / 100, 1)  # Per 100 words
        
        return min(1.0, solution_density / 3)  # Target: 3 solution words per 100 words
    
    def _check_optimistic_tone(self, content: str) -> float:
        """Check for optimistic tone indicators."""
        optimistic_indicators = [
            "opportunity", "potential", "future", "innovation", "growth", "success",
            "achieve", "improve", "enhance", "benefit", "advantage", "positive"
        ]
        pessimistic_indicators = [
            "problem", "crisis", "failure", "decline", "difficult", "impossible",
            "never", "can't", "won't", "disaster"
        ]
        
        content_lower = content.lower()
        optimistic_count = sum(1 for term in optimistic_indicators if term in content_lower)
        pessimistic_count = sum(1 for term in pessimistic_indicators if term in content_lower)
        
        if optimistic_count == 0 and pessimistic_count == 0:
            return 0.6  # Neutral
        
        optimistic_ratio = optimistic_count / (optimistic_count + pessimistic_count + 1)
        return min(1.0, optimistic_ratio * 1.1)
    
    def _check_data_driven(self, content: str) -> float:
        """Check for data-driven content indicators."""
        import re
        
        # Look for numbers, percentages, and data references
        numbers = len(re.findall(r'\d+', content))
        percentages = len(re.findall(r'\d+%', content))
        data_terms = sum(1 for term in ["data", "research", "study", "analysis", "metric"] 
                        if term.lower() in content.lower())
        
        words = len(content.split())
        data_density = (numbers + percentages * 2 + data_terms * 2) / max(words / 100, 1)
        
        return min(1.0, data_density / 5)  # Target density
    
    def _check_accessibility(self, content: str) -> float:
        """Check content accessibility and readability."""
        # Simple readability indicators
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Check for jargon and technical terms
        technical_terms = [
            "paradigm", "synergy", "leverage", "utilize", "facilitate", "optimize",
            "actualize", "operationalize", "systematize"
        ]
        
        jargon_count = sum(1 for term in technical_terms if term.lower() in content.lower())
        words = len(content.split())
        
        # Penalize very long sentences and high jargon
        sentence_score = 1.0 - min(0.5, (avg_sentence_length - 15) / 20)  # Penalty after 15 words
        jargon_score = 1.0 - min(0.3, jargon_count / max(words / 100, 1))
        
        return (sentence_score + jargon_score) / 2
    
    def _calculate_rule_score(
        self, 
        preferred_terms: List[str], 
        avoided_terms: List[str], 
        tone_indicators: Dict[str, float]
    ) -> float:
        """Calculate overall rule-based score."""
        # Weight different components
        term_score = (len(preferred_terms) * 0.1) - (len(avoided_terms) * 0.2)
        term_score = max(0.0, min(1.0, 0.7 + term_score))  # Base 0.7, adjust by terms
        
        tone_score = sum(tone_indicators.values()) / len(tone_indicators)
        
        # Combine with weights
        overall_score = (tone_score * 0.8) + (term_score * 0.2)
        return min(1.0, max(0.0, overall_score))
    
    def _combine_analyses(
        self, 
        vector_analysis: Dict[str, Any], 
        rule_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine vector and rule-based analyses."""
        vector_score = vector_analysis.get("predicted_score", 0.0)
        rule_score = rule_analysis.get("rule_based_score", 0.0)
        vector_confidence = vector_analysis.get("confidence", 0.0)
        
        # Weight based on confidence
        if vector_confidence > 0.7:
            combined_score = (vector_score * 0.7) + (rule_score * 0.3)
        elif vector_confidence > 0.4:
            combined_score = (vector_score * 0.5) + (rule_score * 0.5)
        else:
            combined_score = (vector_score * 0.3) + (rule_score * 0.7)
        
        # Extract dimension scores
        dimension_scores = {
            "overall_alignment": combined_score,
            "tone_consistency": rule_analysis["tone_indicators"].get("professional", 0.0),
            "solution_focus": rule_analysis["tone_indicators"].get("solution_focused", 0.0),
            "optimistic_outlook": rule_analysis["tone_indicators"].get("optimistic", 0.0),
            "data_credibility": rule_analysis["tone_indicators"].get("data_driven", 0.0),
            "accessibility": rule_analysis["tone_indicators"].get("accessible", 0.0)
        }
        
        # Identify strengths and improvement areas
        strengths = [k for k, v in dimension_scores.items() if v >= 0.8]
        improvement_areas = [k for k, v in dimension_scores.items() if v < 0.7]
        
        return {
            "overall_score": combined_score,
            "confidence": (vector_confidence + 0.8) / 2,  # Rule confidence is always 0.8
            "dimension_scores": dimension_scores,
            "strengths": strengths,
            "improvement_areas": improvement_areas
        }
    
    def _generate_recommendations(
        self, 
        analysis: Dict[str, Any], 
        content: str
    ) -> List[str]:
        """Generate specific improvement recommendations."""
        recommendations = []
        dimension_scores = analysis.get("dimension_scores", {})
        
        if dimension_scores.get("tone_consistency", 0) < 0.7:
            recommendations.append("Strengthen professional tone with more credible, data-driven language")
        
        if dimension_scores.get("solution_focus", 0) < 0.7:
            recommendations.append("Increase solution-focused messaging with specific benefits and outcomes")
        
        if dimension_scores.get("optimistic_outlook", 0) < 0.7:
            recommendations.append("Add more optimistic language about future opportunities and potential")
        
        if dimension_scores.get("data_credibility", 0) < 0.7:
            recommendations.append("Include more specific data points, statistics, and credible references")
        
        if dimension_scores.get("accessibility", 0) < 0.7:
            recommendations.append("Improve readability with shorter sentences and less technical jargon")
        
        # Add general recommendations
        if analysis.get("overall_score", 0) < 0.8:
            recommendations.extend([
                "Review EcoTech brand guidelines for voice and tone requirements",
                "Consider using more preferred terminology from brand guidelines",
                "Add specific case studies or examples to support claims"
            ])
        
        return recommendations or ["Content shows good brand voice alignment"]
    
    def _generate_optimization_recommendations(
        self,
        content: str,
        current_score: float,
        target_score: float,
        dimension_scores: Dict[str, float],
        improvement_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized optimization recommendations."""
        recommendations = []
        
        # Prioritize by impact potential
        for area in improvement_areas:
            score = dimension_scores.get(area, 0.0)
            impact = (0.9 - score) * 0.2  # Potential improvement
            
            if area == "data_credibility":
                recommendations.append({
                    "area": area,
                    "current_score": score,
                    "impact_potential": impact,
                    "recommendation": "Add 2-3 specific statistics or data points with credible sources",
                    "effort": "Medium",
                    "priority": "High"
                })
            elif area == "solution_focus":
                recommendations.append({
                    "area": area,
                    "current_score": score,
                    "impact_potential": impact,
                    "recommendation": "Strengthen value proposition with specific business benefits",
                    "effort": "Medium",
                    "priority": "High"
                })
            elif area == "tone_consistency":
                recommendations.append({
                    "area": area,
                    "current_score": score,
                    "impact_potential": impact,
                    "recommendation": "Review language for professional credibility and authority",
                    "effort": "Low",
                    "priority": "Medium"
                })
        
        # Sort by priority and impact
        recommendations.sort(key=lambda x: (x["priority"] == "High", x["impact_potential"]), reverse=True)
        
        return recommendations
    
    def _estimate_optimization_effort(self, current_score: float, target_score: float) -> str:
        """Estimate effort required for optimization."""
        gap = target_score - current_score
        
        if gap <= 0.1:
            return "Low - Minor adjustments needed"
        elif gap <= 0.2:
            return "Medium - Moderate revisions required"
        else:
            return "High - Significant content revision needed"
    
    def _estimate_impact(self, recommendations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Estimate impact of implementing recommendations."""
        if not recommendations:
            return {"score_improvement": 0.0, "confidence": 0.0}
        
        total_impact = sum(rec.get("impact_potential", 0.0) for rec in recommendations)
        high_priority_count = sum(1 for rec in recommendations if rec.get("priority") == "High")
        
        return {
            "score_improvement": min(0.3, total_impact),  # Cap at 0.3 improvement
            "confidence": min(0.9, 0.5 + (high_priority_count * 0.1)),
            "implementation_time": f"{len(recommendations)} * 30 minutes per recommendation"
        }
    
    def _generate_drift_recommendations(self, drift_direction: str, drift_magnitude: float) -> List[str]:
        """Generate recommendations based on voice drift analysis."""
        recommendations = []
        
        if drift_direction == "declining":
            recommendations.extend([
                "Review recent content for brand voice consistency",
                "Provide additional brand guidelines training for content creators",
                "Implement brand voice review process before publication",
                "Use high-scoring content as templates for future creation"
            ])
        elif drift_direction == "improving":
            recommendations.extend([
                "Continue current brand voice practices",
                "Document successful approaches for team reference",
                "Share best practices across content creation team"
            ])
        else:  # stable
            recommendations.extend([
                "Maintain current brand voice consistency practices",
                "Consider periodic brand voice training refreshers",
                "Monitor for seasonal or topic-specific variations"
            ])
        
        return recommendations
    
    def _identify_pattern_matches(self, content: str) -> List[str]:
        """Identify specific brand voice pattern matches."""
        patterns = []
        content_lower = content.lower()
        
        # Check for EcoTech-specific patterns
        if "sustainable" in content_lower and ("innovation" in content_lower or "solution" in content_lower):
            patterns.append("Sustainable innovation messaging")
        
        if any(term in content_lower for term in ["roi", "return", "investment", "savings"]):
            patterns.append("ROI-focused value proposition")
        
        if "future" in content_lower and any(term in content_lower for term in ["ready", "forward", "ahead"]):
            patterns.append("Future-focused optimistic tone")
        
        return patterns
    
    def _load_voice_patterns(self) -> Dict[str, Any]:
        """Load brand voice patterns for analysis."""
        return {
            "professional_indicators": [
                "analysis", "research", "data", "proven", "demonstrated"
            ],
            "solution_indicators": [
                "solution", "solve", "optimize", "improve", "enhance"
            ],
            "optimistic_indicators": [
                "opportunity", "potential", "future", "innovation", "growth"
            ]
        }
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights for different voice dimensions."""
        return {
            "tone_consistency": 0.25,
            "solution_focus": 0.25,
            "data_credibility": 0.20,
            "optimistic_outlook": 0.15,
            "accessibility": 0.15
        }
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "agent_type": "BrandConsistencyAgent",
            "brand_guidelines_loaded": bool(self.brand_guidelines),
            "voice_patterns": len(self.voice_patterns),
            "scoring_dimensions": len(self.scoring_weights),
            "capabilities": [
                "Brand voice analysis",
                "Consistency scoring", 
                "Voice optimization",
                "Drift tracking",
                "Pattern recognition"
            ]
        } 