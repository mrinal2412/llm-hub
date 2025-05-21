import logging

# from .api.prompt_store import stream_chat, ingest
from fastapi import FastAPI, WebSocket, Depends, HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
from backend.flask.db.psql import get_db
from backend.flask.model.models import Prompt, StatusEnum

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
    name:   str = Field(..., min_length=1)
    version: str = Field(..., min_length=1, description="version, e.g. '1.0.0'")
    status: Status
    body:    str = Field(..., min_length=1, description="The full prompt text")

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

@app.post("/prompts/version")
async def add_prompt_version(
    payload: PromptIn,
    db: AsyncSession = Depends(get_db),
):
    # 1. Reject if name+version already exists
    existing = await db.execute(
        select(Prompt).where(Prompt.name == payload.name, Prompt.version == payload.version)
    )
    if existing.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prompt '{payload.name}' with version '{payload.version}' already exists.",
        )

    # 2. Reject if any version with same name is already marked LIVE
    live_check = await db.execute(
        select(Prompt).where(Prompt.name == payload.name, Prompt.status == StatusEnum.LIVE)
    )
    if live_check.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add version to prompt '{payload.name}' because it is marked as LIVE.",
        )

    # 3. Proceed to insert
    prompt_obj = Prompt(
        name=payload.name,
        version=payload.version,
        status=StatusEnum(payload.status),
        body=payload.body,
    )

    db.add(prompt_obj)
    try:
        await db.commit()
        await db.refresh(prompt_obj)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected DB integrity error while adding version."
        )

    return {
        "id": prompt_obj.id,
        "name": prompt_obj.name,
        "version": prompt_obj.version,
        "status": prompt_obj.status.value,
        "body": prompt_obj.body,
    }




@app.post("/prompts")
async def ingest_prompt(
    payload: PromptIn,
    db:      AsyncSession = Depends(get_db),   # ← inject the DB session
):
   
    print(
        f"Ingesting prompt: "
        f"name={payload.name}, "
        f"version={payload.version}, "
        f"status={payload.status.value}"
        f"body={payload.body!r}"
        
    ) 
    prompt_obj = Prompt(
        name    = payload.name,
        version = payload.version,
        status  = StatusEnum(payload.status),
        body    = payload.body,
    )

    db.add(prompt_obj)
    try:
        await db.commit()
        await db.refresh(prompt_obj)   # get back the generated id
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prompt name '{payload.name}' already exists."
        )

    # 4) Return the new record
    return {
        "id":      prompt_obj.id,
        "name":    prompt_obj.name,
        "version": prompt_obj.version,
        "status":  prompt_obj.status.value,
        "body":    prompt_obj.body,
    }
    
    # TODO: insert into your PostgreSQL DB here
    # return {
    #     "message": "Prompt received",
    #     "prompt": {
    #         "name":   payload.name,
    #         "version": payload.version,
    #         "status": payload.status.value
    #     }
    # }

@app.websocket("/stream")
async def stream_chat(websocket: WebSocket):
    await websocket.accept()
    prompt = await websocket.receive_text()
    print(prompt)
    await websocket.send_text("what's upp")
    await websocket.close()


@app.get("/prompts/{name}/versions")
async def get_prompt_versions(
    name: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.name == name)
    )
    prompts = result.scalars().all()

    if not prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prompts found with name '{name}'"
        )

    return [
        {
            "version": p.version,
            "status": p.status.value,
            "body": p.body
        } for p in prompts
    ]
@app.get("/prompts/{name}/live")
async def get_live_prompt_body(
    name: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.name == name, Prompt.status == StatusEnum.LIVE)
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No LIVE version found for prompt '{name}'"
        )

    return {
        "name": prompt.name,
        "version": prompt.version,
        "body": prompt.body
    }


