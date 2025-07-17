"""Comprehensive demo of vector database capabilities."""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

from src.vector_db.init_db import initialize_vector_database, get_database_client, get_langchain_retrievers
from src.vector_db.chroma_client import ChromaVectorDB
from src.vector_db.langchain_retriever import EcoTechRetriever, BrandVoiceRetriever
from src.data.models import ContentType
from src.data.demo_data import get_brand_guidelines

# Configure rich console for beautiful output
console = Console()
logger = logging.getLogger(__name__)


class VectorDatabaseDemo:
    """Comprehensive demonstration of vector database capabilities."""
    
    def __init__(self, persist_directory: str = "./demo_chroma_db"):
        """Initialize demo with ChromaDB client.
        
        Args:
            persist_directory: Directory for demo database
        """
        self.persist_directory = persist_directory
        self.chroma_client = None
        self.ecotech_retriever = None
        self.brand_voice_retriever = None
        self.langchain_retrievers = {}
    
    def setup_database(self, reset: bool = True) -> bool:
        """Set up the vector database with demo data.
        
        Args:
            reset: Whether to reset existing data
            
        Returns:
            True if setup successful
        """
        console.print("\n[bold blue]🚀 Setting up Vector Database Demo[/bold blue]")
        
        try:
            # Initialize database
            with console.status("[bold green]Initializing ChromaDB..."):
                results = initialize_vector_database(
                    persist_directory=self.persist_directory,
                    reset_existing=reset,
                    load_data=True,
                    run_verification=True
                )
            
            if results["status"] != "success":
                console.print(f"[bold red]❌ Setup failed: {results.get('error', 'Unknown error')}[/bold red]")
                return False
            
            # Get client and retrievers
            self.chroma_client = get_database_client(self.persist_directory)
            self.ecotech_retriever = EcoTechRetriever(self.chroma_client)
            self.brand_voice_retriever = BrandVoiceRetriever(self.chroma_client, "brand_voice_examples")
            self.langchain_retrievers = get_langchain_retrievers(self.chroma_client)
            
            # Display setup results
            self._display_setup_results(results)
            
            console.print("[bold green]✅ Vector database setup complete![/bold green]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Setup failed: {e}[/bold red]")
            return False
    
    def _display_setup_results(self, results: Dict[str, Any]) -> None:
        """Display database setup results in a formatted table."""
        
        # Collections table
        collections_table = Table(title="📚 Collections Created")
        collections_table.add_column("Collection Name", style="cyan")
        collections_table.add_column("Documents", justify="right", style="magenta")
        collections_table.add_column("Content Types", style="green")
        collections_table.add_column("Avg Brand Score", justify="right", style="yellow")
        
        for collection_name, stats in results["verification"]["collections"].items():
            content_types = ", ".join(stats.get("content_types", {}).keys())
            collections_table.add_row(
                collection_name,
                str(stats["count"]),
                content_types[:30] + "..." if len(content_types) > 30 else content_types,
                f"{stats.get('avg_brand_voice_score', 0):.3f}"
            )
        
        console.print(collections_table)
        
        # Verification results
        verification = results["verification"]
        console.print(f"\n[bold]📊 Database Verification:[/bold]")
        console.print(f"  Total Documents: {verification['total_documents']}")
        console.print(f"  Search Test: {verification['search_test']['results_found']} results found")
        console.print(f"  Brand Voice Test: {verification['brand_voice_test'].get('predicted_score', 0):.3f} score")
        console.print(f"  Clustering Test: {verification['clustering_test'].get('clusters_created', 0)} clusters")
    
    def demo_semantic_search(self) -> None:
        """Demonstrate semantic search capabilities."""
        
        console.print("\n[bold blue]🔍 Semantic Search Demo[/bold blue]")
        
        # Test queries with different focuses
        test_queries = [
            {
                "query": "smart building IoT sensors energy efficiency",
                "description": "Technical content about smart buildings",
                "collection": "ecotech_content"
            },
            {
                "query": "solar panel return on investment financial benefits",
                "description": "Financial analysis of renewable energy",
                "collection": "ecotech_content"
            },
            {
                "query": "sustainability tips for small businesses",
                "description": "Practical sustainability advice",
                "collection": "ecotech_content"
            },
            {
                "query": "carbon footprint reduction manufacturing",
                "description": "Manufacturing sustainability strategies",
                "collection": "ecotech_content"
            }
        ]
        
        for test in test_queries:
            console.print(f"\n[bold cyan]Query:[/bold cyan] {test['query']}")
            console.print(f"[dim]{test['description']}[/dim]")
            
            start_time = time.time()
            results = self.chroma_client.similarity_search(
                query=test["query"],
                collection_name=test["collection"],
                k=3
            )
            search_time = time.time() - start_time
            
            # Create results table
            results_table = Table()
            results_table.add_column("Title", style="green", width=40)
            results_table.add_column("Type", style="cyan", width=15)
            results_table.add_column("Score", justify="right", style="magenta", width=8)
            results_table.add_column("Brand Voice", justify="right", style="yellow", width=12)
            
            for result in results:
                results_table.add_row(
                    result.content.title[:37] + "..." if len(result.content.title) > 40 else result.content.title,
                    result.content.content_type.value,
                    f"{result.similarity_score:.3f}",
                    f"{result.content.brand_voice_score:.3f}" if result.content.brand_voice_score else "N/A"
                )
            
            console.print(results_table)
            console.print(f"[dim]Search completed in {search_time:.3f} seconds[/dim]")
    
    def demo_brand_voice_analysis(self) -> None:
        """Demonstrate brand voice analysis using embeddings."""
        
        console.print("\n[bold blue]🎯 Brand Voice Analysis Demo[/bold blue]")
        
        # Test content samples with different voice qualities
        test_content = [
            {
                "content": "Our innovative smart building solutions leverage cutting-edge IoT technology to optimize energy consumption while enhancing occupant comfort. These systems deliver measurable ROI through reduced operating costs and improved sustainability performance.",
                "description": "High-quality brand voice example",
                "expected_score": "High (0.8+)"
            },
            {
                "content": "Check out our AMAZING solar panels! They're super cheap and will save you tons of money. Don't wait - buy now before this incredible deal expires!",
                "description": "Poor brand voice example",
                "expected_score": "Low (0.3-)"
            },
            {
                "content": "Sustainable energy solutions represent a strategic investment in your organization's future, providing predictable cost savings while supporting environmental stewardship goals.",
                "description": "Moderate brand voice alignment",
                "expected_score": "Medium (0.5-0.7)"
            }
        ]
        
        brand_guidelines = get_brand_guidelines()
        
        console.print(f"[bold]Brand Guidelines Summary:[/bold]")
        console.print(f"  Voice: {', '.join(brand_guidelines.voice_characteristics[:3])}")
        console.print(f"  Tone: {', '.join(brand_guidelines.tone_attributes[:3])}")
        
        for i, test in enumerate(test_content, 1):
            console.print(f"\n[bold cyan]Test {i}:[/bold cyan] {test['description']}")
            console.print(f"[dim]Expected: {test['expected_score']}[/dim]")
            console.print(f"[italic]Content: \"{test['content'][:100]}...\"[/italic]")
            
            start_time = time.time()
            analysis = self.chroma_client.brand_voice_analysis(
                content=test["content"],
                collection_name="brand_voice_examples"
            )
            analysis_time = time.time() - start_time
            
            # Create analysis results panel
            analysis_text = f"""
Predicted Score: {analysis.get('predicted_score', 0):.3f}
Confidence: {analysis.get('confidence', 0):.3f}
Examples Used: {len(analysis.get('similar_examples', []))}
Analysis: {analysis.get('analysis', 'No analysis available')}
            """
            
            console.print(Panel(analysis_text, title="Brand Voice Analysis", border_style="green"))
            console.print(f"[dim]Analysis completed in {analysis_time:.3f} seconds[/dim]")
    
    def demo_content_clustering(self) -> None:
        """Demonstrate content clustering and topic discovery."""
        
        console.print("\n[bold blue]📊 Content Clustering Demo[/bold blue]")
        
        # Cluster main content collection
        console.print("[bold]Clustering all content by topic similarity...[/bold]")
        
        start_time = time.time()
        clustering_results = self.chroma_client.cluster_content(
            collection_name="ecotech_content",
            num_clusters=5
        )
        clustering_time = time.time() - start_time
        
        if "error" in clustering_results:
            console.print(f"[red]Clustering failed: {clustering_results['error']}[/red]")
            return
        
        # Display clustering results
        clusters_table = Table(title="🗂️ Content Clusters")
        clusters_table.add_column("Cluster", style="cyan", width=10)
        clusters_table.add_column("Size", justify="right", style="magenta", width=8)
        clusters_table.add_column("Top Topics", style="green", width=30)
        clusters_table.add_column("Content Types", style="yellow", width=25)
        clusters_table.add_column("Sample Titles", style="blue", width=40)
        
        for cluster in clustering_results["clusters"]:
            sample_titles = [doc["title"][:30] + "..." if len(doc["title"]) > 30 else doc["title"] 
                           for doc in cluster["documents"][:2]]
            
            clusters_table.add_row(
                f"Cluster {cluster['id']}",
                str(cluster["size"]),
                ", ".join(cluster["topics"][:3]),
                ", ".join(cluster["content_types"]),
                "\n".join(sample_titles)
            )
        
        console.print(clusters_table)
        console.print(f"[dim]Clustering completed in {clustering_time:.3f} seconds[/dim]")
        
        # Cluster by content type
        console.print("\n[bold]Clustering blog posts by subtopic...[/bold]")
        
        blog_clustering = self.chroma_client.cluster_content(
            collection_name="content_blog_post",
            num_clusters=3,
            content_type_filter=ContentType.BLOG_POST
        )
        
        if "error" not in blog_clustering:
            console.print(f"Created {blog_clustering['num_clusters']} blog topic clusters from {blog_clustering['total_documents']} posts")
    
    def demo_content_recommendations(self) -> None:
        """Demonstrate content recommendation system."""
        
        console.print("\n[bold blue]💡 Content Recommendation Demo[/bold blue]")
        
        # Get a sample content piece to find recommendations for
        sample_search = self.chroma_client.similarity_search(
            query="smart building",
            collection_name="ecotech_content",
            k=1
        )
        
        if not sample_search:
            console.print("[red]No content found for recommendation demo[/red]")
            return
        
        source_content = sample_search[0].content
        console.print(f"[bold]Source Content:[/bold] {source_content.title}")
        console.print(f"[dim]Type: {source_content.content_type.value}[/dim]")
        
        # Get similar content recommendations
        start_time = time.time()
        recommendations = self.ecotech_retriever.content_recommendation_retriever(
            content_id=source_content.id,
            collection_name="ecotech_content",
            k=5,
            diversify=True
        )
        rec_time = time.time() - start_time
        
        # Display recommendations
        rec_table = Table(title="🎯 Content Recommendations")
        rec_table.add_column("Title", style="green", width=40)
        rec_table.add_column("Type", style="cyan", width=15)
        rec_table.add_column("Similarity", justify="right", style="magenta", width=10)
        rec_table.add_column("Brand Score", justify="right", style="yellow", width=12)
        
        for rec in recommendations:
            rec_table.add_row(
                rec.content.title[:37] + "..." if len(rec.content.title) > 40 else rec.content.title,
                rec.content.content_type.value,
                f"{rec.similarity_score:.3f}",
                f"{rec.content.brand_voice_score:.3f}" if rec.content.brand_voice_score else "N/A"
            )
        
        console.print(rec_table)
        console.print(f"[dim]Recommendations generated in {rec_time:.3f} seconds[/dim]")
    
    def demo_hybrid_search(self) -> None:
        """Demonstrate hybrid semantic + keyword search."""
        
        console.print("\n[bold blue]🔄 Hybrid Search Demo[/bold blue]")
        
        query = "solar panel cost ROI investment"
        console.print(f"[bold]Query:[/bold] {query}")
        
        # Compare semantic-only vs hybrid search
        console.print("\n[cyan]Semantic Search Only:[/cyan]")
        semantic_results = self.chroma_client.similarity_search(
            query=query,
            collection_name="ecotech_content",
            k=3
        )
        
        for i, result in enumerate(semantic_results, 1):
            console.print(f"{i}. {result.content.title} (Score: {result.similarity_score:.3f})")
        
        console.print("\n[cyan]Hybrid Search (Semantic + Keywords):[/cyan]")
        hybrid_results = self.ecotech_retriever.hybrid_search(
            query=query,
            collection_name="ecotech_content",
            keyword_weight=0.3,
            semantic_weight=0.7,
            k=3
        )
        
        for i, result in enumerate(hybrid_results, 1):
            console.print(f"{i}. {result.content.title} (Score: {result.similarity_score:.3f})")
    
    def demo_langchain_integration(self) -> None:
        """Demonstrate LangChain retriever integration."""
        
        console.print("\n[bold blue]🔗 LangChain Integration Demo[/bold blue]")
        
        # Test different retriever types
        retriever_tests = [
            {
                "name": "Main Content Retriever",
                "retriever": self.langchain_retrievers["main_content"],
                "query": "energy efficiency smart buildings"
            },
            {
                "name": "Brand Voice Retriever",
                "retriever": self.langchain_retrievers["brand_voice"],
                "query": "sustainable technology solutions"
            }
        ]
        
        for test in retriever_tests:
            console.print(f"\n[bold cyan]{test['name']}:[/bold cyan]")
            console.print(f"Query: {test['query']}")
            
            try:
                start_time = time.time()
                documents = test["retriever"].get_relevant_documents(test["query"])
                retrieval_time = time.time() - start_time
                
                console.print(f"Retrieved {len(documents)} LangChain documents in {retrieval_time:.3f}s")
                
                for i, doc in enumerate(documents[:2], 1):
                    title = doc.metadata.get("title", "Untitled")
                    score = doc.metadata.get("similarity_score", 0)
                    console.print(f"  {i}. {title} (Score: {score:.3f})")
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def demo_performance_metrics(self) -> None:
        """Demonstrate performance and scalability metrics."""
        
        console.print("\n[bold blue]⚡ Performance Metrics Demo[/bold blue]")
        
        # Collection statistics
        stats_table = Table(title="📈 Database Statistics")
        stats_table.add_column("Collection", style="cyan")
        stats_table.add_column("Documents", justify="right", style="magenta")
        stats_table.add_column("Avg Brand Score", justify="right", style="yellow")
        stats_table.add_column("Content Types", style="green")
        
        total_docs = 0
        for collection_name in ["ecotech_content", "brand_voice_examples"]:
            try:
                stats = self.chroma_client.get_collection_stats(collection_name)
                total_docs += stats["count"]
                
                content_types = list(stats["content_types"].keys())[:3]
                stats_table.add_row(
                    collection_name,
                    str(stats["count"]),
                    f"{stats.get('avg_brand_voice_score', 0):.3f}",
                    ", ".join(content_types)
                )
            except Exception as e:
                stats_table.add_row(collection_name, "Error", "N/A", str(e)[:20])
        
        console.print(stats_table)
        
        # Search performance test
        console.print("\n[bold]🏃 Search Performance Test:[/bold]")
        
        queries = [
            "smart building energy efficiency",
            "solar panel ROI analysis",
            "sustainable manufacturing processes"
        ]
        
        total_time = 0
        for query in track(queries, description="Running search performance tests..."):
            start_time = time.time()
            results = self.chroma_client.similarity_search(
                query=query,
                collection_name="ecotech_content",
                k=5
            )
            search_time = time.time() - start_time
            total_time += search_time
        
        avg_search_time = total_time / len(queries)
        console.print(f"Average search time: {avg_search_time:.3f} seconds")
        console.print(f"Total documents indexed: {total_docs}")
        console.print(f"Search throughput: ~{1/avg_search_time:.1f} searches/second")
    
    def run_full_demo(self) -> None:
        """Run the complete vector database capabilities demo."""
        
        console.print(Panel.fit(
            "[bold blue]EcoTech Solutions Vector Database Demo[/bold blue]\n"
            "Showcasing AI-powered semantic search, brand voice analysis,\n"
            "content clustering, and LangChain integration",
            border_style="blue"
        ))
        
        # Setup database
        if not self.setup_database(reset=True):
            return
        
        # Run all demonstrations
        demos = [
            ("Semantic Search", self.demo_semantic_search),
            ("Brand Voice Analysis", self.demo_brand_voice_analysis),
            ("Content Clustering", self.demo_content_clustering),
            ("Content Recommendations", self.demo_content_recommendations),
            ("Hybrid Search", self.demo_hybrid_search),
            ("LangChain Integration", self.demo_langchain_integration),
            ("Performance Metrics", self.demo_performance_metrics)
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
            except Exception as e:
                console.print(f"[red]❌ {demo_name} demo failed: {e}[/red]")
                continue
        
        # Summary
        console.print("\n" + "="*60)
        console.print("[bold green]✅ Vector Database Demo Complete![/bold green]")
        console.print("[dim]All AI-powered features demonstrated successfully[/dim]")


def run_vector_database_demo():
    """Run the comprehensive vector database demonstration."""
    demo = VectorDatabaseDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    
    # Run demo
    run_vector_database_demo() 