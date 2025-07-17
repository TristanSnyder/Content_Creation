"""LangChain RAG chains for content creation and analysis."""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import Document
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.memory import ConversationBufferMemory

from src.data.models import ContentType, Platform, GenerationRequest, AgentResponse
from src.rag.mock_llm import MockLLMClient, MockLLMResponse
from src.rag.prompts import (
    CONTENT_GENERATION_PROMPTS,
    BRAND_ANALYSIS_PROMPTS,
    TOPIC_SUGGESTION_PROMPTS,
    IMPROVEMENT_PROMPTS
)

logger = logging.getLogger(__name__)


class EcoTechRAGChains:
    """Comprehensive RAG chains for EcoTech content creation and analysis."""
    
    def __init__(self, retriever, llm_client: MockLLMClient):
        """Initialize RAG chains with retriever and LLM.
        
        Args:
            retriever: LangChain retriever for document retrieval
            llm_client: Mock LLM client for response generation
        """
        self.retriever = retriever
        self.llm = llm_client
        self.memory = ConversationBufferWindowMemory(
            k=5, return_messages=True, memory_key="chat_history"
        )
        
        # Initialize chains
        self._content_generation_chains = {}
        self._brand_analysis_chain = None
        self._topic_suggestion_chain = None
        self._improvement_chain = None
        
        self._initialize_chains()
    
    def _initialize_chains(self) -> None:
        """Initialize all RAG chains."""
        logger.info("Initializing EcoTech RAG chains...")
        
        # Create content generation chains for each content type
        for content_type in ContentType:
            self._content_generation_chains[content_type] = self._create_content_generation_chain(content_type)
        
        # Create specialized analysis chains
        self._brand_analysis_chain = self._create_brand_analysis_chain()
        self._topic_suggestion_chain = self._create_topic_suggestion_chain()
        self._improvement_chain = self._create_improvement_chain()
        
        logger.info(f"Initialized {len(self._content_generation_chains)} content generation chains")
    
    def _create_content_generation_chain(self, content_type: ContentType):
        """Create content generation chain for specific content type."""
        
        # Get content-specific prompt template
        system_prompt = self._get_system_prompt(content_type)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # Create document chain
        document_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=prompt
        )
        
        # Create retrieval chain
        retrieval_chain = create_retrieval_chain(
            retriever=self.retriever,
            combine_docs_chain=document_chain
        )
        
        return retrieval_chain
    
    def _create_brand_analysis_chain(self):
        """Create brand voice analysis chain."""
        
        prompt = PromptTemplate(
            template=BRAND_ANALYSIS_PROMPTS["detailed_analysis"],
            input_variables=["content", "context", "brand_guidelines"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    def _create_topic_suggestion_chain(self):
        """Create topic suggestion chain."""
        
        prompt = PromptTemplate(
            template=TOPIC_SUGGESTION_PROMPTS["strategic_analysis"],
            input_variables=["content_type", "target_audience", "context", "performance_data"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    def _create_improvement_chain(self):
        """Create content improvement chain."""
        
        prompt = PromptTemplate(
            template=IMPROVEMENT_PROMPTS["comprehensive_analysis"],
            input_variables=["content", "context", "performance_goals", "brand_guidelines"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    def generate_content(
        self, 
        request: GenerationRequest,
        use_memory: bool = False
    ) -> AgentResponse:
        """Generate content using RAG chain.
        
        Args:
            request: Content generation request
            use_memory: Whether to use conversation memory
            
        Returns:
            AgentResponse with generated content and metadata
        """
        try:
            # Get appropriate chain for content type
            chain = self._content_generation_chains.get(
                request.content_type, 
                self._content_generation_chains[ContentType.BLOG_POST]
            )
            
            # Prepare input with context
            chain_input = {
                "input": self._build_generation_prompt(request)
            }
            
            # Add memory if requested
            if use_memory:
                chain_input["chat_history"] = self.memory.chat_memory.messages
            
            # Execute chain
            result = chain.invoke(chain_input)
            
            # Extract generated content and context
            generated_content = result.get("answer", "")
            source_docs = result.get("context", [])
            
            # Create agent response
            response = AgentResponse(
                content=generated_content,
                reasoning=f"Generated {request.content_type.value} content using RAG retrieval from {len(source_docs)} relevant documents",
                confidence=0.87,
                sources_used=[doc.metadata.get("title", "Unknown") for doc in source_docs[:3]],
                brand_voice_score=0.85,  # Would be calculated by brand analysis
                suggestions=[
                    "Consider adding specific metrics or case study data",
                    "Ensure call-to-action is clear and compelling",
                    "Review for EcoTech brand voice consistency"
                ]
            )
            
            # Update memory if used
            if use_memory:
                self.memory.save_context(
                    {"input": request.prompt}, 
                    {"output": generated_content}
                )
            
            logger.info(f"Generated {request.content_type.value} content with {len(source_docs)} sources")
            return response
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return AgentResponse(
                content="",
                reasoning=f"Content generation failed: {str(e)}",
                confidence=0.0,
                sources_used=[],
                brand_voice_score=0.0,
                suggestions=["Check input parameters and try again"]
            )
    
    def analyze_brand_voice(
        self, 
        content: str, 
        reference_content_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze content for brand voice consistency.
        
        Args:
            content: Content to analyze
            reference_content_ids: Optional reference content for comparison
            
        Returns:
            Brand voice analysis results
        """
        try:
            # Prepare analysis input
            analysis_input = {
                "query": f'Analyze this content for EcoTech brand voice consistency: "{content}"'
            }
            
            # Execute brand analysis chain
            result = self._brand_analysis_chain.invoke(analysis_input)
            
            # Extract analysis and sources
            analysis_text = result.get("result", "")
            source_docs = result.get("source_documents", [])
            
            # Parse analysis for structured response
            brand_analysis = {
                "content_analyzed": content,
                "analysis": analysis_text,
                "sources_used": [doc.metadata.get("title", "Unknown") for doc in source_docs],
                "confidence": 0.89,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Completed brand voice analysis using {len(source_docs)} reference documents")
            return brand_analysis
            
        except Exception as e:
            logger.error(f"Brand voice analysis failed: {e}")
            return {
                "content_analyzed": content,
                "analysis": f"Analysis failed: {str(e)}",
                "sources_used": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    def suggest_topics(
        self, 
        content_type: ContentType,
        target_audience: Optional[str] = None,
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Suggest content topics based on performance and gaps.
        
        Args:
            content_type: Type of content to suggest topics for
            target_audience: Optional target audience specification
            performance_data: Optional performance data for context
            
        Returns:
            Topic suggestions with rationale
        """
        try:
            # Build topic suggestion query
            query_parts = [
                f"Suggest high-performing topics for {content_type.value} content"
            ]
            
            if target_audience:
                query_parts.append(f"targeting {target_audience}")
            
            if performance_data:
                query_parts.append("based on content performance trends")
            
            query = " ".join(query_parts)
            
            # Execute topic suggestion chain
            result = self._topic_suggestion_chain.invoke({"query": query})
            
            # Extract suggestions and sources
            suggestions_text = result.get("result", "")
            source_docs = result.get("source_documents", [])
            
            # Structure topic suggestions
            topic_suggestions = {
                "content_type": content_type.value,
                "target_audience": target_audience or "General business audience",
                "suggestions": suggestions_text,
                "sources_used": [doc.metadata.get("title", "Unknown") for doc in source_docs],
                "confidence": 0.84,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated topic suggestions for {content_type.value} using {len(source_docs)} sources")
            return topic_suggestions
            
        except Exception as e:
            logger.error(f"Topic suggestion failed: {e}")
            return {
                "content_type": content_type.value,
                "target_audience": target_audience or "Unknown",
                "suggestions": f"Topic suggestion failed: {str(e)}",
                "sources_used": [],
                "confidence": 0.0,
                "generated_at": datetime.now().isoformat()
            }
    
    def suggest_improvements(
        self, 
        content: str,
        performance_goals: Optional[Dict[str, Any]] = None,
        current_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Suggest content improvements using RAG context.
        
        Args:
            content: Content to improve
            performance_goals: Optional performance targets
            current_metrics: Optional current performance metrics
            
        Returns:
            Improvement suggestions with rationale
        """
        try:
            # Build improvement analysis query
            query = f'Analyze this content and suggest specific improvements: "{content[:200]}..."'
            
            if performance_goals:
                query += f" Target goals: {performance_goals}"
            
            # Execute improvement chain
            result = self._improvement_chain.invoke({"query": query})
            
            # Extract improvements and sources
            improvements_text = result.get("result", "")
            source_docs = result.get("source_documents", [])
            
            # Structure improvement suggestions
            improvements = {
                "content_analyzed": content[:200] + "..." if len(content) > 200 else content,
                "improvements": improvements_text,
                "performance_goals": performance_goals or {},
                "current_metrics": current_metrics or {},
                "sources_used": [doc.metadata.get("title", "Unknown") for doc in source_docs],
                "confidence": 0.88,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated improvement suggestions using {len(source_docs)} reference sources")
            return improvements
            
        except Exception as e:
            logger.error(f"Content improvement analysis failed: {e}")
            return {
                "content_analyzed": content[:100] + "...",
                "improvements": f"Improvement analysis failed: {str(e)}",
                "performance_goals": performance_goals or {},
                "current_metrics": current_metrics or {},
                "sources_used": [],
                "confidence": 0.0,
                "generated_at": datetime.now().isoformat()
            }
    
    def conversational_generate(
        self, 
        user_input: str,
        content_type: Optional[ContentType] = None
    ) -> str:
        """Generate content using conversational chain with memory.
        
        Args:
            user_input: User's input/request
            content_type: Optional content type context
            
        Returns:
            Generated response
        """
        try:
            # Create conversational chain
            conversational_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.memory,
                return_source_documents=True
            )
            
            # Generate response
            result = conversational_chain.invoke({"question": user_input})
            
            response = result.get("answer", "")
            source_docs = result.get("source_documents", [])
            
            logger.info(f"Generated conversational response using {len(source_docs)} sources")
            return response
            
        except Exception as e:
            logger.error(f"Conversational generation failed: {e}")
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your request."
    
    def _build_generation_prompt(self, request: GenerationRequest) -> str:
        """Build comprehensive prompt for content generation.
        
        Args:
            request: Generation request with parameters
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            f"Generate {request.content_type.value} content about: {request.prompt}"
        ]
        
        if request.target_audience:
            prompt_parts.append(f"Target audience: {request.target_audience}")
        
        if request.tone:
            prompt_parts.append(f"Tone: {request.tone}")
        
        if request.max_length:
            prompt_parts.append(f"Target length: approximately {request.max_length} words")
        
        prompt_parts.extend([
            "Requirements:",
            "- Follow EcoTech Solutions brand voice (professional, optimistic, solution-focused)",
            "- Include specific data points or examples when possible",
            "- Provide clear value proposition and call-to-action",
            "- Ensure technical accuracy while maintaining accessibility"
        ])
        
        if request.use_rag:
            prompt_parts.append("- Use relevant context from retrieved documents")
        
        return "\n".join(prompt_parts)
    
    def _get_system_prompt(self, content_type: ContentType) -> str:
        """Get system prompt for specific content type.
        
        Args:
            content_type: Content type for specialized prompt
            
        Returns:
            System prompt string
        """
        base_prompt = """You are an expert content creator for EcoTech Solutions, a leading green technology company. 

EcoTech Brand Voice:
- Professional yet approachable
- Optimistic about sustainable future
- Solution-focused and credible
- Educational and informative
- Data-driven with specific examples

Use the provided context documents to inform your response with relevant examples, data points, and technical details."""
        
        content_specific = CONTENT_GENERATION_PROMPTS.get(
            content_type, 
            CONTENT_GENERATION_PROMPTS.get(ContentType.BLOG_POST, "")
        )
        
        return f"{base_prompt}\n\n{content_specific}"
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get statistics about chain usage and performance.
        
        Returns:
            Chain statistics
        """
        return {
            "content_generation_chains": len(self._content_generation_chains),
            "specialized_chains": 3,  # brand, topic, improvement
            "memory_messages": len(self.memory.chat_memory.messages) if self.memory else 0,
            "supported_content_types": [ct.value for ct in self._content_generation_chains.keys()],
            "chain_status": "active"
        }
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        if self.memory:
            self.memory.clear()
            logger.info("Cleared conversation memory")
    
    def export_conversation(self) -> List[Dict[str, str]]:
        """Export conversation history.
        
        Returns:
            List of conversation messages
        """
        if not self.memory:
            return []
        
        messages = []
        for message in self.memory.chat_memory.messages:
            messages.append({
                "type": message.__class__.__name__,
                "content": message.content,
                "timestamp": datetime.now().isoformat()
            })
        
        return messages 