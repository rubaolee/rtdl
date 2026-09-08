"""Closed V4 AABB-relation-to-count lowering for large query batches.

The canonical custom-AABB callback denotes an exact candidate relation.  A
count query does not need to materialise that relation.  This app-neutral
standard-library lowering binds the verified callback/physical schema to one
of the closed containment algebras and reuses the existing true-OptiX prepared
AABB index, whose device result is a checked scalar count.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import threading

from .aabb_index import prepare_aabb_index_2d_columns
from .optix_runtime import (
    _load_optix_library,
    prepare_optix_aabb_box_queries_2d,
    prepare_optix_aabb_point_queries_2d,
)
from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_box_relation_callback import compile_callback, physical_schema
from .v4_typed_physical_schema import verify_typed_physical_schema


class AabbCountAlgebra(str, Enum):
    POINT_CONTAINS = "indexed_box_contains_point_count_u64_v1"
    RANGE_CONTAINS = "indexed_box_contains_query_box_count_u64_v1"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class VerifiedAabbRelationCountAuthority:
    callback_ir_sha256: str
    callback_effect_digest: str
    physical_schema_sha256: str
    target_sha256: str
    native_library_sha256: str
    algebra: AabbCountAlgebra
    authority_nonce: str


def verify_aabb_relation_count_authority(
    *, target, algebra: AabbCountAlgebra,
) -> VerifiedAabbRelationCountAuthority:
    if not isinstance(algebra, AabbCountAlgebra):
        raise TypeError("closed AabbCountAlgebra required")
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    nonce = _digest({
        "kind": "verified_v4_aabb_relation_count_authority_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "physical": physical.schema.schema_sha256,
        "target": target.target_sha256,
        "native": target.native_sha256,
        "algebra": algebra.value,
        "arbitrary_user_reducer_allowed": False,
    })
    return VerifiedAabbRelationCountAuthority(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, target.target_sha256,
        target.native_sha256, algebra, nonce)


class PreparedVerifiedAabbRelationCountV4:
    def __init__(
        self, authority: VerifiedAabbRelationCountAuthority,
        *, indexed_columns, native_library_path: str | Path,
    ) -> None:
        if not isinstance(authority, VerifiedAabbRelationCountAuthority):
            raise TypeError("verified AABB relation-count authority required")
        native_path = Path(native_library_path).resolve()
        if not native_path.is_file():
            raise FileNotFoundError(native_path)
        if _sha(native_path) != authority.native_library_sha256:
            raise RuntimeError("AABB relation-count native differs from target authority")
        os.environ["RTDL_OPTIX_LIB"] = str(native_path)
        os.environ["RTDL_OPTIX_LIBRARY"] = str(native_path)
        self._native_path = native_path
        self._native_sha256 = _sha(native_path)
        self._library = _load_optix_library()
        self._authority = authority
        self._prepared = prepare_aabb_index_2d_columns(
            indexed_columns, backend="optix")
        self._prepared_queries = None
        self._closed = False
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._execution_count = 0
        self._session_identity = _digest({
            "authority": authority.authority_nonce,
            "native": self._native_sha256,
            "indexed_count": len(indexed_columns),
            "physical_lowering": (
                "canonical_v4_aabb_relation_to_device_scalar_count_v1"),
        })

    def bind_queries(self, *, point_queries=None, box_queries=None) -> None:
        """Bind one immutable query batch for repeated native execution."""

        self._guard()
        if self._prepared_queries is not None:
            raise RuntimeError("prepared AABB relation-count queries are already bound")
        if (point_queries is None) == (box_queries is None):
            raise ValueError("bind exactly one point or box query batch")
        if point_queries is not None:
            if self._authority.algebra is not AabbCountAlgebra.POINT_CONTAINS:
                raise ValueError("point queries require the point-contains algebra")
            prepared = prepare_optix_aabb_point_queries_2d(point_queries)
        else:
            if self._authority.algebra is not AabbCountAlgebra.RANGE_CONTAINS:
                raise ValueError("box queries require the range-contains algebra")
            prepared = prepare_optix_aabb_box_queries_2d(box_queries)
        self._prepared_queries = prepared

    def _guard(self) -> None:
        if self._closed:
            raise RuntimeError("prepared AABB relation-count owner is closed")
        if os.getpid() != self._pid or threading.get_ident() != self._thread:
            raise RuntimeError("prepared AABB relation-count owner crossed owner boundary")

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "authority_nonce": self._authority.authority_nonce,
            "native_library_sha256": self._native_sha256,
            "physical_lowering": (
                "canonical_v4_aabb_relation_to_device_scalar_count_v1"),
            "execution_count": self._execution_count,
            "prepared_query_batch_bound": self._prepared_queries is not None,
            "prepared_query_count": (
                0 if self._prepared_queries is None else self._prepared_queries.count
            ),
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "prepare_seconds_reported_separately": True,
        }

    def execute_count(
        self, *, point_queries=None, box_queries=None,
    ) -> dict[str, object]:
        self._guard()
        operation = (
            "point_contains"
            if self._authority.algebra is AabbCountAlgebra.POINT_CONTAINS
            else "range_contains"
        )
        if self._prepared_queries is not None and (
            point_queries is not None or box_queries is not None
        ):
            raise ValueError("bound prepared queries reject per-execution query inputs")
        if (
            operation == "point_contains"
            and box_queries is not None
            and len(box_queries) != 0
        ):
            raise ValueError("point-count authority rejects box queries")
        if (
            operation == "range_contains"
            and point_queries is not None
            and len(point_queries) != 0
        ):
            raise ValueError("range-count authority rejects point queries")
        audit = OptixTraversalAuditSession.open(library=self._library)
        try:
            if self._prepared_queries is not None:
                result = self._prepared.count_prepared_queries(
                    self._prepared_queries, operation=operation)
                query_count = self._prepared_queries.count
            else:
                point_values = () if point_queries is None else point_queries
                box_values = () if box_queries is None else box_queries
                result = self._prepared.count(
                    point_queries=point_values, box_queries=box_values,
                    operation=operation)
                query_count = len(point_values) + len(box_values)
            value = int(result["counts"][operation])
            receipt = audit.finish(
                semantic_digest=_digest({
                    "authority": self._authority.authority_nonce,
                    "algebra": self._authority.algebra.value,
                    "query_count": query_count,
                    "native": self._native_sha256,
                }),
                output_digest=_digest({"count": value}),
                route_identity=(
                    "v4_callback_ir:closed_aabb_relation:device_count_v1"),
            )
        except Exception:
            audit.abort()
            raise
        if receipt["physical_executor_classification"] != "optix_traversal_observed":
            raise RuntimeError("AABB relation-count lowering lacked OptiX traversal")
        if value < 0 or result.get("rt_core_accelerated") is not True:
            raise RuntimeError("AABB relation-count route returned invalid metadata")
        self._execution_count += 1
        return {
            "count": value,
            "operation": operation,
            "physical_result": result,
            "traversal_receipt": receipt,
            "native_library_sha256": self._native_sha256,
            "physical_lowering": (
                "canonical_v4_aabb_relation_to_device_scalar_count_v1"),
        }

    def close(self) -> None:
        if self._closed:
            return
        self._guard()
        try:
            if self._prepared_queries is not None:
                self._prepared_queries.close()
        finally:
            self._prepared.close()
            self._closed = True

    def __enter__(self):
        self._guard()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def __getstate__(self):
        raise RuntimeError("prepared AABB relation-count owner cannot be serialized")


__all__ = [
    "AabbCountAlgebra", "PreparedVerifiedAabbRelationCountV4",
    "VerifiedAabbRelationCountAuthority",
    "verify_aabb_relation_count_authority",
]
