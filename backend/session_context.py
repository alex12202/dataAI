import time
import asyncio
from dataclasses import dataclass, field
from typing import Dict, cast, AsyncGenerator

from fastapi import FastAPI
from contextlib import asynccontextmanager
from semantic_kernel.contents.chat_history import ChatHistory


# 🧠 Session wrapper s historií a časem posledního použití
@dataclass
class SessionWrapper:
    history: ChatHistory
    last_used: float = field(default_factory=lambda: time.time())


# 🧽 Úklid neaktivních session po určité době
async def cleanup_sessions(app: FastAPI, stop_event: asyncio.Event, ttl_seconds: int = 3600, check_interval: int = 600):
    while not stop_event.is_set():
        now = time.time()
        to_delete = []

        for conversation_id, session in app.state.session_histories.items():
            if now - session.last_used > ttl_seconds:
                to_delete.append(conversation_id)

        for conversation_id in to_delete:
            del app.state.session_histories[conversation_id]
            print(f"🗑️ Session '{conversation_id}' expired and was removed")

        await asyncio.sleep(check_interval)


# 🌀 Lifespan handler (nahrazuje @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("🚀 Starting app with in-memory session history...")
    app.state.session_histories = cast(Dict[str, SessionWrapper], {})
    stop_event = asyncio.Event()

    # Background task: čištění starých sessions
    cleanup_task = asyncio.create_task(cleanup_sessions(app, stop_event))

    try:
        yield
    finally:
        print("🛑 Shutting down, cleaning up...")
        stop_event.set()
        await cleanup_task
