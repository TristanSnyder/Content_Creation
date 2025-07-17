"""Multi-agent coordinator for orchestrating content creation workflows."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.data.models import GenerationRequest, AgentResponse, ContentType, Platform
from src.agents.content_agent import ContentStrategyAgent
from src.agents.brand_agent import BrandConsistencyAgent
from src.rag.chains import EcoTechRAGChains
from src.rag.mock_llm import MockLLMClient
from src.vector_db.chroma_client import ChromaVectorDB

logger = logging.getLogger(__name__)


class DistributionAgent:
    """Agent for content distribution planning and optimization."""
    
    def __init__(self, mock_llm: MockLLMClient):
        """Initialize distribution agent.
        
        Args:
            mock_llm: Mock LLM for response generation
        """
        self.llm = mock_llm
        self.platform_specs = self._load_platform_specifications()
        
    def plan_distribution(
        self, 
        content: str, 
        content_type: ContentType,
        target_platforms: Optional[List[Platform]] = None
    ) -> Dict[str, Any]:
        """Plan content distribution across platforms.
        
        Args:
            content: Content to distribute
            content_type: Type of content
            target_platforms: Optional specific platforms
            
        Returns:
            Distribution plan with platform optimizations
        """
        try:
            # Default platform selection based on content type
            if not target_platforms:
                target_platforms = self._select_optimal_platforms(content_type)
            
            distribution_plan = {
                "content_type": content_type.value,
                "target_platforms": [p.value for p in target_platforms],
                "platform_optimizations": {},
                "scheduling_recommendations": {},
                "performance_predictions": {}
            }
            
            # Generate platform-specific optimizations
            for platform in target_platforms:
                optimization = self._optimize_for_platform(content, platform, content_type)
                distribution_plan["platform_optimizations"][platform.value] = optimization
                
                # Add scheduling recommendations
                schedule = self._recommend_schedule(platform, content_type)
                distribution_plan["scheduling_recommendations"][platform.value] = schedule
                
                # Predict performance
                prediction = self._predict_performance(content, platform, content_type)
                distribution_plan["performance_predictions"][platform.value] = prediction
            
            distribution_plan["created_at"] = datetime.now().isoformat()
            return distribution_plan
            
        except Exception as e:
            logger.error(f"Distribution planning failed: {e}")
            return {
                "error": str(e),
                "content_type": content_type.value,
                "created_at": datetime.now().isoformat()
            }
    
    def _select_optimal_platforms(self, content_type: ContentType) -> List[Platform]:
        """Select optimal platforms for content type."""
        platform_map = {
            ContentType.BLOG_POST: [Platform.BLOG, Platform.LINKEDIN, Platform.EMAIL],
            ContentType.SOCIAL_MEDIA: [Platform.LINKEDIN, Platform.TWITTER, Platform.FACEBOOK],
            ContentType.EMAIL_NEWSLETTER: [Platform.EMAIL],
            ContentType.PRODUCT_DESCRIPTION: [Platform.BLOG, Platform.LINKEDIN]
        }
        
        return platform_map.get(content_type, [Platform.BLOG, Platform.LINKEDIN])
    
    def _optimize_for_platform(
        self, 
        content: str, 
        platform: Platform, 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Optimize content for specific platform."""
        specs = self.platform_specs.get(platform, {})
        
        optimization = {
            "original_length": len(content),
            "target_length": specs.get("max_length", len(content)),
            "format_adjustments": [],
            "hashtag_recommendations": [],
            "visual_content_suggestions": []
        }
        
        # Platform-specific optimizations
        if platform == Platform.TWITTER:
            optimization["format_adjustments"] = [
                "Split into thread if over 280 characters",
                "Add compelling hook in first tweet",
                "Include relevant hashtags"
            ]
            optimization["hashtag_recommendations"] = [
                "#GreenTech", "#Sustainability", "#Innovation", "#CleanEnergy"
            ]
        
        elif platform == Platform.LINKEDIN:
            optimization["format_adjustments"] = [
                "Professional tone with business focus",
                "Include industry insights",
                "Add call-to-action for engagement"
            ]
            optimization["hashtag_recommendations"] = [
                "#Sustainability", "#BusinessStrategy", "#Innovation", "#GreenBusiness"
            ]
        
        elif platform == Platform.FACEBOOK:
            optimization["format_adjustments"] = [
                "Community-focused language",
                "Include questions to drive engagement",
                "Visual content emphasis"
            ]
            optimization["visual_content_suggestions"] = [
                "Infographic with key statistics",
                "Behind-the-scenes photos",
                "Customer success story images"
            ]
        
        return optimization
    
    def _recommend_schedule(self, platform: Platform, content_type: ContentType) -> Dict[str, str]:
        """Recommend optimal scheduling for platform and content type."""
        schedule_map = {
            Platform.LINKEDIN: {
                "best_days": "Tuesday-Thursday",
                "best_times": "8-10 AM, 12-2 PM, 5-7 PM",
                "frequency": "3-5 posts per week"
            },
            Platform.TWITTER: {
                "best_days": "Monday-Friday",
                "best_times": "9 AM, 12 PM, 3 PM, 6 PM",
                "frequency": "1-3 tweets per day"
            },
            Platform.FACEBOOK: {
                "best_days": "Tuesday-Saturday",
                "best_times": "9 AM, 1 PM, 3 PM",
                "frequency": "1-2 posts per day"
            },
            Platform.EMAIL: {
                "best_days": "Tuesday-Thursday",
                "best_times": "10 AM, 2 PM",
                "frequency": "Weekly newsletter"
            }
        }
        
        return schedule_map.get(platform, {
            "best_days": "Monday-Friday",
            "best_times": "Business hours",
            "frequency": "Regular posting"
        })
    
    def _predict_performance(
        self, 
        content: str, 
        platform: Platform, 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Predict content performance on platform."""
        # Simulate performance prediction based on content characteristics
        content_length = len(content)
        has_data = any(char.isdigit() for char in content)
        has_cta = any(phrase in content.lower() for phrase in ["contact", "learn more", "schedule"])
        
        base_performance = {
            Platform.LINKEDIN: {"engagement": 0.045, "conversion": 0.034},
            Platform.TWITTER: {"engagement": 0.063, "conversion": 0.019},
            Platform.FACEBOOK: {"engagement": 0.038, "conversion": 0.021},
            Platform.EMAIL: {"engagement": 0.185, "conversion": 0.042}
        }
        
        platform_base = base_performance.get(platform, {"engagement": 0.040, "conversion": 0.025})
        
        # Adjust based on content characteristics
        engagement_multiplier = 1.0
        if has_data:
            engagement_multiplier += 0.15
        if has_cta:
            engagement_multiplier += 0.10
        if 200 <= content_length <= 800:  # Optimal length
            engagement_multiplier += 0.05
        
        return {
            "predicted_engagement_rate": round(platform_base["engagement"] * engagement_multiplier, 3),
            "predicted_conversion_rate": round(platform_base["conversion"] * engagement_multiplier, 3),
            "confidence": 0.75,
            "factors": {
                "has_data_points": has_data,
                "has_call_to_action": has_cta,
                "optimal_length": 200 <= content_length <= 800
            }
        }
    
    def _load_platform_specifications(self) -> Dict[Platform, Dict[str, Any]]:
        """Load platform-specific specifications."""
        return {
            Platform.TWITTER: {
                "max_length": 280,
                "optimal_length": 200,
                "max_hashtags": 3,
                "image_specs": "1200x675px"
            },
            Platform.LINKEDIN: {
                "max_length": 3000,
                "optimal_length": 1500,
                "max_hashtags": 5,
                "image_specs": "1200x627px"
            },
            Platform.FACEBOOK: {
                "max_length": 2200,
                "optimal_length": 500,
                "max_hashtags": 3,
                "image_specs": "1200x630px"
            },
            Platform.EMAIL: {
                "max_length": 5000,
                "optimal_length": 800,
                "subject_line_max": 50,
                "preview_text_max": 90
            }
        }


class AgentCoordinator:
    """Central coordinator for multi-agent content creation workflows."""
    
    def __init__(
        self,
        rag_chains: EcoTechRAGChains,
        vector_db: ChromaVectorDB,
        mock_llm: MockLLMClient
    ):
        """Initialize agent coordinator.
        
        Args:
            rag_chains: EcoTech RAG chains
            vector_db: Vector database for content retrieval
            mock_llm: Mock LLM for response generation
        """
        self.rag_chains = rag_chains
        self.vector_db = vector_db
        self.llm = mock_llm
        
        # Initialize specialized agents
        self.content_agent = ContentStrategyAgent(rag_chains, vector_db, mock_llm)
        self.brand_agent = BrandConsistencyAgent(rag_chains, vector_db, mock_llm)
        self.distribution_agent = DistributionAgent(mock_llm)
        
        # Workflow tracking
        self.active_workflows = {}
        self.workflow_history = []
        
        logger.info("AgentCoordinator initialized with specialized agents")
    
    async def orchestrate_content_creation(
        self, 
        request: GenerationRequest,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Orchestrate complete content creation workflow.
        
        Args:
            request: Content generation request
            workflow_id: Optional workflow identifier
            
        Returns:
            Complete workflow results with content, analysis, and distribution plan
        """
        try:
            workflow_id = workflow_id or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Starting content creation workflow: {workflow_id}")
            
            # Track workflow start
            self.active_workflows[workflow_id] = {
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "request": request.__dict__
            }
            
            # Step 1: Strategy planning
            logger.info("Step 1: Planning content strategy")
            strategy = await self._execute_with_timeout(
                self.content_agent.plan_content_strategy(request),
                timeout_seconds=30
            )
            
            # Step 2: Content generation
            logger.info("Step 2: Generating content with reasoning")
            content_response = await self._execute_with_timeout(
                self.content_agent.generate_with_reasoning(
                    request.prompt, 
                    request.content_type,
                    use_strategy=True
                ),
                timeout_seconds=45
            )
            
            # Step 3: Brand consistency check
            logger.info("Step 3: Analyzing brand voice consistency")
            brand_analysis = await self._execute_with_timeout(
                self._analyze_brand_consistency(content_response.content),
                timeout_seconds=20
            )
            
            # Step 4: Content optimization (if needed)
            optimization_suggestions = None
            if brand_analysis.get("overall_score", 0) < 0.8:
                logger.info("Step 4a: Generating optimization suggestions")
                optimization_suggestions = await self._execute_with_timeout(
                    self.brand_agent.optimize_voice_alignment(
                        content_response.content,
                        target_score=0.9
                    ),
                    timeout_seconds=25
                )
            
            # Step 5: Distribution planning
            logger.info("Step 5: Planning content distribution")
            distribution_plan = await self._execute_with_timeout(
                self._plan_distribution(content_response.content, request),
                timeout_seconds=20
            )
            
            # Step 6: Compile results and reasoning chain
            logger.info("Step 6: Compiling workflow results")
            workflow_results = self._compile_workflow_results(
                workflow_id,
                strategy,
                content_response,
                brand_analysis,
                distribution_plan,
                optimization_suggestions
            )
            
            # Complete workflow
            self._complete_workflow(workflow_id, workflow_results)
            
            logger.info(f"Content creation workflow completed: {workflow_id}")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Content creation workflow failed: {e}")
            self._fail_workflow(workflow_id, str(e))
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    async def collaborative_optimization(
        self, 
        content: str,
        content_type: ContentType,
        target_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Collaborative optimization using multiple agents.
        
        Args:
            content: Content to optimize
            content_type: Type of content
            target_metrics: Optional performance targets
            
        Returns:
            Multi-agent optimization recommendations
        """
        try:
            logger.info("Starting collaborative content optimization")
            
            # Concurrent analysis by different agents
            tasks = [
                self._analyze_brand_consistency(content),
                self.content_agent.optimize_existing_content(content, target_metrics),
                self._analyze_distribution_optimization(content, content_type)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            brand_analysis, content_optimization, distribution_optimization = results
            
            # Combine insights from all agents
            combined_recommendations = self._combine_optimization_insights(
                brand_analysis,
                content_optimization,
                distribution_optimization
            )
            
            return {
                "content_analyzed": content[:200] + "..." if len(content) > 200 else content,
                "brand_analysis": brand_analysis,
                "content_optimization": content_optimization,
                "distribution_optimization": distribution_optimization,
                "combined_recommendations": combined_recommendations,
                "optimization_priority": self._prioritize_optimizations(combined_recommendations),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Collaborative optimization failed: {e}")
            return {"error": str(e)}
    
    async def agent_consultation(
        self, 
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get consultation from multiple agents on a query.
        
        Args:
            query: Question or request for agents
            context: Optional context information
            
        Returns:
            Multi-agent consultation results
        """
        try:
            logger.info(f"Starting agent consultation: {query[:50]}...")
            
            # Route query to appropriate agents
            agent_responses = {}
            
            # Content strategy perspective
            if any(keyword in query.lower() for keyword in ["strategy", "content", "topic", "planning"]):
                # Mock content agent response
                agent_responses["content_strategy"] = {
                    "agent": "ContentStrategyAgent",
                    "response": f"From a content strategy perspective on '{query}': Focus on audience-specific value propositions, data-driven insights, and clear calls-to-action. Consider content series approach for complex topics.",
                    "confidence": 0.85
                }
            
            # Brand voice perspective
            if any(keyword in query.lower() for keyword in ["brand", "voice", "tone", "consistency"]):
                agent_responses["brand_voice"] = {
                    "agent": "BrandConsistencyAgent",
                    "response": f"Regarding brand voice for '{query}': Ensure professional yet approachable tone, solution-focused messaging, and optimistic outlook. Include credible data points and maintain technical accessibility.",
                    "confidence": 0.88
                }
            
            # Distribution perspective
            if any(keyword in query.lower() for keyword in ["distribution", "platform", "social", "schedule"]):
                agent_responses["distribution"] = {
                    "agent": "DistributionAgent",
                    "response": f"For distribution of '{query}': Recommend multi-platform approach with LinkedIn for professional audience, email for detailed insights, and Twitter for quick updates. Schedule during business hours for B2B focus.",
                    "confidence": 0.82
                }
            
            # Synthesize consultation
            synthesis = self._synthesize_consultation(agent_responses, query)
            
            return {
                "query": query,
                "agent_responses": agent_responses,
                "synthesis": synthesis,
                "context_used": context or {},
                "consultation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent consultation failed: {e}")
            return {"error": str(e), "query": query}
    
    async def _execute_with_timeout(self, coro_or_result, timeout_seconds: int = 30):
        """Execute coroutine or return result with timeout."""
        if asyncio.iscoroutine(coro_or_result):
            return await asyncio.wait_for(coro_or_result, timeout=timeout_seconds)
        else:
            # If it's already a result (sync function), return it
            return coro_or_result
    
    async def _analyze_brand_consistency(self, content: str) -> Dict[str, Any]:
        """Analyze brand consistency (async wrapper)."""
        return self.brand_agent.analyze_brand_voice(content)
    
    async def _plan_distribution(self, content: str, request: GenerationRequest) -> Dict[str, Any]:
        """Plan content distribution (async wrapper)."""
        target_platforms = getattr(request, 'platforms', None)
        return self.distribution_agent.plan_distribution(
            content, 
            request.content_type,
            target_platforms
        )
    
    async def _analyze_distribution_optimization(
        self, 
        content: str, 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Analyze distribution optimization opportunities."""
        return {
            "platform_suitability": self._assess_platform_suitability(content, content_type),
            "scheduling_optimization": self._optimize_scheduling(content_type),
            "cross_platform_adaptation": self._suggest_adaptations(content, content_type)
        }
    
    def _assess_platform_suitability(self, content: str, content_type: ContentType) -> Dict[str, float]:
        """Assess content suitability for different platforms."""
        content_length = len(content)
        has_visual_elements = any(word in content.lower() for word in ["image", "chart", "graph", "infographic"])
        is_technical = any(word in content.lower() for word in ["analysis", "data", "research", "technical"])
        
        suitability = {}
        
        # LinkedIn suitability
        linkedin_score = 0.8  # Base score for business content
        if is_technical:
            linkedin_score += 0.1
        if 300 <= content_length <= 1500:
            linkedin_score += 0.05
        suitability["linkedin"] = min(1.0, linkedin_score)
        
        # Twitter suitability
        twitter_score = 0.6  # Base score
        if content_length <= 280:
            twitter_score += 0.3
        elif content_length <= 1000:  # Thread potential
            twitter_score += 0.1
        suitability["twitter"] = min(1.0, twitter_score)
        
        # Email suitability
        email_score = 0.9  # High for detailed content
        if content_length >= 500:
            email_score += 0.05
        suitability["email"] = min(1.0, email_score)
        
        return suitability
    
    def _optimize_scheduling(self, content_type: ContentType) -> Dict[str, str]:
        """Provide scheduling optimization recommendations."""
        return {
            "optimal_timing": "Tuesday-Thursday, 9-11 AM or 2-4 PM",
            "frequency": "3-5 posts per week for thought leadership",
            "seasonal_considerations": "Increase frequency during sustainability awareness periods",
            "audience_timezone": "Focus on business hours in target markets"
        }
    
    def _suggest_adaptations(self, content: str, content_type: ContentType) -> List[Dict[str, str]]:
        """Suggest platform-specific content adaptations."""
        adaptations = []
        
        if len(content) > 500:
            adaptations.append({
                "platform": "Twitter",
                "adaptation": "Create thread with key points, lead with hook statement",
                "effort": "Medium"
            })
        
        adaptations.append({
            "platform": "LinkedIn",
            "adaptation": "Add professional insights and industry implications",
            "effort": "Low"
        })
        
        adaptations.append({
            "platform": "Email",
            "adaptation": "Expand with additional context and resources",
            "effort": "Medium"
        })
        
        return adaptations
    
    def _combine_optimization_insights(
        self,
        brand_analysis: Dict[str, Any],
        content_optimization: Dict[str, Any],
        distribution_optimization: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Combine insights from multiple agents."""
        combined_recommendations = []
        
        # Extract brand recommendations
        if isinstance(brand_analysis, dict) and "recommendations" in brand_analysis:
            for rec in brand_analysis["recommendations"]:
                combined_recommendations.append({
                    "source": "Brand Agent",
                    "category": "Brand Voice",
                    "recommendation": rec,
                    "priority": "High"
                })
        
        # Extract content optimization recommendations
        if isinstance(content_optimization, dict) and "optimization_recommendations" in content_optimization:
            combined_recommendations.append({
                "source": "Content Agent",
                "category": "Content Optimization",
                "recommendation": "Review content optimization suggestions for engagement improvement",
                "priority": "Medium"
            })
        
        # Extract distribution recommendations
        if isinstance(distribution_optimization, dict) and "cross_platform_adaptation" in distribution_optimization:
            for adaptation in distribution_optimization["cross_platform_adaptation"]:
                combined_recommendations.append({
                    "source": "Distribution Agent",
                    "category": "Platform Optimization",
                    "recommendation": f"{adaptation['platform']}: {adaptation['adaptation']}",
                    "priority": "Low" if adaptation.get("effort") == "Low" else "Medium"
                })
        
        return combined_recommendations
    
    def _prioritize_optimizations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize optimization recommendations."""
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: priority_order.get(x.get("priority", "Low"), 1),
            reverse=True
        )
        
        return sorted_recommendations[:5]  # Top 5 priorities
    
    def _synthesize_consultation(
        self, 
        agent_responses: Dict[str, Dict[str, Any]], 
        query: str
    ) -> Dict[str, Any]:
        """Synthesize multi-agent consultation into coherent response."""
        if not agent_responses:
            return {
                "summary": f"No specific agent expertise available for query: {query}",
                "confidence": 0.3
            }
        
        # Calculate overall confidence
        confidences = [resp.get("confidence", 0) for resp in agent_responses.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Create synthesis
        synthesis = {
            "summary": f"Multi-agent analysis of '{query}' provides complementary perspectives:",
            "key_insights": [],
            "recommended_actions": [],
            "confidence": avg_confidence
        }
        
        # Extract key insights
        for agent_name, response in agent_responses.items():
            synthesis["key_insights"].append({
                "agent": agent_name,
                "insight": response.get("response", "No response available")[:150] + "..."
            })
        
        # Generate recommended actions
        if "content_strategy" in agent_responses:
            synthesis["recommended_actions"].append("Develop content strategy with audience-specific value propositions")
        
        if "brand_voice" in agent_responses:
            synthesis["recommended_actions"].append("Ensure brand voice consistency across all content")
        
        if "distribution" in agent_responses:
            synthesis["recommended_actions"].append("Optimize content for multi-platform distribution")
        
        return synthesis
    
    def _compile_workflow_results(
        self,
        workflow_id: str,
        strategy: AgentResponse,
        content_response: AgentResponse,
        brand_analysis: Dict[str, Any],
        distribution_plan: Dict[str, Any],
        optimization_suggestions: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile comprehensive workflow results."""
        
        # Build reasoning chain
        reasoning_chain = [
            {
                "step": 1,
                "agent": "ContentStrategyAgent",
                "action": "Strategy Planning",
                "result": "Comprehensive content strategy developed",
                "confidence": strategy.confidence
            },
            {
                "step": 2,
                "agent": "ContentStrategyAgent", 
                "action": "Content Generation",
                "result": f"Generated {len(content_response.content)} character content",
                "confidence": content_response.confidence
            },
            {
                "step": 3,
                "agent": "BrandConsistencyAgent",
                "action": "Brand Voice Analysis",
                "result": f"Brand voice score: {brand_analysis.get('overall_score', 0):.3f}",
                "confidence": brand_analysis.get("confidence", 0)
            },
            {
                "step": 4,
                "agent": "DistributionAgent",
                "action": "Distribution Planning",
                "result": f"Multi-platform distribution planned for {len(distribution_plan.get('target_platforms', []))} platforms",
                "confidence": 0.85
            }
        ]
        
        if optimization_suggestions:
            reasoning_chain.append({
                "step": 5,
                "agent": "BrandConsistencyAgent",
                "action": "Optimization Suggestions",
                "result": "Brand voice optimization recommendations generated",
                "confidence": 0.80
            })
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "content": {
                "generated_content": content_response.content,
                "content_metadata": {
                    "word_count": len(content_response.content.split()),
                    "character_count": len(content_response.content),
                    "estimated_reading_time": f"{len(content_response.content.split()) // 200 + 1} minutes"
                }
            },
            "strategy": {
                "strategic_approach": strategy.content,
                "reasoning": strategy.reasoning,
                "confidence": strategy.confidence
            },
            "brand_analysis": brand_analysis,
            "distribution_plan": distribution_plan,
            "optimization_suggestions": optimization_suggestions,
            "reasoning_chain": reasoning_chain,
            "overall_confidence": sum(step["confidence"] for step in reasoning_chain) / len(reasoning_chain),
            "recommendations": self._generate_final_recommendations(
                content_response, brand_analysis, distribution_plan
            ),
            "completed_at": datetime.now().isoformat()
        }
    
    def _generate_final_recommendations(
        self,
        content_response: AgentResponse,
        brand_analysis: Dict[str, Any],
        distribution_plan: Dict[str, Any]
    ) -> List[str]:
        """Generate final workflow recommendations."""
        recommendations = []
        
        # Content quality recommendations
        if content_response.brand_voice_score < 0.9:
            recommendations.append("Consider revising content to improve brand voice alignment")
        
        # Brand consistency recommendations
        brand_score = brand_analysis.get("overall_score", 0)
        if brand_score < 0.8:
            recommendations.append("Review brand voice guidelines and incorporate feedback")
        elif brand_score >= 0.9:
            recommendations.append("Content demonstrates excellent brand voice alignment")
        
        # Distribution recommendations
        platforms = distribution_plan.get("target_platforms", [])
        if len(platforms) > 1:
            recommendations.append(f"Optimize content for {len(platforms)} platforms with specific adaptations")
        
        # Performance optimization
        recommendations.extend([
            "Monitor performance metrics post-publication",
            "A/B test different headlines and calls-to-action",
            "Consider creating content series for sustained engagement"
        ])
        
        return recommendations
    
    def _complete_workflow(self, workflow_id: str, results: Dict[str, Any]) -> None:
        """Complete workflow tracking."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now().isoformat()
            
            # Move to history
            self.workflow_history.append(self.active_workflows[workflow_id])
            del self.active_workflows[workflow_id]
    
    def _fail_workflow(self, workflow_id: str, error: str) -> None:
        """Mark workflow as failed."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = error
            self.active_workflows[workflow_id]["failed_at"] = datetime.now().isoformat()
            
            # Move to history
            self.workflow_history.append(self.active_workflows[workflow_id])
            del self.active_workflows[workflow_id]
    
    def get_coordinator_stats(self) -> Dict[str, Any]:
        """Get coordinator performance statistics."""
        return {
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len([w for w in self.workflow_history if w.get("status") == "completed"]),
            "failed_workflows": len([w for w in self.workflow_history if w.get("status") == "failed"]),
            "agents_available": 3,
            "agent_types": ["ContentStrategyAgent", "BrandConsistencyAgent", "DistributionAgent"],
            "workflow_capabilities": [
                "Strategy planning",
                "Content generation", 
                "Brand voice analysis",
                "Distribution planning",
                "Multi-agent coordination",
                "Optimization suggestions"
            ]
        } 