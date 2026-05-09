import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal1589V154OptixPtxArchOverrideTest(unittest.TestCase):
    def test_ptx_arch_override_is_available_for_nvrtc_and_nvcc_paths(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_PTX_ARCH", source)
        self.assertIn('std::string("-arch=") + arch', source)
        self.assertIn('std::string("--gpu-architecture=") + arch', source)


if __name__ == "__main__":
    unittest.main()
