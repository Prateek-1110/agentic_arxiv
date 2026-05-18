import uuid
from typing import List, Dict

from config import MAX_HISTORY_TURNS


_sessions: Dict[str, List[Dict[str, str]]] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = []
    return session_id


def get_history(session_id: str) -> List[Dict[str, str]]:
    return _sessions.get(session_id, [])


def add_turn(session_id: str, role: str, content: str) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []

    _sessions[session_id].append({"role": role, "content": content})

    if len(_sessions[session_id]) > MAX_HISTORY_TURNS * 2:
        _sessions[session_id] = _sessions[session_id][-(MAX_HISTORY_TURNS * 2):]


def delete_session(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def list_sessions() -> List[str]:
    return list(_sessions.keys())