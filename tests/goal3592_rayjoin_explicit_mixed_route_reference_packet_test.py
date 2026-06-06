from __future__ import annotations

import json
import math
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3592_rayjoin_explicit_mixed_route_reference_packet_2026-06-06.md"
GOAL3583_STANDARD = ROOT / "docs" / "reports" / "goal3583_rayjoin_hot_promoted_routes_a5000" / "summary.json"
GOAL3583_STRESS = ROOT / "docs" / "reports" / "goal3583_rayjoin_hot_promoted_routes_stress_a5000" / "summary.json"
GOAL3589_STANDARD = ROOT / "docs" / "reports" / "goal3589_rayjoin_cupy_same_contract_baseline_a5000" / "summary.json"
GOAL3589_STRESS = ROOT / "docs" / "reports" / "goal3589_rayjoin_cupy_same_contract_baseline_stress_a5000" / "summary.json"


def _embree_times(path: pathlib.Path) -> dict[str, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, float] = {}
    for row in payload["ratios"]:
        group = row["comparison_group"]
        if "_pip_" in group:
            result["pip"] = float(row["embree_sec"])
        elif "_lsi_" in group:
            result["lsi"] = float(row["embree_sec"])
        elif "_overlay_seed_" in group:
            result["overlay_seed"] = float(row["embree_sec"])
    return result


def _recommended(path: pathlib.Path, embree_path: pathlib.Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    embree = _embree_times(embree_path)
    rows = []
    for row in payload["rows"]:
        workload = row["workload"]
        cupy_sec = float(row["cupy_cuda_core_baseline"]["hot_median_sec"])
        optix_sec = float(row["rtdl_optix"]["hot_median_sec"])
        if cupy_sec <= optix_sec:
            route = "cupy"
            sec = cupy_sec
        else:
            route = "rtdl_optix"
            sec = optix_sec
        rows.append(
            {
                "workload": workload,
                "route": route,
                "sec": sec,
                "embree_sec": embree[workload],
                "speedup": embree[workload] / sec,
            }
        )
    total_embree = sum(row["embree_sec"] for row in rows)
    total_recommended = sum(row["sec"] for row in rows)
    return {
        "rows": rows,
        "summed_speedup": total_embree / total_recommended,
        "geomean": math.prod(row["speedup"] for row in rows) ** (1.0 / len(rows)),
    }


class Goal3592RayJoinExplicitMixedRouteReferencePacketTest(unittest.TestCase):
    def test_recomputes_standard_packet(self) -> None:
        packet = _recommended(GOAL3589_STANDARD, GOAL3583_STANDARD)
        routes = {row["workload"]: row["route"] for row in packet["rows"]}
        self.assertEqual(routes, {"pip": "cupy", "lsi": "cupy", "overlay_seed": "cupy"})
        self.assertAlmostEqual(packet["summed_speedup"], 1827.3067444965436)
        self.assertAlmostEqual(packet["geomean"], 538.5911180883835)

    def test_recomputes_stress_packet(self) -> None:
        packet = _recommended(GOAL3589_STRESS, GOAL3583_STRESS)
        routes = {row["workload"]: row["route"] for row in packet["rows"]}
        self.assertEqual(routes, {"pip": "cupy", "lsi": "rtdl_optix", "overlay_seed": "cupy"})
        self.assertAlmostEqual(packet["summed_speedup"], 10134.830019684357)
        self.assertAlmostEqual(packet["geomean"], 960.2428263108109)

    def test_report_blocks_automatic_selection_and_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Do not hide this behind automatic dispatch",
            "explicit mixed packet",
            "not pure RTDL/OptiX and not pure CuPy",
            "automatic partner/backend selection",
            "public RT-core speedup claim",
            "true zero-copy claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
