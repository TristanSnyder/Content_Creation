"""Comprehensive demo of LangChain RAG chains and intelligent agents."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.data.models import GenerationRequest, ContentType, Platform
from src.vector_db.chroma_client import ChromaVectorDB
from src.vector_db.langchain_retriever import EcoTechRetriever
from src.rag.chains import EcoTechRAGChains
from src.rag.mock_llm import MockLLMClient
from src.agents.coordinator import AgentCoordinator
from src.agents.content_agent import ContentStrategyAgent
from src.agents.brand_agent import BrandConsistencyAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for beautiful output
console = Console()


class LangChainAgentDemo:
    """Comprehensive demonstration of LangChain RAG and agent capabilities."""
    
    def __init__(self):
        """Initialize demo with all components."""
        self.console = console
        self.vector_db = None
        self.rag_chains = None
        self.agent_coordinator = None
        self.mock_llm = None
        
    async def run_complete_demo(self):
        """Run the complete LangChain RAG and agent demonstration."""
        
        self.console.print(Panel.fit(
            "[bold blue]🤖 EcoTech LangChain RAG & Agent System Demo[/bold blue]\n"
            "[green]Comprehensive demonstration of intelligent content creation agents[/green]",
            border_style="blue"
        ))
        
        try:
            # Initialize system
            await self._initialize_system()
            
            # Demo sections
            await self._demo_rag_chains()
            await self._demo_individual_agents()
            await self._demo_multi_agent_coordination()
            await self._demo_advanced_workflows()
            await self._demo_performance_analytics()
            
            self.console.print(Panel.fit(
                "[bold green]✅ Demo completed successfully![/bold green]\n"
                "[yellow]All LangChain RAG chains and agents demonstrated[/yellow]",
                border_style="green"
            ))
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Demo failed: {e}[/bold red]")
            logger.error(f"Demo failed: {e}")
    
    async def _initialize_system(self):
        """Initialize all system components."""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Initialize vector database
            task1 = progress.add_task("Initializing vector database...", total=None)
            self.vector_db = ChromaVectorDB()
            progress.update(task1, description="✅ Vector database initialized")
            
            # Initialize mock LLM
            task2 = progress.add_task("Setting up mock LLM...", total=None)
            self.mock_llm = MockLLMClient()
            progress.update(task2, description="✅ Mock LLM configured")
            
            # Initialize retriever
            task3 = progress.add_task("Creating LangChain retriever...", total=None)
            retriever = EcoTechRetriever(self.vector_db)
            progress.update(task3, description="✅ LangChain retriever created")
            
            # Initialize RAG chains
            task4 = progress.add_task("Building RAG chains...", total=None)
            self.rag_chains = EcoTechRAGChains(retriever, self.mock_llm)
            progress.update(task4, description="✅ RAG chains built")
            
            # Initialize agent coordinator
            task5 = progress.add_task("Setting up agent coordinator...", total=None)
            self.agent_coordinator = AgentCoordinator(
                self.rag_chains,
                self.vector_db,
                self.mock_llm
            )
            progress.update(task5, description="✅ Agent coordinator ready")
        
        self.console.print("[green]🚀 System initialization complete![/green]\n")
    
    async def _demo_rag_chains(self):
        """Demonstrate RAG chain capabilities."""
        
        self.console.print(Panel.fit(
            "[bold cyan]📚 RAG Chains Demonstration[/bold cyan]\n"
            "[white]Showcasing retrieval-augmented generation capabilities[/white]",
            border_style="cyan"
        ))
        
        # Content generation with RAG
        generation_request = GenerationRequest(
            prompt="Smart building energy optimization strategies for commercial facilities",
            content_type=ContentType.BLOG_POST,
            target_audience="facility managers and building owners",
            tone="professional and informative",
            max_length=800,
            use_rag=True
        )
        
        self.console.print("[yellow]🎯 Generating blog post with RAG context...[/yellow]")
        
        with self.console.status("[bold green]Generating content..."):
            rag_response = self.rag_chains.generate_content(generation_request)
        
        # Display results
        results_table = Table(title="RAG Content Generation Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Content Length", f"{len(rag_response.content)} characters")
        results_table.add_row("Confidence", f"{rag_response.confidence:.3f}")
        results_table.add_row("Brand Voice Score", f"{rag_response.brand_voice_score:.3f}")
        results_table.add_row("Sources Used", str(len(rag_response.sources_used)))
        
        self.console.print(results_table)
        
        # Show content preview
        content_preview = rag_response.content[:300] + "..." if len(rag_response.content) > 300 else rag_response.content
        self.console.print(Panel(
            content_preview,
            title="[bold blue]Generated Content Preview[/bold blue]",
            border_style="blue"
        ))
        
        # Brand voice analysis
        self.console.print("[yellow]🎨 Analyzing brand voice with RAG...[/yellow]")
        
        with self.console.status("[bold green]Analyzing brand voice..."):
            brand_analysis = self.rag_chains.analyze_brand_voice(rag_response.content)
        
        self.console.print(Panel(
            brand_analysis.get("analysis", "Analysis not available")[:400] + "...",
            title="[bold blue]Brand Voice Analysis[/bold blue]",
            border_style="blue"
        ))
        
        # Topic suggestions
        self.console.print("[yellow]💡 Generating strategic topic suggestions...[/yellow]")
        
        with self.console.status("[bold green]Suggesting topics..."):
            topic_suggestions = self.rag_chains.suggest_topics(
                ContentType.BLOG_POST,
                target_audience="business executives"
            )
        
        self.console.print(Panel(
            topic_suggestions.get("suggestions", "No suggestions available")[:400] + "...",
            title="[bold blue]Strategic Topic Suggestions[/bold blue]",
            border_style="blue"
        ))
        
        self.console.print("[green]✅ RAG chains demonstration complete!\n[/green]")
    
    async def _demo_individual_agents(self):
        """Demonstrate individual agent capabilities."""
        
        self.console.print(Panel.fit(
            "[bold magenta]🤖 Individual Agent Demonstrations[/bold magenta]\n"
            "[white]Showcasing specialized agent capabilities with reasoning[/white]",
            border_style="magenta"
        ))
        
        # Content Strategy Agent
        self.console.print("[yellow]📋 Content Strategy Agent - Planning & Generation[/yellow]")
        
        content_agent = self.agent_coordinator.content_agent
        
        # Strategy planning
        strategy_request = GenerationRequest(
            prompt="ROI analysis for commercial solar installations",
            content_type=ContentType.BLOG_POST,
            target_audience="CFOs and financial decision makers",
            tone="analytical and credible"
        )
        
        with self.console.status("[bold green]Planning content strategy..."):
            strategy_response = content_agent.plan_content_strategy(strategy_request)
        
        strategy_table = Table(title="Content Strategy Results")
        strategy_table.add_column("Element", style="cyan")
        strategy_table.add_column("Details", style="green")
        
        strategy_table.add_row("Strategy Confidence", f"{strategy_response.confidence:.3f}")
        strategy_table.add_row("Sources Consulted", str(len(strategy_response.sources_used)))
        strategy_table.add_row("Suggestions Count", str(len(strategy_response.suggestions)))
        
        self.console.print(strategy_table)
        
        # Content generation with reasoning
        with self.console.status("[bold green]Generating content with reasoning..."):
            generation_response = content_agent.generate_with_reasoning(
                "Comprehensive ROI analysis for commercial solar installations with payback calculations",
                ContentType.BLOG_POST,
                use_strategy=True
            )
        
        self.console.print(Panel(
            generation_response.reasoning[:300] + "...",
            title="[bold blue]Agent Reasoning Process[/bold blue]",
            border_style="blue"
        ))
        
        # Brand Consistency Agent
        self.console.print("[yellow]🎨 Brand Consistency Agent - Voice Analysis[/yellow]")
        
        brand_agent = self.agent_coordinator.brand_agent
        
        sample_content = generation_response.content[:500]  # Use generated content sample
        
        with self.console.status("[bold green]Analyzing brand voice consistency..."):
            voice_analysis = brand_agent.analyze_brand_voice(sample_content)
        
        voice_table = Table(title="Brand Voice Analysis Results")
        voice_table.add_column("Dimension", style="cyan")
        voice_table.add_column("Score", style="green")
        voice_table.add_column("Status", style="yellow")
        
        dimension_scores = voice_analysis.get("dimension_scores", {})
        for dimension, score in dimension_scores.items():
            status = "✅ Good" if score >= 0.8 else "⚠️ Needs Improvement" if score >= 0.6 else "❌ Poor"
            voice_table.add_row(dimension.replace("_", " ").title(), f"{score:.3f}", status)
        
        self.console.print(voice_table)
        
        # Voice optimization suggestions
        if voice_analysis.get("overall_score", 0) < 0.8:
            with self.console.status("[bold green]Generating optimization suggestions..."):
                optimization = brand_agent.optimize_voice_alignment(sample_content, target_score=0.9)
            
            if optimization.get("optimization_needed", False):
                self.console.print(Panel(
                    f"Score Gap: {optimization.get('score_gap', 0):.3f}\n"
                    f"Priority Areas: {', '.join(optimization.get('priority_areas', [])[:3])}\n"
                    f"Estimated Effort: {optimization.get('estimated_effort', 'Unknown')}",
                    title="[bold yellow]Optimization Recommendations[/bold yellow]",
                    border_style="yellow"
                ))
        
        self.console.print("[green]✅ Individual agents demonstration complete!\n[/green]")
    
    async def _demo_multi_agent_coordination(self):
        """Demonstrate multi-agent coordination capabilities."""
        
        self.console.print(Panel.fit(
            "[bold red]🔗 Multi-Agent Coordination Demo[/bold red]\n"
            "[white]Showcasing intelligent agent collaboration and workflow orchestration[/white]",
            border_style="red"
        ))
        
        # Complete workflow orchestration
        self.console.print("[yellow]🎭 Orchestrating complete content creation workflow...[/yellow]")
        
        workflow_request = GenerationRequest(
            prompt="Manufacturing sustainability: reducing carbon footprint in production facilities",
            content_type=ContentType.EMAIL_NEWSLETTER,
            target_audience="manufacturing executives and sustainability directors",
            tone="professional and solution-focused",
            max_length=600,
            use_rag=True
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            workflow_task = progress.add_task("Executing multi-agent workflow...", total=None)
            
            workflow_results = await self.agent_coordinator.orchestrate_content_creation(
                workflow_request,
                workflow_id="demo_workflow_001"
            )
            
            progress.update(workflow_task, description="✅ Workflow completed")
        
        # Display workflow results
        workflow_table = Table(title="Multi-Agent Workflow Results")
        workflow_table.add_column("Stage", style="cyan")
        workflow_table.add_column("Agent", style="magenta")
        workflow_table.add_column("Result", style="green")
        workflow_table.add_column("Confidence", style="yellow")
        
        reasoning_chain = workflow_results.get("reasoning_chain", [])
        for step in reasoning_chain:
            workflow_table.add_row(
                f"Step {step['step']}: {step['action']}",
                step['agent'],
                step['result'],
                f"{step['confidence']:.3f}"
            )
        
        self.console.print(workflow_table)
        
        # Overall workflow metrics
        metrics_table = Table(title="Workflow Performance Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        content_metadata = workflow_results.get("content", {}).get("content_metadata", {})
        metrics_table.add_row("Word Count", str(content_metadata.get("word_count", "N/A")))
        metrics_table.add_row("Character Count", str(content_metadata.get("character_count", "N/A")))
        metrics_table.add_row("Reading Time", content_metadata.get("estimated_reading_time", "N/A"))
        metrics_table.add_row("Overall Confidence", f"{workflow_results.get('overall_confidence', 0):.3f}")
        metrics_table.add_row("Workflow Status", workflow_results.get("status", "Unknown"))
        
        self.console.print(metrics_table)
        
        # Brand analysis results
        brand_analysis = workflow_results.get("brand_analysis", {})
        if brand_analysis:
            self.console.print(Panel(
                f"Brand Voice Score: {brand_analysis.get('overall_score', 0):.3f}\n"
                f"Strengths: {', '.join(brand_analysis.get('strengths', [])[:3])}\n"
                f"Improvement Areas: {', '.join(brand_analysis.get('improvement_areas', [])[:3])}",
                title="[bold blue]Brand Analysis Summary[/bold blue]",
                border_style="blue"
            ))
        
        # Distribution plan
        distribution_plan = workflow_results.get("distribution_plan", {})
        if distribution_plan:
            platforms = distribution_plan.get("target_platforms", [])
            self.console.print(Panel(
                f"Target Platforms: {', '.join(platforms)}\n"
                f"Distribution Strategy: Multi-platform optimization\n"
                f"Scheduling: Business hours focus for B2B audience",
                title="[bold green]Distribution Plan[/bold green]",
                border_style="green"
            ))
        
        # Collaborative optimization demo
        self.console.print("[yellow]🤝 Demonstrating collaborative optimization...[/yellow]")
        
        sample_content = "EcoTech Solutions provides innovative green technology systems for commercial buildings, helping reduce energy costs and environmental impact through smart automation and renewable energy integration."
        
        with self.console.status("[bold green]Running collaborative optimization..."):
            optimization_results = await self.agent_coordinator.collaborative_optimization(
                sample_content,
                ContentType.PRODUCT_DESCRIPTION,
                target_metrics={"engagement_rate": 0.08, "conversion_rate": 0.04}
            )
        
        combined_recs = optimization_results.get("combined_recommendations", [])
        if combined_recs:
            opt_table = Table(title="Collaborative Optimization Results")
            opt_table.add_column("Agent", style="magenta")
            opt_table.add_column("Category", style="cyan")
            opt_table.add_column("Recommendation", style="green")
            opt_table.add_column("Priority", style="yellow")
            
            for rec in combined_recs[:5]:  # Show top 5
                opt_table.add_row(
                    rec.get("source", "Unknown"),
                    rec.get("category", "General"),
                    rec.get("recommendation", "No recommendation")[:50] + "...",
                    rec.get("priority", "Medium")
                )
            
            self.console.print(opt_table)
        
        self.console.print("[green]✅ Multi-agent coordination demonstration complete!\n[/green]")
    
    async def _demo_advanced_workflows(self):
        """Demonstrate advanced workflow capabilities."""
        
        self.console.print(Panel.fit(
            "[bold yellow]⚡ Advanced Workflow Demonstrations[/bold yellow]\n"
            "[white]Showcasing sophisticated agent reasoning and tool usage[/white]",
            border_style="yellow"
        ))
        
        # Agent consultation demo
        self.console.print("[yellow]🎯 Agent Consultation - Multi-perspective Analysis[/yellow]")
        
        consultation_query = "How should we approach content strategy for LEED certification topics targeting facility managers?"
        
        with self.console.status("[bold green]Consulting multiple agents..."):
            consultation_results = await self.agent_coordinator.agent_consultation(
                consultation_query,
                context={"content_type": "blog", "audience": "facility_managers"}
            )
        
        agent_responses = consultation_results.get("agent_responses", {})
        consultation_table = Table(title="Multi-Agent Consultation Results")
        consultation_table.add_column("Agent", style="magenta")
        consultation_table.add_column("Perspective", style="cyan")
        consultation_table.add_column("Confidence", style="yellow")
        
        for agent_name, response in agent_responses.items():
            consultation_table.add_row(
                response.get("agent", "Unknown"),
                response.get("response", "No response")[:80] + "...",
                f"{response.get('confidence', 0):.3f}"
            )
        
        self.console.print(consultation_table)
        
        # Show synthesis
        synthesis = consultation_results.get("synthesis", {})
        if synthesis:
            self.console.print(Panel(
                f"Summary: {synthesis.get('summary', 'No summary')}\n"
                f"Confidence: {synthesis.get('confidence', 0):.3f}\n"
                f"Recommended Actions: {len(synthesis.get('recommended_actions', []))} identified",
                title="[bold blue]Consultation Synthesis[/bold blue]",
                border_style="blue"
            ))
        
        # Content gap analysis
        self.console.print("[yellow]📊 Content Gap Analysis - Strategic Planning[/yellow]")
        
        content_agent = self.agent_coordinator.content_agent
        
        with self.console.status("[bold green]Analyzing content gaps..."):
            gap_analysis = content_agent.analyze_content_gaps(
                ContentType.BLOG_POST,
                timeframe="30days"
            )
        
        self.console.print(Panel(
            gap_analysis.get("analysis", "No analysis available")[:400] + "...",
            title="[bold blue]Content Gap Analysis[/bold blue]",
            border_style="blue"
        ))
        
        # Voice drift tracking simulation
        self.console.print("[yellow]📈 Brand Voice Drift Tracking - Consistency Monitoring[/yellow]")
        
        # Simulate content samples over time
        from datetime import timedelta
        base_date = datetime.now()
        
        sample_contents = [
            ("EcoTech delivers innovative sustainable solutions for modern businesses.", base_date - timedelta(days=30)),
            ("Our green technology helps companies reduce costs and environmental impact.", base_date - timedelta(days=20)),
            ("Smart building systems provide amazing energy savings for facilities.", base_date - timedelta(days=10)),
            ("EcoTech Solutions offers proven sustainable innovation for future-ready organizations.", base_date)
        ]
        
        brand_agent = self.agent_coordinator.brand_agent
        
        with self.console.status("[bold green]Tracking voice drift..."):
            drift_analysis = brand_agent.track_voice_drift(sample_contents, window_days=30)
        
        drift_table = Table(title="Brand Voice Drift Analysis")
        drift_table.add_column("Metric", style="cyan")
        drift_table.add_column("Value", style="green")
        
        drift_table.add_row("Sample Count", str(drift_analysis.get("sample_count", 0)))
        drift_table.add_row("Overall Average", f"{drift_analysis.get('overall_average', 0):.3f}")
        drift_table.add_row("Recent Average", f"{drift_analysis.get('recent_average', 0):.3f}")
        drift_table.add_row("Drift Direction", drift_analysis.get("drift_direction", "Unknown"))
        drift_table.add_row("Drift Magnitude", f"{drift_analysis.get('drift_magnitude', 0):.3f}")
        
        self.console.print(drift_table)
        
        self.console.print("[green]✅ Advanced workflows demonstration complete!\n[/green]")
    
    async def _demo_performance_analytics(self):
        """Demonstrate performance analytics and system capabilities."""
        
        self.console.print(Panel.fit(
            "[bold green]📈 Performance Analytics & System Capabilities[/bold green]\n"
            "[white]Showcasing system metrics, performance tracking, and capabilities[/white]",
            border_style="green"
        ))
        
        # System statistics
        self.console.print("[yellow]🔧 System Component Statistics[/yellow]")
        
        # Get stats from all components
        rag_stats = self.rag_chains.get_chain_stats()
        coordinator_stats = self.agent_coordinator.get_coordinator_stats()
        content_agent_stats = self.agent_coordinator.content_agent.get_agent_stats()
        brand_agent_stats = self.agent_coordinator.brand_agent.get_agent_stats()
        
        # Component statistics table
        stats_table = Table(title="System Component Statistics")
        stats_table.add_column("Component", style="cyan")
        stats_table.add_column("Metric", style="magenta")
        stats_table.add_column("Value", style="green")
        
        # RAG chains stats
        stats_table.add_row("RAG Chains", "Content Generation Chains", str(rag_stats.get("content_generation_chains", 0)))
        stats_table.add_row("RAG Chains", "Specialized Chains", str(rag_stats.get("specialized_chains", 0)))
        stats_table.add_row("RAG Chains", "Memory Messages", str(rag_stats.get("memory_messages", 0)))
        
        # Coordinator stats
        stats_table.add_row("Coordinator", "Active Workflows", str(coordinator_stats.get("active_workflows", 0)))
        stats_table.add_row("Coordinator", "Completed Workflows", str(coordinator_stats.get("completed_workflows", 0)))
        stats_table.add_row("Coordinator", "Agents Available", str(coordinator_stats.get("agents_available", 0)))
        
        # Agent stats
        stats_table.add_row("Content Agent", "Tools Available", str(content_agent_stats.get("tools_available", 0)))
        stats_table.add_row("Brand Agent", "Voice Patterns", str(brand_agent_stats.get("voice_patterns", 0)))
        stats_table.add_row("Brand Agent", "Scoring Dimensions", str(brand_agent_stats.get("scoring_dimensions", 0)))
        
        self.console.print(stats_table)
        
        # Capabilities overview
        self.console.print("[yellow]🚀 System Capabilities Overview[/yellow]")
        
        capabilities_table = Table(title="LangChain RAG & Agent Capabilities")
        capabilities_table.add_column("Category", style="cyan")
        capabilities_table.add_column("Capabilities", style="green")
        
        capabilities_table.add_row(
            "RAG Chains",
            "• Content generation with retrieval\n• Brand voice analysis\n• Topic suggestions\n• Content improvement\n• Conversational chains"
        )
        capabilities_table.add_row(
            "Content Strategy Agent",
            "• Strategic planning with reasoning\n• Multi-step content generation\n• Tool-based research\n• Gap analysis\n• Optimization recommendations"
        )
        capabilities_table.add_row(
            "Brand Consistency Agent", 
            "• Voice analysis with embeddings\n• Consistency scoring\n• Voice optimization\n• Drift tracking\n• Pattern recognition"
        )
        capabilities_table.add_row(
            "Multi-Agent Coordination",
            "• Workflow orchestration\n• Collaborative optimization\n• Agent consultation\n• Performance tracking\n• Reasoning chain compilation"
        )
        
        self.console.print(capabilities_table)
        
        # Performance metrics simulation
        self.console.print("[yellow]📊 Performance Metrics Simulation[/yellow]")
        
        performance_table = Table(title="Simulated Performance Metrics")
        performance_table.add_column("Metric", style="cyan")
        performance_table.add_column("Value", style="green")
        performance_table.add_column("Target", style="yellow")
        performance_table.add_column("Status", style="magenta")
        
        metrics = [
            ("Content Generation Speed", "2.3 seconds", "< 3 seconds", "✅ Good"),
            ("Brand Voice Accuracy", "89.2%", "> 85%", "✅ Excellent"),
            ("RAG Retrieval Relevance", "87.6%", "> 80%", "✅ Good"),
            ("Agent Coordination Success", "94.1%", "> 90%", "✅ Excellent"),
            ("Tool Usage Efficiency", "91.8%", "> 85%", "✅ Good")
        ]
        
        for metric, value, target, status in metrics:
            performance_table.add_row(metric, value, target, status)
        
        self.console.print(performance_table)
        
        # Technology stack overview
        self.console.print("[yellow]🛠️ Technology Stack & Integration[/yellow]")
        
        tech_table = Table(title="Technology Stack Components")
        tech_table.add_column("Component", style="cyan")
        tech_table.add_column("Technology", style="green")
        tech_table.add_column("Purpose", style="yellow")
        
        tech_table.add_row("Vector Database", "ChromaDB", "Embeddings storage & semantic search")
        tech_table.add_row("Embeddings", "Sentence Transformers", "Local semantic embeddings")
        tech_table.add_row("LLM Interface", "LangChain + Mock LLM", "Response generation & reasoning")
        tech_table.add_row("RAG Chains", "LangChain Chains", "Retrieval-augmented generation")
        tech_table.add_row("Agent Framework", "LangChain Agents", "Tool-based reasoning agents")
        tech_table.add_row("Orchestration", "Custom Coordinator", "Multi-agent workflow management")
        
        self.console.print(tech_table)
        
        self.console.print("[green]✅ Performance analytics demonstration complete!\n[/green]")
    
    def _format_json_output(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """Format JSON data for display."""
        try:
            json_str = json.dumps(data, indent=2)
            return json_str[:max_length] + "..." if len(json_str) > max_length else json_str
        except Exception:
            return str(data)[:max_length] + "..."


async def main():
    """Run the complete LangChain RAG and agent demonstration."""
    demo = LangChainAgentDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed with error: {e}[/red]")
        logger.error(f"Demo failed: {e}") 