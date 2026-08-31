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
PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION = (
    "rtdl.prepared_geometry_session.v2_14_4.public.v1"
)
PREPARED_GEOMETRY_SESSION_API_MATURITY = (
    "public_contract_device_columnar_prepared_pipeline"
)
PREPARED_GEOMETRY_SESSION_REGIME_LABELS = (
    "cold_cli_one_shot",
    "warm_process_fresh",
    "prepared_base_distinct_query_batch",
    "prepared_replay_same_input_diagnostic",
)
PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY = (
    "PreparedGeometrySession is the public RTDL contract for a prepared base "
    "geometry and explicit query batches. It records regime labels, query-batch "
    "fingerprints, timing fields, and run metadata. It does not run geometry by "
    "itself, does not authorize replay-only speedup claims, does not allow same-input "
    "replay to be called query-many, and does not permit app-specific native logic."
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


def _stable_fingerprint(value: Any) -> str:
    if isinstance(value, str) and value:
        return value
    return _stable_digest(value)


def _validate_no_app_terms(text: str, *, label: str) -> None:
    lowered = str(text).lower()
    for term in PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS:
        if term in lowered:
            raise ValueError(f"{label} must remain generic; found app-shaped term {term!r}")


def _coerce_nonnegative_phase_timing(
    phase_timing: Mapping[str, Any] | None,
) -> dict[str, float]:
    timings: dict[str, float] = {}
    for name, value in dict(phase_timing or {}).items():
        key = str(name)
        if not key:
            raise ValueError("phase timing names must be non-empty")
        seconds = float(value)
        if seconds < 0.0:
            raise ValueError("phase timing values must be non-negative")
        timings[key] = seconds
    return timings


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


@dataclass(frozen=True)
class PreparedQueryBatch:
    """Public metadata for one query batch against a prepared geometry session."""

    session_id: str
    batch_id: str
    query_fingerprint: str
    query_count: int
    coordinate_domain_fingerprint: str
    regime_label: str
    distinct_query_batch: bool
    replay_of_batch_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if not str(self.session_id):
            raise ValueError("PreparedQueryBatch requires a session_id")
        if not str(self.batch_id):
            raise ValueError("PreparedQueryBatch requires a batch_id")
        if not str(self.query_fingerprint):
            raise ValueError("PreparedQueryBatch requires a query_fingerprint")
        if int(self.query_count) <= 0:
            raise ValueError("PreparedQueryBatch query_count must be positive")
        if self.regime_label not in PREPARED_GEOMETRY_SESSION_REGIME_LABELS:
            raise ValueError("unsupported prepared-geometry regime label")
        if self.regime_label == "prepared_base_distinct_query_batch":
            if not bool(self.distinct_query_batch):
                raise ValueError("distinct-query regime requires distinct_query_batch=True")
            if self.replay_of_batch_id is not None:
                raise ValueError("distinct-query regime cannot replay a prior batch")
        if self.regime_label == "prepared_replay_same_input_diagnostic":
            if bool(self.distinct_query_batch):
                raise ValueError("same-input replay cannot be marked distinct")
            if not self.replay_of_batch_id:
                raise ValueError("same-input replay must record replay_of_batch_id")
        object.__setattr__(self, "session_id", str(self.session_id))
        object.__setattr__(self, "batch_id", str(self.batch_id))
        object.__setattr__(self, "query_fingerprint", str(self.query_fingerprint))
        object.__setattr__(self, "query_count", int(self.query_count))
        object.__setattr__(
            self,
            "coordinate_domain_fingerprint",
            str(self.coordinate_domain_fingerprint),
        )
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @property
    def same_input_replay_diagnostic(self) -> bool:
        return self.regime_label == "prepared_replay_same_input_diagnostic"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION,
            "session_id": self.session_id,
            "batch_id": self.batch_id,
            "query_fingerprint": self.query_fingerprint,
            "query_count": self.query_count,
            "coordinate_domain_fingerprint": self.coordinate_domain_fingerprint,
            "regime_label": self.regime_label,
            "distinct_query_batch": bool(self.distinct_query_batch),
            "same_input_replay_diagnostic": self.same_input_replay_diagnostic,
            "replay_of_batch_id": self.replay_of_batch_id,
            "metadata": dict(self.metadata),
            "query_many_claim_authorized": (
                self.regime_label == "prepared_base_distinct_query_batch"
            ),
            "replay_only_speedup_claim_authorized": False,
            "claim_boundary": PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY,
        }


@dataclass
class PreparedGeometrySession:
    """Public wrapper for explicit prepared-base and query-batch accounting."""

    primitive: str
    backend: str
    base_fingerprint: Any
    parameters: Mapping[str, Any] | None = None
    partner: str = "none"
    device: str = "unknown"
    coordinate_domain_fingerprint: Any = "unknown"
    base_phase_timing: Mapping[str, Any] | None = None
    owner: Any = field(default=None, compare=False, repr=False)
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)
    _seen_query_batches: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _query_batches: list[PreparedQueryBatch] = field(default_factory=list, init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        primitive = str(self.primitive).strip()
        backend = str(self.backend).strip().lower()
        partner = str(self.partner).strip().lower()
        device = str(self.device).strip().lower()
        if not primitive:
            raise ValueError("PreparedGeometrySession requires a primitive")
        _validate_no_app_terms(primitive, label="primitive")
        if backend not in PREPARED_SESSION_ALLOWED_BACKENDS:
            raise ValueError("PreparedGeometrySession backend is not supported")
        if not partner:
            raise ValueError("PreparedGeometrySession partner must be explicit, or 'none'")
        if not device:
            raise ValueError("PreparedGeometrySession device must be explicit, or 'unknown'")
        self.primitive = primitive
        self.backend = backend
        self.partner = partner
        self.device = device
        self.base_fingerprint = _stable_fingerprint(self.base_fingerprint)
        self.coordinate_domain_fingerprint = _stable_fingerprint(
            self.coordinate_domain_fingerprint
        )
        self.parameters = dict(self.parameters or {})
        self.base_phase_timing = _coerce_nonnegative_phase_timing(self.base_phase_timing)
        self.metadata = dict(self.metadata or {})

    def __enter__(self) -> "PreparedGeometrySession":
        if self._closed:
            raise ValueError("cannot enter a closed PreparedGeometrySession")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @property
    def cache_key(self) -> RtdlPreparedSessionCacheKey:
        return make_prepared_session_cache_key(
            primitive=self.primitive,
            backend=self.backend,
            input_fingerprints={"base": self.base_fingerprint},
            parameters=self.parameters,
            partner=self.partner,
            device=self.device,
        )

    @property
    def session_id(self) -> str:
        return self.cache_key.stable_id

    @property
    def query_batch_count(self) -> int:
        return len(self._query_batches)

    @property
    def distinct_query_batch_count(self) -> int:
        return sum(1 for batch in self._query_batches if batch.distinct_query_batch)

    @property
    def replay_batch_count(self) -> int:
        return sum(1 for batch in self._query_batches if batch.same_input_replay_diagnostic)

    @property
    def closed(self) -> bool:
        return self._closed

    def prepare_query_batch(
        self,
        query_fingerprint: Any,
        *,
        query_count: int = 1,
        batch_id: str | None = None,
        coordinate_domain_fingerprint: Any | None = None,
        require_distinct: bool = False,
        metadata: Mapping[str, Any] | None = None,
    ) -> PreparedQueryBatch:
        if self._closed:
            raise ValueError("cannot prepare a query batch on a closed session")
        query_digest = _stable_fingerprint(query_fingerprint)
        prior_batch_id = self._seen_query_batches.get(query_digest)
        if prior_batch_id is not None:
            if require_distinct:
                raise ValueError(
                    "same-input replay cannot be labeled prepared-base query-many"
                )
            regime_label = "prepared_replay_same_input_diagnostic"
            distinct = False
            replay_of = prior_batch_id
        else:
            regime_label = "prepared_base_distinct_query_batch"
            distinct = True
            replay_of = None
        resolved_batch_id = str(batch_id or f"query_batch_{len(self._query_batches)}")
        domain = (
            self.coordinate_domain_fingerprint
            if coordinate_domain_fingerprint is None
            else _stable_fingerprint(coordinate_domain_fingerprint)
        )
        batch = PreparedQueryBatch(
            session_id=self.session_id,
            batch_id=resolved_batch_id,
            query_fingerprint=query_digest,
            query_count=int(query_count),
            coordinate_domain_fingerprint=domain,
            regime_label=regime_label,
            distinct_query_batch=distinct,
            replay_of_batch_id=replay_of,
            metadata=dict(metadata or {}),
        )
        self._query_batches.append(batch)
        if prior_batch_id is None:
            self._seen_query_batches[query_digest] = resolved_batch_id
        return batch

    def run_metadata(
        self,
        query_batch: PreparedQueryBatch,
        *,
        output: str = "device_columns",
        phase_timing: Mapping[str, Any] | None = None,
        device_residency: Mapping[str, Any] | None = None,
        result_metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if query_batch.session_id != self.session_id:
            raise ValueError("query batch does not belong to this prepared session")
        if not str(output):
            raise ValueError("prepared-session run output must be named")
        timings = _coerce_nonnegative_phase_timing(phase_timing)
        residency = dict(device_residency or {})
        if residency.get("materializes_host_rows_for_bridge"):
            residency.setdefault("device_resident_candidate", False)
        return {
            "contract_version": PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION,
            "api_maturity": PREPARED_GEOMETRY_SESSION_API_MATURITY,
            "session": self.to_metadata(include_batches=False),
            "query_batch": query_batch.to_metadata(),
            "output": str(output),
            "phase_timing": timings,
            "device_residency": residency,
            "result_metadata": dict(result_metadata or {}),
            "regime_label": query_batch.regime_label,
            "same_input_replay_is_diagnostic": query_batch.same_input_replay_diagnostic,
            "query_many_claim_authorized": (
                query_batch.regime_label == "prepared_base_distinct_query_batch"
            ),
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
            "claim_boundary": PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY,
        }

    def to_metadata(self, *, include_batches: bool = True) -> dict[str, Any]:
        metadata = {
            "contract_version": PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION,
            "api_maturity": PREPARED_GEOMETRY_SESSION_API_MATURITY,
            "session_id": self.session_id,
            "primitive": self.primitive,
            "backend": self.backend,
            "partner": self.partner,
            "device": self.device,
            "base_fingerprint": self.base_fingerprint,
            "coordinate_domain_fingerprint": self.coordinate_domain_fingerprint,
            "parameters": dict(self.parameters),
            "base_phase_timing": dict(self.base_phase_timing),
            "query_batch_count": self.query_batch_count,
            "distinct_query_batch_count": self.distinct_query_batch_count,
            "replay_batch_count": self.replay_batch_count,
            "regime_labels": PREPARED_GEOMETRY_SESSION_REGIME_LABELS,
            "same_input_replay_must_be_diagnostic": True,
            "distinct_query_batch_required_for_query_many": True,
            "cold_cli_one_shot_is_separate_from_warm_process_fresh": True,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
            "metadata": dict(self.metadata),
            "closed": self._closed,
            "claim_boundary": PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY,
        }
        if include_batches:
            metadata["query_batches"] = tuple(
                batch.to_metadata() for batch in self._query_batches
            )
        return metadata

    def close(self) -> None:
        if self._closed:
            return
        close = getattr(self.owner, "close", None)
        if callable(close):
            close()
        self._closed = True


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


def describe_prepared_geometry_session_contract() -> dict[str, Any]:
    return {
        "contract_version": PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION,
        "api_maturity": PREPARED_GEOMETRY_SESSION_API_MATURITY,
        "regime_labels": PREPARED_GEOMETRY_SESSION_REGIME_LABELS,
        "wraps_existing_prepared_session_residency_substrate": True,
        "requires_explicit_base_fingerprint": True,
        "requires_explicit_query_batch_fingerprint": True,
        "same_input_replay_must_be_diagnostic": True,
        "distinct_query_batch_required_for_query_many": True,
        "cold_cli_one_shot_is_separate_from_warm_process_fresh": True,
        "phase_timing_fields_are_metadata_not_measurements": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
        "claim_boundary": PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY,
    }


def prepared_geometry_session(
    *,
    primitive: str,
    backend: str,
    base_fingerprint: Any,
    parameters: Mapping[str, Any] | None = None,
    partner: str = "none",
    device: str = "unknown",
    coordinate_domain_fingerprint: Any = "unknown",
    base_phase_timing: Mapping[str, Any] | None = None,
    owner: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> PreparedGeometrySession:
    return PreparedGeometrySession(
        primitive=primitive,
        backend=backend,
        base_fingerprint=base_fingerprint,
        parameters=parameters,
        partner=partner,
        device=device,
        coordinate_domain_fingerprint=coordinate_domain_fingerprint,
        base_phase_timing=base_phase_timing,
        owner=owner,
        metadata=dict(metadata or {}),
    )


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


def validate_prepared_geometry_session_contract(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = dict(contract or describe_prepared_geometry_session_contract())
    errors: list[str] = []
    if metadata.get("contract_version") != PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION:
        errors.append("unexpected prepared-geometry-session contract version")
    if tuple(metadata.get("regime_labels", ())) != PREPARED_GEOMETRY_SESSION_REGIME_LABELS:
        errors.append("prepared-geometry-session regime labels changed")
    for flag in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "automatic_partner_selection_authorized",
        "app_specific_native_engine_logic_allowed",
    ):
        if metadata.get(flag):
            errors.append(f"{flag} must remain false")
    if not metadata.get("same_input_replay_must_be_diagnostic"):
        errors.append("same-input replay must remain diagnostic")
    if not metadata.get("distinct_query_batch_required_for_query_many"):
        errors.append("query-many must require distinct query batches")
    if not metadata.get("cold_cli_one_shot_is_separate_from_warm_process_fresh"):
        errors.append("cold CLI and warm-process fresh regimes must stay separate")
    return {
        "contract_version": PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "claim_boundary": PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY,
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
    "PREPARED_GEOMETRY_SESSION_API_MATURITY",
    "PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY",
    "PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION",
    "PREPARED_GEOMETRY_SESSION_REGIME_LABELS",
    "PREPARED_SESSION_ALLOWED_BACKENDS",
    "PREPARED_SESSION_ALLOWED_LIFETIME_STATES",
    "PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS",
    "PREPARED_SESSION_INVALIDATION_EVENTS",
    "PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY",
    "PREPARED_SESSION_RESIDENCY_STATUS",
    "PREPARED_SESSION_RESIDENCY_VERSION",
    "PreparedGeometrySession",
    "PreparedQueryBatch",
    "RtdlPreparedSessionCacheKey",
    "RtdlPreparedSessionResidencyPolicy",
    "RtdlPreparedSessionReuseResult",
    "RtdlPreparedSessionTimingRecord",
    "describe_prepared_geometry_session_contract",
    "describe_prepared_session_residency_contract",
    "get_or_prepare_explicit_session",
    "make_prepared_session_cache_key",
    "prepared_geometry_session",
    "summarize_prepared_session_timing_records",
    "validate_prepared_geometry_session_contract",
    "validate_prepared_session_residency_contract",
]
