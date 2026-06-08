import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE_ROOT = ROOT / "src" / "native"


def _native_sources() -> list[Path]:
    return sorted(
        path
        for path in NATIVE_ROOT.rglob("*")
        if path.suffix in {".cpp", ".cu", ".h", ".hpp"}
    )


class Goal3966NativeDirectCudaModuleLoadScanAfterCollectKTest(unittest.TestCase):
    def test_all_direct_cuda_module_loads_use_cubin_payloads(self) -> None:
        load_lines: list[tuple[Path, int, str]] = []
        bad_lines: list[tuple[Path, int, str]] = []
        for path in _native_sources():
            for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if "cuModuleLoadData" not in line:
                    continue
                load_lines.append((path, line_number, line.strip()))
                if "cubin.data()" not in line:
                    bad_lines.append((path, line_number, line.strip()))

        self.assertEqual(28, len(load_lines))
        self.assertEqual([], bad_lines)

    def test_no_direct_ptx_payload_is_loaded_by_cuda_driver(self) -> None:
        offenders: list[tuple[Path, int, str]] = []
        for path in _native_sources():
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for index, line in enumerate(lines):
                if "cuModuleLoadData" not in line:
                    continue
                block = "\n".join(lines[max(0, index - 8) : index + 2])
                if "ptx.c_str()" in block or "ptx.data()" in block:
                    offenders.append((path, index + 1, line.strip()))

        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
