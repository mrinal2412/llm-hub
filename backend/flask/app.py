import logging

# from .api.prompt_store import stream_chat, ingest
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from enum import Enum
from pydantic import constr
from dotenv import load_dotenv
from pathlib import Path
from datadog import initialize, statsd
import os

load_dotenv()
app = FastAPI()

class EchoRequest(BaseModel):
    version: str
    prompt:  str
env = os.environ.get("ENV")

class Status(str, Enum):
    LIVE = "LIVE"
    Draft ="Draft"

class PromptIn(BaseModel):
    name:   constr(min_length=1)
    status: Status
# options = {
#     "api_key": os.environ.get("DATADOG_API_KEY"),
#     "app_key": os.environ.get("DATADOG_APP_KEY"),
# }


# initialize(**options)


# Calculate the absolute path to the 'static' directory
BASE_DIR = Path(__file__).resolve().parent
static_files_path = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(static_files_path)), name="static")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logging.error("Internal server error", exc_info=True)
        return Response("Internal server error", status_code=500)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://redex-frontend-alpha.onrender.com",
        "https://redex-frontend-beta.onrender.com/",
        "https://redex-frontend.onrender.com/",
        "https://beta.redex.ai",
        "https://app.redex.ai",
        "https://redex.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(catch_exceptions_middleware)

# app.include_router(retrieve_doc_router)
# app.include_router(create_project_router)
# app.include_router(get_project_router)
# app.include_router(link_github_router)
# app.include_router(retrieve_org_router)
# app.include_router(tasks_router)
# app.include_router(github_webhook_router)
# app.include_router(onboard_user_router)

@app.get("/")
def hello_world():
    return "Hello World"

@app.post("/echo")
async def echo_endpoint(req: EchoRequest):
    
    print(f"👉 Received echo request: version={req.version!r}, prompt={req.prompt!r}")
    
    # Return exactly what you received
    return {
        "version": req.version,
        "prompt":  req.prompt
    }

@app.post("/prompts")
async def ingest_prompt(payload: PromptIn):
    print(
        f"👉 Ingesting prompt → "
        f"name={payload.name!r}, status={payload.status.value!r}"
    )
    # TODO: insert into your PostgreSQL DB here
    return {
        "message": "Prompt received",
        "prompt": {
            "name":   payload.name,
            "status": payload.status.value
        }
    }

@app.websocket("/stream")
async def stream_chat(websocket: WebSocket):
    await websocket.accept()
    prompt = await websocket.receive_text()
    print(prompt)
    await websocket.send_text("what's upp")
    await websocket.close()


# @app.get("/chat")
# async def stream_chat_api():
#     query = "What is serverless?"
#     return StreamingResponse(stream_chat(query), media_type="text/event-stream")


# @app.get("/ingest")
# async def ingest_api():
#     return await ingest()
