from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "librts-paper"
    / "acquire_exact_ae_archive.py"
)
SPEC = importlib.util.spec_from_file_location("librts_goal5474_acquire", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5474LibrtsResumeSafeDatasetAcquisitionTest(unittest.TestCase):
    def test_goal5479_real_archive_is_size_and_md5_verified(self):
        import json

        payload = json.loads(
            (RESULTS / "librts_goal5479_pod_download_verified.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            payload["status"], "exact_ae_archive_downloaded_and_verified__not_extracted"
        )
        self.assertEqual(payload["verification"]["size_bytes"], MODULE.ARCHIVE_SIZE_BYTES)
        self.assertEqual(payload["verification"]["md5"], MODULE.ARCHIVE_MD5)
        self.assertTrue(payload["verification"]["verified"])
        self.assertTrue(payload["claim_boundary"]["archive_verified"])
        self.assertFalse(payload["claim_boundary"]["archive_extracted"])

    def test_goal5476_pod_plan_authorizes_acquisition_not_full_execution(self):
        import json

        payload = json.loads(
            (RESULTS / "librts_goal5476_pod_acquisition_plan.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["status"], "resume_safe_acquisition_authorized")
        self.assertTrue(payload["host"]["download_authorized"])
        self.assertFalse(payload["host"]["paper_execution_host_suitable"])
        self.assertTrue(
            all(payload["host"]["acquisition_resource_checks"].values())
        )
        self.assertFalse(
            payload["host"]["paper_execution_resource_checks"]["gpu_vram"]
        )
        self.assertFalse(payload["claim_boundary"]["download_executed"])

    def test_missing_nvidia_smi_becomes_a_failed_resource_check(self):
        with mock.patch.object(MODULE.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(MODULE._gpu_identity(), ("unavailable", 0))

    def test_plan_requires_linux_disk_ram_and_tracks_execution_gpu(self):
        destination = Path("/data/librts")
        authorized = MODULE.build_plan(
            destination_dir=destination,
            platform_name="Linux",
            free_disk_bytes=80 * 1024**3,
            ram_bytes=64 * 1024**3,
            gpu_name="NVIDIA RTX 3090",
            gpu_vram_mib=24 * 1024,
        )
        blocked = MODULE.build_plan(
            destination_dir=destination,
            platform_name="Linux",
            free_disk_bytes=80 * 1024**3,
            ram_bytes=16 * 1024**3,
            gpu_name="NVIDIA GTX 1070",
            gpu_vram_mib=8 * 1024,
        )
        self.assertTrue(authorized["host"]["download_authorized"])
        self.assertTrue(authorized["host"]["paper_execution_host_suitable"])
        self.assertFalse(blocked["host"]["download_authorized"])
        self.assertFalse(blocked["claim_boundary"]["exact_inputs_acquired"])

    def test_acquisition_and_paper_execution_resource_gates_are_separate(self):
        plan = MODULE.build_plan(
            destination_dir=Path("/workspace/librts"),
            platform_name="Linux",
            free_disk_bytes=300 * 1024**3,
            ram_bytes=440 * 1024**3,
            gpu_name="NVIDIA RTX 4000 Ada Generation",
            gpu_vram_mib=20_475,
        )
        self.assertTrue(plan["host"]["download_authorized"])
        self.assertFalse(plan["host"]["paper_execution_host_suitable"])
        self.assertFalse(
            plan["host"]["paper_execution_resource_checks"]["gpu_vram"]
        )

    def test_curl_contract_resumes_into_partial_file(self):
        command = MODULE.curl_resume_command(Path("/data/archive.part"))
        self.assertIn("--continue-at", command)
        self.assertEqual(command[command.index("--continue-at") + 1], "-")
        self.assertEqual(
            command[command.index("--output") + 1], str(Path("/data/archive.part"))
        )
        self.assertEqual(command[-1], MODULE.ARCHIVE_URL)

    def test_verified_partial_is_atomically_promoted(self):
        content = b"bounded-fixture-for-resume-contract"
        expected_md5 = hashlib.md5(content, usedforsecurity=False).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial = root / "archive.tar.gz.part"
            final = root / "archive.tar.gz"
            partial.write_bytes(content)
            result = MODULE.promote_verified_partial(
                partial,
                final,
                expected_size_bytes=len(content),
                expected_md5=expected_md5,
            )
            self.assertFalse(partial.exists())
            self.assertEqual(final.read_bytes(), content)
            self.assertTrue(result["verified"])
            self.assertTrue(result["promoted_from_partial"])

    def test_size_or_md5_mismatch_fails_closed_without_promotion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial = root / "archive.tar.gz.part"
            final = root / "archive.tar.gz"
            partial.write_bytes(b"wrong")
            with self.assertRaises(ValueError):
                MODULE.promote_verified_partial(
                    partial,
                    final,
                    expected_size_bytes=5,
                    expected_md5="0" * 32,
                )
            self.assertTrue(partial.exists())
            self.assertFalse(final.exists())


if __name__ == "__main__":
    unittest.main()
