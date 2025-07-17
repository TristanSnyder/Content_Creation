"""Simple test script to validate vector database functionality."""

import logging
import sys
import traceback
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.vector_db.chroma_client import ChromaVectorDB
from src.vector_db.init_db import initialize_vector_database
from src.data.models import ContentType, ContentItem
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_basic_functionality():
    """Test basic vector database functionality."""
    
    print("🧪 Testing Vector Database Basic Functionality")
    print("=" * 50)
    
    test_results = {
        "initialization": False,
        "data_loading": False,
        "semantic_search": False,
        "brand_voice_analysis": False,
        "clustering": False,
        "overall": False
    }
    
    try:
        # 1. Test initialization
        print("\n1. Testing Database Initialization...")
        
        client = ChromaVectorDB(persist_directory="./test_chroma_db")
        collection = client.create_collection("test_collection", reset_if_exists=True)
        
        print("✅ Database initialization successful")
        test_results["initialization"] = True
        
        # 2. Test data loading
        print("\n2. Testing Data Loading...")
        
        # Create test content
        test_content = [
            ContentItem(
                id="test_1",
                title="Smart Building Energy Management",
                content="Smart buildings use IoT sensors and automated systems to optimize energy consumption and reduce costs while improving occupant comfort.",
                content_type=ContentType.BLOG,
                author="Test Author",
                created_at=datetime.now(),
                tags=["smart buildings", "energy", "IoT"],
                brand_voice_score=0.9
            ),
            ContentItem(
                id="test_2", 
                title="Solar Panel ROI Analysis",
                content="Solar panels provide excellent return on investment through energy cost savings and tax incentives, typically paying for themselves within 6-8 years.",
                content_type=ContentType.BLOG,
                author="Test Author",
                created_at=datetime.now(),
                tags=["solar", "ROI", "renewable energy"],
                brand_voice_score=0.85
            )
        ]
        
        added_count = client.add_documents("test_collection", test_content)
        print(f"✅ Added {added_count} test documents")
        test_results["data_loading"] = True
        
        # 3. Test semantic search
        print("\n3. Testing Semantic Search...")
        
        search_results = client.similarity_search(
            query="building energy optimization",
            collection_name="test_collection",
            k=2
        )
        
        print(f"✅ Found {len(search_results)} search results")
        for i, result in enumerate(search_results, 1):
            print(f"   {i}. {result.content.title} (Score: {result.similarity_score:.3f})")
        
        test_results["semantic_search"] = len(search_results) > 0
        
        # 4. Test brand voice analysis
        print("\n4. Testing Brand Voice Analysis...")
        
        analysis = client.brand_voice_analysis(
            content="Our innovative energy solutions help businesses reduce costs while supporting sustainability goals.",
            collection_name="test_collection"
        )
        
        print(f"✅ Brand voice analysis completed")
        print(f"   Predicted score: {analysis.get('predicted_score', 0):.3f}")
        print(f"   Confidence: {analysis.get('confidence', 0):.3f}")
        
        test_results["brand_voice_analysis"] = analysis.get("predicted_score", 0) > 0
        
        # 5. Test clustering (optional - requires scikit-learn)
        print("\n5. Testing Content Clustering...")
        
        try:
            clustering_result = client.cluster_content(
                collection_name="test_collection",
                num_clusters=2
            )
            
            if "error" not in clustering_result:
                print(f"✅ Created {clustering_result.get('num_clusters', 0)} clusters")
                test_results["clustering"] = True
            else:
                print(f"⚠️  Clustering failed: {clustering_result['error']}")
                test_results["clustering"] = False
                
        except Exception as e:
            print(f"⚠️  Clustering not available: {e}")
            test_results["clustering"] = False
        
        # 6. Test collection stats
        print("\n6. Testing Collection Statistics...")
        
        stats = client.get_collection_stats("test_collection")
        print(f"✅ Collection statistics retrieved")
        print(f"   Documents: {stats['count']}")
        print(f"   Avg brand score: {stats.get('avg_brand_voice_score', 0):.3f}")
        
        # Overall result
        test_results["overall"] = all([
            test_results["initialization"],
            test_results["data_loading"], 
            test_results["semantic_search"],
            test_results["brand_voice_analysis"]
        ])
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        traceback.print_exc()
        test_results["overall"] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    overall_status = "✅ ALL TESTS PASSED" if test_results["overall"] else "❌ SOME TESTS FAILED"
    print(f"\nOverall Result: {overall_status}")
    
    return test_results["overall"]


def test_with_demo_data():
    """Test with full demo data initialization."""
    
    print("\n🚀 Testing with Demo Data")
    print("=" * 50)
    
    try:
        print("Initializing vector database with demo data...")
        
        results = initialize_vector_database(
            persist_directory="./test_demo_chroma_db",
            reset_existing=True,
            load_data=True,
            run_verification=True
        )
        
        if results["status"] == "success":
            print("✅ Demo data initialization successful")
            
            print(f"\nDemo Data Summary:")
            print(f"   Total documents: {results['verification']['total_documents']}")
            print(f"   Collections: {len(results['verification']['collections'])}")
            print(f"   Search test results: {results['verification']['search_test']['results_found']}")
            
            return True
        else:
            print(f"❌ Demo data initialization failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Demo data test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    
    print("🧪 Vector Database Test Suite")
    print("Testing local embeddings and semantic search capabilities")
    print("=" * 60)
    
    # Test basic functionality
    basic_test_passed = test_basic_functionality()
    
    # Test with demo data if basic tests pass
    demo_test_passed = False
    if basic_test_passed:
        demo_test_passed = test_with_demo_data()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏆 Final Test Summary:")
    
    if basic_test_passed and demo_test_passed:
        print("✅ All tests passed! Vector database is working correctly.")
        print("   - Local embeddings are functioning")
        print("   - Semantic search is operational")
        print("   - Brand voice analysis is working")
        print("   - Demo data loaded successfully")
        return True
    elif basic_test_passed:
        print("⚠️  Basic tests passed, but demo data test failed.")
        print("   Core functionality is working.")
        return True
    else:
        print("❌ Basic tests failed. Check dependencies and setup.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 