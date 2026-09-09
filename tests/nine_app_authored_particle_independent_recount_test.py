from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/nine_app_authored_particle_independent_recount.py"


def _load():
    name = "nine_app_authored_particle_independent_recount_test_module"
    specification = importlib.util.spec_from_file_location(name, SCRIPT)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load authored Particle independent recount")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class NineAppAuthoredParticleIndependentRecountTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recount = _load()

    def test_bootstrap_is_deterministic_and_bounded(self):
        values = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
        first = self.recount.bootstrap_interval(values)
        second = self.recount.bootstrap_interval(values)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first[0], min(values))
        self.assertLessEqual(first[1], max(values))

    def test_same_float_is_exact_to_binary_roundoff_scale(self):
        self.assertTrue(self.recount._same_float(1.0, 1.0 + 1e-16))
        self.assertFalse(self.recount._same_float(1.0, 1.0 + 1e-12))

if __name__ == "__main__":
    unittest.main()
