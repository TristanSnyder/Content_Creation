"""Content Strategy Agent for intelligent content planning and generation."""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool

from src.data.models import GenerationRequest, AgentResponse, ContentType, Platform
from src.rag.chains import EcoTechRAGChains
from src.rag.mock_llm import MockLLMClient
from src.vector_db.chroma_client import ChromaVectorDB
from src.agents.tools import get_all_tools

logger = logging.getLogger(__name__)


class ContentStrategyAgent:
    """Intelligent agent for content strategy planning and generation."""
    
    def __init__(
        self, 
        rag_chains: EcoTechRAGChains, 
        vector_db: ChromaVectorDB, 
        mock_llm: MockLLMClient
    ):
        """Initialize content strategy agent.
        
        Args:
            rag_chains: EcoTech RAG chains for content generation
            vector_db: Vector database for content search
            mock_llm: Mock LLM for response generation
        """
        self.rag_chains = rag_chains
        self.vector_db = vector_db
        self.llm = mock_llm
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent_executor()
        
        # Track agent state and reasoning
        self.current_strategy = None
        self.reasoning_chain = []
        
        logger.info("ContentStrategyAgent initialized with tools and RAG chains")
    
    def _create_tools(self) -> List[BaseTool]:
        """Create tools available to the agent."""
        return get_all_tools(self.vector_db)
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create LangChain agent executor with tools."""
        
        # Define agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent with function calling capability
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for content strategy agent."""
        return """You are an expert Content Strategy Agent for EcoTech Solutions, a leading green technology company.

Your role is to:
1. Analyze content requests and develop strategic approaches
2. Use available tools to research and gather context
3. Plan comprehensive content strategies with clear reasoning
4. Generate high-quality content that aligns with brand voice
5. Provide optimization recommendations

Available Tools:
- content_search: Find relevant examples and reference materials
- brand_analysis: Analyze content for brand voice consistency
- performance_analysis: Review content performance metrics and trends
- topic_suggestion: Generate strategic topic recommendations
- content_optimization: Provide specific improvement suggestions

EcoTech Brand Guidelines:
- Professional yet approachable tone
- Solution-focused and optimistic messaging
- Data-driven claims with credible sources
- Technical credibility while maintaining accessibility
- Clear value propositions with ROI focus

Always:
1. Use tools to gather relevant context before generating content
2. Explain your reasoning and strategic approach
3. Ensure brand voice consistency
4. Include specific, actionable recommendations
5. Provide confidence assessments for your suggestions

Think step-by-step and explain your decision-making process."""
    
    def plan_content_strategy(self, request: GenerationRequest) -> AgentResponse:
        """Plan comprehensive content strategy with multi-step reasoning.
        
        Args:
            request: Content generation request
            
        Returns:
            AgentResponse with strategy and reasoning
        """
        try:
            logger.info(f"Planning content strategy for {request.content_type.value}")
            
            # Clear previous reasoning chain
            self.reasoning_chain = []
            
            # Step 1: Research and context gathering
            research_input = f"""
            I need to plan a content strategy for {request.content_type.value} about "{request.prompt}".
            Target audience: {request.target_audience or 'business leaders'}
            
            Please help me:
            1. Find relevant existing content for context
            2. Analyze performance trends for this content type
            3. Suggest strategic topics if needed
            4. Provide brand voice guidance
            
            Use the available tools to gather comprehensive context.
            """
            
            # Execute agent planning
            result = self.agent_executor.invoke({"input": research_input})
            
            # Extract strategy and reasoning
            strategy_output = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Build reasoning chain from tool usage
            reasoning_steps = []
            for step in intermediate_steps:
                if isinstance(step, tuple) and len(step) == 2:
                    action, observation = step
                    if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
                        reasoning_steps.append(f"Used {action.tool}: {action.tool_input}")
                        reasoning_steps.append(f"Result: {observation[:200]}...")
            
            # Create comprehensive strategy response
            strategy = self._build_strategy_response(request, strategy_output, reasoning_steps)
            
            self.current_strategy = strategy
            logger.info(f"Content strategy planned with {len(reasoning_steps)} reasoning steps")
            
            return strategy
            
        except Exception as e:
            logger.error(f"Content strategy planning failed: {e}")
            return AgentResponse(
                content="Strategy planning failed",
                reasoning=f"Strategy planning encountered an error: {str(e)}",
                confidence=0.0,
                sources_used=[],
                brand_voice_score=0.0,
                suggestions=["Review request parameters and try again"]
            )
    
    def generate_with_reasoning(
        self, 
        prompt: str, 
        content_type: ContentType,
        use_strategy: bool = True
    ) -> AgentResponse:
        """Generate content with step-by-step reasoning.
        
        Args:
            prompt: Content generation prompt
            content_type: Type of content to generate
            use_strategy: Whether to use previously planned strategy
            
        Returns:
            AgentResponse with generated content and reasoning
        """
        try:
            logger.info(f"Generating {content_type.value} content with reasoning")
            
            # Prepare generation input
            generation_input = f"""
            Generate {content_type.value} content about: "{prompt}"
            
            Requirements:
            1. Use content_search to find relevant examples and context
            2. Apply brand_analysis to ensure voice consistency
            3. Follow EcoTech brand guidelines
            4. Include specific data points and examples
            5. Provide clear value proposition and call-to-action
            
            {'Use the previously planned strategy as guidance.' if use_strategy and self.current_strategy else ''}
            
            Think through each step and use tools to inform your content creation.
            """
            
            # Execute agent generation
            result = self.agent_executor.invoke({"input": generation_input})
            
            # Extract generated content and process
            generated_content = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Build reasoning from tool usage
            reasoning_parts = ["Content generation reasoning:"]
            sources_used = []
            
            for step in intermediate_steps:
                if isinstance(step, tuple) and len(step) == 2:
                    action, observation = step
                    if hasattr(action, 'tool'):
                        reasoning_parts.append(f"- Used {action.tool} tool")
                        if "search" in action.tool.lower():
                            sources_used.append(f"Search results from {action.tool}")
            
            # Estimate brand voice score (would be calculated by brand analysis)
            brand_voice_score = 0.85  # Simulated score
            
            # Generate suggestions
            suggestions = [
                "Review content for specific data points and metrics",
                "Ensure call-to-action is prominent and compelling",
                "Consider adding customer testimonial or case study",
                "Optimize headers and structure for readability"
            ]
            
            response = AgentResponse(
                content=generated_content,
                reasoning="\n".join(reasoning_parts),
                confidence=0.87,
                sources_used=sources_used,
                brand_voice_score=brand_voice_score,
                suggestions=suggestions
            )
            
            logger.info(f"Generated {content_type.value} content with agent reasoning")
            return response
            
        except Exception as e:
            logger.error(f"Content generation with reasoning failed: {e}")
            return AgentResponse(
                content="",
                reasoning=f"Content generation failed: {str(e)}",
                confidence=0.0,
                sources_used=[],
                brand_voice_score=0.0,
                suggestions=["Check input parameters and try again"]
            )
    
    def analyze_content_gaps(
        self, 
        content_type: Optional[ContentType] = None,
        timeframe: str = "30days"
    ) -> Dict[str, Any]:
        """Analyze content gaps and opportunities.
        
        Args:
            content_type: Optional content type to focus on
            timeframe: Analysis timeframe
            
        Returns:
            Content gap analysis results
        """
        try:
            # Use tools to analyze gaps
            gap_analysis_input = f"""
            Analyze content gaps and opportunities for {content_type.value if content_type else 'all content types'}.
            
            Please:
            1. Use performance_analysis to understand current performance
            2. Use topic_suggestion to identify high-potential topics
            3. Use content_search to assess current coverage
            4. Identify strategic opportunities
            
            Provide a comprehensive gap analysis with actionable recommendations.
            """
            
            result = self.agent_executor.invoke({"input": gap_analysis_input})
            
            return {
                "analysis": result.get("output", ""),
                "content_type": content_type.value if content_type else "all",
                "timeframe": timeframe,
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.84
            }
            
        except Exception as e:
            logger.error(f"Content gap analysis failed: {e}")
            return {
                "analysis": f"Gap analysis failed: {str(e)}",
                "content_type": content_type.value if content_type else "all",
                "timeframe": timeframe,
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.0
            }
    
    def optimize_existing_content(
        self, 
        content: str,
        performance_goals: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Optimize existing content for better performance.
        
        Args:
            content: Content to optimize
            performance_goals: Optional performance targets
            
        Returns:
            Content optimization recommendations
        """
        try:
            # Use tools for optimization analysis
            optimization_input = f"""
            Optimize this existing content for better performance:
            
            Content: "{content[:300]}..."
            
            Please:
            1. Use brand_analysis to assess current brand voice alignment
            2. Use content_optimization to provide specific improvement recommendations
            3. Use performance_analysis to understand benchmarks
            4. Provide actionable optimization steps
            
            Performance goals: {json.dumps(performance_goals) if performance_goals else 'Improve engagement and conversion'}
            """
            
            result = self.agent_executor.invoke({"input": optimization_input})
            
            return {
                "original_content": content[:200] + "..." if len(content) > 200 else content,
                "optimization_recommendations": result.get("output", ""),
                "performance_goals": performance_goals or {},
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.88
            }
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return {
                "original_content": content[:100] + "...",
                "optimization_recommendations": f"Optimization failed: {str(e)}",
                "performance_goals": performance_goals or {},
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.0
            }
    
    def _build_strategy_response(
        self, 
        request: GenerationRequest,
        strategy_output: str,
        reasoning_steps: List[str]
    ) -> AgentResponse:
        """Build comprehensive strategy response.
        
        Args:
            request: Original generation request
            strategy_output: Agent strategy output
            reasoning_steps: List of reasoning steps
            
        Returns:
            AgentResponse with strategy and reasoning
        """
        # Extract key strategy elements
        strategy_content = f"""Content Strategy for {request.content_type.value.title()}:

Topic: {request.prompt}
Target Audience: {request.target_audience or 'Business leaders and decision makers'}
Platform: {getattr(request, 'platform', 'Multi-platform')}

Strategic Approach:
{strategy_output}

Key Strategic Elements:
• Value Proposition: Focus on ROI and business benefits
• Technical Credibility: Include specific data points and case studies
• Brand Voice: Maintain EcoTech's professional yet approachable tone
• Call-to-Action: Provide clear next steps for engagement
• SEO Optimization: Target commercial sustainability keywords

Implementation Recommendations:
1. Begin with compelling hook highlighting business benefits
2. Include 2-3 specific case studies or data points
3. Address common objections and concerns
4. Provide multiple engagement options
5. Optimize for target audience sophistication level

Expected Performance:
• Engagement Rate: 15-25% above average for content type
• Conversion Rate: Target 3.5-4.5% based on audience
• Brand Voice Score: Target 0.9+ alignment
• Time on Page: 20-30% improvement over baseline"""
        
        reasoning = f"""Strategy development reasoning:
{chr(10).join(reasoning_steps)}

Strategic decisions:
- Prioritized business value and ROI messaging
- Focused on target audience pain points and interests
- Incorporated EcoTech brand voice requirements
- Planned for measurable performance outcomes
- Considered competitive differentiation opportunities"""
        
        return AgentResponse(
            content=strategy_content,
            reasoning=reasoning,
            confidence=0.89,
            sources_used=["Performance analytics", "Brand guidelines", "Content examples"],
            brand_voice_score=0.91,
            suggestions=[
                "Execute strategy with consistent messaging across touchpoints",
                "Monitor performance metrics and adjust based on results",
                "Consider A/B testing for optimization opportunities",
                "Plan follow-up content series for sustained engagement"
            ]
        )
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance and usage statistics.
        
        Returns:
            Agent statistics
        """
        return {
            "tools_available": len(self.tools),
            "tool_names": [tool.name for tool in self.tools],
            "current_strategy": bool(self.current_strategy),
            "reasoning_steps": len(self.reasoning_chain),
            "agent_type": "ContentStrategyAgent",
            "capabilities": [
                "Strategic content planning",
                "Multi-step reasoning",
                "Tool-based research",
                "Brand voice analysis",
                "Performance optimization"
            ]
        }
    
    def clear_context(self) -> None:
        """Clear agent context and reasoning chain."""
        self.current_strategy = None
        self.reasoning_chain = []
        logger.info("Cleared ContentStrategyAgent context") 