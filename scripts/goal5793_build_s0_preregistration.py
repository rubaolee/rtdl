from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"

SOURCE_OUT = ROOT / "history/internal_docs/goal5793_s0_source_and_admission_freeze_20260822.json"
CANDIDATE_OUT = ROOT / "history/internal_docs/goal5793_s0_known_universe_requalification_20260822.json"
PROTOCOL_OUT = ROOT / "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json"
REPORT_OUT = ROOT / "history/internal_docs/goal5793_s0_preregistration_technical_report_20260822.md"
SELF_REVIEW_OUT = ROOT / "history/internal_docs/self_review_goal5793_s0_preregistration_20260822.md"
RESULT_OUT = ROOT / "history/internal_docs/goal5793_s0_preregistration_result_20260822.json"

A2_CLOSURE = ROOT / "history/internal_docs/goal5789_a2_postreview_closure_and_goal5793_s0_entry_20260822.json"
GOAL5753_UNIVERSE = ROOT / "history/internal_docs/goal5753_held_out_candidate_universe_20260811.json"
GOAL5753_PROTOCOL = ROOT / "history/internal_docs/goal5753_core_freeze_and_selection_protocol_20260811.json"
V26_SOURCE = ROOT / "history/internal_docs/goal5791_portable_source_v26_20260820.tar.gz"

EXPECTED_ROOTS = {
    A2_CLOSURE.relative_to(ROOT).as_posix(): (11247, "ad06d871aafcf792c2163d7c2ec1c38a9b93ffd1a36aa31cf78fdb3d4b7c288e"),
    GOAL5753_UNIVERSE.relative_to(ROOT).as_posix(): (43892, "fb89d1da0e9b7bc18ce3333eb11a5920ffdef9f23ba227f4ecbf96e898234b05"),
    GOAL5753_PROTOCOL.relative_to(ROOT).as_posix(): (4529, "b0cc376dd212cef2c3fc5902009a0785f30d029ccdeb8e5bc524e5785423db8b"),
    V26_SOURCE.relative_to(ROOT).as_posix(): (4124847, "5f75d2f2793e1ec3151994031bb7ca6121fc058fc8d634ba40ae9e14f6118373"),
}

HISTORICAL_CATALOG_ROOTS = (
    {
        "commit": "89079f4c0d60b8a8517b8b302170868de1e3e4a7",
        "path": "docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md",
        "bytes": 10800,
        "sha256": "972403628507c9655acd5fdaf20349feb859c46929b6dd3431bc4af37dbe6437",
        "meaning": "the 32 normalized workload families later represented by the Goal5753 rows were catalogued and discussed at roadmap/feasibility level; this is not paper-specific source review",
    },
    {
        "commit": "ccd86697daa54467ab256aeba49798bf9ee06d64",
        "path": "docs/reports/goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md",
        "bytes": 8165,
        "sha256": "590de7ef35aea6244949f187498fb3f45a90e4fc3a59ee0b538f6ba8910169ac",
        "meaning": "the same 32 normalized workload families received workload-scope feasibility/risk treatment; this is not paper-specific source review",
    },
)

HISTORICAL_WORKLOAD_FAMILIES = (
    "ANN",
    "BFS",
    "Barnes-Hut",
    "Binary Search",
    "Continuous CD",
    "DBSCAN",
    "Discrete CD",
    "FRNN",
    "Graph Drawing",
    "Index Scan",
    "Infrared Radiation",
    "Line-Segment Intersection",
    "Non-euclidean kNN",
    "Outlier Detection",
    "Particle Simulation",
    "Particle Tracking",
    "Particle Transport",
    "Particle-Mesh Coupling",
    "Penetration Depth",
    "Point Location",
    "Point Queries",
    "Point in Polygon",
    "RMQ",
    "Radio Wave Propagation",
    "Range Queries",
    "Segmentation",
    "Set Intersection",
    "SpMM",
    "Space Skipping",
    "Triangle Counting",
    "Voxelization",
    "kNN",
)

COMPLETE_SOURCE_EXPECTED = {
    "file_count": 326,
    "total_bytes": 14587884,
    "rows_canonical_bytes": 46672,
    "rows_sha256": "f26b55e6d9a120a34882e9c7ada44df5503f1f90f83db893d1d6957ab0202f97",
}

CRITICAL_EXPLANATORY_PATHS = (
    "Makefile",
    "VERSION",
    "pyproject.toml",
    "requirements.txt",
    "scripts/goal5789_a2_build_contract_evidence.py",
    "scripts/goal5789_a2_independent_compatibility_checker.py",
    "scripts/goal5789_a2_materialize_callback_ir_authority.py",
    "scripts/goal5789_independent_compatibility_checker.py",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/native/rtdl_optix.cpp",
    "src/rtdsl/physical_execution_provenance.py",
    "src/rtdsl/v4_bounded_relation.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_bounded_relation_optix_runtime.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_builtin_triangle_standard_library.py",
    "src/rtdsl/v4_callback_abi.py",
    "src/rtdsl/v4_callback_frontend.py",
    "src/rtdsl/v4_callback_ir.py",
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_callback_optix_wrapper_codegen.py",
    "src/rtdsl/v4_callback_poc.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_semantic_physical_admission.py",
    "src/rtdsl/v4_semantically_admitted_compiler.py",
    "src/rtdsl/v4_spatial_candidate_callback.py",
    "src/rtdsl/v4_triangle_optix_compiler.py",
    "src/rtdsl/v4_triangle_optix_runtime.py",
    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
    "src/rtdsl/v4_triangle_reduction.py",
    "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
    "src/rtdsl/v4_triangle_reduction_optix_runtime.py",
    "src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "src/rtdsl/v4_typed_physical_schema.py",
)

CRITICAL_EXPLANATORY_EXPECTED = {
    "file_count": 41,
    "total_bytes": 3559681,
    "rows_sha256": "f2a8887ac279e71f5425b9ec5ad12b5ce0c258a2e219f254322d101866797138",
}

# These 12 rows were the only rows not already excluded by the earlier Goal5753
# inventory plus later exact implementation/use chronology.  The table records
# what was actually found.  Missing source is never interpreted as eligibility.
PRIMARY_REQUALIFICATION: dict[str, dict[str, Any]] = {
    "Kim2025RTPDPD::penetration_depth": {
        "doi": "10.1007/s00371-025-04007-3",
        "primary_landing_url": "https://arxiv.org/abs/2502.12463",
        "primary_pdf_url": "https://arxiv.org/pdf/2502.12463v1",
        "primary_version": "arXiv v1",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 4368509,
        "primary_sha256": "5b7515a51a7fe99bfd12a943c30627cfcb120f1347cdc4ed088fe01c9c36c301",
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "penetration surface and sampled bidirectional Hausdorff penetration depth",
        "oracle_kind": "brute-force vertex-pair and bounded sampled-ray reference",
        "physical_geometry_family": "builtin_triangle",
        "composition": "point-in-polyhedron plus penetration surfaces plus bidirectional sampling plus global maximum",
        "source_gaps": ["no public author code located"],
    },
    "Zhang2025RTSpMSpMHR::spmm": {
        "doi": "10.1145/3695053.3731072",
        "primary_landing_url": "https://dl.acm.org/doi/10.1145/3695053.3731072",
        "primary_pdf_url": "https://dl.acm.org/doi/pdf/10.1145/3695053.3731072",
        "primary_version": "publisher version",
        "primary_fetch_status": "UNAVAILABLE_HTTP_403",
        "primary_bytes": None,
        "primary_sha256": None,
        "primary_redistributable": False,
        "author_code_status": "COMMIT_AND_TREE_PINNED__ARCHIVE_BYTES_OBSERVED_NOT_EMBEDDED",
        "author_code": {
            "url": "https://github.com/escalab/RTSpMSpM",
            "commit": "216add0bf257e9e586565b0a109690481bddb10f",
            "tree": "c972df5c9f08724036eb0ca86d8869762365081b",
            "archive_url": "https://codeload.github.com/escalab/RTSpMSpM/zip/216add0bf257e9e586565b0a109690481bddb10f",
            "archive_bytes": 29604060,
            "archive_sha256": "a78b1bc7cefc334b7d2c12477cc484bfcab37cd18ce687d5a381181ce1b3660a",
            "license_spdx": "MIT",
        },
        "semantic_request": "sparse matrix multiplication with one ray per A nonzero and any-hit products from matching B nonzeros",
        "oracle_kind": "exact bounded sparse matrix multiplication",
        "physical_geometry_family": "builtin_sphere__not_registered",
        "composition": "any-hit product accumulation with atomics",
        "source_gaps": ["publisher paper bytes unavailable; code must not substitute for paper semantics"],
    },
    "zhao2023leveraging::particle_simulation": {
        "doi": "10.1002/nme.7139",
        "primary_landing_url": "https://onlinelibrary.wiley.com/doi/full/10.1002/nme.7139",
        "primary_pdf_url": "https://jzhao.people.ust.hk/home/PDFs/2023-NME-Shiwei.pdf",
        "primary_version": "author PDF",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 7607777,
        "primary_sha256": "85add3b8fc8d9e6d069675fff24468017a34b376f14dafabeb2a68e750dc3923",
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "particle radius-neighbor/contact list followed by DEM update",
        "oracle_kind": "exact brute-force radius-neighbor/contact oracle",
        "physical_geometry_family": "custom_aabb",
        "composition": "short-ray all-hit neighborhood then dynamic physics update",
        "source_gaps": ["paper states code/data available on request; no public author code located"],
    },
    "Hashinoki2023ImplementationOR::radio_wave_propagation": {
        "doi": "10.1109/IPDPSW59300.2023.00115",
        "primary_landing_url": "https://ieeexplore.ieee.org/document/10196526",
        "primary_pdf_url": None,
        "primary_version": "target workshop paper unavailable; author precursor pinned separately",
        "primary_fetch_status": "TARGET_PAPER_UNAVAILABLE__PRECURSOR_OBSERVED_NOT_EMBEDDED__REFETCH_REQUIRED",
        "primary_bytes": None,
        "primary_sha256": None,
        "primary_redistributable": False,
        "precursor": {
            "url": "https://ipsj.ixsq.nii.ac.jp/record/218962/files/IPSJ-HPC22185024.pdf",
            "bytes": 851267,
            "sha256": "99f751fc8902879ebafc36b275eefc1eb067ee4a7220fea46f246db53520743f",
        },
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "shooting-and-bouncing-rays radio propagation with receiver/scene intersections and recursive reflection",
        "oracle_kind": "bounded path-enumeration and accumulated path/material reference not yet frozen",
        "physical_geometry_family": "sphere_and_plane__not_registered_as_exact_pair",
        "composition": "recursive continuation plus path length and reflection-coefficient accumulation",
        "source_gaps": ["exact target paper unavailable", "no author code located", "oracle not frozen"],
    },
    "zellmann2020accelerating::graph_drawing": {
        "doi": "10.1109/VIS47514.2020.00026",
        "primary_landing_url": "https://arxiv.org/abs/2008.11235",
        "primary_pdf_url": "https://arxiv.org/pdf/2008.11235v1",
        "primary_version": "arXiv v1",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 28486124,
        "primary_sha256": "bee6ef11ec8da83bf39689a7eee77bfdab0153f2a571a4d30a06bd572c21e2a2",
        "primary_redistributable": False,
        "author_code_status": "COMMIT_AND_TREE_PINNED__ARCHIVE_BYTES_OBSERVED_NOT_EMBEDDED",
        "author_code": {
            "url": "https://github.com/owl-project/owl-graph-drawing",
            "commit": "c9c8974eabf2c82ebb94ad0c18fd5110cf985475",
            "tree": "370c6ce68f30b717765230377abef4742f8e4d0e",
            "archive_bytes": 24971,
            "archive_sha256": "534e62f0b48ee3a5f2c14f3ae2ea942252b6c3e687aa7db8bec18088df137162",
            "license_spdx": "MIT",
        },
        "semantic_request": "finite-radius repulsive force for force-directed graph drawing",
        "oracle_kind": "bounded CPU all-pairs force reference",
        "physical_geometry_family": "custom_aabb",
        "composition": "radius-neighbor callback plus iterative global position updates",
        "source_gaps": [],
    },
    "Morrical2019EfficientSS::space_skipping": {
        "doi": "10.1109/VISUAL.2019.8933539",
        "primary_landing_url": "https://arxiv.org/abs/1908.01906",
        "primary_pdf_url": "https://arxiv.org/pdf/1908.01906v1",
        "primary_version": "arXiv v1",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 2341113,
        "primary_sha256": "3f45186c43e7d7264a28f1ea3cdba443e498b84cb1a2811c694627b8e7be5f72",
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "entry/exit discovery for volume partitions followed by adaptive ray marching and opacity integration",
        "oracle_kind": "exact bounded discrete oracle not yet established",
        "physical_geometry_family": "builtin_triangle",
        "composition": "two traces plus continuation, adaptive sampling, integration and early termination",
        "source_gaps": ["no author code located", "exact bounded discrete oracle not frozen"],
    },
    "Petrescu2019GPUSR::segmentation": {
        "doi": "10.1109/ACCESS.2019.2917721",
        "primary_landing_url": "https://ieeexplore.ieee.org/document/8718269",
        "primary_pdf_url": "https://ieeexplore.ieee.org/ielx7/6287639/8600701/08718269.pdf",
        "primary_version": "publisher PDF",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 2242526,
        "primary_sha256": "8d6cbcf20f9c82db0a672d431eb042d82280c39b56d1c6674ed8133749ec86d6",
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "GPU ray-stepping image segmentation",
        "oracle_kind": "image segmentation reference",
        "physical_geometry_family": "none__software_dda_not_rt_core",
        "composition": "GPU thread manually steps image pixels with DDA/staircase",
        "source_gaps": ["no author code located"],
    },
    "Chan2018ParticlemeshCI::particle_mesh_coupling": {
        "doi": "10.1002/cav.1787",
        "primary_landing_url": "https://onlinelibrary.wiley.com/doi/abs/10.1002/cav.1787",
        "primary_pdf_url": None,
        "primary_version": "publisher metadata/abstract only",
        "primary_fetch_status": "FULL_PAPER_UNAVAILABLE",
        "primary_bytes": None,
        "primary_sha256": None,
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "SPH neighbor search, particle-mesh collision and momentum/energy coupling",
        "oracle_kind": "full bounded SPH/collision state evolution not frozen",
        "physical_geometry_family": "builtin_triangle_and_neighbor_search",
        "composition": "neighbor/collision queries plus global physics continuation",
        "source_gaps": ["exact paper unavailable", "no author code located", "oracle not frozen"],
    },
    "Liu2025RayTC::infrared_radiation": {
        "doi": "10.1016/j.ijthermalsci.2025.109904",
        "primary_landing_url": "https://www.sciencedirect.com/science/article/pii/S1290072925002273",
        "primary_pdf_url": None,
        "primary_version": "closed publisher article",
        "primary_fetch_status": "FULL_PAPER_UNAVAILABLE",
        "primary_bytes": None,
        "primary_sha256": None,
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "reverse Monte Carlo infrared signature through media and wall interactions",
        "oracle_kind": "statistical/numerical signature oracle not frozen",
        "physical_geometry_family": "likely_builtin_triangle__not_source_frozen",
        "composition": "boundary traversal plus stochastic weighted continuation and materials",
        "source_gaps": ["exact paper unavailable", "no author code located", "statistical oracle not frozen"],
    },
    "Cui2024RTSRTAM::particle_transport": {
        "doi": "10.1109/ISPA63168.2024.00082",
        "primary_landing_url": "https://ieeexplore.ieee.org/document/10885104",
        "primary_pdf_url": None,
        "primary_version": "indexed abstract",
        "primary_fetch_status": "FULL_PAPER_UNAVAILABLE",
        "primary_bytes": None,
        "primary_sha256": None,
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "particle transport on a modified shared RT-cache architecture",
        "oracle_kind": "architecture simulation",
        "physical_geometry_family": "nonstock_modified_rt_hardware",
        "composition": "redirect table and altered RT-accelerator/SM cache organization",
        "source_gaps": ["exact paper unavailable", "no executable stock-RT artifact"],
    },
    "Salmon2019ExploitingHR::particle_transport": {
        "doi": "10.1109/PMBS49563.2019.00008",
        "primary_landing_url": "https://sc19.supercomputing.org/proceedings/workshops/workshop_files/ws_pmbsf102s2-file1.pdf",
        "primary_pdf_url": "https://sc19.supercomputing.org/proceedings/workshops/workshop_files/ws_pmbsf102s2-file1.pdf",
        "primary_version": "SC workshop PDF",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 1992364,
        "primary_sha256": "9cd0cd561c697bdee2aed8aa13c97ce6431bc9060740e8f9fb9efbae7c7429a0",
        "primary_redistributable": False,
        "author_code_status": "EXACT_OPTIX_OPENMC_PORT_NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "nearest-surface and inside/outside tracking followed by stochastic particle transport and tallies",
        "oracle_kind": "deterministic seed-bounded trace or statistical tally oracle not frozen",
        "physical_geometry_family": "builtin_triangle",
        "composition": "surface traversal plus stochastic interactions, material tracking, continuation and tallies",
        "source_gaps": ["exact author OptiX/OpenMC port not found", "deterministic oracle not frozen"],
    },
    "Schwarz2010FastPS::voxelization": {
        "doi": "10.1145/1882261.1866201",
        "primary_landing_url": "https://www.michael-schwarz.com/research/publ/files/vox-siga10.pdf",
        "primary_pdf_url": "https://www.michael-schwarz.com/research/publ/files/vox-siga10.pdf",
        "primary_version": "author PDF",
        "primary_fetch_status": "OBSERVED_2026_08_22__NOT_EMBEDDED__REFETCH_REQUIRED_FOR_REHASH",
        "primary_bytes": 6420310,
        "primary_sha256": "d5a9e7098e520aeafd47db70eb60a69b0dab6b4bf03c825a57cc992196fc3919",
        "primary_redistributable": False,
        "author_code_status": "NOT_FOUND_IN_NONREPLAYABLE_S0_SEARCH__NONEXISTENCE_NOT_CLAIMED",
        "author_code": None,
        "semantic_request": "parallel surface and solid voxelization",
        "oracle_kind": "voxel occupancy reference",
        "physical_geometry_family": "none__cuda_rasterization_not_rt_core",
        "composition": "triangle-box overlap and rasterization/tile parallelism",
        "source_gaps": ["no author code located"],
    },
}

SOURCE_GAP_ANALYZED = {
    "Zhang2025RTSpMSpMHR::spmm",
    "Hashinoki2023ImplementationOR::radio_wave_propagation",
    "Morrical2019EfficientSS::space_skipping",
    "Liu2025RayTC::infrared_radiation",
    "Salmon2019ExploitingHR::particle_transport",
}

SOURCE_GAP_STRESS_AXES = {
    "Zhang2025RTSpMSpMHR::spmm": ["different_geometry:builtin_sphere_unregistered", "multiplicity:any_hit_product_accumulation"],
    "Hashinoki2023ImplementationOR::radio_wave_propagation": ["different_composition:recursive_reflection", "risk:continuation", "risk:path_material_accumulation"],
    "Morrical2019EfficientSS::space_skipping": ["different_composition:entry_exit_plus_marching", "risk:continuation", "risk:early_termination"],
    "Liu2025RayTC::infrared_radiation": ["different_composition:stochastic_transport", "risk:weighted_continuation", "risk:material_boundary"],
    "Salmon2019ExploitingHR::particle_transport": ["different_composition:stochastic_transport", "risk:continuation", "risk:tally_and_material_state"],
}

EXCLUSION_OVERRIDES = {
    "Kim2025RTPDPD::penetration_depth": "EXCLUDE_DESIGN_CONTAMINATION__HAUSDORFF_PIP_AND_TRIANGLE_COLLISION",
    "Sui2024HardwareAcceleratedRT::discrete_cd": "EXCLUDE_PRE_FREEZE_SAME_PAPER_COLLISION_IMPLEMENTATION",
    "Sui2024HardwareAcceleratedRT::continuous_cd": "EXCLUDE_PRE_FREEZE_SAME_PAPER_COLLISION_IMPLEMENTATION",
    "Meneses2024RTXRMQ::rmq": "EXCLUDE_IMPLEMENTED_RESULT_AND_A2_LEGACY_REPLAY",
    "zhao2023leveraging::particle_simulation": "EXCLUDE_DESIGN_CONTAMINATION__CUSTOM_AABB_RADIUS_NEIGHBOR",
    "Morrical2022AcceleratingUM::point_location": "EXCLUDE_NORMALIZED_PROBLEM_FAMILY_CONTAMINATION__MESH_POINT_LOCATION",
    "Wang2022AnGP::particle_tracking": "EXCLUDE_IMPLEMENTED_RESULT__GOAL5753_PARTICLE",
    "zellmann2020accelerating::graph_drawing": "EXCLUDE_DESIGN_CONTAMINATION__RADIUS_NEIGHBOR_AND_ITERATIVE_COMPOSITION",
    "Petrescu2019GPUSR::segmentation": "EXCLUDE_NON_RT_CORE_PRIMARY_SOURCE",
    "Chan2018ParticlemeshCI::particle_mesh_coupling": "EXCLUDE_DESIGN_CONTAMINATION_AND_SOURCE_GAP",
    "Cui2024RTSRTAM::particle_transport": "EXCLUDE_REQUIRES_NONSTOCK_RT_HARDWARE",
    "Schwarz2010FastPS::voxelization": "EXCLUDE_NON_RT_CORE_PRIMARY_SOURCE",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "file_sha256": sha256_bytes(data),
    }


def seal(document: dict[str, Any], field: str) -> dict[str, Any]:
    body = dict(document)
    body.pop(field, None)
    document[field] = sha256_bytes(canonical_bytes(body))
    return document


def json_bytes(document: dict[str, Any]) -> bytes:
    return json.dumps(
        document,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def assert_expected_roots() -> None:
    for relative, (expected_bytes, expected_sha) in EXPECTED_ROOTS.items():
        data = (ROOT / relative).read_bytes()
        if len(data) != expected_bytes or sha256_bytes(data) != expected_sha:
            raise RuntimeError(f"predecessor drift: {relative}")


def historical_catalog_roots() -> list[dict[str, Any]]:
    roots: list[dict[str, Any]] = []
    for row in HISTORICAL_CATALOG_ROOTS:
        data = subprocess.check_output(["git", "show", f"{row['commit']}:{row['path']}"], cwd=ROOT)
        if len(data) != row["bytes"] or sha256_bytes(data) != row["sha256"]:
            raise RuntimeError(f"historical catalog root drift: {row['path']}")
        roots.append(dict(row))
    return roots


def source_rows() -> list[dict[str, Any]]:
    paths: list[Path] = []
    for path in (ROOT / "src").rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"symlink is outside the declared regular-file surface: {path}")
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".nbc", ".nbi"}:
            continue
        paths.append(path)
    declarations = [ROOT / name for name in ("Makefile", "pyproject.toml", "requirements.txt", "VERSION")]
    if any(path.is_symlink() or not path.is_file() for path in declarations):
        raise RuntimeError("declared source/build identity roots must be regular non-symlink files")
    paths.extend(declarations)
    rows = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        if PurePosixPath(relative).as_posix() != relative:
            raise RuntimeError(f"noncanonical source path: {relative}")
        data = path.read_bytes()
        rows.append({"path": relative, "sha256": sha256_bytes(data), "size_bytes": len(data)})
    rows.sort(key=lambda row: row["path"].encode("utf-8"))
    return rows


def critical_rows() -> list[dict[str, Any]]:
    rows = []
    for relative in CRITICAL_EXPLANATORY_PATHS:
        path = ROOT / relative
        data = path.read_bytes()
        rows.append({"path": relative, "sha256": sha256_bytes(data), "size_bytes": len(data)})
    rows.sort(key=lambda row: row["path"].encode("utf-8"))
    return rows


def v26_overlap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    members: dict[str, bytes] = {}
    with tarfile.open(V26_SOURCE, "r:gz") as archive:
        for member in archive.getmembers():
            if member.isfile():
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"unreadable v26 member: {member.name}")
                members[member.name] = extracted.read()
            elif member.isdir():
                continue
            else:
                raise RuntimeError(f"unsafe v26 member type: {member.name}")
    present = []
    missing = []
    mismatches = []
    for row in rows:
        data = members.get(row["path"])
        if data is None:
            missing.append(row["path"])
        elif len(data) != row["size_bytes"] or sha256_bytes(data) != row["sha256"]:
            mismatches.append(row["path"])
        else:
            present.append(row["path"])
    if len(present) != 324 or missing != ["VERSION", "requirements.txt"] or mismatches:
        raise RuntimeError("v26 overlap does not match reviewed 324/326 custody boundary")
    return {
        "predecessor": identity(V26_SOURCE),
        "present_and_byte_identical_count": len(present),
        "missing_count": len(missing),
        "missing_paths": missing,
        "mismatch_count": len(mismatches),
        "mismatch_paths": mismatches,
        "claim": "324/326 current source/build rows have exact v26 byte custody; the whole v26 tree is not claimed current",
    }


def build_source_authority() -> dict[str, Any]:
    complete = source_rows()
    complete_summary = {
        "file_count": len(complete),
        "total_bytes": sum(row["size_bytes"] for row in complete),
        "rows_canonical_bytes": len(canonical_bytes(complete)),
        "rows_sha256": sha256_bytes(canonical_bytes(complete)),
    }
    if complete_summary != COMPLETE_SOURCE_EXPECTED:
        raise RuntimeError(f"complete source authority mismatch: {complete_summary}")
    critical = critical_rows()
    critical_summary = {
        "file_count": len(critical),
        "total_bytes": sum(row["size_bytes"] for row in critical),
        "rows_sha256": sha256_bytes(canonical_bytes(critical)),
    }
    if critical_summary != CRITICAL_EXPLANATORY_EXPECTED:
        raise RuntimeError(f"critical explanatory surface mismatch: {critical_summary}")
    document = {
        "schema": "rtdl.goal5793.s0.source_and_admission_freeze.v1",
        "goal": 5793,
        "date": DATE,
        "status": "FROZEN_DECLARED_PRODUCT_NATIVE_SOURCE_CODE_SURFACE__PACKAGE_BUILD_AND_EXECUTION_ENVIRONMENT_NOT_YET_FROZEN",
        "declared_product_native_source_zero_drift_authority": {
            "complete_for_declared_surface": True,
            "complete_build_or_package_closure": False,
            "scope": "all regular non-symlink src/** files excluding cache artifacts, plus the four named declarations Makefile, pyproject.toml, requirements.txt and VERSION",
            "exclusions": ["__pycache__", "*.pyc", "*.nbc", "*.nbi"],
            "summary": complete_summary,
            "rows": complete,
        },
        "critical_explanatory_submanifest": {
            "complete_authority": False,
            "purpose": "responsibility explanation only; not a complete import or execution closure",
            "summary": critical_summary,
            "rows": critical,
            "classification": {
                "critical_product_admission_native_count": 33,
                "historical_evidence_evaluator_count": 4,
                "build_environment_declaration_count": 4,
            },
        },
        "v26_custody": v26_overlap(complete),
        "controlling_scientific_verdict_path": {
            "product_primitive": "src/rtdsl/v4_semantic_physical_admission.py:evaluate_semantic_physical_admission",
            "family_facades": [
                "admit_builtin_triangle_compilation",
                "admit_triangle_reduction_compilation",
                "admit_bounded_relation_compilation",
            ],
            "goal5789_v1_checker_role": "independent normalized-certificate replay only",
            "goal5789_a2_checker_role": "historical five-program/four-binding regression only",
            "new_candidate_controlled_by_a2_checker": False,
            "generic_examiner_exists": False,
            "registry_derivation_frozen": False,
        },
        "execution_environment_and_shared_native_requirements": {
            "authority_created": False,
            "required_before_search_or_entropy": True,
            "required_exact_fields": [
                "clean source archive and sys.path/PYTHONPATH",
                "Python executable bytes and version",
                "NumPy, Numba, llvmlite and CuPy exact package identities or explicit not-used flags",
                "CUDA toolkit, nvcc, header tree and compile options",
                "OptiX header tree and ABI",
                "host compiler, linker and command line",
                "explicit GPU architecture and non-time-derived RTDL_OPTIX_BUILD_ID",
                "resolved absolute libnvrtc and native OptiX library paths plus file hashes",
                "libcuda, driver, GEOS, libstdc++ and glibc resolved identities",
                "GPU model, compute capability and driver",
                "Numba child cache variables and exact leaf-cache authority",
            ],
            "ambient_native_search_allowed": False,
            "clock_derived_build_id_allowed": False,
            "requirements_txt_is_a_lockfile": False,
        },
        "claim_boundary": {
            "all_326_files_are_scientific_tcb_claimed": False,
            "complete_package_or_build_closure_claimed": False,
            "complete_import_closure_claimed_for_41_files": False,
            "toolchain_frozen": False,
            "native_binary_frozen": False,
            "new_candidate_checker_exists": False,
            "product_change_authorized": False,
        },
    }
    return seal(document, "source_authority_sha256")


def default_primary() -> dict[str, Any]:
    return {
        "doi": None,
        "primary_landing_url": None,
        "primary_pdf_url": None,
        "primary_version": None,
        "primary_fetch_status": "NOT_REOPENED__PREEXISTING_CONTAMINATION_ALREADY_EXCLUDES",
        "primary_bytes": None,
        "primary_sha256": None,
        "primary_redistributable": False,
        "author_code_status": "NOT_REOPENED__PREEXISTING_CONTAMINATION_ALREADY_EXCLUDES",
        "author_code": None,
        "semantic_request": None,
        "oracle_kind": None,
        "physical_geometry_family": None,
        "composition": None,
        "source_gaps": [],
        "primary_or_code_bytes_embedded_in_s0_review_artifact": False,
        "reviewer_rehash_requires_network_refetch_or_separate_authority": True,
        "author_code_nonexistence_claimed": False,
        "source_observation_controls_selection_eligibility": False,
    }


def build_candidate_authority() -> dict[str, Any]:
    universe = json.loads(GOAL5753_UNIVERSE.read_text(encoding="utf-8"))
    source_rows_raw = universe["source_rows"]
    if len(source_rows_raw) != 35 or [row["source_index"] for row in source_rows_raw] != list(range(35)):
        raise RuntimeError("Goal5753 source row set drift")
    workload_families = tuple(sorted({row["problem"] for row in source_rows_raw}, key=lambda value: value.encode("utf-8")))
    if workload_families != HISTORICAL_WORKLOAD_FAMILIES:
        raise RuntimeError("Goal5753 32-family projection drift")
    historical = historical_catalog_roots()
    rows = []
    for raw in source_rows_raw:
        candidate_id = raw["candidate_id"]
        primary = dict(default_primary())
        primary.update(PRIMARY_REQUALIFICATION.get(candidate_id, {}))
        if candidate_id in SOURCE_GAP_ANALYZED:
            status = "SOURCE_GAP_ANALYZED__PERMANENTLY_SELECTION_INELIGIBLE"
            reason = "original Goal5753 catalog identity was exposed before the generic examiner freeze; source/oracle/family gaps are recorded only as an audit finding and can never be repaired into Goal5793 selection eligibility"
            role_a = role_b = role_c = "NOT_QUALIFIED__PERMANENTLY_INELIGIBLE"
            expected = "NOT_APPLICABLE__LEGACY_CATALOG_ROW_PERMANENTLY_INELIGIBLE"
        else:
            status = "EXCLUDED"
            if candidate_id in EXCLUSION_OVERRIDES:
                reason = EXCLUSION_OVERRIDES[candidate_id]
            elif not raw["eligible"]:
                reason = f"EXCLUDE_GOAL5753_PREEXISTING_USE__{raw['disposition']}"
            else:
                raise RuntimeError(f"unclassified old-eligible candidate: {candidate_id}")
            role_a = role_b = role_c = "NOT_QUALIFIED"
            expected = "NOT_APPLICABLE__EXCLUDED_BEFORE_SELECTION"
        rows.append(
            {
                "source_index": raw["source_index"],
                "candidate_id": candidate_id,
                "citation_key": raw["citation_key"],
                "paper": raw["paper"],
                "problem": raw["problem"],
                "goal5753_original_eligible": raw["eligible"],
                "goal5753_original_disposition": raw["disposition"],
                "paper_identity_visible_via_goal5753_catalog": True,
                "normalized_workload_family_assessed_via_goal519_521": True,
                "paper_specific_source_level_assessment_before_s0": "NOT_CLAIMED",
                "unseen_claimed": False,
                "blind_claimed": False,
                "held_out_from_design_claimed": False,
                "historical_catalog_roots": historical,
                "primary_source_requalification": primary,
                "performance_fields_present_but_ignored": sorted(raw["survey_measurements"].keys()),
                "performance_or_ease_used_for_eligibility": False,
                "eligibility_status": status,
                "eligibility_reason": reason,
                "descriptive_stress_axes_not_role_qualification": SOURCE_GAP_STRESS_AXES.get(candidate_id, []),
                "role_a_unconventional_correct_expected_admission": role_a,
                "role_b_different_geometry_or_composition": role_b,
                "role_c_non_obvious_risk": role_c,
                "expected_disposition": expected,
                "selection_forbidden": True,
                "selection_forbidden_reason": "all original Goal5753 rows are permanently ineligible after pre-examiner author exposure; additionally this catalog has zero qualified Role-A expected-admission candidates and zero valid ordered triplets",
            }
        )
    rows.sort(key=lambda row: row["source_index"])
    counts = {
        "survey_rows": 35,
        "excluded_rows": sum(row["eligibility_status"] == "EXCLUDED" for row in rows),
        "source_gap_analyzed_permanently_ineligible_rows": sum(row["eligibility_status"].startswith("SOURCE_GAP_ANALYZED") for row in rows),
        "selection_eligible_rows": 0,
        "qualified_role_a_rows": 0,
        "qualified_role_b_rows": 0,
        "qualified_role_c_rows": 0,
        "eligible_ordered_triplets": 0,
    }
    if counts != {
        "survey_rows": 35,
        "excluded_rows": 30,
        "source_gap_analyzed_permanently_ineligible_rows": 5,
        "selection_eligible_rows": 0,
        "qualified_role_a_rows": 0,
        "qualified_role_b_rows": 0,
        "qualified_role_c_rows": 0,
        "eligible_ordered_triplets": 0,
    }:
        raise RuntimeError(f"unexpected requalification counts: {counts}")
    document = {
        "schema": "rtdl.goal5793.s0.known_universe_requalification.v1",
        "goal": 5793,
        "date": DATE,
        "status": "FROZEN_35_ROW_REQUALIFICATION__ZERO_QUALIFIED_ROLE_A__ZERO_TRIPLETS__NO_ENTROPY",
        "source_universe": identity(GOAL5753_UNIVERSE),
        "source_universe_historical_filename_disclaimer": "the immutable path contains held_out only as a historical filename; it is not checker/calculus generalization evidence and no held-out claim is made",
        "source_protocol": identity(GOAL5753_PROTOCOL),
        "survey_source": universe["source"],
        "historical_author_exposure": {
            "exact_35_paper_problem_identities_visible_via_goal5753_catalog": True,
            "normalized_workload_family_count": 32,
            "normalized_workload_families": list(HISTORICAL_WORKLOAD_FAMILIES),
            "normalized_workload_families_assessed_via_goal519_521": True,
            "paper_specific_source_level_feasibility_assessment_before_s0_claimed": False,
            "unseen_or_blind_wording_allowed": False,
            "strongest_allowed_description_for_old_35": "fully enumerated 35-row author-seen legacy catalog; permanently selection-ineligible for Goal5793",
            "roots": historical,
        },
        "uniform_policy": {
            "all_35_rows_preserved": True,
            "all_35_rows_permanently_selection_ineligible": True,
            "later_query_match_to_any_old_identity_is_duplicate_crosslink_only": True,
            "old_exclusions_preserved": True,
            "missing_primary_source_is_a_gap_not_eligibility": True,
            "same_paper_and_normalized_problem_family_contamination_excluded": True,
            "non_rt_core_and_nonstock_hardware_excluded": True,
            "performance_speedup_and_implementation_ease_ignored": True,
            "manual_fallback_allowed": False,
        },
        "role_definitions": {
            "A": "UNCONVENTIONAL_CORRECT_EXPECTED_ADMISSION; mandatory exact source/oracle, existing registered family and obligation projection, categorical expected COMPATIBLE, plus at least one enumerated structural-axis difference from every X1-frozen positive vector; rejection or UNKNOWN is retained",
            "B": "DIFFERENT_GEOMETRY_OR_COMPOSITION; exact source-backed geometry/composition-axis difference from every X1-frozen positive vector; expected disposition is frozen and may honestly be COMPATIBLE, UNKNOWN or INCOMPATIBLE",
            "C": "NON_OBVIOUS_RISK; at least one source-backed true flag from the fixed multiplicity/tie_boundary/continuation/ownership_epoch/global_composition risk vocabulary; honest failure is retained",
            "unresolved_or_disputed_role": "SELECTION_INELIGIBLE__NO_HUMAN_FALLBACK",
        },
        "counts": counts,
        "ordered_triplets": [],
        "ordered_triplet_rows_sha256": sha256_bytes(canonical_bytes([])),
        "rows": rows,
        "source_evidence_reachability": {
            "primary_pdf_or_code_archive_bytes_embedded": False,
            "observed_hashes_are_reviewer_reachable_without_refetch": False,
            "why_noncontrolling": "every original 35-row identity is permanently selection-ineligible regardless of later source closure",
            "allowed_claim": "URL/version/hash observations and exact Git commit/tree pins; no self-contained primary-source packet claim",
        },
        "claim_boundary": {
            "old_goal5753_eligible_count_remains_current": False,
            "current_pool_has_expected_admission_positive": False,
            "current_pool_supports_entropy_draw": False,
            "candidate_unseen_claimed": False,
            "candidate_blind_claimed": False,
            "held_out_from_checker_design_claimed": False,
            "old_35_can_reenter_future_expansion": False,
            "paper_specific_source_feasibility_for_all_35_claimed": False,
            "systematic_expansion_required": True,
        },
    }
    return seal(document, "candidate_authority_sha256")


def build_protocol_authority() -> dict[str, Any]:
    queries = [
        "ray tracing core",
        "ray tracing cores",
        "ray tracing unit",
        "ray tracing units",
        "ray tracing accelerator",
        "ray tracing accelerators",
        "hardware ray tracing",
        "DirectX Raytracing",
        "Vulkan ray tracing",
        "OptiX",
        "HIPRT",
    ]
    document = {
        "schema": "rtdl.goal5793.s0.protocol_and_stage_authority.v1",
        "goal": 5793,
        "date": DATE,
        "status": "PROTOCOL_FROZEN__GENERIC_EXAMINER_AND_EXPANSION_NOT_EXECUTED__NO_ENTROPY",
        "state_machine": [
            "A2_CLOSED",
            "S0_35ROW_FROZEN__EXTERNAL_REVIEW_PENDING",
            "S0_35ROW_TERMINAL_REVIEWED",
            "X1_GENERIC_EXAMINER_REGISTRY_ENV_SHARED_NATIVE_IMPLEMENTED_REVIEWED",
            "X2_HARVESTER_ENTROPY_CLIENT_AND_EXPANSION_PROTOCOL_IMPLEMENTED_OFFLINE_REVIEWED",
            "X3_FIRST_LIVE_SEARCH_EXECUTED__SCIENCE_PROJECTED__TRIPLETS_FROZEN_REVIEWED",
            "E0_DEFERRED_NIST_ANCHOR_AND_FUTURE_TARGET",
            "E1_SELECTED_TRIPLET",
            "P1_SELECTED_SCIENCE_PREREG_REVIEWED",
            "P2_CANDIDATE_IMPLEMENTATION_FREEZE",
            "P3_EXAMS",
            "RESULT",
            "TERMINAL_SINGLE_EXPANSION_EMPTY_CONTAMINATED_OR_PROTOCOL_INVALID",
            "TERMINAL_SEARCH_INFRASTRUCTURE_FAILURE",
            "TERMINAL_ENTROPY_OR_COUNTER_INFRASTRUCTURE_FAILURE",
            "TERMINAL_VALID_SCIENTIFIC_RESULT",
        ],
        "stage_transition_guards": {
            "S0_TO_X1": "exact returned S0 review with P0=0/P1=0 plus append-only owner absorption/closure that authorizes X1 only",
            "X1_TO_X2": "exact generic examiner, registry derivation, environment and shared-native authorities; hostile tests; returned external review P0=0/P1=0; append-only owner closure",
            "X2_TO_X3": "exact offline harvester, taxonomy, enumerator, NIST verifier, trust bundle and selection client; zero live calls; returned external review P0=0/P1=0; append-only owner closure",
            "X3_TO_E0": "one complete live search with all pages/responses preserved; complete append-only row table and all preentropy science projections frozen; zero preselection decision invocations; exact triplet manifest nonempty; returned external review P0=0/P1=0; append-only owner closure",
            "E0_TO_E1": "authenticated first-next anchor and exact future target satisfy the frozen NIST verifier and selection mapping; no alternate pulse",
            "E1_TO_P1": "selected triplet identity is the exact indexed member of the reviewed ordered-triplet manifest",
            "P1_TO_P2": "selected rows retain preentropy science projections; exact bounded inputs, allowed paths and outcome consequences are separately reviewed and owner-closed",
            "P2_TO_P3": "candidate app-only implementation and all mechanical identity slots are frozen; zero 326-source drift; functional execution separately authorized; no POD/SSH or timing",
            "P3_TO_RESULT": "all three lineages retained, including rejection/UNKNOWN/failure/invalid successors, with no replacement or rescue",
            "state_label_alone_never_authorizes_transition": True,
            "every_transition_requires_exact_predecessor_artifact_and_internal_seal": True,
            "transition_receipt_exact_schema": {
                "required_keys": [
                    "schema",
                    "from_state",
                    "to_state",
                    "predecessor_root_path_bytes_file_sha256_internal_seal",
                    "single_cfr_path_bytes_file_sha256",
                    "returned_review_path_bytes_file_sha256_verdict_p0_p1",
                    "owner_closure_path_bytes_file_sha256_internal_seal",
                    "authorization_exact_keyset_and_values",
                    "transition_receipt_sha256",
                ],
                "returned_review_required_p0": 0,
                "returned_review_required_p1": 0,
                "missing_unknown_or_extra_field": "FAIL_CLOSED__TRANSITION_NOT_AUTHORIZED",
                "authorization_is_never_inferred_from_state_label": True,
            },
            "terminal_sink_states": [
                "TERMINAL_SINGLE_EXPANSION_EMPTY_CONTAMINATED_OR_PROTOCOL_INVALID",
                "TERMINAL_SEARCH_INFRASTRUCTURE_FAILURE",
                "TERMINAL_ENTROPY_OR_COUNTER_INFRASTRUCTURE_FAILURE",
                "TERMINAL_VALID_SCIENTIFIC_RESULT",
            ],
        },
        "current_state": "S0_35ROW_FROZEN__EXTERNAL_REVIEW_PENDING",
        "current_literals": {
            "known_universe_rows": 35,
            "old_catalog_selection_eligible_count": 0,
            "qualified_role_a_count": 0,
            "eligible_ordered_triplet_count": 0,
            "generic_examiner_exists": False,
            "systematic_search_execution_count": 0,
            "live_provider_call_count": 0,
            "entropy_draw_count": 0,
            "anchor": None,
            "target_output": None,
            "selected_triplet": None,
            "candidate_implementation_count": 0,
            "exam_count": 0,
        },
        "x1_generic_examiner_contract": {
            "implementation_authorized_now": False,
            "search_or_entropy_authorized_by_x1": False,
            "location": "scripts/ and tests/ only; zero src/** changes",
            "decision_code_forbidden_inputs": [
                "candidate_id",
                "citation_key",
                "source_index",
                "role_assignment",
                "expected_disposition",
                "selected_index",
                "performance_expectation",
                "implementation_ease",
            ],
            "required_controlling_path": [
                "candidate-agnostic registry derivation from predeclared family template and mechanical identity slots",
                "product evaluate_semantic_physical_admission",
                "matching family admit_* facade",
                "if compatible: matching compile_semantically_admitted_* and run_semantically_admitted_*",
                "independent Goal5789-v1 normalized-certificate replay",
                "independent oracle and behavioral true-OptiX receipt",
            ],
            "product_vs_independent_disagreement": "INFRA_INVALID__NEVER_PICK_FAVORABLE_VERDICT",
            "registry_derivation": {
                "must_be_frozen_before_expansion_search": True,
                "allowed_postfreeze_slots": [
                    "IR digest",
                    "effect digest",
                    "schema digest",
                    "ABI digest",
                    "plan digest",
                    "native digest",
                    "source digest",
                ],
                "forbidden_postfreeze_changes": [
                    "semantic obligation",
                    "physical guarantee",
                    "geometry family",
                    "role or opcode",
                    "rule",
                    "registry template",
                    "facade",
                ],
            },
            "required_hostiles": [
                "candidate metadata rename/swap/permutation leaves decision projection invariant",
                "expected disposition mutation leaves decision projection invariant",
                "candidate-keyed/hash-keyed/index-keyed branches absent by AST and mutation audit",
                "existing 15-lane baseline and semantic/physical adversarial mutations replay",
            ],
            "presearch_positive_vector_freeze": {
                "required": True,
                "content": "exact structural-axis vectors for every current compatible positive, frozen before any expansion result is observed",
                "candidate_or_outcome_specific_edits_allowed": False,
            },
            "pre_x1_declared_project_exposure_registry": {
                "must_be_complete_and_reviewed_before_x2_implementation_or_first_live_call": True,
                "minimum_sources": [
                    "all regular repository text/JSON/Markdown/bibliography paths in the frozen S0 workspace snapshot",
                    "all unique strict-UTF8 text/JSON/Markdown/bibliography/source blobs reachable from every Git commit reachable in the local repository, keyed by blob SHA-256 and original commit/path",
                    "all predecessor review/CFR/result/report/manifests and all safely readable archive-member contents reachable from the S0 DAG",
                    "all Goal5753 35-row identities and aliases",
                    "owner append-only disclosure of off-repository papers/code used to design, implement, tune or evaluate the frozen checker/calculus",
                ],
                "normalized_aliases": ["DOI", "versionless arXiv id", "OpenAlex work id", "normalized title plus first author plus year", "citation key as noncontrolling alias"],
                "all_matches_permanently_selection_ineligible_and_crosslink_only": True,
                "absence_means_only_not_matched_to_the_frozen_declared_registry": True,
                "complete_author_mental_exposure_claimed": False,
                "archive_scan_rule": "recursively enumerate each reachable supported tar/zip/gzip container under frozen depth/byte limits; reject unsafe, duplicate, linked or aliased members; hash every container/member; extract identifiers from every strict-UTF8 text/JSON/Markdown/bibliography/source member and from every PDF through the frozen parser; any unsupported, unreadable or limit-exceeding member is an explicit registry-coverage gap",
                "archive_member_path_or_index_only_is_sufficient": False,
                "registry_coverage_gap_allows_unseen_claim": False,
                "unseen_blind_or_held_out_claim_allowed": False,
                "later_discovered_preexisting_project_exposure": "PROTOCOL_CONTAMINATION__TERMINATE_SINGLE_EXPANSION__NO_REPLACEMENT_OR_REUSE",
            },
            "private_registry_issuer_if_used": {
                "public_api_only": False,
                "supports_user_usability_claim": False,
                "scope": "calculus experiment only until a public product catalog exists",
            },
        },
        "x1_environment_and_shared_native_contract": {
            "implementation_authorized_now": False,
            "must_freeze_all_fields_listed_in_source_authority": True,
            "one_shared_native_or_exact_derivation_for_all_exams": True,
            "candidate_specific_native_build_allowed": False,
            "ambient_library_search_allowed": False,
            "time_derived_build_identity_allowed": False,
            "home_gpu_authorized_now": False,
            "pod_or_ssh_allowed_for_goal5793": False,
            "registered_or_performance_timing_count": 0,
        },
        "x2_systematic_expansion": {
            "implementation_or_query_execution_authorized_now": False,
            "harvester_implementation_network_access_allowed": False,
            "harvester_implementation_fixture_mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
            "entropy_client_or_verifier_implementation_authorized_now": False,
            "entropy_client_or_verifier_network_access_during_implementation_allowed": False,
            "entropy_client_and_verifier_must_be_frozen_reviewed_and_owner_closed_before_first_live_search": True,
            "entropy_client_offline_fixture_requirements": [
                "exact target response accepted only when the parsed RFC3339 timeStamp equals committed target_ms",
                "next-closest target response rejected even when HTTP status is 200",
                "wrong chainIndex, pulseIndex, URI, output length, certificateId, signature or chain proof rejected",
                "same exact target URI retained across missing and nonexact responses",
                "selection mapping known-answer test reproduced byte-for-byte",
                "selection N=0 makes zero beacon/hash requests and terminates without selection",
                "selection N=1 still authenticates anchor/target, records counter-0 digest and selects index 0",
                "rejection-boundary and counter-exhaustion vectors reproduce exactly",
            ],
            "live_provider_call_count_before_x2_owner_closure_required": 0,
            "first_live_provider_call_stage": "X3_ONLY_AFTER_X2_EXTERNAL_REVIEW_AND_OWNER_CLOSURE",
            "publication_date_window": {"from": "2018-01-01", "through": DATE},
            "logical_search_terms": queries,
            "global_query_execution_order": {
                "provider_order": ["OpenAlex Works API", "arXiv API"],
                "term_order": queries,
                "loop_order": "for each provider in provider_order, execute each term in term_order; finish and validate every page of one provider-term query before starting the next",
                "concurrent_or_interleaved_requests_allowed": False,
                "worker_count": 1,
                "provider_index_snapshot_or_pagination_consistency_failure": "INFRA_INVALID__TERMINATE_SINGLE_EXPANSION__NO_PARTIAL_UNIVERSE_OR_RERUN",
            },
            "providers": [
                {
                    "name": "OpenAlex Works API",
                    "endpoint": "https://api.openalex.org/works",
                    "documentation": "https://help.openalex.org/",
                    "request_template": {
                        "search": "exact logical term string",
                        "filter": "from_publication_date:2018-01-01,to_publication_date:2026-08-22",
                        "per-page": 200,
                        "cursor_initial": "*",
                    },
                    "pagination_rule": "follow response.meta.next_cursor exactly until null; preserve every page including zero-result pages; no relevance cutoff or early stop",
                    "per_page": 200,
                },
                {
                    "name": "arXiv API",
                    "endpoint": "https://export.arxiv.org/api/query",
                    "documentation": "https://info.arxiv.org/help/api/user-manual.html",
                    "request_template": {
                        "search_query": "submittedDate:[201801010000 TO 202608222359] AND all:\"<exact logical term>\"",
                        "start_initial": 0,
                        "max_results": 500,
                        "sortBy": "submittedDate",
                        "sortOrder": "ascending",
                    },
                    "pagination_rule": "increment start by the exact returned entry count until start reaches opensearch:totalResults; preserve every page; three-second minimum inter-request delay; no relevance cutoff",
                    "page_size": 500,
                },
            ],
            "request_failure_policy": {
                "retry_same_request_only": True,
                "retry_delay_seconds": [3, 6, 12, 24, 48],
                "maximum_attempts_including_initial": 6,
                "schema_drift_incomplete_pagination_truncation_or_exhausted_retry": "INFRA_INVALID__NO_PARTIAL_UNIVERSE__NO_ALTERNATE_PROVIDER_OR_QUERY",
                "partial_results_eligible": False,
                "openalex_repeated_nonnull_cursor_or_no_progress": "INFRA_INVALID__NO_PARTIAL_UNIVERSE",
                "arxiv_zero_entries_before_start_reaches_stable_total_or_total_changes": "INFRA_INVALID__NO_PARTIAL_UNIVERSE",
                "duplicate_page_body_or_request_identity": "INFRA_INVALID__NO_PARTIAL_UNIVERSE",
            },
            "raw_response_rule": "preserve every raw response body, request URL/params, headers, retrieval UTC time and SHA-256; no row may be omitted because full text or code is missing",
            "uniform_full_text_resolution": {
                "applies_to_every_deduplicated_row_before_any_role_decision": True,
                "ordered_url_slots": [
                    "arXiv PDF URL mechanically derived from a provider-returned arXiv id",
                    "OpenAlex primary_location.pdf_url when is_oa is true",
                    "OpenAlex best_oa_location.pdf_url when is_oa is true",
                    "remaining OpenAlex locations with is_oa true and non-null pdf_url, sorted by normalized URL UTF-8 bytes",
                    "https://doi.org/<normalized DOI> requested with Accept: application/pdf and at most ten recorded HTTPS redirects",
                ],
                "duplicate_normalized_urls_attempted_once": True,
                "per_url_attempt_policy": "same exact six-attempt retry schedule as provider requests; no row-specific extension",
                "successful_full_text_rule": "HTTP 200 final response, Content-Type application/pdf after parameter stripping, body begins %PDF-, nonempty SHA-256 and preserved raw bytes",
                "authoritative_work_identity_crosscheck": {
                    "arxiv_slot": "requested versioned arXiv id must equal the provider-returned normalized versioned id and the preserved arXiv landing metadata",
                    "doi_slot": "requested normalized DOI, complete redirect chain and final landing identity must preserve the same normalized DOI",
                    "openalex_slot": "the selected OA location must be an exact member of the preserved OpenAlex record for the same deduplication component",
                    "document_identity": "the frozen PDF parser must extract and match a controlling DOI/arXiv id, or otherwise exact normalized title plus first author plus publication year, against the component authority",
                    "missing_ambiguous_or_conflicting_identity": "SOURCE_GAP__SELECTION_INELIGIBLE__NO_MANUAL_VERSION_SUBSTITUTION",
                    "manual_paper_or_version_choice_allowed": False,
                },
                "first_success_controls_primary_full_text": True,
                "later_slots_after_first_success_requested": False,
                "general_web_search_author_homepage_search_or_manual_extra_attempt_allowed": False,
                "unresolved_result": "SOURCE_GAP__SELECTION_INELIGIBLE_FOR_THIS_SINGLE_EXPANSION",
                "all_attempts_redirects_status_headers_bodies_and_errors_preserved": True,
                "source_resolution_outcome_cannot_drop_a_row_from_the_append_only_universe": True,
            },
            "author_code_policy": {
                "author_code_required_for_selection_eligibility": False,
                "availability_or_convenience_used_for_role_or_ranking": False,
                "only_direct_machine-readable artifact or repository links from preserved provider records or controlling primary full text may be followed": True,
                "general_repository_search_allowed": False,
                "direct_link_extraction_and_resolution": {
                    "source_order": [
                        "preserved OpenAlex record locations in their preserved array order",
                        "preserved arXiv metadata links in their preserved array order",
                        "controlling primary PDF hyperlinks in PDF object order then annotation index order",
                    ],
                    "url_normalization": "RFC3986 absolute HTTPS URL; lowercase scheme and host; remove default port; remove fragment; preserve path/query bytes; reject credentials and non-HTTPS URLs",
                    "crawl_depth": 1,
                    "repository_page_link_following_allowed": False,
                    "redirect_limit": 10,
                    "all_direct_links_are_attempted_in_order": True,
                    "first_success_short_circuit_allowed": False,
                    "multiple_distinct_repository_or_ref_candidates": "NA_AMBIGUOUS_AUTHOR_CODE__NO_MANUAL_CHOICE",
                    "stop_condition": "after every unique normalized direct link has one resolution lineage or the fixed request retry schedule terminates",
                },
                "repository_materialization": {
                    "git_ref_resolution": "record remote URL, requested ref, resolved 40-hex commit and tree; an unqualified repository URL resolves its advertised default-branch HEAD once at the preserved response time",
                    "archive_identity": "preserve exact downloaded archive bytes, SHA-256, member manifest and license; regenerated archives are not equivalent",
                    "submodules": "preserve gitlink path+commit and fetch each direct submodule once; any unavailable gitlink makes the author-code comparison NA_INCOMPLETE_SUBMODULE",
                    "git_lfs": "preserve pointer bytes, oid and size and fetch each object once; any unavailable object makes the author-code comparison NA_INCOMPLETE_LFS",
                    "conflicting_ref_or_tree": "NA_AMBIGUOUS_AUTHOR_CODE__NO_MANUAL_CHOICE",
                    "missing_or_unmaterializable_code_affects_scientific_eligibility": False,
                },
                "every_followed_link_and_failure_preserved": True,
            },
            "deduplication_algorithm": {
                "raw_nodes": "one immutable node per returned provider record; retain provider, page, ordinal, raw bytes and normalized identifiers",
                "edge_rules_in_order": [
                    "same non-null normalized DOI",
                    "same non-null versionless arXiv identifier",
                    "same non-null canonical OpenAlex work identifier",
                ],
                "component_algorithm": "compute the full transitive closure with deterministic union-find over raw-node ids sorted by UTF-8 bytes; component membership is independent of provider/page/input order",
                "strong_identifier_conflict": "if one connected component contains more than one distinct non-null normalized DOI or more than one distinct non-null versionless arXiv id, mark every node IDENTITY_CONFLICT__SELECTION_INELIGIBLE; do not split, merge or resolve by hand",
                "fallback_identity_is_never_an_equivalence_edge": True,
                "fallback_cross_component_rule": "after strong-ID closure, if the same fallback identity occurs in two or more distinct raw-node components, including an all-fallback/no-strong-ID collision, preserve every raw node and mark every touched component FALLBACK_IDENTITY_AMBIGUOUS__SELECTION_INELIGIBLE; do not merge, weight, split or resolve by hand",
                "post_full_text_closure_rule": "extract all newly observed DOI/arXiv/OpenAlex aliases from the controlling full text, add them to the raw nodes, rerun the full closure/conflict/old-exposure checks before emitting the final append-only row table",
                "representative_rule": "within a conflict-free component choose the lexicographically smallest UTF-8 normalized value at the first nonempty priority level DOI, arXiv or OpenAlex; a singleton no-strong-ID raw node may use its fallback digest; prefix it with doi:, arxiv:, openalex:, or fallback_sha256:",
                "all_aliases_preserved_and_crosslinked": True,
                "provider_or_input_order_can_change_components_or_representative": False,
                "unresolved_conflict_human_fallback_allowed": False,
            },
            "canonical_work_identity": {
                "priority": ["lowercase normalized DOI", "lowercase versionless arXiv id", "uppercase OpenAlex W identifier", "fallback identity digest"],
                "doi_rule": "trim ASCII whitespace; remove one case-insensitive doi: or https://doi.org/ prefix; ASCII lowercase; reject embedded whitespace",
                "arxiv_rule": "take API id tail; remove one terminal v[0-9]+; ASCII lowercase",
                "openalex_rule": "take canonical W[0-9]+ token and uppercase W",
                "fallback_rule": "sha256 of canonical JSON {title:NFKC-casefold-whitespace-collapse,first_author:NFKC-casefold-whitespace-collapse,year:plain integer}",
                "candidate_id_rule": "prefix the first available identity with doi:, arxiv:, openalex:, or fallback_sha256:",
            },
            "old_35_duplicate_policy": {
                "old_rows_can_become_selection_eligible": False,
                "query_matches_are_retained_as_duplicate_crosslinks": True,
                "alias_registry_must_be_frozen_and_reviewed_before_first_live_call": True,
                "alias_inputs": ["candidate_id", "citation_key", "paper title", "DOI where already pinned", "arXiv id where already pinned"],
                "matching_is_transitive_over_the_frozen_deduplication_components": True,
                "any_component_touching_an_old_35_alias_is_permanently_selection_ineligible": True,
            },
            "uniform_inclusion_gate": [
                "primary paper or exact authoritative version can be pinned",
                "stock programmable RT API or hardware path; no modified-hardware-only proposal",
                "non-graphics scientific or general-purpose computation",
                "bounded independent semantic oracle can be frozen",
                "not used to design, implement, tune or evaluate the frozen checker/calculus",
                "preimplementation primary-source projection predicts no src/native/rule/role/opcode/family change",
            ],
            "forbidden_screening_features": [
                "within-role estimated probability of compatibility, admission, rejection, or any favorable outcome",
                "expected speedup",
                "implementation ease",
                "paper prestige",
                "availability of a convenient existing RTDL app",
            ],
            "single_expansion_only": True,
            "manual_fallback_or_second_query_round": False,
            "empty_role_or_triplet_outcome": "TERMINAL_NEGATIVE__NO_SELECTION__NO_RESCUE",
            "literature_completeness_claimed": False,
        },
        "x3_preentropy_science_projection": {
            "applies_to": "every retrieved row before eligibility, triplet enumeration, anchor or entropy",
            "required_exact_fields": [
                "canonical candidate id and work identity",
                "all source/code/oracle pins and source gaps",
                "normalized problem-family id and source anchors",
                "semantic domain plus exact obligation projection",
                "physical geometry family plus exact guarantee projection",
                "oracle kind, exactness, inputs and independent implementation authority",
                "structural-axis vector",
                "risk-flag vector",
                "categorical expected disposition",
                "Role-A, Role-B and Role-C booleans with mechanical reason ids",
                "preimplementation core-change prediction",
                "product-path classification and exact public/private call surface",
            ],
            "normalized_problem_family_rule": {
                "controlled_vocabulary_frozen_before_first_live_call": True,
                "unmapped_label_after_first_live_call": "SELECTION_INELIGIBLE__NO_TAXONOMY_AMENDMENT_DURING_SINGLE_EXPANSION",
                "new_split_merge_or_label_after_first_live_call_allowed": False,
                "taxonomy_amendment_consequence": "TERMINATE_CURRENT_SINGLE_EXPANSION__SEPARATE_PREREGISTRATION_REQUIRED__NO_REUSE_OF_OBSERVED_ROWS",
                "unresolved_or_reviewer_disputed_assignment": "SELECTION_INELIGIBLE__NO_HUMAN_FALLBACK",
                "postentropy_split_merge_or_rename_allowed": False,
            },
            "structural_axis_vocabulary": [
                "geometry_family",
                "primitive_type",
                "ray_construction",
                "hit_policy",
                "multiplicity",
                "boundary_convention",
                "tie_break",
                "numeric_domain",
                "overflow_domain",
                "decode",
                "continuation",
                "composition",
                "ownership_epoch",
            ],
            "structural_value_protocol": {
                "exact_allowed_values_per_axis_frozen_and_reviewed_in_x2_before_first_live_call": True,
                "candidate_vector_exact_keyset_equals_structural_axis_vocabulary": True,
                "unmapped_or_disputed_value": "SELECTION_INELIGIBLE__NO_POSTSEARCH_VOCABULARY_EXTENSION",
                "role_a_difference": "candidate vector has at least one unequal normalized axis value versus each X1-frozen compatible-positive vector",
                "role_b_difference_axes": ["geometry_family", "primitive_type", "continuation", "composition"],
                "role_b_difference": "at least one role_b_difference_axes value differs from every X1-frozen compatible-positive vector",
            },
            "risk_flag_vocabulary": ["multiplicity", "tie_boundary", "continuation", "ownership_epoch", "global_composition"],
            "risk_flag_derivation": {
                "multiplicity": "true iff requested correctness depends on more than one accepted hit per logical query or on exact duplicate multiplicity",
                "tie_boundary": "true iff requested correctness can change under equal keys/distances or inclusive-versus-exclusive boundary choice",
                "continuation": "true iff a traversal result or callback state determines whether or how a subsequent traversal is issued",
                "ownership_epoch": "true iff requested correctness depends on mutable ownership, update epoch, or cross-trace state version",
                "global_composition": "true iff the requested output requires a global aggregation or iterative composition beyond independent per-query decoding",
                "required_source_anchor_for_each_true_flag": True,
                "unresolved_or_disputed_flag": "SELECTION_INELIGIBLE__NO_HUMAN_FALLBACK",
            },
            "role_predicates": {
                "A": "eligible AND stock_rt AND exact_source_and_oracle AND existing_registered_family AND expected_disposition==COMPATIBLE AND matching public admit/compile/run facade reachable AND no_core_change_predicted AND for every X1-frozen positive P there exists at least one structural-axis A such that candidate[A] != P[A]",
                "B": "eligible AND stock_rt AND exact_source_basis AND for every X1-frozen positive P there exists at least one axis A in [geometry_family,primitive_type,continuation,composition] such that candidate[A] != P[A]; expected disposition may be COMPATIBLE, UNKNOWN or INCOMPATIBLE",
                "C": "eligible AND stock_rt AND exact_source_basis AND at least one fixed risk flag is true",
            },
            "role_predicate_quantifiers": {
                "A": "all(any(candidate[axis] != positive[axis] for axis in structural_axis_vocabulary) for positive in x1_frozen_positive_vectors)",
                "B": "all(any(candidate[axis] != positive[axis] for axis in role_b_difference_axes) for positive in x1_frozen_positive_vectors)",
                "C": "any(candidate_risk_flags[flag] is true for flag in risk_flag_vocabulary)",
                "empty_x1_positive_vector_set": "INFRA_INVALID__ROLE_DIVERSITY_UNDEFINED",
            },
            "role_a_categorical_expected_compatible_required": True,
            "role_a_expected_compatible_is_a_required_categorical_predicate_not_a_success_probability_or_ranking_feature": True,
            "within_role_ranking_by_success_probability_allowed": False,
            "projection_change_after_x3_closure_allowed": False,
            "actual_core_change_discovered_after_selection": "VALID_SCIENTIFIC_INCOMPATIBLE_OR_UNKNOWN__NOT_INFRA_INVALID__NO_RECLASSIFICATION_OR_REPLACEMENT",
            "actual_exam_outcome_or_checker_verdict_available_when_projection_is_authored": False,
            "preselection_decision_isolation": {
                "future_candidate_examiner_invocation_count_before_selection": 0,
                "future_candidate_authority_materializer_invocation_count_before_selection": 0,
                "future_candidate_product_evaluate_admit_compile_run_invocation_count_before_selection": 0,
                "future_candidate_app_implementation_count_before_selection": 0,
                "future_candidate_execution_receipt_count_before_selection": 0,
                "science_projection_route_may_parse_preserved_primary_sources_and_construct_declarative_obligation_fields": True,
                "science_projection_route_may_import_or_call_generic_examiner_product_evaluate_admit_compile_run_or_candidate_app": False,
                "required_evidence": [
                    "static import and call audit over projection code",
                    "zero examiner/materializer/product-decision invocation ledger",
                    "zero candidate implementation and execution receipt manifest",
                ],
                "violation": "PRESELECTION_OUTCOME_LEAKAGE__TERMINATE_SINGLE_EXPANSION__NO_SELECTION_OR_REUSE",
            },
            "product_path_classification": {
                "exact_enum": [
                    "PUBLIC_FACADE_AND_PUBLIC_AUTHORITY_ISSUANCE",
                    "PUBLIC_FACADE_WITH_PRIVATE_REGISTRY_ISSUER",
                    "REFERENCE_ADMISSION_ONLY",
                ],
                "private_registry_issuer_must_be_disclosed": True,
                "only_public_facade_and_public_authority_issuance_supports_end_user_product_path": True,
                "private_or_reference_path_supports_usability_claim": False,
                "classification_change_after_x3_closure_allowed": False,
            },
        },
        "x3_triplet_enumeration": {
            "candidate_set": "only uniformly eligible X3 rows not matched through the deterministic transitive alias closure to the frozen pre-X1 declared project-exposure registry; all registry matches, including the original 35, remain append-only visible and permanently ineligible; no unseen or complete-author-exposure claim",
            "ordered_roles": ["A", "B", "C"],
            "constraints": [
                "three distinct candidate ids",
                "three distinct canonical work identities",
                "three distinct normalized problem families",
                "A satisfies unconventional correct expected-admission predicate",
                "B satisfies different geometry or composition predicate",
                "C satisfies a non-obvious multiplicity/tie/boundary/continuation/epoch/global-composition risk predicate",
            ],
            "enumerator": "sort eligible rows by UTF-8 bytes of canonical candidate_id; nested loops over A-qualified, B-qualified, C-qualified rows; retain exactly the triples satisfying every constraint; emit [A_id,B_id,C_id]; sort triples lexicographically as three-element tuples by comparing each element's UTF-8 byte string in A-then-B-then-C order, never by delimiter-free concatenation",
            "conflict_group_derivation": {
                "manual_conflict_group_ids_allowed": False,
                "same_work_conflict": "same deterministic deduplication component/canonical work identity",
                "same_problem_conflict": "same exact normalized problem-family vocabulary value",
                "additional_conflict_types": [],
                "unknown_or_disputed_conflict": "SELECTION_INELIGIBLE__NO_HUMAN_FALLBACK",
                "pairwise_distinctness_uses_only_same_work_and_same_problem_conflicts": True,
            },
            "citation_key_used_for_uniqueness_or_probability": False,
            "manual_pruning_allowed": False,
        },
        "deferred_entropy": {
            "authorized_now": False,
            "provider": "NIST Randomness Beacon 2.0 Beta",
            "documentation": "https://csrc.nist.gov/Projects/interoperable-randomness-beacons/beacon-20",
            "api_base": "https://beacon.nist.gov/beacon/2.0",
            "normative_source_authority": {
                "nist_ir_8213_draft": {
                    "url": "https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8213-draft.pdf",
                    "doi": "10.6028/NIST.IR.8213-draft",
                    "bytes_observed_2026_08_22": 762001,
                    "sha256_observed_2026_08_22": "6fee39f6cd82d6c1ab219e29bdec77cbf3e07075324ac3202661d7578ee8f183",
                    "status": "DRAFT",
                },
                "nist_beacon_2_xsd": {
                    "url": "https://csrc.nist.gov/csrc/media/Projects/interoperable-randomness-beacons/documents/certificate/beacon-2.0.xsd",
                    "bytes_observed_2026_08_22": 19033,
                    "sha256_observed_2026_08_22": "24c5b5b6508c0c33db2cda1902ea7f3b2009224895ba4e3fe275b7f4511675d6",
                },
                "service_status": "NIST Beacon 2.0 Beta / work in progress",
                "x2_must_preserve_exact_source_bytes_and_hashes": True,
                "refetch_drift_can_be_silently_adopted": False,
                "refetch_drift_consequence": "INFRA_INVALID__SEPARATE_SUCCESSOR_PROTOCOL_REVIEW_REQUIRED__NO_SELECTION",
            },
            "prerequisite": "X3 owner closure binds nonempty exact triplet manifest",
            "pulse_response_schema": {
                "top_level_exact_keys": ["pulse"],
                "pulse_required_keys": [
                    "uri",
                    "version",
                    "cipherSuite",
                    "period",
                    "certificateId",
                    "chainIndex",
                    "pulseIndex",
                    "timeStamp",
                    "localRandomValue",
                    "external",
                    "listValues",
                    "precommitmentValue",
                    "statusCode",
                    "signatureValue",
                    "outputValue",
                ],
                "external_required_keys": ["sourceId", "statusCode", "value"],
                "list_value_required_keys": ["uri", "type", "value"],
                "raw_response_bytes_and_headers_preserved": True,
                "timeStamp_raw_encoding": "strict RFC3339 UTC with exactly millisecond precision and terminal Z",
                "timeStamp_selection_projection": "parse to exact Unix milliseconds as a plain nonnegative JSON integer",
                "statusCode_required": 0,
                "external_statusCode_required": 0,
                "version_required": "2.0",
                "cipherSuite_required": 0,
                "period_required_ms": 60000,
                "fixed_512_bit_hex_fields": ["certificateId", "localRandomValue", "external.sourceId", "external.value", "listValues[*].value", "precommitmentValue", "outputValue"],
                "hex_fields_case_normalization": "validate hexadecimal first, then ASCII lowercase for the selection projection; preserve raw case in the response evidence",
            },
            "pulse_output_encoding": "outputValue must be exactly 128 hexadecimal characters and is normalized to lowercase",
            "authentication_and_chain_verification": {
                "verifier_implementation_must_be_frozen_before_first_live_search": True,
                "trust_bundle_exact_bytes_reviewed_before_first_live_search": True,
                "certificate_path_template": "/certificate/<pulse.certificateId>",
                "trust_bundle_required_contents": "exact DER bytes and SHA-256 for every accepted root/intermediate/public-key authority, allowed certificate policies/key usages/algorithms and a deterministic path-building rule, all reviewed before first live search",
                "certificate_rule": "for each accepted pulse fetch exactly its certificateId; preserve raw certificate bytes and SHA-256; independently recompute the normative certificate identifier; require certificate validity at pulse time, frozen trust path, key usage, algorithm and signed-pulse verification",
                "certificate_change_between_anchor_and_target_allowed": True,
                "certificate_change_rule": "each certificate independently validates to the same pre-search-reviewed trust bundle; both certificateIds enter the selection frame",
                "signature_rule": "for cipherSuite 0, independently serialize the exact signed-pulse fields under the frozen NIST IR 8213 rule and verify anchor and target signatureValue using each captured pulse certificate; never trust server status alone",
                "output_recomputation_rule": "for cipherSuite 0, independently recompute outputValue from the exact normative field serialization and compare all 512 bits; never use the returned outputValue without this equality",
                "chain_rule": "independently verify every NIST Beacon 2.0 previous-output, precommitment and hash-chain relation required by cipherSuite 0; preserve every fetched proof pulse byte and identity",
                "x2_required_offline_vectors": [
                    "valid strictly synthetic cipherSuite-0 signed pulse with frozen test key/certificate/trust path, previous/precommitment chain and independently recomputed outputValue",
                    "valid chain and certificate",
                    "wrong certificate identifier",
                    "expired or not-yet-valid certificate",
                    "wrong trust path or key usage",
                    "wrong signed-field serialization or signature",
                    "wrong independently recomputed outputValue",
                    "wrong previous-output or precommitment link",
                ],
                "tls_and_nist_service_remain_external_tcb": True,
                "verification_failure": "INFRA_INVALID__NO_SELECTION__NO_ALTERNATE_CERTIFICATE_PROVIDER_OR_PULSE",
            },
            "anchor_rule": {
                "x3_closure_time_encoding": "strict YYYY-MM-DDTHH:MM:SS.mmmZ; exact integer calendar conversion to Unix milliseconds; no float timestamp conversion",
                "not_before_ms": "x3 closure Unix milliseconds + 3600000",
                "request_method": "GET",
                "request_path": "/pulse/time/next/<not_before_ms>",
                "redirects_query_or_fragments_allowed": False,
                "acceptance": "valid signed/certificate/output-verified pulse whose parsed timeStamp is strictly greater than not_before_ms; independently fetch and authenticate its unique previous pulse and require same chain, previous pulseIndex + 1 == anchor pulseIndex, previous timeStamp + 60000 == anchor timeStamp, and previous parsed timeStamp <= not_before_ms < anchor parsed timeStamp",
                "previous_link_rule": "anchor.listValues contains exactly one entry whose type is previous; that entry URI equals the independently fetched previous pulse URI and its normalized 512-bit value equals the fetched previous pulse outputValue; any missing, duplicate or unequal previous link is INFRA_INVALID",
                "all_request_attempts_and_predecessor_bytes_preserved": True,
            },
            "target_rule": {
                "target_ms": "anchor parsed timeStamp milliseconds + 86400000",
                "request_method": "GET",
                "request_path": "/pulse/time/<target_ms>",
                "redirects_query_or_fragments_allowed": False,
                "required_exact_response": [
                    "parsed RFC3339 timeStamp in Unix milliseconds equals target_ms exactly; next-closest response is rejected",
                    "chainIndex equals anchor.chainIndex",
                    "pulseIndex equals anchor.pulseIndex + 1440",
                    "uri names the exact accepted chainIndex and pulseIndex",
                    "version equals 2.0, period equals 60000 and statusCode equals 0",
                    "the target certificate independently validates against the pre-search-reviewed trust bundle",
                    "signature, output recomputation, certificate and hash-chain verification succeed",
                ],
                "missing_or_nonexact_response": "record and poll the same exact target URI only; never adopt returned next-closest pulse or change target",
                "poll_schedule_seconds_after_target_ms": [0, 15, 30, 60, 120, 300, 600, 1200, 1800, 3600],
                "poll_request_count_max": 10,
                "poll_deadline_ms": "target_ms + 3600000",
                "response_or_error_for_every_attempt_preserved": True,
                "after_final_scheduled_attempt_without_exact_valid_pulse": "TERMINAL_INFRASTRUCTURE_FAILURE__NO_SELECTION__NO_ALTERNATE_OR_DELAYED_RETRY",
                "permanent_api_schema_trust_or_certificate_failure": "TERMINAL_INFRASTRUCTURE_FAILURE__NO_SELECTION",
            },
            "alternate_or_next_available_target_allowed": False,
            "target_offset_pulses": 1440,
            "domain": "rtdl.goal5793.triplet.selection.v1",
            "selection_encoding": {
                "hash": "SHA-256",
                "frame_magic_hex": "5254444c3537393353454c0001",
                "frame_rule": "magic || u16be(field_count) || concatenated framed fields",
                "field_rule": "u16be(name_byte_length) || ASCII(name) || u64be(value_byte_length) || value",
                "field_names_unique": True,
                "field_order": [
                    "domain",
                    "s0_protocol_authority_file_sha256",
                    "complete_source_rows_sha256",
                    "x1_examiner_closure_file_sha256",
                    "x2_harvester_entropy_closure_file_sha256",
                    "x3_science_triplet_owner_closure_file_sha256",
                    "expanded_append_only_row_table_file_sha256",
                    "preentropy_science_projection_rows_sha256",
                    "ordered_triplets_rows_sha256",
                    "ordered_triplet_count",
                    "anchor_chain_index",
                    "anchor_pulse_index",
                    "anchor_timestamp_ms",
                    "anchor_certificate_id",
                    "anchor_output_value",
                    "target_chain_index",
                    "target_pulse_index",
                    "target_timestamp_ms",
                    "target_certificate_id",
                    "target_output_value",
                    "counter",
                ],
                "value_encodings": {
                    "domain": "exact UTF-8 bytes without BOM or terminator",
                    "sha256_fields": "strict lowercase 64-hex decoded to 32 bytes",
                    "ordered_triplet_count_chain_index_pulse_index_timestamp_ms_counter": "unsigned u64be",
                    "certificate_id_and_output_value": "strict 128-hex decoded to 64 bytes",
                },
                "counter_start": 0,
                "counter_step": 1,
                "counter_max": 18446744073709551615,
                "digest_interpretation": "unsigned 256-bit big-endian integer x",
                "rejection_rule": "limit=floor(2^256/N)*N; accept first x < limit; selected zero-based index=x mod N; record every rejected counter and digest",
                "selected_object_rule": "ordered_triplets[selected zero-based index], with no re-sort after manifest freeze",
            },
            "known_answer_test": {
                "kat_id": "goal5793-selection-tlv-v1-counter0",
                "synthetic_not_beacon_entropy": True,
                "inputs": {
                    "domain": "rtdl.goal5793.triplet.selection.v1",
                    "s0_protocol_authority_file_sha256": "00" * 32,
                    "complete_source_rows_sha256": "11" * 32,
                    "x1_examiner_closure_file_sha256": "22" * 32,
                    "x2_harvester_entropy_closure_file_sha256": "33" * 32,
                    "x3_science_triplet_owner_closure_file_sha256": "44" * 32,
                    "expanded_append_only_row_table_file_sha256": "55" * 32,
                    "preentropy_science_projection_rows_sha256": "66" * 32,
                    "ordered_triplets_rows_sha256": "77" * 32,
                    "ordered_triplet_count": 7,
                    "anchor_chain_index": 2,
                    "anchor_pulse_index": 1000000,
                    "anchor_timestamp_ms": 1800000000000,
                    "anchor_certificate_id": "88" * 64,
                    "anchor_output_value": "99" * 64,
                    "target_chain_index": 2,
                    "target_pulse_index": 1001440,
                    "target_timestamp_ms": 1800086400000,
                    "target_certificate_id": "aa" * 64,
                    "target_output_value": "bb" * 64,
                    "counter": 0,
                },
                "expected": {
                    "field_count": 21,
                    "frame_bytes": 1345,
                    "frame_sha256": "a5904e12a9795bdc984b73095cc38cc670328fbb074a8db5e736c1fff0d4d92e",
                    "x_decimal": "74886584832908832518649213642884520782693134635426788984410478727705251862830",
                    "n": 7,
                    "threshold_hex": "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe",
                    "accepted": True,
                    "selected_zero_based_index": 2,
                },
            },
            "rejection_boundary_test": {
                "n": 7,
                "threshold_hex": "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe",
                "synthetic_digest_sequence": [
                    "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe",
                    "000000000000000000000000000000000000000000000000000000000000000a",
                ],
                "expected": ["REJECT_X_EQUALS_THRESHOLD", "ACCEPT_INDEX_3"],
            },
            "cardinality_rules": {
                "n_zero": "TERMINAL_NEGATIVE__NO_BEACON_REQUEST__NO_HASH__NO_SELECTION__NO_RESCUE",
                "n_one": "authenticate anchor and exact target, evaluate and record counter 0 digest, then select index 0",
                "n_greater_than_one": "counter-mode rejection sampling",
                "counter_exhaustion": "TERMINAL_INFRASTRUCTURE_FAILURE__NO_FALLBACK",
            },
            "cardinality_known_answer_tests": {
                "n_zero": {
                    "input_triplet_count": 0,
                    "beacon_request_count": 0,
                    "hash_evaluation_count": 0,
                    "selected_index": None,
                    "terminal": "TERMINAL_NEGATIVE__NO_BEACON_REQUEST__NO_HASH__NO_SELECTION__NO_RESCUE",
                },
                "n_one": {
                    "input_triplet_count": 1,
                    "anchor_and_exact_target_authentication_required": True,
                    "counter": 0,
                    "hash_evaluation_count": 1,
                    "selected_index": 0,
                    "returned_digest_must_be_recorded": True,
                },
                "counter_exhaustion": {
                    "last_counter": 18446744073709551615,
                    "next_counter_allowed": False,
                    "selected_index": None,
                    "terminal": "TERMINAL_INFRASTRUCTURE_FAILURE__NO_FALLBACK",
                },
            },
            "current_anchor": None,
            "current_target": None,
            "current_selection": None,
        },
        "postselection_input_and_implementation_freeze": {
            "required_before_implementation": [
                "exact bounded input instances and data identities",
                "app-owned implementation and allowed-path manifest",
                "mechanical fill of only the predeclared IR/effect/schema/ABI/plan/native/source identity slots before first verdict",
                "exact commands and functional receipt requirements",
                "allowed and forbidden paths",
                "all outcome consequences",
            ],
            "science_fields_already_frozen_preentropy": ["source and oracle authority", "semantic obligations", "physical guarantees", "expected disposition", "role predicates", "boundary/tie/multiplicity/numeric/overflow/continuation/composition rules"],
            "selected_candidate_science_projection_change_allowed": False,
            "valid_incompatible_unknown_or_zero_of_three": "TERMINAL_SCIENTIFIC_RESULT__NO_RESCUE",
            "infra_invalid": "same candidate and same science only; preserve lineage; successor requires separate review",
            "replacement_row_or_candidate_allowed": False,
            "result_dependent_validity_allowed": False,
        },
        "structural_friction_ledger": {
            "measurement_spec_and_implementation_must_be_frozen_reviewed_and_owner_closed_in_x2_before_first_live_search": True,
            "required_for_all_three_rows_including_failures": [
                "app-owned file count and source lines",
                "public facade call count",
                "private API call count and exact call sites",
                "manual semantic/physical authority field count",
                "raw CUDA/OptiX token count",
                "generated stage inventory",
                "first diagnostic/failure location",
                "public_api_only flag",
                "author-code or direct CUDA/OptiX responsibility comparison when exact source exists",
            ],
            "metric_definitions": {
                "app_owned_file_count": "count unique canonical regular source paths under the candidate's frozen app-owned allowed roots; tests, data, generated outputs and evidence are reported separately and never silently included",
                "app_owned_nonblank_physical_source_lines": "decode strict UTF-8, normalize CRLF/CR to LF, split on LF, and count lines containing at least one non-ASCII-whitespace byte; comments remain code; generated paths are excluded and separately reported",
                "public_and_private_api_calls": "count unique Python-AST Call source locations resolved against the exact X1-frozen public/private callable registry; report unique static call sites, not dynamic invocations; unresolved calls are a separate nonzero unresolved count",
                "manual_authority_fields": "count unique canonical scalar leaf paths explicitly supplied by app-owned source/config to the frozen authority schema and not filled by the frozen mechanical derivation; report defaults, derived leaves and unresolved leaves separately",
                "raw_cuda_optix_tokens": "tokenize strict UTF-8 app-owned source with the X2-frozen lexer and exact case-sensitive CUDA/OptiX symbol/namespace/header registry; report total lexical occurrences and unique source locations",
                "generated_stage_inventory": "presence and exact artifact identity for each X2-frozen stage enum from source projection through IR/effects/PTX/wrapper/layout/native/receipt; absent stages require a reason",
                "first_diagnostic_failure_location": "the earliest stage in the X2-frozen total stage order with a fail-closed reason; ties use reason-id UTF-8 order",
            },
            "per_metric_record_schema": {
                "VALUE": {"exact_keys": ["status", "value", "unit", "reason", "source_pins"], "status": "VALUE", "reason": None, "source_pins_nonempty": True},
                "NA": {"exact_keys": ["status", "value", "unit", "reason", "source_pins"], "status": "NA", "value": None, "reason_is_exact_nonempty_id": True},
                "bool_int_float_aliases_allowed": False,
                "extra_or_missing_keys_allowed": False,
            },
            "metric_units": {
                "app_owned_file_count": "files",
                "app_owned_nonblank_physical_source_lines": "lines",
                "public_api_calls": "unique_static_call_sites",
                "private_api_calls": "unique_static_call_sites",
                "unresolved_api_calls": "unique_static_call_sites",
                "manual_authority_fields": "unique_scalar_leaf_paths",
                "raw_cuda_optix_tokens": "lexical_occurrences_and_unique_locations",
                "generated_stage_inventory": "stage_records",
                "first_diagnostic_failure_location": "stage_enum_or_NA",
            },
            "missingness_rules": {
                "not_reached_metric": "null plus exact NOT_REACHED_<stage> reason; never numeric zero",
                "not_applicable_metric": "null plus exact NOT_APPLICABLE reason and reviewed predicate; never numeric zero",
                "unresolved_metric": "null plus exact unresolved reason; row remains in denominator",
                "author_or_direct_baseline_without_exact_functionally_matched_source": "null plus NO_EXACT_FUNCTIONALLY_MATCHED_BASELINE; no favorable substitution",
                "multiple_or_ambiguous_author_baselines": "null plus NA_AMBIGUOUS_AUTHOR_CODE; no manual baseline choice",
            },
            "required_for_every_attempt_successor_and_abandoned_lineage": True,
            "append_only_lineage_ids_and_predecessor_successor_links_required": True,
            "denominator": "all selected candidates and every attempt, successor and abandoned lineage, including rejected, UNKNOWN, invalid and failed rows; no dropped or replaced lineage",
            "per_metric_denominator_rule": "for each metric report available_count, na_count and total_lineage_count; total_lineage_count is identical to the append-only lineage denominator and NA remains visible",
            "cross_metric_aggregation_over_different_availability_sets_allowed": False,
            "author_or_direct_baseline_comparison_rule": "only exact functionally matched frozen source may be compared; zero, missing, incomplete or ambiguous baselines remain NA and cannot enter a favorable aggregate",
            "usability_study_count": 0,
            "supports_easy_or_better_than_cuda_claim": False,
            "interpretation": "structural integration responsibility and abstraction-leakage evidence only; it cannot determine human usability or productivity; those questions require a separate preregistered independent developer study",
        },
        "claim_lint": {
            "forbidden_unqualified_terms": ["unseen", "blind", "held-out", "held out", "literature-complete", "complete literature", "geometry-family generalization", "easy", "productive", "awkward", "simpler", "less code", "lower friction", "reduces burden", "easier than CUDA", "better than OptiX"],
            "required_old_catalog_wording": "fully enumerated 35-row author-seen legacy catalog; permanently selection-ineligible",
            "strongest_future_experiment_wording": "query-defined, post-examiner-frozen, existing-family bounded compositional generalization experiment",
            "legacy_filename_exception": "an immutable path containing held_out may be quoted only as a historical filename and must be adjacent to a disclaimer that it is not checker/calculus generalization evidence",
        },
        "external_review_and_absorption_dag": {
            "current_formal_output_count": 8,
            "single_cfr_path": "history/internal_docs/call_for_review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md",
            "reviewer_receives_exactly_one_file": True,
            "separate_packet_exists_or_is_sent": False,
            "dependency_order": [
                "source+candidate+protocol+report+self-review+authoring-tools",
                "root result",
                "independent audit",
                "single CFR",
                "owner send receipt",
                "owner-returned review",
                "append-only owner absorption and closure",
            ],
            "owner_send_receipt_required_exact_fields": ["CFR path", "CFR bytes", "CFR file SHA-256", "send time", "recipient selected by owner"],
            "returned_review_required": {"verdict_p0": 0, "verdict_p1": 0, "review_file_identity_pinned": True},
            "owner_closure_required_exact_bindings": ["CFR", "root result", "independent audit", "owner send receipt", "returned review"],
            "owner_closure_may_authorize": "X1 generic-examiner, registry-derivation, environment and shared-native work only",
            "owner_closure_may_not_authorize": ["live search", "entropy", "selection", "candidate implementation", "candidate execution", "POD", "SSH", "timing"],
            "state_or_filename_alone_never_authorizes_transition": True,
        },
        "permanent_goal5793_invariants": {
            "goal5793_pod_or_ssh_allowed_ever": False,
            "registered_or_performance_timing_count_required": 0,
            "product_src_native_family_role_opcode_rule_facade_change_allowed": False,
            "candidate_app_code_must_remain_outside_src": True,
            "home_gpu_if_ever_requires_separate_external_review_and_owner_authorization": True,
            "home_gpu_scope_if_ever_authorized": "functional true-OptiX only; zero registered or performance timing",
            "valid_scientific_failure_can_relax_an_invariant": False,
        },
        "authorization": {
            "authorizes_generic_examiner_implementation": False,
            "authorizes_environment_or_shared_native_materialization": False,
            "authorizes_systematic_search": False,
            "authorizes_entropy_anchor_or_draw": False,
            "authorizes_candidate_selection": False,
            "authorizes_candidate_implementation": False,
            "authorizes_candidate_execution": False,
            "authorizes_product_or_src_change": False,
            "authorizes_gpu_home_pod_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_external_contact": False,
            "authorizes_publication_or_submission": False,
        },
    }
    return seal(document, "protocol_authority_sha256")


def render_report(source: dict[str, Any], candidates: dict[str, Any], protocol: dict[str, Any]) -> bytes:
    source_digest = source["declared_product_native_source_zero_drift_authority"]["summary"]["rows_sha256"]
    lines = [
        "# Goal5793 S0 preregistration technical report",
        "",
        "## Outcome first",
        "",
        "The frozen 35-row Goal5753 catalog cannot legally enter Goal5793 selection. Thirty rows are excluded and five retain useful source-gap/stress analysis, but all 35 are permanently selection-ineligible because their identities entered the project before the generic examiner freeze. Independently, there are zero qualified Role-A candidates (the mandatory unconventional correct expected-admission challenge), zero valid ordered triplets, and therefore no entropy may be drawn.",
        "",
        "This is not repaired by lowering the gate, completing one of the five old rows, or hand-picking a convenient paper. S0 freezes a staged solution: independently review a candidate-agnostic examiner, registry derivation, exact environment and shared native first; independently review an offline harvester and exact query protocol; execute that search once; freeze every returned row's science projection and all valid triplets; only then use a future NIST pulse.",
        "",
        "## Frozen source and verdict boundary",
        "",
        f"The declared product/native-source zero-drift code surface is 326 regular non-symlink files / 14,587,884 bytes / `{source_digest}`. Its exact scope is all `src/**` plus four named declarations; it is not claimed to be a complete package/build closure (for example, package metadata references `README.md`). A 41-file surface is retained only as a responsibility-oriented explanatory submanifest and is not a complete import closure. The current surface overlaps the v26 archive on 324/326 rows with zero mismatch; `requirements.txt` and `VERSION` are the two new custody roots.",
        "",
        "A2's five-program checker is a historical regression mechanism, not the future Goal5793 decision maker. The future examiner must drive the frozen product calculus/facades and an independent normalized-certificate replay without reading candidate identity, role or expected result. Environment, toolchain, native library and registry derivation are not yet frozen and therefore search, entropy and selection remain forbidden.",
        "",
        "## Candidate audit",
        "",
        "Goal5753 proves that all 35 exact paper/problem identities were visible to the project. The earlier Goal519/Goal521 blobs separately prove roadmap/feasibility treatment for the 32 normalized workload families; they do not prove paper-specific source review for every row. The manuscript must not call these rows unseen, blind, or checker/calculus generalization evidence. The precise description is: *fully enumerated 35-row author-seen legacy catalog; permanently selection-ineligible*.",
        "",
        "RTSpMSpM, radio propagation, space skipping, infrared radiation and OpenMC particle transport retain descriptive diversity/risk annotations and explicit source/oracle/family gaps. Those annotations are not Role qualifications, and later filling a gap cannot reintroduce an old row. The observed primary/code bytes are not embedded in this S0; URLs, versions and observed hashes are disclosed, and a reviewer must refetch or use a separate authority to rehash them. These observations do not control the zero-eligibility result.",
        "",
        "## Anti-overfitting and no-rescue sequence",
        "",
        "1. Externally review and close this S0.",
        "2. Implement, attack, externally review and close the candidate-agnostic examiner plus exact environment/shared-native authority and a frozen declared project-exposure registry. The registry scans the frozen repository/predecessor DAG and adds an owner disclosure of off-repository design sources; it does not claim complete author mental exposure. No search is allowed before that closure.",
        "3. Implement the frozen OpenAlex/arXiv harvester and the NIST pulse verifier/selection client using offline synthetic fixtures only, externally review both, and only after closure make the first live search request. Execute every exact query once and preserve every response, failure and retry.",
        "4. Uniformly retain and screen all returned rows. Before any triplet or entropy, freeze every row's source/oracle authority, normalized family, semantic obligations, physical guarantees, expected disposition, structural vector, risk vector, public/private product-path classification and mechanical Role-A/B/C decision. Old-catalog matches remain duplicate cross-links only.",
        "5. Externally review the complete query-defined row table, science projections and mechanically enumerated triplets. If Role A or the triplet set is empty, record a terminal negative. Otherwise obtain the deferred exact NIST anchor and target pulse.",
        "6. After selection, freeze only input instances, app-owned implementation paths and the predeclared identity slots; semantic/oracle/physical/expected fields cannot change.",
        "7. Preserve valid rejection, UNKNOWN, failure and 0/3. No candidate replacement, family rescue, rule rescue or outcome-conditioned rerun is allowed.",
        "",
        "Before selection, future-candidate examiner, authority-materializer, product evaluate/admit/compile/run, app implementation and execution-receipt counts must all remain zero. The selection preimage binds the exact S0, X1, X2 and X3 closures; complete expanded row table; complete pre-entropy science table; and ordered triplets. Its 21-field length-framed TLV mapping has an exact normal KAT, rejection-boundary vector and N=0/N=1 rules. NIST pulses are accepted only after independent certificate/signature/output/chain verification; a next-closest timestamp is rejected, and the exact target URI is polled only on a fixed one-hour schedule.",
        "",
        "## Usability boundary",
        "",
        "Goal5793 will collect an append-only structural-friction ledger for every selected candidate and every attempt, successor and abandoned lineage: public/private calls, app-owned code, manual authority fields, raw low-level tokens, generated stages and diagnostic location. Each row must be classified as public facade plus public authority issuance, public facade plus private registry issuance, or reference admission only. A private/reference path cannot be advertised as an end-user product path. The ledger can identify structural integration burden and abstraction leakage only. It is not a human usability study and cannot support human-experience, productivity, or better-than-CUDA/OptiX claims. A separate independent developer study would be required for those claims.",
        "",
        "## Current authorization",
        "",
        "This artifact authorizes nothing. It requests external review of S0. Generic examiner work, search, entropy, selection, implementation, execution, product changes, GPU, external contact and publication all remain false until their exact predecessor closures. Goal5793 permanently allows no POD/SSH and requires zero registered/performance timings; a future Home-GPU step, if separately authorized, is functional true-OptiX only.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def render_self_review() -> bytes:
    lines = [
        "# Self-review: Goal5793 S0 preregistration",
        "",
        "Verdict: **READY FOR INDEPENDENT REVIEW AT S0-ONLY SCOPE; P0=0 / P1=0 / P2=0.**",
        "",
        "## Decisions challenged",
        "",
        "- I tried the tempting shortcut—reuse Goal5753's 17 old eligible rows—and rejected it. Later work contaminated twelve of those rows; the remaining five do not contain a source-qualified expected-admission positive.",
        "- I checked whether a negative current pool could justify hand expansion. It cannot. The only defensible repair is to freeze the examiner and the uniform search protocol before exposing search results.",
        "- I checked whether RTXRMQ could count as checker-calculus generalization evidence. It predates the checker/calculus and is only a legacy no-special-case replay; it cannot enter Goal5793.",
        "- I checked whether the 41 highlighted files were the complete core. They are not: Python package initialization, late imports and compile children require the full 322-file `src/**` authority. The 41-file list is explicitly non-complete.",
        "- I checked whether source bytes alone freeze execution. They do not. Dynamic NVRTC/native loading, compiler paths, build ID, dependencies and GPU/driver remain a separate mandatory authority.",
        "- I checked whether structural code counts establish usability. They do not. The ledger is diagnostic only; usability claims remain false.",
        "",
        "## Falsification conditions",
        "",
        "S0 is invalid if any of the 326 rows drifts, any of the 35 rows disappears or is allowed to reenter, Role A or triplet count is reported nonzero, any entropy/search/selection field is non-null, the 41-file list is called complete, the 32-family versus 35-paper exposure boundary is blurred, or any downstream stage is authorized early.",
        "",
        "The future bounded experiment is killed or narrowed if the generic examiner depends on candidate metadata, if registry obligations are chosen after search, if any eligible row's science projection is changed after triplet freeze, if the systematic query set changes after results, if a next-closest NIST pulse is accepted, or if a valid rejection/UNKNOWN triggers replacement or product rescue.",
        "",
        "## Scope retained",
        "",
        "This S0 does not prove generalization, usability, soundness, completeness, third-family support or production readiness. It establishes a path for a query-defined, post-examiner-frozen, existing-family bounded compositional generalization experiment without candidate selection after observing outcomes.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def write_create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def prevalidate_outputs(outputs: dict[Path, bytes]) -> None:
    spec = importlib.util.spec_from_file_location(
        "goal5793_s0_prewrite_auditor",
        ROOT / "scripts/goal5793_audit_s0_preregistration.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent S0 auditor")
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    auditor.validate_documents(
        json.loads(outputs[SOURCE_OUT].decode("utf-8")),
        json.loads(outputs[CANDIDATE_OUT].decode("utf-8")),
        json.loads(outputs[PROTOCOL_OUT].decode("utf-8")),
        json.loads(outputs[RESULT_OUT].decode("utf-8")),
        outputs[REPORT_OUT].decode("utf-8"),
        outputs[SELF_REVIEW_OUT].decode("utf-8"),
        virtual_files=outputs,
    )


def build_documents() -> dict[Path, bytes]:
    assert_expected_roots()
    source = build_source_authority()
    candidates = build_candidate_authority()
    protocol = build_protocol_authority()
    source_data = json_bytes(source)
    candidate_data = json_bytes(candidates)
    protocol_data = json_bytes(protocol)
    report_data = render_report(source, candidates, protocol)
    self_review_data = render_self_review()

    supporting = []
    for path, data in (
        (SOURCE_OUT, source_data),
        (CANDIDATE_OUT, candidate_data),
        (PROTOCOL_OUT, protocol_data),
        (REPORT_OUT, report_data),
        (SELF_REVIEW_OUT, self_review_data),
    ):
        supporting.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(data),
                "file_sha256": sha256_bytes(data),
            }
        )
    tool_paths = [
        ROOT / "scripts/goal5793_build_s0_preregistration.py",
        ROOT / "scripts/goal5793_audit_s0_preregistration.py",
        ROOT / "tests/goal5793_s0_preregistration_test.py",
    ]
    result = {
        "schema": "rtdl.goal5793.s0.preregistration_result.v1",
        "goal": 5793,
        "date": DATE,
        "status": "FROZEN_35_ROW_REQUALIFICATION__ZERO_QUALIFIED_ROLE_A__ZERO_TRIPLETS__SYSTEMATIC_EXPANSION_REQUIRED__NO_ENTROPY__EXTERNAL_REVIEW_PENDING",
        "predecessor": identity(A2_CLOSURE),
        "predecessor_internal_seal": "650de991134431cebe1b9d66273a6283116209e6d1363a4cbf98421bfad03aa4",
        "supporting_artifacts": supporting,
        "authoring_tools": [identity(path) for path in tool_paths],
        "current_result": {
            "declared_product_native_source_zero_drift_file_count": 326,
            "known_candidate_rows": 35,
            "excluded_rows": 30,
            "source_gap_analyzed_permanently_ineligible_rows": 5,
            "qualified_role_a_rows": 0,
            "eligible_ordered_triplets": 0,
            "systematic_search_execution_count": 0,
            "entropy_draw_count": 0,
            "selected_candidate_count": 0,
            "candidate_implementation_count": 0,
            "exam_count": 0,
        },
        "transaction_commit_marker": {
            "result_is_last_create_only_output": True,
            "supporting_artifact_count": 5,
            "complete_transaction_requires_result_and_all_supporting_identities": True,
        },
        "next_gate_requested_not_authorized": "external review P0=0/P1=0 plus owner absorption may authorize X1 generic-examiner/registry/environment/shared-native work only",
        "single_external_review_entrypoint": "history/internal_docs/call_for_review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md",
        "claim_boundary": {
            "generalization_claimed": False,
            "held_out_or_unseen_claimed": False,
            "usability_claimed": False,
            "soundness_or_completeness_claimed": False,
            "third_family_claimed": False,
            "all_path_gate_claimed": False,
            "production_claimed": False,
            "performance_claimed": False,
            "goal5793_scientific_result_claimed": False,
            "literature_complete_claimed": False,
            "geometry_family_generalization_claimed": False,
        },
        "authorization": {
            "authorizes_generic_examiner_implementation": False,
            "authorizes_registry_or_environment_materialization": False,
            "authorizes_systematic_search": False,
            "authorizes_entropy": False,
            "authorizes_candidate_selection": False,
            "authorizes_candidate_implementation": False,
            "authorizes_candidate_execution": False,
            "authorizes_product_checker_native_app_change": False,
            "authorizes_gpu_home_pod_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_external_reviewer_contact": False,
            "authorizes_public_release_publication_or_submission": False,
        },
        "permanent_goal5793_invariants": {
            "goal5793_pod_or_ssh_allowed_ever": False,
            "registered_or_performance_timing_count_required": 0,
            "product_src_native_family_role_opcode_rule_facade_change_allowed": False,
        },
    }
    seal(result, "result_sha256")
    return {
        SOURCE_OUT: source_data,
        CANDIDATE_OUT: candidate_data,
        PROTOCOL_OUT: protocol_data,
        REPORT_OUT: report_data,
        SELF_REVIEW_OUT: self_review_data,
        RESULT_OUT: json_bytes(result),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="create the six frozen S0 outputs")
    args = parser.parse_args()
    outputs = build_documents()
    prevalidate_outputs(outputs)
    if args.write:
        for path in outputs:
            if path.exists():
                raise FileExistsError(f"create-only output already exists: {path}")
        for path, data in outputs.items():
            write_create_only(path, data)
    summary = {
        "outputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
            for path, data in outputs.items()
        ],
        "write_performed": args.write,
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
