from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts" / "rtdl_pod_env_probe.sh"
EXECUTOR = ROOT / "scripts" / "goal1267_v1_2_optix_targeted_pod_executor.sh"
MAKEFILE = ROOT / "Makefile"


class Goal1271PodEnvDiversityTest(unittest.TestCase):
    def test_probe_accepts_preconfigured_cuda_and_optix_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cuda = tmp_path / "cuda-12.8"
            nvcc = cuda / "bin" / "nvcc"
            optix = tmp_path / "optix-dev"
            output_env = tmp_path / "env.sh"
            output_json = tmp_path / "env.json"
            nvcc.parent.mkdir(parents=True)
            nvcc.write_text("#!/usr/bin/env bash\necho 'Cuda compilation tools, release 12.8'\n", encoding="utf-8")
            nvcc.chmod(nvcc.stat().st_mode | stat.S_IXUSR)
            (cuda / "lib64").mkdir()
            (optix / "include").mkdir(parents=True)
            (optix / "include" / "optix.h").write_text("// fake optix header\n", encoding="utf-8")
            env = {
                **os.environ,
                "INSTALL_DEPS": "0",
                "CUDA_PREFIX": str(cuda),
                "NVCC": str(nvcc),
                "OPTIX_PREFIX": str(optix),
                "OUTPUT_ENV": str(output_env),
                "OUTPUT_JSON": str(output_json),
            }

            subprocess.run([str(PROBE)], cwd=ROOT, env=env, check=True, text=True, stdout=subprocess.PIPE)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            env_text = output_env.read_text(encoding="utf-8")

        self.assertEqual(payload["cuda_prefix"], str(cuda))
        self.assertEqual(payload["nvcc"], str(nvcc))
        self.assertEqual(payload["optix_prefix"], str(optix))
        self.assertTrue(payload["nvcc_exists"])
        self.assertTrue(payload["optix_header_exists"])
        self.assertIn(f'export CUDA_PREFIX="{cuda}"', env_text)
        self.assertIn(f'export OPTIX_PREFIX="{optix}"', env_text)

    def test_executor_uses_probe_instead_of_fixed_pod_layout(self) -> None:
        text = EXECUTOR.read_text(encoding="utf-8")
        probe_text = PROBE.read_text(encoding="utf-8")

        self.assertIn("scripts/rtdl_pod_env_probe.sh", text)
        self.assertIn("source \"${RESULT_DIR}/rtdl_pod_env.sh\"", text)
        self.assertIn("rtdl_pod_env.json", text)
        self.assertIn("libgeos-dev", probe_text)
        self.assertIn("libembree-dev", probe_text)
        self.assertIn("cuda-nvcc-13-0", probe_text)
        self.assertIn("cuda-nvcc-12-8", probe_text)
        self.assertIn("dnf install", probe_text)
        self.assertIn("yum install", probe_text)
        self.assertNotIn("git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev", text)
        self.assertNotIn("export CUDA_PREFIX=\"${CUDA_PREFIX:-/usr/local/cuda}\"", text)

    def test_makefile_detects_versioned_cuda_prefixes(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")

        self.assertIn("CUDA_CANDIDATES", text)
        self.assertIn("/usr/local/cuda-12.8", text)
        self.assertIn("$(wildcard /usr/local/cuda-*)", text)
        self.assertIn("CUDA_PREFIX ?= $(or $(firstword $(wildcard $(CUDA_CANDIDATES))),/usr/local/cuda)", text)


if __name__ == "__main__":
    unittest.main()
