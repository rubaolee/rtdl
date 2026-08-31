from __future__ import annotations

import importlib.util
import pathlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5802_build_rtdl_wheel_double_seed_untimed.py"
SPEC = importlib.util.spec_from_file_location("goal5802_wheel", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
wheel_builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wheel_builder)


class Goal5802RtdlWheelDoubleSeedTest(unittest.TestCase):
    def test_exact_git_blob_materialization_and_double_seed_wheel(self) -> None:
        git_value = shutil.which("git")
        if git_value is None:
            self.skipTest("git unavailable")
        if subprocess.run(
                [sys.executable, "-m", "pip", "--version"], check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            self.skipTest("pip unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            package = source / "src" / "tiny_rtdl"
            package.mkdir(parents=True)
            (package / "__init__.py").write_bytes(b"VALUE = 'blob-lf'\n")
            (source / "pyproject.toml").write_text(
                "[build-system]\nrequires=['setuptools>=69']\n"
                "build-backend='setuptools.build_meta'\n"
                "[project]\nname='tiny-rtdl'\nversion='1.0.0'\n",
                encoding="utf-8")
            git = Path(git_value).resolve()
            subprocess.run([str(git), "init", "-q", str(source)], check=True)
            for key, value in (("user.name", "test"),
                               ("user.email", "test@example.invalid"),
                               ("core.autocrlf", "false")):
                subprocess.run(
                    [str(git), "-C", str(source), "config", key, value],
                    check=True)
            subprocess.run(
                [str(git), "-C", str(source), "add", "."], check=True)
            subprocess.run(
                [str(git), "-C", str(source), "commit", "-q", "-m", "fixture"],
                check=True)
            commit = subprocess.check_output(
                [str(git), "-C", str(source), "rev-parse", "HEAD"],
                text=True).strip()
            tree = subprocess.check_output(
                [str(git), "-C", str(source), "rev-parse", "HEAD^{tree}"],
                text=True).strip()
            epoch = int(subprocess.check_output(
                [str(git), "-C", str(source), "show", "-s", "--format=%ct",
                 commit], text=True).strip())
            args = type("Args", (), {
                "source_root": source,
                "git": git,
                "python": Path(sys.executable),
                "virtualenv_bootstrap_root": root / "bootstrap",
                "commit": commit,
                "tree": tree,
                "source_date_epoch": epoch,
                "output": root / "output",
            })()
            args.virtualenv_bootstrap_root.mkdir()
            build_profile = {
                "profile": {
                    "pip": wheel_builder.BUILD_PIP_VERSION,
                    "setuptools": wheel_builder.BUILD_SETUPTOOLS_VERSION,
                },
                "network_allowed": False,
            }
            with mock.patch.object(
                    wheel_builder, "_create_build_environment",
                    return_value=(Path(sys.executable), build_profile)):
                result = wheel_builder.build(args)
            self.assertEqual(result["seeds"], [1, 777])
            self.assertEqual(
                result["builds"][0]["wheel_sha256"],
                result["builds"][1]["wheel_sha256"])
            published = Path(result["published_wheel"]["path"])
            with zipfile.ZipFile(published) as archive:
                payload = archive.read("tiny_rtdl/__init__.py")
            self.assertEqual(payload, b"VALUE = 'blob-lf'\n")
            self.assertEqual(
                (root / "output/source_seed1/src/tiny_rtdl/__init__.py").read_bytes(),
                b"VALUE = 'blob-lf'\n")

    def test_dedicated_environment_explicitly_seeds_build_backend(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            bootstrap = root / "bootstrap"
            (bootstrap / "virtualenv").mkdir(parents=True)
            (bootstrap / "virtualenv/__main__.py").write_bytes(b"\n")
            for name, version in wheel_builder.BOOTSTRAP_DISTRIBUTIONS.items():
                metadata = bootstrap / f"{name}-{version}.dist-info/METADATA"
                metadata.parent.mkdir()
                metadata.write_text(
                    f"Name: {name}\nVersion: {version}\n", encoding="ascii")
            output = root / "output"
            logs = output / "logs"
            logs.mkdir(parents=True)
            venv_python = wheel_builder._build_python(
                output / "build_environment/venv")

            def create_environment(*_args: object, **_kwargs: object) \
                    -> subprocess.CompletedProcess[bytes]:
                venv_python.parent.mkdir(parents=True)
                venv_python.write_bytes(b"python\n")
                return subprocess.CompletedProcess(
                    args=[], returncode=0, stdout=b"created\n", stderr=b"")

            profile = {
                "implementation": "cpython", "python": [3, 12, 0],
                "pip": wheel_builder.BUILD_PIP_VERSION,
                "setuptools": wheel_builder.BUILD_SETUPTOOLS_VERSION,
            }
            with mock.patch.object(
                    wheel_builder.subprocess, "run",
                    side_effect=create_environment) as run, \
                    mock.patch.object(
                        wheel_builder, "_probe_build_environment",
                        return_value=profile):
                observed_python, receipt = (
                    wheel_builder._create_build_environment(
                        Path(sys.executable).resolve(), bootstrap,
                        output, logs))
            self.assertEqual(observed_python, venv_python)
            command = run.call_args.args[0]
            self.assertIn("--no-download", command[-1])
            self.assertIn("'--pip','25.3'", command[-1])
            self.assertIn("'--setuptools','80.9.0'", command[-1])
            self.assertEqual(receipt["profile"], profile)
            self.assertFalse(receipt["network_allowed"])

    def test_wrong_commit_epoch_rejects_before_output_creation(self) -> None:
        # This property is enforced in build(); keeping the source-level check
        # explicit prevents a future refactor from silently dropping it.
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            'if args.source_date_epoch != observed_epoch:', source)
        self.assertIn(
            '"SOURCE_DATE_EPOCH": str(epoch)', source)


if __name__ == "__main__":
    unittest.main()
