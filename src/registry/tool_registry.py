"""Registry for tools and executable actions."""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Metadata describing a registered tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_permissions: List[str] = Field(default_factory=list)


class ToolRegistry:
    """Central registry for executable tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Any]] = {}
        self._definitions: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        required_permissions: Optional[List[str]] = None,
    ) -> None:
        """Register a new tool."""
        if name in self._tools:
            logger.warning("Tool '%s' is already registered. Overwriting.", name)
            
        if not description:
            description = inspect.getdoc(func) or "No description provided."
            
        definition = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {},
            required_permissions=required_permissions or [],
        )

        self._tools[name] = func
        self._definitions[name] = definition
        logger.debug("Registered tool: %s", name)

    def unregister(self, name: str) -> None:
        """Unregister a tool."""
        self._tools.pop(name, None)
        self._definitions.pop(name, None)

    def get_tool(self, name: str) -> Optional[Callable[..., Any]]:
        """Retrieve a tool's executable function."""
        return self._tools.get(name)

    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve a tool's definition metadata."""
        return self._definitions.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._definitions.values())

    async def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name with the given arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found.")
            
        # In a real implementation, we would check permissions and validate args here
        if inspect.iscoroutinefunction(tool):
            return await tool(**kwargs)
        return tool(**kwargs)
