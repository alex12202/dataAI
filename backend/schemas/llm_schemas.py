from typing import Optional
from pydantic import BaseModel

class ChatCompletionRequest(BaseModel):
    system_message: Optional[str] = None
    user_message: str
    conversation_id: str
    output_mode: Optional[str] = "text"  # Options: "text", "table", "chart", "html"
