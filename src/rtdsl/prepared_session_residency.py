from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
import hashlib
import json
import math
from typing import Any, Iterable, Mapping


PREPARED_SESSION_RESIDENCY_VERSION = "rtdl.v2_10.prepared_session_residency.goal3873.v1"
PREPARED_SESSION_RESIDENCY_STATUS = "internal_contract_not_release_authorization"
PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY = (
    "Prepared-session residency records explicit cache keys, lifetimes, invalidation "
    "events, and cold/hot timing phases. It does not authorize release action, public "
    "speedup wording, broad RT-core wording, true-zero-copy wording, automatic "
    "partner/backend selection, or app-specific native-engine logic."
)

PREPARED_SESSION_ALLOWED_BACKENDS = (
    "cpu",
    "embree",
    "optix",
    "hiprt",
    "apple_rt",
    "vulkan",
    "oracle",
)
PREPARED_SESSION_ALLOWED_LIFETIME_STATES = (
    "caller_retained",
    "session_retained",
    "released",
)
PREPARED_SESSION_INVALIDATION_EVENTS = (
    "explicit_invalidate",
    "input_fingerprint_change",
    "parameter_change",
    "backend_context_reset",
    "memory_pressure",
    "failure_cleanup",
    "close",
)
PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS = (
    "hausdorff",
    "hausdorff_xhd",
    "xhd",
    "rayjoin",
    "spatial_rayjoin",
    "dbscan",
    "rt_dbscan",
    "barnes",
    "barnes_hut",
    "database",
    "raydb",
    "raydb_style",
    "pip",
    "polygon",
    "knn",
    "robot_collision",
    "contact_manifold",
    "librts",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(value[key]) for key in sorted(value)}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _stable_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()[:24]


def _validate_no_app_terms(text: str, *, label: str) -> None:
    lowered = str(text).lower()
    for term in PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS:
        if term in lowered:
            raise ValueError(f"{label} must remain generic; found app-shaped term {term!r}")


@dataclass(frozen=True)
class RtdlPreparedSessionCacheKey:
    """Stable, explicit key for caller-owned prepared-session reuse."""

    primitive: str
    backend: str
    input_fingerprints: tuple[tuple[str, str], ...]
    parameter_fingerprint: tuple[tuple[str, str], ...] = ()
    partner: str = "none"
    device: str = "unknown"

    def __post_init__(self) -> None:
        primitive = str(self.primitive).strip()
        backend = str(self.backend).strip().lower()
        partner = str(self.partner).strip().lower()
        device = str(self.device).strip().lower()
        if not primitive:
            raise ValueError("prepared-session cache key requires a primitive")
        _validate_no_app_terms(primitive, label="primitive")
        if backend not in PREPARED_SESSION_ALLOWED_BACKENDS:
            raise ValueError("prepared-session backend is not supported")
        if not partner:
            raise ValueError("prepared-session partner must be explicit, or 'none'")
        if not device:
            raise ValueError("prepared-session device must be explicit, or 'unknown'")
        inputs = tuple((str(name), str(fingerprint)) for name, fingerprint in self.input_fingerprints)
        parameters = tuple((str(name), str(fingerprint)) for name, fingerprint in self.parameter_fingerprint)
        if not inputs:
            raise ValueError("prepared-session cache key requires input fingerprints")
        if len({name for name, _ in inputs}) != len(inputs):
            raise ValueError("prepared-session input fingerprints must have unique names")
        object.__setattr__(self, "primitive", primitive)
        object.__setattr__(self, "backend", backend)
        object.__setattr__(self, "partner", partner)
        object.__setattr__(self, "device", device)
        object.__setattr__(self, "input_fingerprints", inputs)
        object.__setattr__(self, "parameter_fingerprint", parameters)

    @property
    def stable_id(self) -> str:
        return _stable_digest(
            {
                "primitive": self.primitive,
                "backend": self.backend,
                "partner": self.partner,
                "device": self.device,
                "inputs": self.input_fingerprints,
                "parameters": self.parameter_fingerprint,
            }
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "stable_id": self.stable_id,
            "primitive": self.primitive,
            "backend": self.backend,
            "partner": self.partner,
            "device": self.device,
            "input_fingerprints": self.input_fingerprints,
            "parameter_fingerprint": self.parameter_fingerprint,
            "explicit_key_required": True,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        }


@dataclass(frozen=True)
class RtdlPreparedSessionResidencyPolicy:
    cache_key: RtdlPreparedSessionCacheKey
    cache_enabled: bool = False
    lifetime_state: str = "session_retained"
    reuse_scope: str = "explicit_user_session"
    invalidation_events: tuple[str, ...] = ("explicit_invalidate", "backend_context_reset", "close")
    cold_prepare_phase: str = "prepare_scene_or_payload"
    hot_query_phase: str = "prepared_query"

    def __post_init__(self) -> None:
        if self.lifetime_state not in PREPARED_SESSION_ALLOWED_LIFETIME_STATES:
            raise ValueError("unsupported prepared-session lifetime state")
        if not str(self.reuse_scope):
            raise ValueError("prepared-session reuse scope must be explicit")
        events = tuple(str(event) for event in self.invalidation_events)
        if not events:
            raise ValueError("prepared-session invalidation events must be explicit")
        for event in events:
            if event not in PREPARED_SESSION_INVALIDATION_EVENTS:
                raise ValueError(f"unsupported prepared-session invalidation event: {event}")
        if bool(self.cache_enabled) and "explicit_invalidate" not in events:
            raise ValueError("enabled prepared-session caches must support explicit_invalidate")
        object.__setattr__(self, "invalidation_events", events)

    @property
    def release_authorized(self) -> bool:
        return False

    @property
    def public_speedup_claim_authorized(self) -> bool:
        return False

    @property
    def broad_rt_core_claim_authorized(self) -> bool:
        return False

    @property
    def true_zero_copy_claim_authorized(self) -> bool:
        return False

    @property
    def automatic_partner_selection_authorized(self) -> bool:
        return False

    @property
    def app_specific_native_engine_logic_allowed(self) -> bool:
        return False

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "status": PREPARED_SESSION_RESIDENCY_STATUS,
            "cache_key": self.cache_key.to_metadata(),
            "cache_enabled": bool(self.cache_enabled),
            "lifetime_state": self.lifetime_state,
            "reuse_scope": self.reuse_scope,
            "invalidation_events": self.invalidation_events,
            "cold_prepare_phase": self.cold_prepare_phase,
            "hot_query_phase": self.hot_query_phase,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
        }


@dataclass(frozen=True)
class RtdlPreparedSessionTimingRecord:
    row_id: str
    prepare_sec: float
    hot_query_sec: float
    repeat: int
    warmup: int = 0
    request_count: int = 1
    prepared_session_policy: RtdlPreparedSessionResidencyPolicy | None = None

    def __post_init__(self) -> None:
        if not str(self.row_id):
            raise ValueError("prepared-session timing record requires a row_id")
        if float(self.prepare_sec) < 0.0:
            raise ValueError("prepare_sec must be non-negative")
        if float(self.hot_query_sec) <= 0.0:
            raise ValueError("hot_query_sec must be positive")
        if int(self.repeat) <= 0:
            raise ValueError("repeat must be positive")
        if int(self.warmup) < 0:
            raise ValueError("warmup must be non-negative")
        if int(self.request_count) <= 0:
            raise ValueError("request_count must be positive")

    @property
    def prepare_to_hot_query_ratio(self) -> float:
        return float(self.prepare_sec) / float(self.hot_query_sec)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "row_id": self.row_id,
            "prepare_sec": float(self.prepare_sec),
            "hot_query_sec": float(self.hot_query_sec),
            "prepare_to_hot_query_ratio": self.prepare_to_hot_query_ratio,
            "repeat": int(self.repeat),
            "warmup": int(self.warmup),
            "request_count": int(self.request_count),
            "prepared_session_policy": (
                None
                if self.prepared_session_policy is None
                else self.prepared_session_policy.to_metadata()
            ),
            "cold_hot_split_required": True,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
        }


class ExplicitPreparedSessionCache:
    """Small explicit cache for caller-owned prepared handles.

    The cache is intentionally not global and does not create sessions. Callers
    provide both the stable key and the prepared value, so cache use is visible
    in user code and in metadata.
    """

    def __init__(self, *, max_entries: int = 8) -> None:
        if int(max_entries) <= 0:
            raise ValueError("prepared-session cache max_entries must be positive")
        self.max_entries = int(max_entries)
        self._entries: OrderedDict[str, tuple[RtdlPreparedSessionCacheKey, Any]] = OrderedDict()
        self._event_log: list[dict[str, Any]] = []

    def put(self, key: RtdlPreparedSessionCacheKey, value: Any) -> str:
        stable_id = key.stable_id
        self._entries[stable_id] = (key, value)
        self._entries.move_to_end(stable_id)
        self._event_log.append({"event": "put", "stable_id": stable_id})
        while len(self._entries) > self.max_entries:
            evicted_id, (_, evicted_value) = self._entries.popitem(last=False)
            self._close_value(evicted_value)
            self._event_log.append({"event": "evict_lru", "stable_id": evicted_id})
        return stable_id

    def get(self, key: RtdlPreparedSessionCacheKey) -> Any | None:
        stable_id = key.stable_id
        entry = self._entries.get(stable_id)
        if entry is None:
            self._event_log.append({"event": "miss", "stable_id": stable_id})
            return None
        self._entries.move_to_end(stable_id)
        self._event_log.append({"event": "hit", "stable_id": stable_id})
        return entry[1]

    def invalidate(
        self,
        key: RtdlPreparedSessionCacheKey,
        *,
        event: str = "explicit_invalidate",
    ) -> bool:
        if event not in PREPARED_SESSION_INVALIDATION_EVENTS:
            raise ValueError("unsupported prepared-session invalidation event")
        stable_id = key.stable_id
        entry = self._entries.pop(stable_id, None)
        self._event_log.append({"event": event, "stable_id": stable_id, "found": entry is not None})
        if entry is None:
            return False
        self._close_value(entry[1])
        return True

    def clear(self, *, event: str = "close") -> None:
        if event not in PREPARED_SESSION_INVALIDATION_EVENTS:
            raise ValueError("unsupported prepared-session invalidation event")
        for stable_id, (_, value) in list(self._entries.items()):
            self._close_value(value)
            self._event_log.append({"event": event, "stable_id": stable_id, "found": True})
        self._entries.clear()

    @property
    def event_log(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(row) for row in self._event_log)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "status": PREPARED_SESSION_RESIDENCY_STATUS,
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
            "stable_ids": tuple(self._entries.keys()),
            "event_log": self.event_log,
            "cache_is_explicit": True,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
        }

    @staticmethod
    def _close_value(value: Any) -> None:
        close = getattr(value, "close", None)
        if callable(close):
            close()


@dataclass(frozen=True)
class RtdlPreparedSessionReuseResult:
    value: Any = field(compare=False, repr=False)
    cache_key: RtdlPreparedSessionCacheKey
    policy: RtdlPreparedSessionResidencyPolicy
    cache_hit: bool
    cache_event_log: tuple[dict[str, Any], ...] = ()

    @property
    def release_authorized(self) -> bool:
        return False

    @property
    def public_speedup_claim_authorized(self) -> bool:
        return False

    @property
    def true_zero_copy_claim_authorized(self) -> bool:
        return False

    @property
    def automatic_partner_selection_authorized(self) -> bool:
        return False

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "stable_id": self.cache_key.stable_id,
            "cache_hit": bool(self.cache_hit),
            "cache_key": self.cache_key.to_metadata(),
            "policy": self.policy.to_metadata(),
            "cache_event_log": self.cache_event_log,
            "explicit_cache_lookup": True,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
        }


def get_or_prepare_explicit_session(
    cache: ExplicitPreparedSessionCache,
    key: RtdlPreparedSessionCacheKey,
    prepare_session: Any,
    *,
    policy: RtdlPreparedSessionResidencyPolicy | None = None,
) -> RtdlPreparedSessionReuseResult:
    """Get a prepared session from an explicit cache or call the caller's prepare function.

    The helper deliberately requires the cache, key, and prepare function from
    the caller. It never chooses a backend, partner, primitive, or device.
    """

    if not isinstance(cache, ExplicitPreparedSessionCache):
        raise TypeError("cache must be an ExplicitPreparedSessionCache")
    if policy is None:
        policy = RtdlPreparedSessionResidencyPolicy(cache_key=key, cache_enabled=True)
    if policy.cache_key != key:
        raise ValueError("prepared-session reuse policy key must match the lookup key")
    cached = cache.get(key)
    if cached is not None:
        return RtdlPreparedSessionReuseResult(
            value=cached,
            cache_key=key,
            policy=policy,
            cache_hit=True,
            cache_event_log=cache.event_log,
        )
    if not callable(prepare_session):
        raise TypeError("prepare_session must be callable on a cache miss")
    value = prepare_session()
    cache.put(key, value)
    return RtdlPreparedSessionReuseResult(
        value=value,
        cache_key=key,
        policy=policy,
        cache_hit=False,
        cache_event_log=cache.event_log,
    )


def make_prepared_session_cache_key(
    *,
    primitive: str,
    backend: str,
    input_fingerprints: Mapping[str, Any],
    parameters: Mapping[str, Any] | None = None,
    partner: str = "none",
    device: str = "unknown",
) -> RtdlPreparedSessionCacheKey:
    return RtdlPreparedSessionCacheKey(
        primitive=primitive,
        backend=backend,
        input_fingerprints=tuple(
            (str(name), _stable_digest(value)) for name, value in sorted(input_fingerprints.items())
        ),
        parameter_fingerprint=tuple(
            (str(name), _stable_digest(value))
            for name, value in sorted((parameters or {}).items())
        ),
        partner=partner,
        device=device,
    )


def describe_prepared_session_residency_contract() -> dict[str, Any]:
    return {
        "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
        "status": PREPARED_SESSION_RESIDENCY_STATUS,
        "allowed_backends": PREPARED_SESSION_ALLOWED_BACKENDS,
        "allowed_lifetime_states": PREPARED_SESSION_ALLOWED_LIFETIME_STATES,
        "invalidation_events": PREPARED_SESSION_INVALIDATION_EVENTS,
        "requires_explicit_cache_key": True,
        "requires_visible_invalidation": True,
        "requires_cold_hot_phase_split": True,
        "no_hidden_automatic_partner_backend_selection": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
        "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
    }


def validate_prepared_session_residency_contract(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = dict(contract or describe_prepared_session_residency_contract())
    errors: list[str] = []
    if metadata.get("contract_version") != PREPARED_SESSION_RESIDENCY_VERSION:
        errors.append("unexpected prepared-session residency contract version")
    if metadata.get("status") != PREPARED_SESSION_RESIDENCY_STATUS:
        errors.append("prepared-session residency status must stay internal/non-authorizing")
    for flag in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "broad_rt_core_claim_authorized",
        "true_zero_copy_claim_authorized",
        "automatic_partner_selection_authorized",
        "app_specific_native_engine_logic_allowed",
    ):
        if metadata.get(flag):
            errors.append(f"{flag} must remain false")
    if not metadata.get("requires_explicit_cache_key"):
        errors.append("prepared-session residency must require explicit cache keys")
    if not metadata.get("requires_visible_invalidation"):
        errors.append("prepared-session residency must require visible invalidation")
    if not metadata.get("requires_cold_hot_phase_split"):
        errors.append("prepared-session residency must require cold/hot phase split")
    return {
        "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
    }


def summarize_prepared_session_timing_records(
    records: Iterable[RtdlPreparedSessionTimingRecord],
) -> dict[str, Any]:
    rows = tuple(record.to_metadata() for record in records)
    ratios = [float(row["prepare_to_hot_query_ratio"]) for row in rows]
    geomean = math.prod(ratios) ** (1.0 / len(ratios)) if ratios else 0.0
    return {
        "contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
        "row_count": len(rows),
        "geomean_prepare_to_hot_query_ratio": geomean,
        "max_prepare_to_hot_query_ratio": max(ratios) if ratios else 0.0,
        "rows": rows,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
    }


__all__ = [
    "ExplicitPreparedSessionCache",
    "PREPARED_SESSION_ALLOWED_BACKENDS",
    "PREPARED_SESSION_ALLOWED_LIFETIME_STATES",
    "PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS",
    "PREPARED_SESSION_INVALIDATION_EVENTS",
    "PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY",
    "PREPARED_SESSION_RESIDENCY_STATUS",
    "PREPARED_SESSION_RESIDENCY_VERSION",
    "RtdlPreparedSessionCacheKey",
    "RtdlPreparedSessionResidencyPolicy",
    "RtdlPreparedSessionReuseResult",
    "RtdlPreparedSessionTimingRecord",
    "describe_prepared_session_residency_contract",
    "get_or_prepare_explicit_session",
    "make_prepared_session_cache_key",
    "summarize_prepared_session_timing_records",
    "validate_prepared_session_residency_contract",
]
