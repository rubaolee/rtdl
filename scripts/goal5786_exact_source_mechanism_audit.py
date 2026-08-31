#!/usr/bin/env python3
"""Bind Goal5786 causal statements to the exact Goal5785 source bytes.

This audit intentionally proves only source/control-flow facts.  It never turns
source occurrences into elapsed seconds or predicted savings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_tokens(text: str, *, path: str, tokens: tuple[str, ...]) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise RuntimeError(f"{path}: missing required source facts: {missing!r}")


def line_of(text: str, token: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if token in line:
            return index
    raise RuntimeError(f"source token not found: {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-archive-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.source_root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    if len(args.source_archive_sha256) != 64:
        raise ValueError("source archive SHA-256 must contain 64 hex characters")

    relative_paths = {
        "frontdoors": "scripts/goal5776_real_scale_frontdoors.py",
        "xhd_app": "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
        "xhd_v2": "Paper-reproduction-apps/x-hd-paper/v2_true_optix_direct.py",
        "xhd_lowering": "src/rtdsl/v4_global_nearest_witness_lowering.py",
        "rayjoin_app": "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
        "particle_app": (
            "Paper-reproduction-apps/goal5753-held-out-particle-tracking/"
            "v4_whole_app.py"
        ),
        "rtnn_app": "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
        "rtdbscan_app": "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
        "rtbh_app": "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
        "librts_app": "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
        "triangle_app": "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    }
    paths = {name: root / relative for name, relative in relative_paths.items()}
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    texts = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}

    require_tokens(
        texts["frontdoors"],
        path=relative_paths["frontdoors"],
        tokens=(
            "registered += float(loading_seconds + preparation_seconds + close_seconds)",
            "row_execute_seconds={row_id: complete_wall}",
            "loading_seconds=0.0,",
            "preparation_seconds=0.0, close_seconds=0.0, matched=True",
        ),
    )
    require_tokens(
        texts["xhd_app"],
        path=relative_paths["xhd_app"],
        tokens=(
            "started = time.perf_counter()",
            "nearest = self.owner.execute_global_witness(source_values)",
            "elapsed = time.perf_counter() - started",
            "# Correctness-oracle work belongs outside the prepared endpoint timer.",
            "expected = _expected_for(source_values, self.targets)",
        ),
    )
    require_tokens(
        texts["xhd_lowering"],
        path=relative_paths["xhd_lowering"],
        tokens=(
            "physical = self._prepared.run(queries)",
            "receipt = audit.finish(",
            'metadata.get("full_nearest_state_host_projection_used") is not False',
            'int(metadata.get("bounded_witness_host_projection_rows", 0)) != 1',
        ),
    )
    require_tokens(
        texts["xhd_v2"],
        path=relative_paths["xhd_v2"],
        tokens=(
            "with prepare_certified_nearest_global_witness_3d_optix(",
            "physical = prepared.run(queries)",
        ),
    )
    require_tokens(
        texts["rayjoin_app"],
        path=relative_paths["rayjoin_app"],
        tokens=(
            "compiled = prepared_compiled_relation",
            "if compiled is None:",
            "result = legacy.run_v2_prepared_six_batch(args)",
            "lowered = execute_verified_planar_overlay_v4(",
            "physical_runner=run_physical",
        ),
    )

    # These application fronts intentionally have different preparation chains.
    # Presence is a source fact; it is not an elapsed-time or eliminability claim.
    prepare_markers = {
        "particle_tracking": ("prepare_v4", "prepare_builtin_triangle_callback"),
        "triangle_counting": ("prepare_v4", "compile_standard_triangle_program"),
        "rt_dbscan": ("prepare_v4", "prepare_verified_radius_graph_grouped_v4"),
        "rtnn": ("prepare_v4", "prepare_verified_ranked_distance_window_v4"),
        "x_hd": ("prepare_v4", "prepare_verified_global_nearest_witness_v4"),
        "rt_barneshut": ("prepare_v4", "prepare_hierarchy_frontier"),
        "librts": ("prepare_v4", "prepare_bounded_relation_callback"),
    }
    app_texts = {
        "particle_tracking": texts["particle_app"],
        "triangle_counting": texts["triangle_app"],
        "rt_dbscan": texts["rtdbscan_app"],
        "rtnn": texts["rtnn_app"],
        "x_hd": texts["xhd_app"],
        "rt_barneshut": texts["rtbh_app"],
        "librts": texts["librts_app"],
    }
    for app, markers in prepare_markers.items():
        require_tokens(app_texts[app], path=app, tokens=markers)

    payload = {
        "schema": "rtdl.goal5786.exact_source_mechanism_audit.v1",
        "status": "PASS__SOURCE_FACTS_ONLY__NO_PREDICTED_SAVING",
        "exact_goal5785_source_archive_sha256": args.source_archive_sha256.lower(),
        "source_files": {
            name: {
                "path": relative_paths[name],
                "sha256": sha256(paths[name]),
            }
            for name in sorted(paths)
        },
        "source_facts": {
            "cold_registered_endpoint_is_loading_plus_preparation_plus_execute_plus_close": True,
            "rayjoin_cold_registered_as_single_complete_execute_envelope": True,
            "rayjoin_cold_finer_subphase_attribution_available": False,
            "xhd_prepared_timer_contains_global_witness_call_and_result_projection": True,
            "xhd_correctness_oracle_is_outside_prepared_timer": True,
            "xhd_v2_and_v4_both_call_certified_global_witness_optix_family": True,
            "xhd_v4_requires_bounded_one_row_host_projection_metadata": True,
            "cold_preparation_frontdoors_have_distinct_family_specific_chains": True,
            "one_uniform_eliminable_preparation_duplicate_proven_by_source": False,
        },
        "source_locations": {
            "cold_sum_line": line_of(
                texts["frontdoors"],
                "registered += float(loading_seconds + preparation_seconds + close_seconds)",
            ),
            "rayjoin_complete_wall_line": line_of(
                texts["frontdoors"], "row_execute_seconds={row_id: complete_wall}"
            ),
            "xhd_timer_start_line": line_of(
                texts["xhd_app"], "started = time.perf_counter()"
            ),
            "xhd_global_witness_call_line": line_of(
                texts["xhd_app"],
                "nearest = self.owner.execute_global_witness(source_values)",
            ),
            "xhd_timer_stop_line": line_of(
                texts["xhd_app"], "elapsed = time.perf_counter() - started"
            ),
            "xhd_oracle_boundary_line": line_of(
                texts["xhd_app"],
                "# Correctness-oracle work belongs outside the prepared endpoint timer.",
            ),
        },
        "preparation_family_markers": {
            app: list(markers) for app, markers in sorted(prepare_markers.items())
        },
        "interpretation_contract": {
            "source_occurrence_is_timed_cause": False,
            "source_occurrence_is_predicted_saving": False,
            "phase_location_is_eliminability_proof": False,
            "goal5785_bytes_changed": False,
            "product_or_native_changed": False,
            "gpu_or_worker_used": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
