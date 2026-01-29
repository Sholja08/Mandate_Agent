from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class AgentDecision(BaseModel):
    """Schema for agent decision output"""

    intent: str = Field(
        description="High-level user intent: GREETING, LIST_MANDATES, VIEW_DETAILS, PAUSE_MANDATE, UNPAUSE_MANDATE, REVOKE_MANDATE"
    )
    thought: str = Field(
        description="Agent's internal reasoning process"
    )
    action: str = Field(
        description="Action to take: get_all_mandates, get_mandate_details, pause_mandate, unpause_mandate, revoke_mandate, output"
    )
    action_input: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters for the action. Use 'query' key for mandate searches, 'message' key for output action"
    )

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "examples": [
                {
                    "intent": "GREETING",
                    "thought": "User is greeting, respond politely",
                    "action": "output",
                    "action_input": {"message": "Hello! How can I help you with your UPI mandates today?"}
                },
                {
                    "intent": "LIST_MANDATES",
                    "thought": "User wants to see all mandates",
                    "action": "get_all_mandates",
                    "action_input": {}
                },
                {
                    "intent": "PAUSE_MANDATE",
                    "thought": "User wants to pause Netflix mandate",
                    "action": "pause_mandate",
                    "action_input": {"query": "Netflix"}
                }
            ]
        }