"""Arkade V3 canonical semantic front door."""

from __future__ import annotations

from typing import Mapping

from arkade_contract import ArkadeAlgorithm, FrozenArkadeView
from rtdsl.metric_knn import (
    MetricKnn3DKind,
    MetricKnn3DSpec,
    compile_metric_knn_3d,
)


def _metric(algorithm: ArkadeAlgorithm) -> MetricKnn3DKind:
    if algorithm is ArkadeAlgorithm.FR_LINF:
        return MetricKnn3DKind.L_INFINITY_FILTER_REFINE
    if algorithm is ArkadeAlgorithm.MT_COSINE:
        return MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM
    raise TypeError("algorithm must be ArkadeAlgorithm")


def run_v3(
    *,
    algorithm: ArkadeAlgorithm,
    view: FrozenArkadeView,
    data_points,
    query_points,
    data_ids,
    query_ids,
    target_identity: Mapping[str, object],
    memory_limit_bytes: int,
) -> dict[str, object]:
    spec = MetricKnn3DSpec(
        metric=_metric(algorithm),
        data_count=view.data_count,
        query_count=view.query_count,
        k=view.k,
        initial_geometric_radius=view.initial_radius,
        maximum_rounds=32,
        maximum_candidate_rows=view.data_count * view.query_count,
    )
    program = compile_metric_knn_3d(
        spec,
        target_identity=target_identity,
        memory_limit_bytes=memory_limit_bytes,
    )
    result = program.execute(
        data_points,
        query_points,
        data_ids=data_ids,
        query_ids=query_ids,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "method": "v3_compiler_true_optix",
            "application_selected_paper_algorithm": algorithm.value,
            "default_selected_between_paper_algorithms": False,
            "opaque_user_callback_allowed": False,
        }
    )
    body = dict(result)
    body["metadata"] = metadata
    return body


def run_v3_reference_for_functional_validation(
    *,
    algorithm: ArkadeAlgorithm,
    view: FrozenArkadeView,
    data_points,
    query_points,
    data_ids,
    query_ids,
    target_identity: Mapping[str, object],
    memory_limit_bytes: int,
) -> dict[str, object]:
    """Named CPU semantic model; never a selectable production provider."""

    spec = MetricKnn3DSpec(
        metric=_metric(algorithm),
        data_count=view.data_count,
        query_count=view.query_count,
        k=view.k,
        initial_geometric_radius=view.initial_radius,
        maximum_rounds=32,
        maximum_candidate_rows=view.data_count * view.query_count,
    )
    program = compile_metric_knn_3d(
        spec,
        target_identity=target_identity,
        memory_limit_bytes=memory_limit_bytes,
    )
    result = program.execute_reference_for_functional_validation(
        data_points,
        query_points,
        data_ids=data_ids,
        query_ids=query_ids,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "method": "v3_compiler_true_optix",
            "application_selected_paper_algorithm": algorithm.value,
            "default_selected_between_paper_algorithms": False,
            "opaque_user_callback_allowed": False,
        }
    )
    body = dict(result)
    body["metadata"] = metadata
    return body


class PreparedArkadeV3:
    """Compiler-owned prepared V3 program for repeated paper search calls."""

    def __init__(self, *, algorithm: ArkadeAlgorithm, program, prepared) -> None:
        self._algorithm = algorithm
        self._program = program
        self._prepared = prepared
        self._closed = False

    def execute(self, query_points, *, query_ids) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Arkade V3 owner is closed")
        result = self._prepared.execute(query_points, query_ids=query_ids)
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "method": "v3_compiler_true_optix",
                "application_selected_paper_algorithm": self._algorithm.value,
                "default_selected_between_paper_algorithms": False,
                "opaque_user_callback_allowed": False,
                "prepared_program_reused": True,
            }
        )
        body = dict(result)
        body["metadata"] = metadata
        return body

    def close(self) -> None:
        if self._closed:
            return
        self._prepared.close()
        self._closed = True

    def __enter__(self) -> "PreparedArkadeV3":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_v3(
    *,
    algorithm: ArkadeAlgorithm,
    view: FrozenArkadeView,
    data_points,
    data_ids,
    target_identity: Mapping[str, object],
    memory_limit_bytes: int,
) -> PreparedArkadeV3:
    spec = MetricKnn3DSpec(
        metric=_metric(algorithm),
        data_count=view.data_count,
        query_count=view.query_count,
        k=view.k,
        initial_geometric_radius=view.initial_radius,
        maximum_rounds=32,
        maximum_candidate_rows=view.data_count * view.query_count,
    )
    program = compile_metric_knn_3d(
        spec,
        target_identity=target_identity,
        memory_limit_bytes=memory_limit_bytes,
    )
    prepared = program.prepare(data_points, data_ids=data_ids)
    return PreparedArkadeV3(
        algorithm=algorithm,
        program=program,
        prepared=prepared,
    )


__all__ = [
    "PreparedArkadeV3",
    "prepare_v3",
    "run_v3",
    "run_v3_reference_for_functional_validation",
]
