import unittest

from experiments.goal5814_particle_tracking import build_particle_rtdlexe


_REQUIRED = [
    "--native", "native.so",
    "--nvcc", "nvcc",
    "--optix-include", "optix/include",
    "--cuda-include", "cuda/include",
    "--controlling-policy", "policy.json",
    "--build-directory", "build",
    "--artifact-directory", "artifacts",
    "--manifest", "manifest.json",
]


class Goal5814ParticleTargetBuildProvenanceTest(unittest.TestCase):
    def test_default_provenance_preserves_lx1_freeze_lineage(self):
        arguments = build_particle_rtdlexe._argument_parser().parse_args(
            _REQUIRED)
        self.assertEqual(arguments.build_host, "lx1")
        self.assertEqual(
            arguments.deployment_id,
            "goal5814/lx1/particle-strict-interior/freeze-v1",
        )

    def test_target_provenance_is_explicit_and_not_lx1(self):
        arguments = build_particle_rtdlexe._argument_parser().parse_args(
            _REQUIRED + [
                "--build-host", "b7f901018414",
                "--deployment-id",
                "goal5814/rtx-a5000-cc86/particle-strict-interior/freeze-v1",
            ])
        self.assertEqual(arguments.build_host, "b7f901018414")
        self.assertEqual(
            arguments.deployment_id,
            "goal5814/rtx-a5000-cc86/particle-strict-interior/freeze-v1",
        )
        self.assertNotEqual(arguments.build_host, "lx1")


if __name__ == "__main__":
    unittest.main()
