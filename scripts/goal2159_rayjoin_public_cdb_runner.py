from __future__ import annotations

import argparse
import json
import os
import signal
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.rtdl_rayjoin_v2_spatial_join_app import run_rayjoin_workload
from rtdsl.datasets import CdbDataset
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import download_rayjoin_sample
from rtdsl.datasets import load_cdb
from rtdsl.datasets import write_cdb


DEFAULT_DATA_DIR = ROOT / "data" / "rayjoin"


@dataclass(frozen=True)
class SliceSpec:
    source: str
    start: int
    count: int
    filename: str


@dataclass(frozen=True)
class CaseSpec:
    label: str
    workload: str
    dataset: str
    slices: tuple[SliceSpec, ...]
    note: str


CASES: dict[str, CaseSpec] = {
    "pip_county512": CaseSpec(
        label="pip_county512",
        workload="pip",
        dataset="{county_0_512}",
        slices=(SliceSpec("br_county", 0, 512, "br_county_start0_count512.cdb"),),
        note="Point-in-polygon over a bounded county slice.",
    ),
    "lsi_county64_soil64_prefix": CaseSpec(
        label="lsi_county64_soil64_prefix",
        workload="lsi",
        dataset="{county_0_64} + {soil_0_64}",
        slices=(
            SliceSpec("br_county", 0, 64, "br_county_start0_count64.cdb"),
            SliceSpec("br_soil", 0, 64, "br_soil_start0_count64.cdb"),
        ),
        note="Prefix county/soil LSI slice retained as a zero-hit control.",
    ),
    "lsi_county256_soil256_count48": CaseSpec(
        label="lsi_county256_soil256_count48",
        workload="lsi",
        dataset="{county_256_48} + {soil_256_48}",
        slices=(
            SliceSpec("br_county", 256, 48, "br_county_start256_count48.cdb"),
            SliceSpec("br_soil", 256, 48, "br_soil_start256_count48.cdb"),
        ),
        note="First nonzero county/soil LSI slice from the Goal2157 offset search.",
    ),
    "lsi_county256_soil256_count128": CaseSpec(
        label="lsi_county256_soil256_count128",
        workload="lsi",
        dataset="{county_256_128} + {soil_256_128}",
        slices=(
            SliceSpec("br_county", 256, 128, "br_county_start256_count128.cdb"),
            SliceSpec("br_soil", 256, 128, "br_soil_start256_count128.cdb"),
        ),
        note="Larger nonzero county/soil LSI slice with a mild warm OptiX win.",
    ),
    "lsi_county256_soil256_count192": CaseSpec(
        label="lsi_county256_soil256_count192",
        workload="lsi",
        dataset="{county_256_192} + {soil_256_192}",
        slices=(
            SliceSpec("br_county", 256, 192, "br_county_start256_count192.cdb"),
            SliceSpec("br_soil", 256, 192, "br_soil_start256_count192.cdb"),
        ),
        note="Best Goal2157 bounded nonzero county/soil LSI slice.",
    ),
    "lsi_county64_self_positive_control": CaseSpec(
        label="lsi_county64_self_positive_control",
        workload="lsi",
        dataset="{county_0_64} + {county_0_64}",
        slices=(SliceSpec("br_county", 0, 64, "br_county_start0_count64.cdb"),),
        note="Self-join endpoint-touch diagnostic; not RayJoin performance evidence.",
    ),
    "overlay_county128_soil128": CaseSpec(
        label="overlay_county128_soil128",
        workload="overlay_seed",
        dataset="{county_0_128} + {soil_0_128}",
        slices=(
            SliceSpec("br_county", 0, 128, "br_county_start0_count128.cdb"),
            SliceSpec("br_soil", 0, 128, "br_soil_start0_count128.cdb"),
        ),
        note="Bounded overlay dependency row slice.",
    ),
}


class StepTimeout(Exception):
    pass


def _signal_handler(signum, frame) -> None:
    raise StepTimeout()


def _maybe_download_samples(data_dir: Path, *, download: bool) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in ("br_county", "br_soil"):
        path = data_dir / f"{name}.cdb"
        if path.exists():
            continue
        if not download:
            raise FileNotFoundError(f"{path} is missing; rerun with --download")
        download_rayjoin_sample(name, path)


def _source_path(data_dir: Path, source: str) -> Path:
    return data_dir / f"{source}.cdb"


def _slice_key(spec: SliceSpec) -> str:
    prefix = "county" if spec.source == "br_county" else "soil"
    return f"{prefix}_{spec.start}_{spec.count}"


def _materialize_slices(data_dir: Path, selected_cases: tuple[CaseSpec, ...]) -> dict[str, dict[str, object]]:
    needed: dict[SliceSpec, None] = {}
    for case in selected_cases:
        for spec in case.slices:
            needed[spec] = None

    loaded: dict[str, CdbDataset] = {}
    materialized: dict[str, dict[str, object]] = {}
    for spec in needed:
        if spec.source not in loaded:
            loaded[spec.source] = load_cdb(_source_path(data_dir, spec.source))
        source = loaded[spec.source]
        sliced = CdbDataset(
            name=f"{spec.source}_start{spec.start}_count{spec.count}",
            chains=tuple(source.chains[spec.start : spec.start + spec.count]),
        )
        path = write_cdb(sliced, data_dir / spec.filename)
        segment_count = len(chains_to_segments(sliced))
        materialized[_slice_key(spec)] = {
            "path": str(path),
            "source": spec.source,
            "start": spec.start,
            "count": spec.count,
            "chains": len(sliced.chains),
            "segments": segment_count,
            "bytes": path.stat().st_size,
        }
    return materialized


def _resolve_dataset_template(template: str, slices: dict[str, dict[str, object]]) -> str:
    values = {key: value["path"] for key, value in slices.items()}
    return template.format(**values)


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _run_case(
    case: CaseSpec,
    dataset: str,
    *,
    backends: tuple[str, ...],
    warmups: int,
    repeats: int,
    step_timeout: int,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "workload": case.workload,
        "dataset": dataset,
        "note": case.note,
        "backends": {},
    }
    for backend in backends:
        print(f"[goal2159] start {case.label}/{backend}", flush=True)
        start = time.perf_counter()
        times: list[float] = []
        rows: list[int] = []
        parity: list[bool] = []
        if hasattr(signal, "SIGALRM"):
            signal.alarm(step_timeout)
        try:
            for index in range(warmups):
                result = run_rayjoin_workload(case.workload, backend=backend, dataset=dataset, include_rows=False)
                print(
                    f"[goal2159] warmup {case.label}/{backend} {index + 1}/{warmups} "
                    f"app={float(result['elapsed_sec']):.6f}s rows={int(result['row_count'])} "
                    f"parity={bool(result['parity_vs_cpu_python_reference'])}",
                    flush=True,
                )
            for index in range(repeats):
                result = run_rayjoin_workload(case.workload, backend=backend, dataset=dataset, include_rows=False)
                times.append(float(result["elapsed_sec"]))
                rows.append(int(result["row_count"]))
                parity.append(bool(result["parity_vs_cpu_python_reference"]))
                print(
                    f"[goal2159] repeat {case.label}/{backend} {index + 1}/{repeats} "
                    f"app={times[-1]:.6f}s rows={rows[-1]} parity={parity[-1]}",
                    flush=True,
                )
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            payload["backends"][backend] = {
                "status": "ok",
                "elapsed_outer_sec": time.perf_counter() - start,
                "app_elapsed_sec_values": times,
                "app_elapsed_sec_median": _median(times),
                "row_counts": rows,
                "row_count_consistent": len(set(rows)) == 1,
                "all_parity_vs_cpu_python_reference": all(parity),
                "rt_core_accelerated": backend == "optix",
            }
        except StepTimeout:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            payload["backends"][backend] = {
                "status": "timeout",
                "elapsed_outer_sec": time.perf_counter() - start,
            }
        except Exception as exc:  # pragma: no cover - artifact path records runtime failures.
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            payload["backends"][backend] = {
                "status": "error",
                "elapsed_outer_sec": time.perf_counter() - start,
                "error": repr(exc),
            }
    return payload


def build_artifact(args: argparse.Namespace) -> dict[str, object]:
    selected = tuple(CASES[name] for name in args.cases.split(",") if name)
    if not selected:
        raise ValueError("at least one case must be selected")

    data_dir = Path(args.data_dir)
    _maybe_download_samples(data_dir, download=args.download)
    slices = _materialize_slices(data_dir, selected)
    backends = tuple(backend.strip() for backend in args.backends.split(",") if backend.strip())

    artifact: dict[str, object] = {
        "goal": "2159",
        "commit": os.popen("git rev-parse HEAD").read().strip(),
        "data_dir": str(data_dir),
        "warmups": args.warmups,
        "repeats": args.repeats,
        "step_timeout_sec": args.step_timeout,
        "slices": slices,
        "cases": {},
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "whole_app_rayjoin_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }
    for case in selected:
        dataset = _resolve_dataset_template(case.dataset, slices)
        if args.dry_run:
            artifact["cases"][case.label] = {
                "workload": case.workload,
                "dataset": dataset,
                "note": case.note,
                "backends": {backend: {"status": "dry_run"} for backend in backends},
            }
            continue
        artifact["cases"][case.label] = _run_case(
            case,
            dataset,
            backends=backends,
            warmups=args.warmups,
            repeats=args.repeats,
            step_timeout=args.step_timeout,
        )
    return artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded public RayJoin CDB RTDL v2 evidence cases.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directory containing or receiving RayJoin CDB files.")
    parser.add_argument("--output", required=True, help="JSON artifact path.")
    parser.add_argument("--download", action="store_true", help="Download missing public RayJoin samples.")
    parser.add_argument("--dry-run", action="store_true", help="Write planned slices/cases without running backends.")
    parser.add_argument("--cases", default=",".join(CASES), help="Comma-separated case labels.")
    parser.add_argument("--backends", default="cpu,embree,optix", help="Comma-separated backends.")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--step-timeout", type=int, default=240)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = build_artifact(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2159] wrote {output}", flush=True)


if __name__ == "__main__":
    main()
