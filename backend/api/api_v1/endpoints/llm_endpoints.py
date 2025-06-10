import logging
import time
import json
import asyncio
import random
from fastapi import APIRouter, HTTPException, Request
from semantic_kernel.contents.chat_history import ChatHistory

from backend.decorators import log_endpoint
from backend.dependencies import chat_completion, execution_settings, kernel
from backend.schemas.llm_schemas import ChatCompletionRequest
from backend.session_context import SessionWrapper
from backend.utils.formatting_utils import (
    format_csv_to_text,
    format_csv_to_markdown_table,
    format_csv_to_html_table
)
from backend.utils.charts import plot_csv_bar_chart

logger = logging.getLogger(__name__)
router = APIRouter()


def get_session_history(request: Request, conversation_id: str):
    histories = request.app.state.session_histories
    if conversation_id not in histories:
        histories[conversation_id] = SessionWrapper(history=ChatHistory())

    session_history = histories[conversation_id]
    session_history.last_used = time.time()
    return session_history


async def retry_with_backoff(func, *args, retries=5, base_delay=1.0, max_delay=30.0, **kwargs):
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Detect 429 Too Many Requests errors (adjust detection as needed)
            if "429" in str(e) or "Too Many Requests" in str(e):
                delay = min(max_delay, base_delay * 2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited, retrying in {delay:.2f}s (attempt {attempt + 1}/{retries})...")
                await asyncio.sleep(delay)
            else:
                raise e
    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")


async def process_chat_completion(
    payload: ChatCompletionRequest,
    request: Request
):
    if not payload.user_message.strip():
        raise HTTPException(status_code=400, detail="User message must be provided")

    conversation_id = payload.conversation_id
    session_history = get_session_history(request, conversation_id)
    session_history.last_used = time.time()

    session_history.history.add_user_message(payload.user_message)

    if payload.system_message != session_history.history.system_message:
        session_history.history.system_message = payload.system_message

    # Call LLM with retry
    result = await retry_with_backoff(
        chat_completion.get_chat_message_content,
        chat_history=session_history.history,
        settings=execution_settings,
        kernel=kernel,
    )

    if not result:
        raise HTTPException(status_code=500, detail="Empty response from AI model")

    tool_result = getattr(result, "tool_calls", None)
    tool_output = ""

    if tool_result and isinstance(tool_result, list):
        for tool_call in tool_result:
            if hasattr(tool_call, "result") and tool_call.result:
                try:
                    parsed = json.loads(tool_call.result)
                    if parsed.get("status") != "success":
                        tool_output += f"\n\n⚠️ Tool Error: {parsed.get('message')}"
                    else:
                        csv_data = parsed.get("raw_csv", "")
                        output_mode = getattr(payload, "output_mode", "text").lower()

                        if output_mode == "table":
                            formatted = format_csv_to_markdown_table(csv_data)
                        elif output_mode == "chart":
                            chart = plot_csv_bar_chart(csv_data)
                            formatted = f'<img src="data:image/png;base64,{chart}"/>'
                        elif output_mode == "html":
                            formatted = format_csv_to_html_table(csv_data)
                        else:
                            formatted = format_csv_to_text(csv_data)

                        tool_output += f"\n\n📊 Tool Result:\n{formatted}"

                except Exception as e:
                    tool_output += f"\n\n⚠️ Failed to parse tool output: {e}"

    final_answer = f"{str(result)}{tool_output}"
    session_history.history.add_message(result)

    return {"answer": final_answer}


@router.post("/chat_completion")
@log_endpoint
async def chat_completion_endpoint(
    payload: ChatCompletionRequest,
    request: Request
):
    return await process_chat_completion(payload, request)


@router.delete("/reset_chat_history")
@log_endpoint
async def reset_chat_history(conversation_id: str, request: Request):
    session_history = get_session_history(request, conversation_id)
    session_history.history.clear()
