from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "docs/reports/goal2097_tutorial_pod_validation"
OUTDIR.mkdir(parents=True, exist_ok=True)
TIMEOUT = int(os.environ.get("STEP_TIMEOUT_SECONDS", "90"))

BASE_ENV = os.environ.copy()
BASE_ENV.update(
    {
        "PYTHONPATH": "src:.",
        "RTDL_EMBREE_LIBRARY": str(ROOT / "build/librtdl_embree.so"),
        "RTDL_OPTIX_LIBRARY": str(ROOT / "build/librtdl_optix.so"),
        "CUDA_HOME": "/usr/local/cuda-12",
        "RTDL_OPTIX_PTX_ARCH": os.environ.get("RTDL_OPTIX_PTX_ARCH", "compute_89"),
        "RTDL_OPTIX_PTX_COMPILER": "nvcc",
        "RTDL_NVCC": "/usr/local/cuda-12/bin/nvcc",
        "RTDL_NVCC_CCBIN": "/usr/bin/g++",
    }
)
BASE_ENV["PATH"] = "/usr/local/cuda-12/bin:" + BASE_ENV.get("PATH", "")
BASE_ENV["LD_LIBRARY_PATH"] = (
    "/usr/local/cuda-12/targets/x86_64-linux/lib:"
    "/usr/local/cuda-12/lib64:"
    "/usr/local/cuda-12/compat:"
    + BASE_ENV.get("LD_LIBRARY_PATH", "")
)

COMMANDS = [
    ("hello_world", "portable", "python3 examples/v2_0/getting_started/rtdl_hello_world.py"),
    ("sorting_demo", "embree", "python3 scripts/rtdl_sorting_demo.py --backend embree 3 1 4 1 5 0 2 5"),
    ("sorting_demo", "optix", "python3 scripts/rtdl_sorting_demo.py --backend optix 3 1 4 1 5 0 2 5"),
    ("feature_quickstart_cookbook", "portable", "python3 examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py"),
    ("partner_anyhit_numpy", "embree", "python3 examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend embree"),
    ("partner_anyhit_numpy", "optix", "python3 examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend optix"),
    ("partner_anyhit_cupy", "embree", "python3 examples/v2_0/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend embree"),
    ("partner_anyhit_cupy", "optix", "python3 examples/v2_0/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend optix"),
    ("segment_polygon_hitcount", "embree", "python3 examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py --backend embree"),
    ("segment_polygon_hitcount", "optix", "python3 examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py --backend optix"),
    ("segment_polygon_anyhit_rows", "embree", "python3 examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py --backend embree"),
    ("segment_polygon_anyhit_rows", "optix", "python3 examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py --backend optix --optix-mode native"),
    ("polygon_pair_overlap_area_rows", "embree", "python3 examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py --backend embree"),
    ("polygon_pair_overlap_area_rows", "optix", "python3 examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py --backend optix"),
    ("polygon_set_jaccard", "embree", "python3 examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py --backend embree"),
    ("polygon_set_jaccard", "optix", "python3 examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py --backend optix"),
    ("fixed_radius_neighbors", "embree", "python3 examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend embree"),
    ("fixed_radius_neighbors", "optix", "python3 examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend optix"),
    ("knn_rows", "embree", "python3 examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend embree"),
    ("knn_rows", "optix", "python3 examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend optix"),
    ("hausdorff_distance_app", "embree", "python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend embree"),
    ("hausdorff_distance_app", "optix", "python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend optix"),
    ("hausdorff_threshold", "optix_rt", "python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend optix --optix-summary-mode directed_threshold_prepared --hausdorff-threshold 0.4 --require-rt-core"),
    ("graph_bfs", "embree", "python3 examples/v2_0/features/graph/rtdl_graph_bfs.py --backend embree"),
    ("graph_bfs", "optix", "python3 examples/v2_0/features/graph/rtdl_graph_bfs.py --backend optix"),
    ("graph_bfs_native", "optix_rt", "python3 examples/v2_0/features/graph/rtdl_graph_bfs.py --backend optix --optix-graph-mode native"),
    ("graph_triangle_count", "embree", "python3 examples/v2_0/features/graph/rtdl_graph_triangle_count.py --backend embree"),
    ("graph_triangle_count", "optix", "python3 examples/v2_0/features/graph/rtdl_graph_triangle_count.py --backend optix"),
    ("graph_triangle_count_native", "optix_rt", "python3 examples/v2_0/features/graph/rtdl_graph_triangle_count.py --backend optix --optix-graph-mode native"),
    ("graph_analytics_visibility", "optix_rt", "python3 examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py --backend optix --scenario visibility_edges --require-rt-core"),
    ("db_conjunctive_scan", "embree", "python3 examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend embree"),
    ("db_conjunctive_scan", "optix", "python3 examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend optix"),
    ("db_grouped_count", "embree", "python3 examples/v2_0/features/database/rtdl_db_grouped_count.py --backend embree"),
    ("db_grouped_count", "optix", "python3 examples/v2_0/features/database/rtdl_db_grouped_count.py --backend optix"),
    ("db_grouped_sum", "embree", "python3 examples/v2_0/features/database/rtdl_db_grouped_sum.py --backend embree"),
    ("db_grouped_sum", "optix", "python3 examples/v2_0/features/database/rtdl_db_grouped_sum.py --backend optix"),
    ("database_analytics_app", "embree", "python3 examples/v2_0/apps/analytics/rtdl_database_analytics_app.py --backend embree"),
    ("database_analytics_app", "optix", "python3 examples/v2_0/apps/analytics/rtdl_database_analytics_app.py --backend optix"),
    ("database_analytics_compact", "optix_rt", "python3 examples/v2_0/apps/analytics/rtdl_database_analytics_app.py --backend optix --output-mode compact_summary --require-rt-core"),
    ("visual_lit_ball", "embree", "python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend embree --compare-backend none --width 32 --height 16 --triangles 64 --output /tmp/rtdl_lit_ball_embree.txt"),
    ("visual_lit_ball", "optix", "python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend optix --compare-backend none --width 32 --height 16 --triangles 64 --output /tmp/rtdl_lit_ball_optix.txt"),
]


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:]


results = []
start_all = time.time()
for idx, (name, backend, command) in enumerate(COMMANDS, start=1):
    print(f"[goal2097] START {idx}/{len(COMMANDS)} {name} {backend}: {command}", flush=True)
    started = time.time()
    try:
        proc = subprocess.run(
            shlex.split(command),
            cwd=ROOT,
            env=BASE_ENV,
            text=True,
            capture_output=True,
            timeout=TIMEOUT,
        )
        status = "pass" if proc.returncode == 0 else "fail"
        stdout = tail(proc.stdout)
        stderr = tail(proc.stderr)
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        stdout = tail(exc.stdout if isinstance(exc.stdout, str) else "")
        stderr = tail(exc.stderr if isinstance(exc.stderr, str) else "")
        returncode = None
    elapsed = time.time() - started
    result = {
        "name": name,
        "backend": backend,
        "command": command,
        "status": status,
        "returncode": returncode,
        "elapsed_seconds": elapsed,
        "stdout_tail": stdout,
        "stderr_tail": stderr,
    }
    results.append(result)
    print(f"[goal2097] END {idx}/{len(COMMANDS)} {name} {backend}: {status} {elapsed:.2f}s", flush=True)
    if status != "pass":
        print("[goal2097] STDERR_TAIL_START", flush=True)
        print(tail(stderr or stdout, 1200), flush=True)
        print("[goal2097] STDERR_TAIL_END", flush=True)

summary = {
    "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "timeout_seconds": TIMEOUT,
    "total_elapsed_seconds": time.time() - start_all,
    "counts": {s: sum(1 for r in results if r["status"] == s) for s in ("pass", "fail", "timeout")},
    "results": results,
}
json_path = OUTDIR / "goal2097_tutorial_matrix_results.json"
json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

md = [
    "# Goal2097 Tutorial Pod Validation\n\n",
    f"Commit: `{summary['commit']}`\n\n",
    f"Timeout per command: `{TIMEOUT}` seconds\n\n",
    "| Tutorial command | Backend | Status | Seconds |\n",
    "| --- | --- | --- | ---: |\n",
]
for r in results:
    md.append(f"| `{r['name']}` | `{r['backend']}` | `{r['status']}` | {r['elapsed_seconds']:.2f} |\n")
md.append("\n## Failures\n\n")
failures = [r for r in results if r["status"] != "pass"]
if not failures:
    md.append("None.\n")
else:
    for r in failures:
        md.append(f"### {r['name']} / {r['backend']}\n\n")
        md.append(f"Command: `{r['command']}`\n\n")
        md.append("```text\n")
        md.append(tail((r["stderr_tail"] or r["stdout_tail"] or "").strip(), 2000))
        md.append("\n```\n\n")
md_path = OUTDIR / "goal2097_tutorial_matrix_results.md"
md_path.write_text("".join(md), encoding="utf-8")
print(f"[goal2097] WROTE {json_path}")
print(f"[goal2097] WROTE {md_path}")
if failures:
    sys.exit(1)
