from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import json
from pathlib import Path
from textwrap import dedent

from .baseline_runner import representative_dataset_names


SUPPORTED_GENERATE_ONLY_WORKLOADS = ("segment_polygon_hitcount",)
SUPPORTED_GENERATE_ONLY_BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix")
SUPPORTED_GENERATE_ONLY_OUTPUT_MODES = ("rows", "summary")
SUPPORTED_GENERATE_ONLY_ARTIFACT_SHAPES = ("single_file", "handoff_bundle")


@dataclass(frozen=True)
class GenerateOnlyRequest:
    workload: str
    dataset: str
    backend: str
    verify: bool = True
    output_mode: str = "rows"
    artifact_shape: str = "single_file"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _normalize_request(request: GenerateOnlyRequest | dict[str, object]) -> GenerateOnlyRequest:
    if isinstance(request, GenerateOnlyRequest):
        normalized = request
    else:
        normalized = GenerateOnlyRequest(
            workload=str(request["workload"]),
            dataset=str(request["dataset"]),
            backend=str(request["backend"]),
            verify=bool(request.get("verify", True)),
            output_mode=str(request.get("output_mode", "rows")),
            artifact_shape=str(request.get("artifact_shape", "single_file")),
        )
    _validate_request(normalized)
    return normalized


def _validate_request(request: GenerateOnlyRequest) -> None:
    if request.workload not in SUPPORTED_GENERATE_ONLY_WORKLOADS:
        raise ValueError(f"unsupported generate-only workload `{request.workload}`")
    if request.backend not in SUPPORTED_GENERATE_ONLY_BACKENDS:
        raise ValueError(f"unsupported generate-only backend `{request.backend}`")
    if request.output_mode not in SUPPORTED_GENERATE_ONLY_OUTPUT_MODES:
        raise ValueError(f"unsupported generate-only output mode `{request.output_mode}`")
    if request.artifact_shape not in SUPPORTED_GENERATE_ONLY_ARTIFACT_SHAPES:
        raise ValueError(f"unsupported generate-only artifact shape `{request.artifact_shape}`")
    datasets = representative_dataset_names(request.workload)
    if request.dataset not in datasets:
        raise ValueError(
            f"unsupported generate-only dataset `{request.dataset}` for workload `{request.workload}`"
        )


def generate_python_program(
    request: GenerateOnlyRequest | dict[str, object],
    output_path: str | Path,
) -> dict[str, object]:
    normalized = _normalize_request(request)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = render_python_program(normalized)
    destination.write_text(source, encoding="utf-8")
    return {
        "output_path": str(destination),
        "request": normalized.to_dict(),
    }


def generate_handoff_bundle(
    request: GenerateOnlyRequest | dict[str, object],
    output_dir: str | Path,
) -> dict[str, object]:
    normalized = _normalize_request(request)
    bundle_root = Path(output_dir)
    bundle_root.mkdir(parents=True, exist_ok=True)
    program_name = _bundle_program_name(normalized)
    program_path = bundle_root / program_name
    manifest_path = bundle_root / "request.json"
    readme_path = bundle_root / "README.md"
    program_path.write_text(render_python_program(normalized), encoding="utf-8")
    manifest_path.write_text(json.dumps(normalized.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readme_path.write_text(_render_bundle_readme(normalized, program_name, bundle_root), encoding="utf-8")
    return {
        "output_dir": str(bundle_root),
        "program": str(program_path),
        "manifest": str(manifest_path),
        "readme": str(readme_path),
        "request": normalized.to_dict(),
    }


def render_python_program(request: GenerateOnlyRequest | dict[str, object]) -> str:
    normalized = _normalize_request(request)
    if normalized.workload == "segment_polygon_hitcount":
        return _render_segment_polygon_hitcount_program(normalized)
    raise AssertionError(f"unreachable workload `{normalized.workload}`")


def _bundle_program_name(request: GenerateOnlyRequest) -> str:
    dataset_token = request.dataset.replace("/", "_").replace(".", "_")
    return f"generated_{request.workload}_{request.backend}_{dataset_token}.py"


def _render_bundle_readme(request: GenerateOnlyRequest, program_name: str, bundle_root: Path) -> str:
    bundle_rel = bundle_root.as_posix()
    return dedent(
        f"""
        # RTDL Generate-Only Handoff Bundle

        This bundle was generated from RTDL Goal 113 generate-only maturation.

        ## Request

        - workload: `{request.workload}`
        - dataset: `{request.dataset}`
        - backend: `{request.backend}`
        - verify: `{str(request.verify).lower()}`
        - output mode: `{request.output_mode}`
        - artifact shape: `{request.artifact_shape}`

        ## Files

        - `{program_name}`: runnable generated RTDL program
        - `request.json`: structured request manifest
        - `README.md`: this handoff note

        ## Run

        From the RTDL repo root:

        ```bash
        PYTHONPATH=src:. python3 {bundle_rel}/{program_name}
        ```

        The generated program contains:

        - the RTDL kernel
        - accepted dataset construction logic
        - the requested backend runner
        - verification against `cpu_python_reference` when enabled
        """
    ).lstrip()


def _render_segment_polygon_hitcount_program(request: GenerateOnlyRequest) -> str:
    dataset_literal = json.dumps(request.dataset)
    backend_literal = json.dumps(request.backend)
    output_mode_literal = json.dumps(request.output_mode)
    verify_literal = "True" if request.verify else "False"
    return dedent(
        f"""
        from __future__ import annotations

        import json
        import sys
        from pathlib import Path


        def _find_repo_root(start: Path) -> Path:
            for candidate in (start, *start.parents):
                if (candidate / "src" / "rtdsl" / "__init__.py").exists():
                    return candidate
            raise RuntimeError("could not locate RTDL repo root from generated program path")


        ROOT = _find_repo_root(Path(__file__).resolve().parent)
        sys.path.insert(0, str(ROOT / "src"))
        sys.path.insert(0, str(ROOT))

        import rtdsl as rt

        REQUEST_WORKLOAD = "segment_polygon_hitcount"
        REQUEST_DATASET = {dataset_literal}
        REQUEST_BACKEND = {backend_literal}
        REQUEST_VERIFY = {verify_literal}
        REQUEST_OUTPUT_MODE = {output_mode_literal}


        @rt.kernel(backend="rtdl", precision="float_approx")
        def generated_segment_polygon_hitcount():
            segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
            polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
            candidates = rt.traverse(segments, polygons, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
            return rt.emit(hits, fields=["segment_id", "hit_count"])


        def build_fixture_case() -> dict[str, object]:
            county = rt.load_cdb("tests/fixtures/rayjoin/br_county_subset.cdb")
            segments = tuple(
                rt.Segment(**{{k: v for k, v in record.items() if k in {{"id", "x0", "y0", "x1", "y1"}}}})
                for record in rt.chains_to_segments(county)[:10]
            )
            polygons = tuple(
                rt.Polygon(id=chain.chain_id, vertices=tuple((point.x, point.y) for point in chain.points))
                for chain in county.chains[:2]
                if len(chain.points) >= 3
            )
            return {{"segments": segments, "polygons": polygons}}


        def tile_segments(segments, *, copies: int, step_x: float, step_y: float):
            tiled = []
            for copy_index in range(copies):
                dx = copy_index * step_x
                dy = copy_index * step_y
                for segment in segments:
                    tiled.append(
                        rt.Segment(
                            id=int(segment.id) + copy_index * 10,
                            x0=float(segment.x0) + dx,
                            y0=float(segment.y0) + dy,
                            x1=float(segment.x1) + dx,
                            y1=float(segment.y1) + dy,
                        )
                    )
            return tuple(tiled)


        def tile_polygons(polygons, *, copies: int, step_x: float, step_y: float):
            tiled = []
            for copy_index in range(copies):
                dx = copy_index * step_x
                dy = copy_index * step_y
                for polygon in polygons:
                    tiled.append(
                        rt.Polygon(
                            id=int(polygon.id) + copy_index * 10,
                            vertices=tuple((float(x) + dx, float(y) + dy) for x, y in polygon.vertices),
                        )
                    )
            return tuple(tiled)


        def build_case() -> dict[str, object]:
            # Generated case block for the requested dataset.
            if REQUEST_DATASET == "authored_segment_polygon_minimal":
                return {{
                    "segments": (
                        rt.Segment(id=1, x0=-1.0, y0=1.0, x1=3.0, y1=1.0),
                        rt.Segment(id=2, x0=5.0, y0=5.0, x1=6.0, y1=6.0),
                    ),
                    "polygons": (
                        rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
                        rt.Polygon(id=11, vertices=((4.0, 4.0), (7.0, 4.0), (7.0, 7.0), (4.0, 7.0))),
                    ),
                }}
            if REQUEST_DATASET == "tests/fixtures/rayjoin/br_county_subset.cdb":
                return build_fixture_case()
            if REQUEST_DATASET == "derived/br_county_subset_segment_polygon_tiled_x4":
                case = build_fixture_case()
                return {{
                    "segments": tile_segments(case["segments"], copies=4, step_x=30.0, step_y=20.0),
                    "polygons": tile_polygons(case["polygons"], copies=4, step_x=30.0, step_y=20.0),
                }}
            raise ValueError(f"unsupported generated dataset `{{REQUEST_DATASET}}`")


        def run_backend(case_inputs: dict[str, object]):
            if REQUEST_BACKEND == "cpu_python_reference":
                return rt.run_cpu_python_reference(generated_segment_polygon_hitcount, **case_inputs)
            if REQUEST_BACKEND == "cpu":
                return rt.run_cpu(generated_segment_polygon_hitcount, **case_inputs)
            if REQUEST_BACKEND == "embree":
                return rt.run_embree(generated_segment_polygon_hitcount, **case_inputs)
            if REQUEST_BACKEND == "optix":
                return rt.run_optix(generated_segment_polygon_hitcount, **case_inputs)
            raise ValueError(f"unsupported generated backend `{{REQUEST_BACKEND}}`")


        def verify_rows(case_inputs: dict[str, object], actual_rows) -> bool:
            expected_rows = rt.run_cpu_python_reference(generated_segment_polygon_hitcount, **case_inputs)
            return rt.compare_baseline_rows(REQUEST_WORKLOAD, expected_rows, actual_rows)


        def format_payload(actual_rows, verified: bool | None) -> dict[str, object]:
            payload = {{
                "workload": REQUEST_WORKLOAD,
                "dataset": REQUEST_DATASET,
                "backend": REQUEST_BACKEND,
                "verification_requested": REQUEST_VERIFY,
            }}
            if verified is not None:
                payload["verified_against_cpu_python_reference"] = verified
            if REQUEST_OUTPUT_MODE == "summary":
                payload["row_count"] = len(actual_rows)
            else:
                payload["rows"] = actual_rows
            return payload


        def main() -> int:
            # Generated by RTDL Goal 113 generate-only maturation.
            case_inputs = build_case()
            actual_rows = run_backend(case_inputs)
            verified = verify_rows(case_inputs, actual_rows) if REQUEST_VERIFY else None
            payload = format_payload(actual_rows, verified)
            print(json.dumps(payload, indent=2, sort_keys=True))
            if verified is False:
                raise SystemExit("generated program verification failed")
            return 0


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    ).lstrip()
