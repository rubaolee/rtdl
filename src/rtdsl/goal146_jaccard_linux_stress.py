from __future__ import annotations

import json
import platform
import time
from datetime import datetime
from pathlib import Path

from .goal141_public_jaccard_audit import MONUSEG_DEFAULT_XML
from .goal141_public_jaccard_audit import build_goal141_public_case
from .goal141_public_jaccard_audit import tile_polygon_set


def _rows_equal(left: tuple[dict[str, float | int], ...], right: tuple[dict[str, float | int], ...]) -> bool:
    if len(left) != len(right):
        return False
    for left_row, right_row in zip(left, right):
        if any(int(left_row[key]) != int(right_row[key]) for key in ("intersection_area", "left_area", "right_area", "union_area")):
            return False
        if abs(float(left_row["jaccard_similarity"]) - float(right_row["jaccard_similarity"])) > 1.0e-9:
            return False
    return True


def _time_backend(backend_name: str, kernel, *, left, right) -> tuple[tuple[dict[str, object], ...], float]:
    import rtdsl as rt

    dispatch = {
        "cpu_python_reference": rt.run_cpu_python_reference,
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
    }
    start = time.perf_counter()
    rows = dispatch[backend_name](kernel, left=left, right=right)
    return rows, time.perf_counter() - start


def run_goal146_jaccard_linux_stress(
    *,
    zip_path: str | Path,
    xml_name: str = MONUSEG_DEFAULT_XML,
    polygon_limit: int = 16,
    copies: tuple[int, ...] = (64, 128),
) -> dict[str, object]:
    import rtdsl as rt
    from examples.rtdl_polygon_set_jaccard import polygon_set_jaccard_reference

    case = build_goal141_public_case(
        zip_path,
        xml_name=xml_name,
        polygon_limit=polygon_limit,
    )
    max_x = max(int(vertex[0]) for polygon in case.left_polygons for vertex in polygon.vertices)
    min_x = min(int(vertex[0]) for polygon in case.left_polygons for vertex in polygon.vertices)
    stride_x = (max_x - min_x) + 8
    backend_order = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan")
    rows = []
    for copy_count in copies:
        left_polygons = tile_polygon_set(case.left_polygons, copies=copy_count, stride_x=stride_x)
        right_polygons = tile_polygon_set(case.right_polygons, copies=copy_count, stride_x=stride_x)
        backend_rows: dict[str, tuple[dict[str, object], ...]] = {}
        backend_seconds: dict[str, float] = {}
        for backend_name in backend_order:
            result_rows, sec = _time_backend(
                backend_name,
                polygon_set_jaccard_reference,
                left=left_polygons,
                right=right_polygons,
            )
            backend_rows[backend_name] = result_rows
            backend_seconds[backend_name] = sec
        truth_rows = backend_rows["cpu_python_reference"]
        rows.append(
            {
                "copies": copy_count,
                "left_polygon_count": len(left_polygons),
                "right_polygon_count": len(right_polygons),
                "backend_seconds": backend_seconds,
                "consistency_vs_python": {
                    backend_name: _rows_equal(truth_rows, backend_rows[backend_name])
                    for backend_name in backend_order
                },
                "result_rows": truth_rows,
            }
        )
    return {
        "suite": "goal146_jaccard_linux_stress",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "boundary": {
            "goal": "wrapper-level Linux stress and consistency for polygon_set_jaccard",
            "accepted_claim": (
                "Embree, OptiX, and Vulkan participate through the public run surfaces "
                "with documented native CPU/oracle fallback for this workload."
            ),
            "timing_interpretation": (
                "The reported Embree, OptiX, and Vulkan times are wrapper end-to-end "
                "execution times under the same native CPU/oracle fallback. Small timing "
                "differences versus the CPU row should be treated as measurement noise or "
                "wrapper-surface overhead variation, not as backend-specific Jaccard speedup."
            ),
            "not_claimed": (
                "No native Embree/OptiX/Vulkan Jaccard implementation, prepared-path story, "
                "or RT-core maturity is claimed here."
            ),
        },
        "dataset": {
            "kind": "public_real_data_derived_pair",
            "source": "MoNuSeg 2018 Training Data",
            "xml_name": case.xml_name,
            "raw_polygon_count": case.raw_polygon_count,
            "selected_polygon_count": case.selected_polygon_count,
            "base_left_polygon_count": len(case.left_polygons),
            "base_right_polygon_count": len(case.right_polygons),
            "pair_derivation": "right set is the same real-data-derived unit-cell polygon set shifted by +1 cell in x",
        },
        "rows": rows,
    }


def render_goal146_markdown(payload: dict[str, object]) -> str:
    dataset = payload["dataset"]
    boundary = payload["boundary"]
    lines = [
        "# Goal 146 Jaccard Linux Stress",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- host: `{payload['host']['platform']}`",
        f"- source: `{dataset['source']}`",
        f"- xml_name: `{dataset['xml_name']}`",
        f"- selected_polygon_count: `{dataset['selected_polygon_count']}`",
        f"- base_left_polygon_count: `{dataset['base_left_polygon_count']}`",
        f"- base_right_polygon_count: `{dataset['base_right_polygon_count']}`",
        f"- accepted_claim: `{boundary['accepted_claim']}`",
        f"- timing_interpretation: `{boundary['timing_interpretation']}`",
        f"- not_claimed: `{boundary['not_claimed']}`",
        "",
        "| copies | left_polygon_count | right_polygon_count | python_sec | cpu_sec | embree_sec | optix_sec | vulkan_sec | cpu_ok | embree_ok | optix_ok | vulkan_ok | jaccard_similarity |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        result = row["result_rows"][0]
        backend_seconds = row["backend_seconds"]
        consistency = row["consistency_vs_python"]
        lines.append(
            f"| `{row['copies']}` | `{row['left_polygon_count']}` | `{row['right_polygon_count']}` | "
            f"`{backend_seconds['cpu_python_reference']:.6f}` | `{backend_seconds['cpu']:.6f}` | "
            f"`{backend_seconds['embree']:.6f}` | `{backend_seconds['optix']:.6f}` | "
            f"`{backend_seconds['vulkan']:.6f}` | `{consistency['cpu']}` | "
            f"`{consistency['embree']}` | `{consistency['optix']}` | `{consistency['vulkan']}` | "
            f"`{result['jaccard_similarity']:.6f}` |"
        )
    lines.append("")
    lines.append("Timing note: the Embree, OptiX, and Vulkan rows above are wrapper-surface timings under the same native CPU/oracle fallback path used for this workload. Small differences versus the CPU row should be read as measurement noise or wrapper-overhead variation, not as backend-specific Jaccard acceleration.")
    lines.append("")
    return "\n".join(lines)


def write_goal146_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "summary.json"
    markdown_path = output_path / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_goal146_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
