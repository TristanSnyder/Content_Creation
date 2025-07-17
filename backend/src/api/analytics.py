"""Analytics API endpoints for performance metrics and reporting."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel, Field

from src.data.demo_data import get_demo_analytics
from src.data.models import ContentType, Platform

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Request/Response models
class AnalyticsRequest(BaseModel):
    """Request model for analytics data."""
    
    content_ids: Optional[List[str]] = Field(None, description="Specific content IDs to analyze")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    platform: Optional[Platform] = Field(None, description="Filter by platform")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for analysis")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to retrieve")


# API Endpoints
@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days for overview")
) -> Dict[str, Any]:
    """Get comprehensive analytics overview."""
    try:
        logger.info(f"Getting analytics overview for {days} days")
        
        # Get demo analytics data
        analytics_data = get_demo_analytics()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        overview = {
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "key_metrics": {
                "total_pageviews": analytics_data.get("total_pageviews", 125000),
                "total_users": analytics_data.get("total_users", 45000),
                "average_session_duration": analytics_data.get("average_session_duration", 185),
                "bounce_rate": 0.42,
                "conversion_rate": analytics_data.get("conversion_rate_by_platform", {}).get("overall", 0.034)
            },
            "content_performance": {
                "top_performing": analytics_data.get("top_performing_keywords", [])[:5],
                "by_content_type": {
                    "blog_posts": {"views": 65000, "conversion_rate": 0.028},
                    "social_media": {"views": 35000, "engagement_rate": 0.071},
                    "email_newsletters": {"opens": 25000, "click_rate": 0.185},
                    "product_descriptions": {"views": 15000, "conversion_rate": 0.098}
                }
            },
            "traffic_sources": {
                "organic_search": 0.45,
                "direct": 0.25,
                "social": 0.15,
                "referral": 0.10,
                "email": 0.05
            },
            "audience_insights": analytics_data.get("audience_engagement_by_persona", {}),
            "generated_at": datetime.now().isoformat()
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"Analytics overview failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analytics overview failed",
                "message": str(e)
            }
        )


@router.post("/content-performance")
async def analyze_content_performance(
    request: AnalyticsRequest
) -> Dict[str, Any]:
    """Analyze performance of specific content pieces."""
    try:
        logger.info("Analyzing content performance")
        
        analytics_data = get_demo_analytics()
        
        # Simulate content-specific analytics
        content_performance = {}
        
        if request.content_ids:
            for content_id in request.content_ids:
                content_performance[content_id] = {
                    "views": analytics_data.get("monthly_growth_rate", 1250) * 10,
                    "unique_views": analytics_data.get("monthly_growth_rate", 1250) * 8,
                    "engagement_rate": analytics_data.get("average_engagement_rate", 5.2) / 100,
                    "conversion_rate": analytics_data.get("conversion_rate_by_platform", {}).get("blog", 0.028),
                    "time_on_page": analytics_data.get("average_session_duration", 185),
                    "bounce_rate": 0.35,
                    "social_shares": 45,
                    "comments": 12
                }
        else:
            # Aggregate performance
            content_performance = {
                "aggregate": {
                    "total_content_pieces": 47,
                    "average_views": 2400,
                    "average_engagement_rate": analytics_data.get("average_engagement_rate", 5.2) / 100,
                    "average_conversion_rate": 0.031,
                    "top_performing_content": [
                        {"title": "Smart Building ROI Analysis", "views": 8500, "conversion_rate": 0.045},
                        {"title": "Solar Energy Implementation", "views": 7200, "conversion_rate": 0.038},
                        {"title": "Manufacturing Sustainability", "views": 6800, "conversion_rate": 0.042}
                    ]
                }
            }
        
        response = {
            "analysis_type": "content_performance",
            "filters": {
                "content_ids": request.content_ids,
                "content_type": request.content_type.value if request.content_type else None,
                "platform": request.platform.value if request.platform else None
            },
            "performance_data": content_performance,
            "insights": [
                "ROI-focused content performs 25% better than average",
                "Technical content has longer engagement but lower conversion",
                "Social media integration increases shareability by 40%"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Content performance analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Content performance analysis failed",
                "message": str(e)
            }
        )


@router.get("/brand-voice-trends")
async def get_brand_voice_trends(
    days: int = Query(30, ge=7, le=90, description="Number of days for trend analysis")
) -> Dict[str, Any]:
    """Analyze brand voice consistency trends over time."""
    try:
        logger.info(f"Analyzing brand voice trends for {days} days")
        
        # Generate mock trend data
        trend_data = []
        base_score = 0.85
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # Simulate some variation in brand voice scores
            score_variation = (i % 7 - 3) * 0.02  # Weekly pattern
            daily_score = max(0.7, min(1.0, base_score + score_variation))
            
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "brand_voice_score": round(daily_score, 3),
                "content_pieces": 2 if i % 7 < 5 else 1,  # Fewer on weekends
                "consistency_rating": "Excellent" if daily_score >= 0.9 else "Good" if daily_score >= 0.8 else "Needs Improvement"
            })
        
        # Calculate summary statistics
        scores = [item["brand_voice_score"] for item in trend_data]
        avg_score = sum(scores) / len(scores)
        recent_avg = sum(scores[-7:]) / min(7, len(scores))
        trend_direction = "improving" if recent_avg > avg_score else "declining" if recent_avg < avg_score - 0.02 else "stable"
        
        response = {
            "date_range": {
                "start_date": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "days_analyzed": days
            },
            "trend_data": trend_data,
            "summary": {
                "average_score": round(avg_score, 3),
                "recent_average": round(recent_avg, 3),
                "trend_direction": trend_direction,
                "consistency_rating": "Good",
                "total_content_analyzed": sum(item["content_pieces"] for item in trend_data)
            },
            "recommendations": [
                "Maintain current brand voice practices" if trend_direction == "stable" else f"Focus on {trend_direction} brand consistency",
                "Continue regular brand voice training for content creators",
                "Use high-scoring content as templates for future creation"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Brand voice trends analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Brand voice trends analysis failed",
                "message": str(e)
            }
        )


@router.get("/platform-performance")
async def get_platform_performance() -> Dict[str, Any]:
    """Analyze performance across different platforms."""
    try:
        logger.info("Analyzing platform performance")
        
        analytics_data = get_demo_analytics()
        platform_data = analytics_data.get("conversion_rate_by_platform", {})
        
        platform_performance = {
            "linkedin": {
                "conversion_rate": platform_data.get("linkedin", 0.034),
                "engagement_rate": 0.056,
                "reach": 25000,
                "best_content_types": ["Blog posts", "Industry insights", "Case studies"],
                "optimal_posting_times": ["Tuesday-Thursday 9-11 AM", "1-3 PM"]
            },
            "twitter": {
                "conversion_rate": platform_data.get("twitter", 0.019),
                "engagement_rate": 0.063,
                "reach": 35000,
                "best_content_types": ["Quick tips", "Industry news", "Thread series"],
                "optimal_posting_times": ["Monday-Friday 9 AM", "12 PM", "6 PM"]
            },
            "blog": {
                "conversion_rate": platform_data.get("blog", 0.028),
                "time_on_page": 185,
                "bounce_rate": 0.42,
                "best_content_types": ["How-to guides", "ROI analysis", "Case studies"],
                "seo_performance": "Strong"
            },
            "email": {
                "conversion_rate": platform_data.get("email", 0.042),
                "open_rate": 0.245,
                "click_rate": 0.185,
                "best_content_types": ["Newsletters", "Product updates", "Educational content"],
                "optimal_send_times": ["Tuesday-Thursday 10 AM"]
            }
        }
        
        response = {
            "platform_performance": platform_performance,
            "cross_platform_insights": {
                "best_performing_platform": "email",
                "highest_engagement": "twitter",
                "best_conversion": "email",
                "content_synergy": "Blog + LinkedIn combination shows 35% higher engagement"
            },
            "recommendations": [
                "Increase email marketing frequency for better conversion",
                "Use Twitter for engagement and brand awareness",
                "Leverage LinkedIn for B2B lead generation",
                "Cross-promote blog content on social platforms"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Platform performance analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Platform performance analysis failed",
                "message": str(e)
            }
        )


@router.get("/roi-analysis")
async def get_roi_analysis(
    period: str = Query("monthly", description="Analysis period (weekly, monthly, quarterly)")
) -> Dict[str, Any]:
    """Analyze return on investment for content creation efforts."""
    try:
        logger.info(f"Generating ROI analysis for {period} period")
        
        # Simulate ROI calculations
        periods = {
            "weekly": {"multiplier": 0.25, "label": "Weekly"},
            "monthly": {"multiplier": 1.0, "label": "Monthly"},
            "quarterly": {"multiplier": 3.0, "label": "Quarterly"}
        }
        
        period_config = periods.get(period, periods["monthly"])
        base_multiplier = period_config["multiplier"]
        
        roi_data = {
            "period": period_config["label"],
            "content_investment": {
                "creation_hours": int(160 * base_multiplier),  # 160 hours/month base
                "tools_cost": 2500 * base_multiplier,
                "team_cost": 15000 * base_multiplier,
                "total_investment": 17500 * base_multiplier
            },
            "content_returns": {
                "leads_generated": int(85 * base_multiplier),
                "conversions": int(28 * base_multiplier),
                "revenue_attributed": 45000 * base_multiplier,
                "brand_awareness_value": 12000 * base_multiplier,
                "total_return": 57000 * base_multiplier
            },
            "roi_metrics": {
                "roi_percentage": 226,  # (57000 - 17500) / 17500 * 100
                "cost_per_lead": round(17500 * base_multiplier / max(85 * base_multiplier, 1), 2),
                "cost_per_conversion": round(17500 * base_multiplier / max(28 * base_multiplier, 1), 2),
                "revenue_per_content_piece": round(57000 * base_multiplier / max(47 * base_multiplier, 1), 2)
            },
            "performance_by_content_type": {
                "blog_posts": {"roi": 245, "cost_efficiency": "High"},
                "social_media": {"roi": 180, "cost_efficiency": "Medium"},
                "email_newsletters": {"roi": 320, "cost_efficiency": "Very High"},
                "product_descriptions": {"roi": 280, "cost_efficiency": "High"}
            }
        }
        
        response = {
            "roi_analysis": roi_data,
            "insights": [
                f"Content marketing ROI of {roi_data['roi_metrics']['roi_percentage']}% exceeds industry average",
                "Email newsletters provide highest ROI per content piece",
                "Blog content shows strong long-term value generation",
                "Social media content drives brand awareness but lower direct ROI"
            ],
            "recommendations": [
                "Increase investment in email newsletter content",
                "Optimize blog content for search visibility",
                "Develop more case studies and ROI-focused content",
                "Track attribution more accurately for better ROI measurement"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"ROI analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ROI analysis failed",
                "message": str(e)
            }
        )


@router.get("/stats")
async def get_analytics_stats() -> Dict[str, Any]:
    """Get analytics system statistics and capabilities."""
    try:
        analytics_data = get_demo_analytics()
        
        stats = {
            "data_sources": [
                "Content Management System",
                "Google Analytics",
                "Social Media Platforms",
                "Email Marketing Platform",
                "Brand Voice Analysis System"
            ],
            "metrics_tracked": [
                "Page views and unique visitors",
                "Engagement rates and time on page",
                "Conversion rates and lead generation",
                "Brand voice consistency scores",
                "Social media performance",
                "Email marketing metrics",
                "ROI and revenue attribution"
            ],
            "current_data": {
                "total_content_pieces": 47,
                "total_pageviews": analytics_data.get("total_pageviews", 125000),
                "total_users": analytics_data.get("total_users", 45000),
                "average_brand_voice_score": analytics_data.get("average_brand_voice_score", 0.89),
                "monthly_growth_rate": f"{analytics_data.get('monthly_growth_rate', 12.5)}%"
            },
            "reporting_capabilities": [
                "Real-time performance monitoring",
                "Brand voice trend analysis",
                "Platform-specific performance",
                "ROI and revenue attribution",
                "Content optimization recommendations",
                "Audience segmentation analysis"
            ],
            "system_status": "operational",
            "last_updated": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get analytics stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve analytics statistics",
                "message": str(e)
            }
        ) 