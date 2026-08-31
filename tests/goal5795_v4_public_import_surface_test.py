from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal5795PublicImportSurfaceTest(unittest.TestCase):
    def test_public_import_and_compile_do_not_open_native_or_start_compiler(self):
        code = textwrap.dedent("""
            import ctypes
            import subprocess
            import sys
            import rtdsl

            baseline = set(sys.modules)

            def forbidden(*args, **kwargs):
                raise AssertionError('GPU/native/compiler action during public import or compile')

            ctypes.CDLL = forbidden
            subprocess.Popen = forbidden
            import rtdsl.v4 as v4

            required = {
                'AnyHitProofAuthority', 'AnyHitProtocolProof',
                'BoundedRelationBatch', 'BoundedRelationProtocol',
                'BoundedRelationStaticInput', 'CallbackProgramSpec',
                'MaterializedProtocolProgram', 'PreparedProtocolProgram',
                'ProtocolExecutionResult', 'ProtocolLifecycleError',
                'ProtocolPhysicalPlan',
                'TriangleReductionBatch', 'TriangleReductionMode',
                'TriangleReductionProtocol', 'TriangleReductionStaticInput',
                'V4Target', 'V4Toolchain', 'VerifiedProtocolProgram',
                'compile_protocol_program', 'materialize_protocol_program',
                'standard_protocol_physical_plan',
            }
            missing = sorted(required - set(v4.__all__))
            if missing:
                raise SystemExit('missing exports: ' + repr(missing))
            bounded = v4.BoundedRelationProtocol(8)
            triangle = v4.TriangleReductionProtocol()
            bounded_plan = v4.standard_protocol_physical_plan(bounded)
            triangle_plan = v4.standard_protocol_physical_plan(triangle)
            bounded_proof = v4.AnyHitProtocolProof(
                bounded_plan.callback_ir_sha256,
                bounded_plan.effect_digest,
                '0' * 64,
                'external_machine_checked_order_independence_v1')
            triangle_proof = v4.AnyHitProtocolProof(
                triangle_plan.callback_ir_sha256,
                triangle_plan.effect_digest,
                '1' * 64,
                'external_machine_checked_order_independence_v1')
            v4.compile_protocol_program(
                bounded,
                physical_plan=bounded_plan,
                any_hit_proof=bounded_proof)
            v4.compile_protocol_program(
                triangle,
                physical_plan=triangle_plan,
                any_hit_proof=triangle_proof)
            newly_forbidden = sorted(name for name in set(sys.modules) - baseline if
                name == 'cupy' or name.startswith('cupy.') or
                'optix_compiler' in name or 'prepared_runtime' in name or
                name == 'rtdsl.v4_callback_numba_codegen')
            if newly_forbidden:
                raise SystemExit('new backend imports: ' + repr(newly_forbidden))
        """)
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join((
            str(ROOT / "src"), str(ROOT)))
        completed = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT, env=environment,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(
            completed.returncode, 0,
            completed.stdout + completed.stderr,
        )

    def test_public_module_does_not_export_raw_backend_escape_objects(self):
        from rtdsl import v4

        forbidden = {
            "_load_optix_library",
            "VerifiedBoundedRelationExecutable",
            "VerifiedTriangleReductionExecutable",
            "prepare_bounded_relation_callback",
            "prepare_triangle_reduction_callback",
            "open_v4_callback_provider",
        }
        self.assertTrue(forbidden.isdisjoint(v4.__all__))


if __name__ == "__main__":
    unittest.main()
