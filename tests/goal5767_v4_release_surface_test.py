from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import unittest

import rtdsl
import rtdsl.v4 as v4


ROOT = Path(__file__).resolve().parents[1]


class Goal5767V4ReleaseSurfaceTest(unittest.TestCase):
    def test_public_version_and_closed_surface(self):
        self.assertEqual(rtdsl.__version__, "4.0.0rc1")
        self.assertEqual(v4.V4_API_VERSION, "4.0.0rc1")
        self.assertEqual(v4.__all__, sorted(v4.__all__))
        for forbidden in (
            "exec", "eval", "compile", "load_user_ptx", "register_provider",
            "candidate_override", "arbitrary_callback",
        ):
            self.assertNotIn(forbidden, v4.__all__)

    def test_quickstart_executes_verified_cpu_semantics(self):
        path = ROOT / "examples/current/v4_restricted_callback_quickstart.py"
        spec = importlib.util.spec_from_file_location("rtdl_v4_quickstart", path)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.run_quickstart()
        self.assertEqual(result["status"], "verified_cpu_semantics")
        self.assertEqual(result["bounds"]["lower"], (4.0, -1.0, -1.0))
        self.assertEqual(result["first_hit"], {"t": 4.0, "item_id": 3})
        self.assertFalse(result["user_source_executed_by_python"])
        self.assertFalse(result["gpu_execution_claimed"])
        self.assertRegex(result["callback_ir_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(result["callback_abi_sha256"], r"^[0-9a-f]{64}$")

    def test_documentation_topology_and_claim_boundary(self):
        required = (
            "README.md",
            "docs/v4/README.md",
            "docs/v4/tutorial.md",
            "docs/v4/api_reference.md",
            "docs/v4/security_model.md",
            "docs/v4/nine_app_coverage.md",
            "docs/v4/migration_from_v3.md",
        )
        for name in required:
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertGreater(len(text), 500, name)
            for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if "://" in link or link.startswith("#"):
                    continue
                target = ((ROOT / name).parent / link.split("#", 1)[0]).resolve()
                self.assertTrue(target.exists(), f"{name}: missing {link}")
        combined = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in required)
        for required_phrase in (
            "never imported or executed",
            "fail-closed",
            "nine Paper Apps",
            "research release candidate",
            "does not prove",
        ):
            self.assertIn(required_phrase.lower(), combined.lower())

    def test_security_document_names_each_load_bearing_boundary(self):
        text = (ROOT / "docs/v4/security_model.md").read_text(encoding="utf-8").lower()
        for token in (
            "imports", "recursion", "unbounded loops", "user ptx",
            "overflow", "nonfinite", "geometry proof", "status",
            "behavioral", "native", "not prove",
        ):
            self.assertIn(token, text)

    def test_coverage_is_nine_apps_thirteen_lanes_without_performance_claim(self):
        text = (ROOT / "docs/v4/nine_app_coverage.md").read_text(encoding="utf-8")
        for app in (
            "Particle Tracking", "RayDB", "Triangle Counting", "LibRTS",
            "RTNN", "RT-DBSCAN", "X-HD", "RayJoin", "RT-BarnesHut",
        ):
            self.assertIn(app, text)
        self.assertIn("9 applications / 13 paper lanes", text)
        self.assertNotRegex(text.lower(), r"\bv4 (?:outperforms|beats)\b")

    def test_quickstart_output_is_json_serializable(self):
        path = ROOT / "examples/current/v4_restricted_callback_quickstart.py"
        spec = importlib.util.spec_from_file_location("rtdl_v4_quickstart_json", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        json.dumps(module.run_quickstart(), sort_keys=True)


if __name__ == "__main__":
    unittest.main()
