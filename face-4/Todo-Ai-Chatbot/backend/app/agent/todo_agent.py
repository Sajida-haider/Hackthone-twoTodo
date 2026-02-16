"""TodoAgent - AI assistant for task management."""
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
import os

from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.update_task import update_task
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.delete_task import delete_task


class TodoAgent:
    """
    AI agent for managing tasks through natural language.

    Uses OpenAI GPT to understand user intent and invoke appropriate MCP tools.
    """

    def __init__(self):
        """Initialize TodoAgent with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Don't raise error - allow graceful degradation
            self.client = None
            self.model = None
            print("[WARNING] OPENAI_API_KEY not set - chatbot will return error messages")
            return

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4"

        # Define available tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks or filter by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed"],
                                "description": "Filter tasks by status (optional)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

        self.system_prompt = """You are a helpful AI assistant that helps users manage their todo tasks.

You have access to the following task management functions:
- add_task: Create a new task
- list_tasks: Show all tasks or filter by status
- complete_task: Mark a task as done
- update_task: Modify an existing task
- delete_task: Remove a task

When users ask you to do something with their tasks, use the appropriate function.
Always be friendly and confirm what actions you've taken.
If a task operation fails, explain the error in a user-friendly way.
When listing tasks, format them nicely for the user."""

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process a user message and return response with tool calls.

        Args:
            user_id: User identifier
            message: User's message
            conversation_history: Previous messages in conversation

        Returns:
            Dict with response text and tool_calls
        """
        # Check if OpenAI client is available
        if not self.client:
            return {
                "response": "Sorry, the AI chatbot is currently unavailable. The OpenAI API key is not configured. Please contact the administrator to set up the OPENAI_API_KEY environment variable.",
                "tool_calls": []
            }

        try:
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            tool_calls_results = []

            # Execute tool calls if any
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Add user_id to all tool calls
                    function_args["user_id"] = user_id

                    # Execute the appropriate tool
                    if function_name == "add_task":
                        result = await add_task(**function_args)
                    elif function_name == "list_tasks":
                        result = await list_tasks(**function_args)
                    elif function_name == "complete_task":
                        result = await complete_task(**function_args)
                    elif function_name == "update_task":
                        result = await update_task(**function_args)
                    elif function_name == "delete_task":
                        result = await delete_task(**function_args)
                    else:
                        result = {"result": "error", "error_message": f"Unknown function: {function_name}"}

                    tool_calls_results.append({
                        "tool": function_name,
                        "parameters": {k: v for k, v in function_args.items() if k != "user_id"},
                        "result": result.get("result", "error"),
                        "error_message": result.get("error_message")
                    })

                # Get final response after tool execution
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Add tool results
                for i, tool_call in enumerate(assistant_message.tool_calls):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_calls_results[i])
                    })

                # Get final response
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )

                response_text = final_response.choices[0].message.content
            else:
                response_text = assistant_message.content

            return {
                "response": response_text or "I'm here to help with your tasks!",
                "tool_calls": tool_calls_results
            }

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "tool_calls": []
            }


# Global agent instance
_agent_instance = None


def get_agent() -> TodoAgent:
    """Get or create TodoAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TodoAgent()
    return _agent_instance
