"""Public successor namespace for RTDL V4 static built-in spheres.

This separate namespace preserves the byte-frozen ``rtdsl.v4`` release
surface while exposing the complete Goal5833 lifecycle.  Compiler and native
runtime modules remain lazily imported by materialize/prepare.
"""

from .v4_public_builtin_sphere import (
    BuiltinSphereFieldIds,
    BuiltinSphereStaticInput,
    MaterializedBuiltinSphereProgram,
    MotionSegmentBatch,
    PreparedBuiltinSphereProgram,
    PublicSphereLifecycleError,
    V4SphereTarget,
    VerifiedBuiltinSphereProgram,
    VerifiedBuiltinSphereSource,
    compile_builtin_sphere_callback_program,
    first_contact_source,
    materialize_builtin_sphere_callback_program,
    verify_builtin_sphere_callback_source,
)
from .v4_sphere_physical_schema import (
    BUILTIN_SPHERE_CONTRACT,
    SpherePhysicalSchemaError,
)


__all__ = sorted([
    "BUILTIN_SPHERE_CONTRACT",
    "BuiltinSphereFieldIds",
    "BuiltinSphereStaticInput",
    "MaterializedBuiltinSphereProgram",
    "MotionSegmentBatch",
    "PreparedBuiltinSphereProgram",
    "PublicSphereLifecycleError",
    "SpherePhysicalSchemaError",
    "V4SphereTarget",
    "VerifiedBuiltinSphereProgram",
    "VerifiedBuiltinSphereSource",
    "compile_builtin_sphere_callback_program",
    "first_contact_source",
    "materialize_builtin_sphere_callback_program",
    "verify_builtin_sphere_callback_source",
])
