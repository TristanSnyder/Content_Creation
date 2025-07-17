"""LangChain RAG (Retrieval-Augmented Generation) module for EcoTech Solutions.

This module provides sophisticated RAG chains, intelligent agents, and custom tools
for content strategy, generation, and analysis using LangChain.

Key Components:
- EcoTechRAGChains: Comprehensive RAG chain implementations
- ContentStrategyAgent: Intelligent agent for content planning and generation
- BrandConsistencyAgent: Specialized agent for brand voice analysis
- Custom LangChain tools for content analysis and optimization
- Multi-agent coordination system
- Mock LLM with realistic responses for demonstration

Features:
- Retrieval-augmented content generation
- Brand voice consistency analysis
- Content performance analysis
- Topic suggestion and gap analysis
- Multi-step agent reasoning
- Tool-based content optimization
"""

from .chains import EcoTechRAGChains
from .mock_llm import MockLLMClient, MockLLMResponse
from .prompts import (
    CONTENT_GENERATION_PROMPTS,
    BRAND_ANALYSIS_PROMPTS,
    TOPIC_SUGGESTION_PROMPTS,
    IMPROVEMENT_PROMPTS
)

__all__ = [
    "EcoTechRAGChains",
    "MockLLMClient",
    "MockLLMResponse",
    "CONTENT_GENERATION_PROMPTS",
    "BRAND_ANALYSIS_PROMPTS", 
    "TOPIC_SUGGESTION_PROMPTS",
    "IMPROVEMENT_PROMPTS"
] 