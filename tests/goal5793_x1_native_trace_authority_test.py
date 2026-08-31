from __future__ import annotations

import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/goal5793_x1_build_native_trace_authority.py"


def load_module():
    spec = importlib.util.spec_from_file_location("goal5793_x1_native_trace_authority", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NativeTraceAuthorityTest(unittest.TestCase):
    def test_parser_rejects_gpu_marker(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            trace = root / "trace.1"
            trace.write_text('execve("/usr/bin/nvidia-smi", ["nvidia-smi"], 0x0) = 0\n', encoding="utf-8")
            with self.assertRaisesRegex(module.TraceAuthorityError, "gpu_or_discovery"):
                module._parse_trace(root, root)

    def test_parser_captures_read_exec_and_trace_identity(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            trace_root = root / "trace"
            trace_root.mkdir()
            (trace_root / "trace.2").write_text(
                'execve("/opt/tool", ["tool", "--flag"], 0x0) = 0\n'
                'openat(AT_FDCWD, "/opt/header.h", O_RDONLY|O_CLOEXEC) = 3\n',
                encoding="utf-8",
            )
            first = module._parse_trace(trace_root, root)
            second = module._parse_trace(trace_root, root)
            self.assertEqual(first, second)
            self.assertEqual(first["forbidden_gpu_marker_hits"], [])
            self.assertEqual(len(first["accesses"]), 2)
            self.assertEqual(first["successful_execs"][0]["argv"], ["tool", "--flag"])

    def test_archive_is_canonical_and_deterministic(self):
        module = load_module()
        payloads = {"z": b"last", "a": b"first"}
        first = module._tar_bytes(payloads)
        second = module._tar_bytes(payloads)
        self.assertEqual(first, second)
        with tarfile.open(fileobj=io.BytesIO(first), mode="r:gz") as archive:
            self.assertEqual(archive.getnames(), ["a", "z"])
            for member in archive.getmembers():
                self.assertEqual((member.mode, member.uid, member.gid, member.mtime), (0o444, 0, 0, 0))
                self.assertEqual((member.uname, member.gname), ("", ""))

    def test_strace_string_truncation_fails_closed(self):
        module = load_module()
        with self.assertRaisesRegex(module.TraceAuthorityError, "truncated"):
            module._decode_strace_string("/usr/include/very...")


if __name__ == "__main__":
    unittest.main()
