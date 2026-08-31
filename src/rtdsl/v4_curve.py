"""Public successor namespace for RTDL V4 round-linear built-in curves."""

from .v4_curve_physical_schema import (
    BUILTIN_CURVE_BOOLEAN_TEMPLATE,
    BUILTIN_CURVE_CONTRACT,
    BuiltinCurveBooleanPhysicalSchema,
    CurvePhysicalSchemaError,
)
from .v4_public_builtin_curve import (
    BuiltinCurveBooleanFieldIds,
    BuiltinCurveFieldIds,
    BuiltinCurveStaticInput,
    CurveBooleanSegmentBatch,
    CurveMotionSegmentBatch,
    MaterializedBuiltinCurveProgram,
    PreparedBuiltinCurveProgram,
    PublicCurveLifecycleError,
    V4CurveTarget,
    VerifiedBuiltinCurveProgram,
    VerifiedBuiltinCurveSource,
    compile_builtin_curve_callback_program,
    curve_any_contact_boolean_source,
    curve_first_contact_source,
    materialize_builtin_curve_callback_program,
    verify_builtin_curve_callback_source,
    verify_builtin_curve_boolean_callback_source,
)


__all__ = sorted([
    "BUILTIN_CURVE_BOOLEAN_TEMPLATE",
    "BUILTIN_CURVE_CONTRACT",
    "BuiltinCurveBooleanFieldIds",
    "BuiltinCurveBooleanPhysicalSchema",
    "BuiltinCurveFieldIds",
    "BuiltinCurveStaticInput",
    "CurveBooleanSegmentBatch",
    "CurveMotionSegmentBatch",
    "CurvePhysicalSchemaError",
    "MaterializedBuiltinCurveProgram",
    "PreparedBuiltinCurveProgram",
    "PublicCurveLifecycleError",
    "V4CurveTarget",
    "VerifiedBuiltinCurveProgram",
    "VerifiedBuiltinCurveSource",
    "compile_builtin_curve_callback_program",
    "curve_any_contact_boolean_source",
    "curve_first_contact_source",
    "materialize_builtin_curve_callback_program",
    "verify_builtin_curve_callback_source",
    "verify_builtin_curve_boolean_callback_source",
])
