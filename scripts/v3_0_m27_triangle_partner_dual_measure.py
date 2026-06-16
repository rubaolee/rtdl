from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M27 triangle-counting CuPy/Numba partner summary evidence."
    )
    parser.add_argument("--cliques", type=int, default=5000)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--prewarm-cliques", type=int, default=10)
    parser.add_argument("--skip-prewarm", action="store_true")
    parser.add_argument("--partners", default="cupy,numba")
    parser.add_argument("--modes", default="rt_graph_2a1_generic_rt,rt_graph_1a2_generic_rt")
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--edge-file",
        type=Path,
        default=Path("build/goal4424_m27_triangle_k4_cliques.edge"),
    )
    parser.add_argument(
        "--numba-cuda-home",
        type=Path,
        default=Path(os.environ["RTDL_NUMBA_CUDA_HOME"]) if os.environ.get("RTDL_NUMBA_CUDA_HOME") else None,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4424_v3_0_m27_triangle_partner_dual_evidence.json"),
    )
    args = parser.parse_args()

    if args.cliques < 1:
        raise ValueError("--cliques must be at least 1")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.repeat < 1:
        raise ValueError("--repeat must be at least 1")
    if args.prewarm_cliques < 1:
        raise ValueError("--prewarm-cliques must be at least 1")
    partners = tuple(partner.strip() for partner in args.partners.split(",") if partner.strip())
    modes = tuple(mode.strip() for mode in args.modes.split(",") if mode.strip())
    if not partners:
        raise ValueError("--partners must include at least one partner")
    if not modes:
        raise ValueError("--modes must include at least one mode")
    unsupported_partners = sorted(set(partners) - {"cupy", "numba"})
    if unsupported_partners:
        raise ValueError(f"unsupported partner(s): {', '.join(unsupported_partners)}")
    unsupported_modes = sorted(set(modes) - {"rt_graph_2a1_generic_rt", "rt_graph_1a2_generic_rt"})
    if unsupported_modes:
        raise ValueError(f"unsupported mode(s): {', '.join(unsupported_modes)}")

    numba_cuda_home = _apply_numba_cuda_home(args.numba_cuda_home)

    from examples.current.research_benchmarks.triangle_counting import (
        rtdl_triangle_counting_benchmark_app as app,
    )
    from examples.current.research_benchmarks.triangle_counting.rt_graph_contract import (
        write_binary_edges,
    )

    args.edge_file.parent.mkdir(parents=True, exist_ok=True)
    write_binary_edges(args.edge_file, _k4_clique_edges(args.cliques))
    prewarm_edge_file = args.edge_file.with_suffix(".prewarm.edge")
    prewarm = {
        "enabled": not args.skip_prewarm,
        "cliques": args.prewarm_cliques if not args.skip_prewarm else 0,
        "edge_file": str(prewarm_edge_file) if not args.skip_prewarm else None,
    }
    if not args.skip_prewarm:
        write_binary_edges(prewarm_edge_file, _k4_clique_edges(args.prewarm_cliques))
        _prewarm_partner_routes(
            app=app,
            edge_file=prewarm_edge_file,
            modes=modes,
            partners=partners,
        )

    rows = []
    for mode in modes:
        for partner in partners:
            payload = app.run_app(
                mode,
                edge_file=str(args.edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner=partner,
                warmup=args.warmup,
                repeat=args.repeat,
            )
            rows.append(_compact_row(payload))

    signatures_by_mode: dict[str, set[str]] = {}
    for row in rows:
        signatures_by_mode.setdefault(str(row["mode"]), set()).add(json.dumps(row["signature"], sort_keys=True))
    payload = {
        "version": "rtdl.v3_0.triangle_partner_dual.m27",
        "status": "m27_triangle_counting_exposes_cupy_and_numba_partner_summary_routes",
        "parameters": {
            "cliques": args.cliques,
            "edge_count": args.cliques * 6,
            "expected_triangle_count": args.cliques * 4,
            "warmup": args.warmup,
            "repeat": args.repeat,
            "prewarm": prewarm,
            "partners": partners,
            "modes": modes,
            "edge_file": str(args.edge_file),
            "hardware": args.hardware or _hardware_label(),
        },
        "rows": tuple(rows),
        "comparison": {
            "signature_match_by_mode": {
                mode: len(signatures) == 1 for mode, signatures in sorted(signatures_by_mode.items())
            },
            "all_triangle_counts_match_oracle": all(row["triangle_count_matches_oracle"] for row in rows),
            "partners_covered": tuple(sorted({str(row["partner"]) for row in rows})),
            "modes_covered": tuple(sorted({str(row["mode"]) for row in rows})),
            "rt_core_accelerated": all(bool(row["rt_core_accelerated"]) for row in rows),
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
        "claim_boundary": {
            "cupy_route": "gpu_graph_contract_builder_and_optix_device_column_summary",
            "numba_route": "cpu_contract_then_numba_device_upload_and_optix_device_column_summary",
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
            "automatic_partner_selection_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "runner_numba_cuda_home": numba_cuda_home,
    }
    if not payload["comparison"]["all_triangle_counts_match_oracle"]:
        raise RuntimeError("M27 triangle partner route failed oracle parity")
    if not all(payload["comparison"]["signature_match_by_mode"].values()):
        raise RuntimeError("M27 triangle partner signatures differ within a mode")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": payload["comparison"], "rows": rows}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _compact_row(payload: dict[str, object]) -> dict[str, object]:
    contract = dict(payload["rt_graph_contract"])
    transfer = dict((payload.get("generic_rt_summary") or {}).get("transfer_metadata") or {})
    session = dict(payload["v2_4_prepared_session"])
    timing = dict(payload["timing_ms"])
    return {
        "mode": payload["mode"],
        "partner": payload["partner"],
        "backend": payload["backend"],
        "partner_summary_contract_used": payload["partner_summary_contract_used"],
        "rt_core_accelerated": payload["rt_core_accelerated"],
        "primitive_count": payload["primitive_count"],
        "ray_count": payload["ray_count"],
        "oracle_triangle_count": payload["oracle_triangle_count"],
        "triangle_count_matches_oracle": payload["triangle_count_matches_oracle"],
        "partner_contract_label": contract.get("partner"),
        "partner_construction_mode": (contract.get("partner_timing_ms") or {}).get("construction_mode"),
        "partner_timing_ms": contract.get("partner_timing_ms"),
        "timing_ms": {
            "build_contract": timing.get("build_contract"),
            "build_geometry": timing.get("build_geometry"),
            "prepare_scene_ms": timing.get("prepare_scene_ms"),
            "query_median_ms": timing.get("query_median_ms"),
            "query_min_ms": timing.get("query_min_ms"),
            "query_max_ms": timing.get("query_max_ms"),
            "total": timing.get("total"),
        },
        "transfer_source_protocols": tuple(transfer.get("source_protocols") or ()),
        "v2_4_input_source_protocols": tuple(
            buffer["source_protocol"] for buffer in session.get("input_buffers", ())
        ),
        "summary_contract": (payload.get("generic_rt_summary") or {}).get("contract"),
        "signature": {
            "primitive_count": int(payload["primitive_count"]),
            "ray_count": int(payload["ray_count"]),
            "oracle_triangle_count": int(payload["oracle_triangle_count"]),
            "result_triangle_count": int(
                payload.get("generic_rt_weighted_triangle_count", payload.get("generic_rt_triangle_count"))
            ),
        },
    }


def _prewarm_partner_routes(
    *,
    app: object,
    edge_file: Path,
    modes: tuple[str, ...],
    partners: tuple[str, ...],
) -> None:
    for mode in modes:
        for partner in partners:
            app.run_app(
                mode,
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner=partner,
                warmup=0,
                repeat=1,
            )


def _k4_clique_edges(clique_count: int) -> tuple[tuple[int, int], ...]:
    edges: list[tuple[int, int]] = []
    for index in range(int(clique_count)):
        base = index * 4
        edges.extend(
            (
                (base + 0, base + 1),
                (base + 0, base + 2),
                (base + 0, base + 3),
                (base + 1, base + 2),
                (base + 1, base + 3),
                (base + 2, base + 3),
            )
        )
    return tuple(edges)


def _apply_numba_cuda_home(cuda_home: Path | None) -> dict[str, object]:
    if cuda_home is None:
        return {
            "configured": False,
            "reason": "not_requested",
            "cuda_home": os.environ.get("CUDA_HOME"),
            "cuda_path": os.environ.get("CUDA_PATH"),
        }
    home = cuda_home.resolve()
    nvvm_dir = home / "nvvm" / "lib64"
    bin_dir = home / "bin"
    if not (nvvm_dir / "libnvvm.so").exists() and not any(nvvm_dir.glob("libnvvm.so*")):
        raise FileNotFoundError(f"Numba CUDA home is missing NVVM library under {nvvm_dir}")
    if not (home / "nvvm" / "libdevice" / "libdevice.10.bc").exists():
        raise FileNotFoundError(f"Numba CUDA home is missing libdevice.10.bc under {home / 'nvvm/libdevice'}")
    os.environ["CUDA_HOME"] = str(home)
    os.environ["CUDA_PATH"] = str(home)
    os.environ["PATH"] = os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")])
    os.environ["LD_LIBRARY_PATH"] = os.pathsep.join([str(nvvm_dir), os.environ.get("LD_LIBRARY_PATH", "")])
    return {
        "configured": True,
        "cuda_home": str(home),
        "nvvm_dir": str(nvvm_dir),
        "bin_dir": str(bin_dir),
        "ptxas_version": _run_text([str(bin_dir / "ptxas"), "--version"]),
    }


def _hardware_label() -> str:
    gpu = _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,pci.bus_id",
            "--format=csv,noheader",
        ]
    ).strip()
    if gpu:
        return gpu.splitlines()[0]
    return f"{platform.platform()} / {platform.processor() or platform.machine()}"


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


if __name__ == "__main__":
    raise SystemExit(main())
