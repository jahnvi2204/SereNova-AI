"""
Primary HTTP API (FastAPI). Import `app` from here or from `server` (re-export).
Run: python server.py   or:  uvicorn fastapi_server:app --host 0.0.0.0 --port 5000
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import DuplicateKeyError

from auth import generate_token, hash_password, verify_password, verify_token
from config import Config
from database import db
from gemini_service import gemini_service
from agent_service import agentic_chat_service
from observability.request_metrics import RequestTimingMiddleware
from utils import object_id_to_str, str_to_object_id


logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SeraNova AI API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTimingMiddleware)


def get_bearer_token(authorization: Optional[str] = None) -> Optional[str]:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return authorization.strip() or None


async def require_user(authorization: Optional[str] = Header(None)) -> str:
    tok = get_bearer_token(authorization)
    if not tok:
        raise HTTPException(status_code=401, detail="Authentication required")
    uid = verify_token(tok)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return uid


# --- Auth models & routes ---


class SignupBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    email: str
    password: str
    fullName: str = Field(alias="fullName")


class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
async def fa_signup(body: SignupBody):
    try:
        email = body.email.strip().lower()
        password = body.password
        full_name = body.fullName.strip()
        if not email or not password:
            raise HTTPException(400, "Email and password are required")
        if not full_name:
            raise HTTPException(400, "Full name is required")
        if "@" not in email or "." not in email:
            raise HTTPException(400, "Invalid email format")
        if len(password) < 8:
            raise HTTPException(400, "Password must be at least 8 characters long")
        users = db.get_collection("users")
        if users.find_one({"email": email}):
            raise HTTPException(409, "User with this email already exists")
        doc = {
            "email": email,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "last_login": None,
        }
        result = users.insert_one(doc)
        uid = str(result.inserted_id)
        return {
            "message": "User created successfully",
            "token": generate_token(uid),
            "user": {"id": uid, "email": email, "full_name": full_name},
        }
    except DuplicateKeyError:
        raise HTTPException(409, "User with this email already exists")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Signup: %s", e)
        raise HTTPException(500, "Failed to create user")


@app.post("/auth/login")
async def fa_login(body: LoginBody):
    try:
        email = body.email.strip().lower()
        password = body.password
        if not email or not password:
            raise HTTPException(400, "Email and password are required")
        users = db.get_collection("users")
        user = users.find_one({"email": email})
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(401, "Invalid email or password")
        uid = str(user["_id"])
        users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.utcnow()}})
        return {
            "message": "Login successful",
            "token": generate_token(uid),
            "user": {
                "id": uid,
                "email": user["email"],
                "full_name": user.get("full_name", ""),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login: %s", e)
        raise HTTPException(500, "Failed to authenticate user")


@app.get("/auth/verify")
async def fa_verify(authorization: Optional[str] = Header(None)):
    tok = get_bearer_token(authorization)
    if not tok:
        raise HTTPException(401, "Token is required")
    uid = verify_token(tok)
    if not uid:
        raise HTTPException(401, "Invalid or expired token")
    user = db.get_collection("users").find_one({"_id": ObjectId(uid)})
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "valid": True,
        "user": {
            "id": uid,
            "email": user["email"],
            "full_name": user.get("full_name", ""),
        },
    }


@app.post("/auth/logout")
async def fa_logout():
    return {"message": "Logged out successfully"}


# --- Chat ---


class MessageBody(BaseModel):
    message: str


@app.post("/chat/predict")
async def fa_predict(
    body: MessageBody, user_id: str = Depends(require_user)
):
    r = agentic_chat_service.generate_agent_response(
        user_input=body.message.strip(), history=[]
    )
    return r


@app.post("/chat/predict-public")
async def fa_predict_public(body: MessageBody):
    r = agentic_chat_service.generate_agent_response(
        user_input=body.message.strip(), history=[]
    )
    return r


@app.get("/chat/sessions")
async def fa_sessions(user_id: str = Depends(require_user)):
    sessions = list(
        db.get_collection("chat_sessions").find({"user_id": user_id}).sort("last_updated", -1)
    )
    return {
        "sessions": [
            {
                "id": object_id_to_str(s["_id"]),
                "title": s.get("title", "Untitled Session"),
                "created_at": s["created_at"].isoformat(),
                "last_updated": s["last_updated"].isoformat(),
            }
            for s in sessions
        ]
    }


class CreateSessionBody(BaseModel):
    title: str = "New Chat"


@app.post("/chat/sessions")
async def fa_create_session(
    body: CreateSessionBody, user_id: str = Depends(require_user)
):
    title = (body.title or "New Chat").strip() or "New Chat"
    doc = {
        "user_id": user_id,
        "title": title,
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
    }
    r = db.get_collection("chat_sessions").insert_one(doc)
    sid = str(r.inserted_id)
    return {
        "message": "Session created successfully",
        "session": {
            "id": sid,
            "title": title,
            "created_at": doc["created_at"].isoformat(),
            "last_updated": doc["last_updated"].isoformat(),
        },
    }


def _load_session(sid: str, user_id: str):
    o = str_to_object_id(sid)
    if not o:
        raise HTTPException(400, "Invalid session ID")
    s = db.get_collection("chat_sessions").find_one({"_id": o})
    if not s:
        raise HTTPException(404, "Session not found")
    if s["user_id"] != user_id:
        raise HTTPException(403, "Unauthorized access to session")
    return s, o


@app.get("/chat/sessions/{session_id}/messages")
async def fa_get_messages(
    session_id: str, user_id: str = Depends(require_user)
):
    _load_session(session_id, user_id)
    msgs = list(
        db.get_collection("messages")
        .find({"session_id": session_id})
        .sort("created_at", 1)
    )
    return {
        "messages": [
            {
                "id": object_id_to_str(m["_id"]),
                "message": m.get("message", ""),
                "response": m.get("response", ""),
                "intent": m.get("intent", ""),
                "created_at": m["created_at"].isoformat(),
            }
            for m in msgs
        ]
    }


@app.post("/chat/sessions/{session_id}/messages")
async def fa_add_message(
    session_id: str, body: MessageBody, user_id: str = Depends(require_user)
):
    if not (body.message or "").strip():
        raise HTTPException(400, "Message is required")
    _load_session(session_id, user_id)
    col = db.get_collection("messages")
    past = list(col.find({"session_id": session_id}).sort("created_at", -1).limit(8))
    past.reverse()
    history = [
        {"message": p.get("message", ""), "response": p.get("response", "")} for p in past
    ]
    ai = agentic_chat_service.generate_agent_response(
        user_input=body.message.strip(),
        history=history,
        extra_context={"session_id": session_id},
    )
    existing = col.count_documents({"session_id": session_id})
    is_first = existing == 0
    mdoc = {
        "session_id": session_id,
        "message": body.message.strip(),
        "response": ai.get("response", ""),
        "intent": ai.get("intent", ""),
        "created_at": datetime.utcnow(),
    }
    ins = col.insert_one(mdoc)
    upd: Dict[str, Any] = {"last_updated": datetime.utcnow()}
    if is_first and ai.get("intent"):
        t = str(ai.get("intent", "")).replace("_", " ").title()
        if t:
            upd["title"] = t
    db.get_collection("chat_sessions").update_one(
        {"_id": str_to_object_id(session_id)}, {"$set": upd}
    )
    return {
        "message": "Message added successfully",
        "message_id": str(ins.inserted_id),
        "response": ai.get("response", ""),
        "intent": ai.get("intent", ""),
        "agent": ai.get("agent", {}),
    }


class UpdateSessionBody(BaseModel):
    title: Optional[str] = None


@app.patch("/chat/sessions/{session_id}")
@app.put("/chat/sessions/{session_id}")
async def fa_update_session(
    session_id: str, body: UpdateSessionBody, user_id: str = Depends(require_user)
):
    _, oid = _load_session(session_id, user_id)
    upd: Dict[str, Any] = {}
    if body.title and body.title.strip():
        upd["title"] = body.title.strip()
    if upd:
        upd["last_updated"] = datetime.utcnow()
        db.get_collection("chat_sessions").update_one({"_id": oid}, {"$set": upd})
    s = db.get_collection("chat_sessions").find_one({"_id": oid})
    return {
        "message": "Session updated successfully",
        "session": {
            "id": session_id,
            "title": s.get("title", "Untitled Session") if s else "",
            "last_updated": s["last_updated"].isoformat() if s else "",
        },
    }


@app.delete("/chat/sessions/{session_id}")
async def fa_delete_session(session_id: str, user_id: str = Depends(require_user)):
    _, oid = _load_session(session_id, user_id)
    db.get_collection("messages").delete_many({"session_id": session_id})
    db.get_collection("chat_sessions").delete_one({"_id": oid})
    return {"message": "Session deleted successfully"}


class PlaylistBody(BaseModel):
    mood: str


@app.post("/chat/playlists")
async def fa_playlists(body: PlaylistBody, user_id: str = Depends(require_user)):
    if not (body.mood or "").strip():
        raise HTTPException(400, "Mood is required")
    return gemini_service.get_spotify_playlist_recommendations(body.mood.strip())


class AgentBody(BaseModel):
    message: str
    session_id: str = ""


@app.post("/chat/agent")
async def fa_agent(body: AgentBody, user_id: str = Depends(require_user)):
    if not (body.message or "").strip():
        raise HTTPException(400, "Message is required")
    history: List[Dict[str, Any]] = []
    if (body.session_id or "").strip():
        sid = body.session_id.strip()
        _load_session(sid, user_id)
        past = list(
            db.get_collection("messages")
            .find({"session_id": sid})
            .sort("created_at", -1)
            .limit(8)
        )
        past.reverse()
        history = [
            {"message": p.get("message", ""), "response": p.get("response", "")} for p in past
        ]
    ex: Dict[str, Any] = {}
    if (body.session_id or "").strip():
        ex["session_id"] = body.session_id.strip()
    return agentic_chat_service.generate_agent_response(
        user_input=body.message.strip(), history=history, extra_context=ex or None
    )


@app.get("/")
async def home():
    return {
        "message": "Welcome to the SeraNova AI (Gemini) Chatbot API (FastAPI)!",
        "status": "running",
    }


@app.get("/health")
async def health():
    try:
        h = db.get_collection("users").database
        h.client.admin.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error("Health: %s", e)
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )
