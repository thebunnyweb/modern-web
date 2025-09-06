# document_converter.py
from __future__ import annotations
from typing import Any, Dict, List, Optional

# ✅ adjust these to your modules
from app.core.graphql_types import (
    MongoDoc,
    Event, Metadata,
    LatestAction, LatestMessage,
    Intent, IntentRanking,
    Response, ResponseSelector, ResponseSelectorDefault,
)

# ---------- tiny helpers ----------

def _as_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}

def _as_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []

def _get_in(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def _to_str(x: Any) -> Optional[str]:
    return str(x) if x is not None else None

def _to_float(x: Any) -> Optional[float]:
    try:
        return float(x) if x is not None else None
    except Exception:
        return None

def _to_bool(x: Any, default: bool = False) -> bool:
    if isinstance(x, bool):
        return x
    if x in (0, 1):
        return bool(x)
    return default

# ---------- safe builders ----------

def _build_metadata(d: Any) -> Optional[Metadata]:
    d = _as_dict(d)
    if not d:
        return None
    return Metadata(
        model_id=_to_str(d.get("model_id")),
        assistant_id=_to_str(d.get("assistant_id")),
    )

def _build_event(e: Any) -> Event:
    e = _as_dict(e)
    return Event(
        event=_to_str(e.get("event")) or "",
        timestamp=_to_float(e.get("timestamp")) or 0.0,
        metadata=_build_metadata(e.get("metadata")),
        name=_to_str(e.get("name")) or "",
        policy=e.get("policy"),                      # JSON field in your schema
        confidence=_to_float(e.get("confidence")) or 0.0,
        action_text=_to_str(e.get("action_text")),
        hide_rule_turn=_to_bool(e.get("hide_rule_turn"), False),
    )

def _build_latest_action(d: Any) -> LatestAction:
    d = _as_dict(d)
    return LatestAction(
        action_name=_to_str(d.get("action_name")) or "",
    )

def _build_intent(d: Any) -> Intent:
    d = _as_dict(d)
    return Intent(
        name=_to_str(d.get("name")) or "",
        confidence=_to_float(d.get("confidence")) or 0.0,
    )

def _build_intent_ranking_list(items: Any) -> List[IntentRanking]:
    out: List[IntentRanking] = []
    for it in _as_list(items):
        it = _as_dict(it)
        if not it:
            continue
        out.append(IntentRanking(
            name=_to_str(it.get("name")) or "",
            confidence=_to_float(it.get("confidence")) or 0.0,
        ))
    return out

def _build_response_selector(d: Dict[str, Any]) -> ResponseSelector:
    rs = _as_dict(_get_in(d, ["latest_message", "response_selector"], {}))
    rs_default = _as_dict(rs.get("default", {}))

    # response (dict → Response | None)
    response_payload = _as_dict(rs_default.get("response"))
    response_obj = Response(**response_payload) if response_payload else None

    return ResponseSelector(
        all_retrieval_intents=_as_list(rs.get("all_retrieval_intents")),
        default=ResponseSelectorDefault(
            response=response_obj,
            ranking=_as_list(rs_default.get("ranking")),
        ),
    )

def _build_latest_message(d: Dict[str, Any]) -> LatestMessage:
    lm = _as_dict(d.get("latest_message"))
    return LatestMessage(
        intent=_build_intent(_get_in(d, ["latest_message", "intent"], {})),
        entities=_as_list(lm.get("entities")),
        text=_to_str(lm.get("text")),
        message_id=_to_str(lm.get("message_id")),
        metadata=_as_dict(lm.get("metadata")),
        text_tokens=_as_list(lm.get("text_tokens")),
        intent_ranking=_build_intent_ranking_list(lm.get("intent_ranking")),
        response_selector=_build_response_selector(d),
    )

# ---------- public API ----------

def to_mongo_doc(d: dict) -> MongoDoc:
    d = _as_dict(d)

    events = [_build_event(e) for e in _as_list(d.get("events"))]

    return MongoDoc(
        id=_to_str(d.get("_id")) or _to_str(d.get("id")) or "",
        sender_id=_to_str(d.get("sender_id")) or "",
        active_loop=_as_dict(d.get("active_loop")),
        events=events,

        followup_action=d.get("followup_action"),
        latest_action=_build_latest_action(d.get("latest_action", {})),
        latest_action_name=_to_str(d.get("latest_action_name")) or "",
        latest_event_time=_to_float(d.get("latest_event_time")) or 0.0,
        latest_input_channel=_to_str(d.get("latest_input_channel")) or "",

        latest_message=_build_latest_message(d),

        paused=_to_bool(d.get("paused"), False),
        slots=_as_dict(d.get("slots")),
    )




@strawberry.type
class Query:
    @strawberry.field
    async def documents(
        self,
        filter: JSON = strawberry.UNSET,          # arbitrary Mongo filter
        limit: int = 10,
        skip: int = 0,
        sort: Optional[List[SortInput]] = None,
    ) -> list[MongoDoc]:
        # clamp limit to protect DB
        MAX_LIMIT = 200
        lim = max(1, min(limit, MAX_LIMIT))

        # build filter
        mongo_filter = filter or {}
        if mongo_filter is strawberry.UNSET:
            mongo_filter = {}

        # optional: sanitize to prevent bad fields/operators
        mongo_filter = sanitize_filter(mongo_filter)

        # build sort
        sort_spec = []
        for s in (sort or []):
            dir_ = 1 if s.direction >= 0 else -1
            sort_spec.append((s.field, dir_))

        docs = await get_documents(filters=mongo_filter, limit=lim, skip=skip, sort=sort_spec)
        return [to_mongo_doc(d) for d in docs]