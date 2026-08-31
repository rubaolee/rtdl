import importlib.util
import sys
import tempfile
import unittest
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5309_full_public_arcgis_point_count_mbr_probe.py"
)


def _load_probe_module():
    spec = importlib.util.spec_from_file_location("goal5309_probe", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5309XhdFullPublicArcgisProbeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.probe = _load_probe_module()

    def _count_geometry(self, geometry: dict) -> int:
        total = 0
        for sequence, close in self.probe._geometry_author_sequences(geometry):
            total += self.probe._author_sequence_point_count(sequence, close=close)
        return total

    def _points_geometry(self, geometry: dict) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        for sequence, close in self.probe._geometry_author_sequences(geometry):
            points.extend(self.probe._iter_author_points_from_sequence(sequence, close=close))
        return points

    def test_polygon_outer_ring_is_closed_when_needed(self) -> None:
        geometry = {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]],
        }

        self.assertEqual(self._count_geometry(geometry), 4)
        self.assertEqual(
            self._points_geometry(geometry),
            [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)],
        )

    def test_already_closed_polygon_outer_ring_is_not_double_closed(self) -> None:
        geometry = {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]],
        }

        self.assertEqual(self._count_geometry(geometry), 3)
        self.assertEqual(self._points_geometry(geometry)[-1], (0.0, 0.0))

    def test_linestring_is_not_closed(self) -> None:
        geometry = {
            "type": "LineString",
            "coordinates": [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]],
        }

        self.assertEqual(self._count_geometry(geometry), 3)
        self.assertEqual(
            self._points_geometry(geometry),
            [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)],
        )

    def test_point_is_single_author_point(self) -> None:
        geometry = {"type": "Point", "coordinates": [2.5, 3.5]}

        self.assertEqual(self._count_geometry(geometry), 1)
        self.assertEqual(self._points_geometry(geometry), [(2.5, 3.5)])

    def test_checkpoint_loader_marks_resume_state(self) -> None:
        spec = self.probe.ServiceSpec(
            key="demo",
            paper_basename="demo.wkt",
            service_url="https://example.test/FeatureServer",
            max_record_count=10,
            paper_point_count=3,
            paper_mbr=((0.0, 1.0), (0.0, 1.0)),
        )
        payload = {
            "key": "demo",
            "features_seen": 2,
            "pages_seen": 1,
            "author_loader_point_count": 7,
            "geometry_types": {"Polygon": 2},
            "sample_labels": ["a"],
            "mbr": [0.0, 1.0, 0.0, 1.0],
            "complete": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "demo.json"
            checkpoint.write_text(json.dumps(payload), encoding="utf-8")

            acc = self.probe._load_checkpoint_accumulator(checkpoint, spec, 5)

        self.assertIsNotNone(acc)
        self.assertTrue(acc["resumed_from_checkpoint"])
        self.assertEqual(acc["checkpoint_features_seen_at_start"], 2)
        self.assertEqual(acc["features_seen"], 2)
        self.assertFalse(acc["complete"])


if __name__ == "__main__":
    unittest.main()
