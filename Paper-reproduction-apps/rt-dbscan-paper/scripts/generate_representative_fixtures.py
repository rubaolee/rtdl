from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "Paper-reproduction-apps").exists())
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
FIXTURE_DIR = APP_DIR / "data" / "fixtures"
MANIFEST_PATH = FIXTURE_DIR / "representative_fixtures_manifest.json"


def _grid_cluster(
    *,
    center: tuple[float, float, float],
    shape: tuple[int, int, int],
    spacing: float,
) -> list[tuple[float, float, float]]:
    nx, ny, nz = shape
    cx, cy, cz = center
    ox = (nx - 1) * spacing / 2.0
    oy = (ny - 1) * spacing / 2.0
    oz = (nz - 1) * spacing / 2.0
    points: list[tuple[float, float, float]] = []
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                points.append((cx + ix * spacing - ox, cy + iy * spacing - oy, cz + iz * spacing - oz))
    return points


def _write_csv(path: Path, points: list[tuple[float, float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(f"{x:.9f},{y:.9f},{z:.9f}" for x, y, z in points)
    path.write_text(text + "\n", encoding="utf-8")


def _case_medium_two_clusters() -> dict[str, object]:
    points: list[tuple[float, float, float]] = []
    points.extend(_grid_cluster(center=(0.0, 0.0, 0.0), shape=(4, 4, 3), spacing=0.035))
    points.extend(_grid_cluster(center=(1.0, 0.0, 0.0), shape=(4, 4, 3), spacing=0.035))
    points.extend([(2.0, 2.0, 2.0), (2.35, 2.2, 2.1), (-1.5, 1.4, 0.8), (0.5, 1.8, -1.4)])
    filename = "representative_medium_two_clusters3d.csv"
    _write_csv(FIXTURE_DIR / filename, points)
    return {
        "name": "representative_medium_two_clusters3d",
        "path": f"data/fixtures/{filename}",
        "point_count": len(points),
        "epsilon": 0.09,
        "min_points": 6,
        "description": "Two dense 3D components plus four distant noise points.",
    }


def _case_border_shell() -> dict[str, object]:
    points: list[tuple[float, float, float]] = []
    # Place likely border points first so the author's xID > primID call-2 path
    # can observe later core neighbors, matching the Goal5095 fixture policy.
    points.extend([(-0.105, 0.0, 0.0), (0.105, 0.0, 0.0), (1.0 - 0.105, 0.0, 0.0), (1.0 + 0.105, 0.0, 0.0)])
    points.extend(_grid_cluster(center=(0.0, 0.0, 0.0), shape=(3, 3, 3), spacing=0.035))
    points.extend(_grid_cluster(center=(1.0, 0.0, 0.0), shape=(3, 3, 3), spacing=0.035))
    points.extend([(3.0, 0.0, 0.0), (3.3, 0.3, 0.0)])
    filename = "representative_border_shell3d.csv"
    _write_csv(FIXTURE_DIR / filename, points)
    return {
        "name": "representative_border_shell3d",
        "path": f"data/fixtures/{filename}",
        "point_count": len(points),
        "epsilon": 0.085,
        "min_points": 8,
        "description": "Two compact components, early border-shell points, and two noise points.",
    }


def _case_three_components() -> dict[str, object]:
    points: list[tuple[float, float, float]] = []
    points.extend(_grid_cluster(center=(0.0, 0.0, 0.0), shape=(3, 3, 3), spacing=0.04))
    points.extend(_grid_cluster(center=(1.0, 0.5, 0.0), shape=(3, 3, 2), spacing=0.04))
    points.extend(_grid_cluster(center=(-0.8, 1.0, 0.2), shape=(4, 2, 2), spacing=0.04))
    points.extend([(2.0, 2.0, 2.0), (2.3, 2.0, 2.1), (-2.0, -2.0, 0.0)])
    filename = "representative_three_components_noise3d.csv"
    _write_csv(FIXTURE_DIR / filename, points)
    return {
        "name": "representative_three_components_noise3d",
        "path": f"data/fixtures/{filename}",
        "point_count": len(points),
        "epsilon": 0.095,
        "min_points": 6,
        "description": "Three components of different sizes plus three noise points.",
    }


def generate() -> dict[str, object]:
    cases = [_case_medium_two_clusters(), _case_border_shell(), _case_three_components()]
    manifest = {
        "schema": "rtdl.paper_reproduction.rt_dbscan.representative_fixtures.v1",
        "paper_app": "rt-dbscan-paper",
        "generated_by": "generate_representative_fixtures.py",
        "claim_boundary": "Synthetic same-input representative fixtures only; not exact paper datasets.",
        "cases": cases,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    manifest = generate()
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
