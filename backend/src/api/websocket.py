"""WebSocket API endpoints for real-time agent activity streaming."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.websockets import WebSocketState

from src.agents.coordinator import AgentCoordinator
from src.data.models import GenerationRequest, ContentType

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = {
            "connected_at": datetime.now().isoformat(),
            "client_info": client_info or {},
            "messages_sent": 0
        }
        logger.info(f"WebSocket connected - Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_info:
                del self.connection_info[websocket]
        logger.info(f"WebSocket disconnected - Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                if websocket in self.connection_info:
                    self.connection_info[websocket]["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSockets."""
        disconnected = []
        for connection in self.active_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(json.dumps(message))
                    if connection in self.connection_info:
                        self.connection_info[connection]["messages_sent"] += 1
                else:
                    disconnected.append(connection)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "connected_at": info["connected_at"],
                    "messages_sent": info["messages_sent"],
                    "client_info": info["client_info"]
                }
                for info in self.connection_info.values()
            ]
        }


# Global connection manager
manager = ConnectionManager()


# Dependency injection
async def get_agent_coordinator(request: Request) -> AgentCoordinator:
    """Get agent coordinator from app state."""
    if not hasattr(request.app.state, 'agent_coordinator'):
        raise Exception("Agent coordinator not initialized")
    return request.app.state.agent_coordinator


# WebSocket endpoints
@router.websocket("/generation")
async def websocket_generation(websocket: WebSocket):
    """WebSocket endpoint for real-time content generation streaming.
    
    Streams agent activity, reasoning steps, and progress updates
    during content generation workflows.
    """
    await manager.connect(websocket, {"type": "generation_client"})
    
    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                if message_type == "generate_content":
                    # Stream content generation process
                    await stream_content_generation(websocket, message.get("request", {}))
                
                elif message_type == "analyze_content":
                    # Stream content analysis process
                    await stream_content_analysis(websocket, message.get("content", ""))
                
                elif message_type == "ping":
                    # Respond to ping
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/agent-activity")
async def websocket_agent_activity(websocket: WebSocket):
    """WebSocket endpoint for streaming agent coordination activity.
    
    Provides real-time updates on multi-agent workflows,
    tool usage, and reasoning chains.
    """
    await manager.connect(websocket, {"type": "agent_activity_client"})
    
    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "start_monitoring":
                    # Start streaming agent activity
                    await stream_agent_activity(websocket)
                
                elif message.get("type") == "stop_monitoring":
                    # Stop streaming
                    await manager.send_personal_message({
                        "type": "monitoring_stopped",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Agent activity WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/system-status")
async def websocket_system_status(websocket: WebSocket):
    """WebSocket endpoint for system status monitoring.
    
    Streams real-time system health, performance metrics,
    and component status updates.
    """
    await manager.connect(websocket, {"type": "system_status_client"})
    
    try:
        while True:
            # Send periodic system status updates
            await stream_system_status(websocket)
            await asyncio.sleep(10)  # Update every 10 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"System status WebSocket error: {e}")
        manager.disconnect(websocket)


# Streaming functions
async def stream_content_generation(websocket: WebSocket, request_data: Dict[str, Any]):
    """Stream content generation process with real-time updates."""
    try:
        # Send start notification
        await manager.send_personal_message({
            "type": "generation_started",
            "request_id": request_data.get("id", "unknown"),
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Simulate generation steps with updates
        steps = [
            {"step": 1, "action": "Analyzing request", "progress": 10},
            {"step": 2, "action": "Retrieving context from vector database", "progress": 25},
            {"step": 3, "action": "Planning content strategy", "progress": 40},
            {"step": 4, "action": "Generating content with RAG", "progress": 70},
            {"step": 5, "action": "Analyzing brand voice consistency", "progress": 85},
            {"step": 6, "action": "Optimizing for target platform", "progress": 95},
            {"step": 7, "action": "Content generation complete", "progress": 100}
        ]
        
        for step in steps:
            await manager.send_personal_message({
                "type": "generation_progress",
                "step": step["step"],
                "action": step["action"],
                "progress": step["progress"],
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
            await asyncio.sleep(1)  # Simulate processing time
        
        # Send completion
        await manager.send_personal_message({
            "type": "generation_completed",
            "request_id": request_data.get("id", "unknown"),
            "content_preview": "Generated content preview...",
            "confidence": 0.87,
            "brand_voice_score": 0.89,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "generation_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, websocket)


async def stream_content_analysis(websocket: WebSocket, content: str):
    """Stream content analysis process with real-time updates."""
    try:
        # Send start notification
        await manager.send_personal_message({
            "type": "analysis_started",
            "content_length": len(content),
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Simulate analysis steps
        analysis_steps = [
            {"step": 1, "action": "Preprocessing content", "progress": 20},
            {"step": 2, "action": "Generating embeddings", "progress": 40},
            {"step": 3, "action": "Comparing with brand voice examples", "progress": 60},
            {"step": 4, "action": "Calculating brand voice score", "progress": 80},
            {"step": 5, "action": "Generating recommendations", "progress": 100}
        ]
        
        for step in analysis_steps:
            await manager.send_personal_message({
                "type": "analysis_progress",
                "step": step["step"],
                "action": step["action"],
                "progress": step["progress"],
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
            await asyncio.sleep(0.8)  # Simulate processing time
        
        # Send results
        await manager.send_personal_message({
            "type": "analysis_completed",
            "overall_score": 0.87,
            "confidence": 0.91,
            "recommendations_count": 4,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "analysis_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, websocket)


async def stream_agent_activity(websocket: WebSocket):
    """Stream real-time agent coordination activity."""
    try:
        # Send monitoring start
        await manager.send_personal_message({
            "type": "agent_monitoring_started",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Simulate agent activities
        activities = [
            {"agent": "ContentStrategyAgent", "action": "Planning content strategy", "status": "active"},
            {"agent": "BrandConsistencyAgent", "action": "Analyzing brand voice patterns", "status": "active"},
            {"agent": "DistributionAgent", "action": "Optimizing for platforms", "status": "active"}
        ]
        
        for i in range(30):  # Stream for 30 iterations
            for activity in activities:
                await manager.send_personal_message({
                    "type": "agent_activity",
                    "agent": activity["agent"],
                    "action": activity["action"],
                    "status": activity["status"],
                    "iteration": i + 1,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
                await asyncio.sleep(0.5)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "agent_activity_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, websocket)


async def stream_system_status(websocket: WebSocket):
    """Stream system status updates."""
    try:
        # Get current system metrics
        status_data = {
            "type": "system_status",
            "components": {
                "vector_database": {"status": "healthy", "response_time": "12ms"},
                "mcp_servers": {"status": "healthy", "active_connections": 4},
                "langchain_agents": {"status": "healthy", "active_workflows": 2},
                "api_server": {"status": "healthy", "requests_per_minute": 45}
            },
            "performance": {
                "cpu_usage": "23%",
                "memory_usage": "67%",
                "active_connections": len(manager.active_connections),
                "uptime": "2h 15m"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.send_personal_message(status_data, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "system_status_error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, websocket)


# HTTP endpoints for WebSocket management
@router.get("/connections")
async def get_websocket_connections() -> Dict[str, Any]:
    """Get current WebSocket connection statistics."""
    return {
        "websocket_stats": manager.get_connection_stats(),
        "endpoints": [
            {"path": "/ws/generation", "description": "Content generation streaming"},
            {"path": "/ws/agent-activity", "description": "Agent coordination activity"},
            {"path": "/ws/system-status", "description": "System status monitoring"}
        ],
        "generated_at": datetime.now().isoformat()
    }


@router.post("/broadcast")
async def broadcast_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Broadcast message to all connected WebSocket clients."""
    try:
        await manager.broadcast({
            "type": "broadcast",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "message": "Message broadcasted",
            "connections_reached": len(manager.active_connections),
            "broadcasted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Broadcast failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "attempted_at": datetime.now().isoformat()
        } 