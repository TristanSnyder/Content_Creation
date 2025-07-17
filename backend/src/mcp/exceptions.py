"""Custom exceptions for MCP protocol handling."""

from typing import Optional, Dict, Any


class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize MCP error.
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class MCPAuthenticationError(MCPError):
    """Exception raised when MCP authentication fails."""
    
    def __init__(self, platform: str, message: str = "Authentication failed"):
        """Initialize authentication error.
        
        Args:
            platform: Platform name where authentication failed
            message: Error message
        """
        super().__init__(message, error_code="AUTH_FAILED", details={"platform": platform})
        self.platform = platform


class MCPTimeoutError(MCPError):
    """Exception raised when MCP request times out."""
    
    def __init__(self, timeout_seconds: float, operation: str = "request"):
        """Initialize timeout error.
        
        Args:
            timeout_seconds: Timeout duration that was exceeded
            operation: Operation that timed out
        """
        message = f"MCP {operation} timed out after {timeout_seconds} seconds"
        super().__init__(message, error_code="TIMEOUT", details={
            "timeout_seconds": timeout_seconds,
            "operation": operation
        })
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class MCPRateLimitError(MCPError):
    """Exception raised when MCP rate limit is exceeded."""
    
    def __init__(self, platform: str, retry_after: Optional[int] = None):
        """Initialize rate limit error.
        
        Args:
            platform: Platform that returned rate limit error
            retry_after: Seconds to wait before retry (if provided)
        """
        message = f"Rate limit exceeded for {platform}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        
        super().__init__(message, error_code="RATE_LIMIT", details={
            "platform": platform,
            "retry_after": retry_after
        })
        self.platform = platform
        self.retry_after = retry_after


class MCPConnectionError(MCPError):
    """Exception raised when MCP connection fails."""
    
    def __init__(self, platform: str, original_error: Optional[Exception] = None):
        """Initialize connection error.
        
        Args:
            platform: Platform where connection failed
            original_error: Original exception that caused the connection failure
        """
        message = f"Failed to connect to {platform}"
        if original_error:
            message += f": {str(original_error)}"
        
        super().__init__(message, error_code="CONNECTION_FAILED", details={
            "platform": platform,
            "original_error": str(original_error) if original_error else None
        })
        self.platform = platform
        self.original_error = original_error


class MCPValidationError(MCPError):
    """Exception raised when MCP message validation fails."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        """Initialize validation error.
        
        Args:
            field: Field that failed validation
            message: Validation error message
            value: Value that failed validation
        """
        full_message = f"Validation failed for field '{field}': {message}"
        super().__init__(full_message, error_code="VALIDATION_FAILED", details={
            "field": field,
            "validation_message": message,
            "invalid_value": value
        })
        self.field = field
        self.validation_message = message
        self.invalid_value = value


class MCPProtocolError(MCPError):
    """Exception raised when MCP protocol specification is violated."""
    
    def __init__(self, message: str, protocol_version: str = "1.0"):
        """Initialize protocol error.
        
        Args:
            message: Protocol error message
            protocol_version: MCP protocol version
        """
        super().__init__(message, error_code="PROTOCOL_VIOLATION", details={
            "protocol_version": protocol_version
        })
        self.protocol_version = protocol_version


class MCPResourceNotFoundError(MCPError):
    """Exception raised when requested MCP resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str, platform: str):
        """Initialize resource not found error.
        
        Args:
            resource_type: Type of resource (post, page, user, etc.)
            resource_id: ID of the resource that wasn't found
            platform: Platform where resource was not found
        """
        message = f"{resource_type.title()} with ID '{resource_id}' not found on {platform}"
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", details={
            "resource_type": resource_type,
            "resource_id": resource_id,
            "platform": platform
        })
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.platform = platform


class MCPPermissionError(MCPError):
    """Exception raised when MCP request lacks required permissions."""
    
    def __init__(self, action: str, platform: str, required_permission: Optional[str] = None):
        """Initialize permission error.
        
        Args:
            action: Action that was attempted
            platform: Platform where permission was denied
            required_permission: Required permission level
        """
        message = f"Permission denied for action '{action}' on {platform}"
        if required_permission:
            message += f". Required permission: {required_permission}"
        
        super().__init__(message, error_code="PERMISSION_DENIED", details={
            "action": action,
            "platform": platform,
            "required_permission": required_permission
        })
        self.action = action
        self.platform = platform
        self.required_permission = required_permission 