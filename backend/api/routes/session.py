from fastapi import APIRouter, HTTPException

from memory.session_store import get_history, delete_session, list_sessions

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/{session_id}")
async def get_session_history(session_id: str):
    history = get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session_id, "history": history}


@router.delete("/{session_id}")
async def clear_session(session_id: str):
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"status": "deleted", "session_id": session_id}


@router.get("/")
async def all_sessions():
    return {"sessions": list_sessions()}