"""Frozen Arkade input, strict independent oracle and four-lane contract."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import io
from pathlib import Path
import tarfile

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
AUTHOR_ARCHIVE = (
    ROOT
    / "history/internal_docs/goal5744_arkade_author_source_commit_45b9425e_20260809.tar.gz"
)
AUTHOR_ARCHIVE_SHA256 = (
    "49d19eea86f4c8d14b931d71acce208c5204013329f77f87e774c5498b78f8ab"
)
AUTHOR_SAMPLE_SHA256 = (
    "17e0898b0d9a340d6808feb858bc8bd5e568031f25cdb593d6dc6e6189fbf0f6"
)
AUTHOR_ARCHIVE_PREFIX = "Arkade-45b9425e/"


class ArkadeAlgorithm(str, Enum):
    FR_LINF = "FR_LINF"
    MT_COSINE = "MT_COSINE"


@dataclass(frozen=True)
class FrozenArkadeView:
    stable_id: str
    data_begin: int
    data_end: int
    query_begin: int
    query_end: int
    k: int
    initial_radius: float

    @property
    def data_count(self) -> int:
        return self.data_end - self.data_begin

    @property
    def query_count(self) -> int:
        return self.query_end - self.query_begin


FROZEN_VIEWS = {
    "author_sample_readme_small_v1": FrozenArkadeView(
        stable_id="author_sample_readme_small_v1",
        data_begin=0,
        data_end=1000,
        query_begin=1000,
        query_end=1010,
        k=10,
        initial_radius=0.000532197361814063,
    ),
    "author_sample_full_control_v1": FrozenArkadeView(
        stable_id="author_sample_full_control_v1",
        data_begin=0,
        data_end=9000,
        query_begin=9000,
        query_end=10000,
        k=10,
        initial_radius=0.0004316173413081853,
    ),
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_author_sample_bytes(
    archive_path: Path = AUTHOR_ARCHIVE,
) -> bytes:
    archive_path = Path(archive_path)
    archive_bytes = archive_path.read_bytes()
    if _sha256_bytes(archive_bytes) != AUTHOR_ARCHIVE_SHA256:
        raise RuntimeError("Arkade author archive identity mismatch")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        member = archive.getmember(
            AUTHOR_ARCHIVE_PREFIX + "datasets/sample_gowalla.txt"
        )
        handle = archive.extractfile(member)
        if handle is None:
            raise RuntimeError("Arkade author sample is absent from the archive")
        sample = handle.read()
    if _sha256_bytes(sample) != AUTHOR_SAMPLE_SHA256:
        raise RuntimeError("Arkade author sample identity mismatch")
    return sample


def load_frozen_view(
    view_id: str,
    *,
    archive_path: Path = AUTHOR_ARCHIVE,
) -> dict[str, object]:
    try:
        view = FROZEN_VIEWS[view_id]
    except KeyError as exc:
        raise ValueError(f"unknown frozen Arkade view: {view_id}") from exc
    sample = np.loadtxt(
        io.BytesIO(load_author_sample_bytes(archive_path)),
        dtype=np.float32,
    )
    if sample.shape != (10000, 3) or not bool(np.all(np.isfinite(sample))):
        raise RuntimeError("Arkade author sample shape or finiteness mismatch")
    data = np.ascontiguousarray(sample[view.data_begin : view.data_end], dtype=np.float32)
    queries = np.ascontiguousarray(
        sample[view.query_begin : view.query_end], dtype=np.float32
    )
    return {
        "view": view,
        "data_points": data,
        "query_points": queries,
        "data_ids": np.arange(view.data_count, dtype=np.uint32),
        "query_ids": np.arange(view.query_count, dtype=np.uint32),
    }


def _normalized(points: np.ndarray, *, name: str) -> np.ndarray:
    # Match the language contract exactly: consume binary32 inputs, compute
    # the normalization in the host semantic domain, then freeze the result
    # back to binary32 before native packing.
    values = np.ascontiguousarray(points, dtype=np.float32).astype(np.float64)
    norms = np.linalg.norm(values, axis=1)
    if not bool(np.all(np.isfinite(norms))) or bool(np.any(norms == 0.0)):
        raise ValueError(f"{name} contains a zero or invalid vector")
    # Arkade's OptiX program consumes float coordinates.  Freeze the rounded
    # normalized space instead of pretending the public binary64 oracle is the
    # same program.  Determinism is supplied by RTDL's explicit ID tie break.
    return np.ascontiguousarray(values / norms[:, None], dtype=np.float32)


def independent_oracle(
    algorithm: ArkadeAlgorithm,
    data_points,
    query_points,
    *,
    k: int,
    data_ids=None,
) -> dict[str, np.ndarray]:
    """Independent all-pairs oracle for the frozen binary32 RTDL contract.

    The public Arkade source ranks float distances and does not define a stable
    ID tie break.  RTDL makes that missing boundary explicit: transformed
    coordinates and metric keys are binary32, then equal keys are ordered by
    U32 item ID.  This is stricter and deterministic; it is not relabelled as
    the byte behavior of the incomplete public output path.
    """

    if not isinstance(algorithm, ArkadeAlgorithm):
        raise TypeError("algorithm must be ArkadeAlgorithm")
    data = np.ascontiguousarray(data_points, dtype=np.float32)
    queries = np.ascontiguousarray(query_points, dtype=np.float32)
    if data.ndim != 2 or data.shape[1:] != (3,):
        raise ValueError("data_points must be [N,3]")
    if queries.ndim != 2 or queries.shape[1:] != (3,):
        raise ValueError("query_points must be [Q,3]")
    if not 0 < k <= len(data):
        raise ValueError("k is outside the data domain")
    if data_ids is None:
        ids = np.arange(len(data), dtype=np.uint32)
    else:
        ids = np.asarray(data_ids, dtype=np.uint32)
        if ids.shape != (len(data),) or len(np.unique(ids)) != len(data):
            raise ValueError("data_ids must be unique and match data_points")
    if algorithm is ArkadeAlgorithm.MT_COSINE:
        data = _normalized(data, name="data_points")
        queries = _normalized(queries, name="query_points")
    ordered_ids = np.empty((len(queries), k), dtype=np.uint32)
    ordered_distances = np.empty((len(queries), k), dtype=np.float64)
    for query_index, query in enumerate(queries):
        if algorithm is ArkadeAlgorithm.FR_LINF:
            distances = np.ascontiguousarray(
                np.max(np.abs(data - query), axis=1), dtype=np.float32
            )
        else:
            delta = np.ascontiguousarray(data - query, dtype=np.float32)
            xy = np.ascontiguousarray(
                np.float32(delta[:, 0] * delta[:, 0])
                + np.float32(delta[:, 1] * delta[:, 1]),
                dtype=np.float32,
            )
            distances = np.ascontiguousarray(
                np.float32(xy + np.float32(delta[:, 2] * delta[:, 2])),
                dtype=np.float32,
            )
        order = np.lexsort((ids.astype(np.uint64), distances))[:k]
        ordered_ids[query_index, :] = ids[order]
        ordered_distances[query_index, :] = distances[order]
    return {
        "ordered_item_ids": ordered_ids,
        "ordered_metric_distances": ordered_distances,
    }


def ordered_item_id_sha256(values) -> str:
    array = np.ascontiguousarray(values, dtype="<u4")
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def compare_to_oracle(actual: dict[str, object], expected: dict[str, np.ndarray]) -> None:
    observed = np.asarray(actual["ordered_item_ids"], dtype=np.uint32)
    wanted = np.asarray(expected["ordered_item_ids"], dtype=np.uint32)
    if observed.shape != wanted.shape or not bool(np.array_equal(observed, wanted)):
        mismatch = np.argwhere(observed != wanted)
        first = tuple(int(value) for value in mismatch[0]) if mismatch.size else None
        raise RuntimeError(f"Arkade ordered item-id output mismatch; first={first}")


__all__ = [
    "AUTHOR_ARCHIVE",
    "AUTHOR_ARCHIVE_SHA256",
    "AUTHOR_SAMPLE_SHA256",
    "ArkadeAlgorithm",
    "FROZEN_VIEWS",
    "FrozenArkadeView",
    "compare_to_oracle",
    "independent_oracle",
    "load_author_sample_bytes",
    "load_frozen_view",
    "ordered_item_id_sha256",
]
