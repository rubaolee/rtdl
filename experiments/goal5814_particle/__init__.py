"""Goal5814 Particle owner and separately gated measurement modules.

The import surface below remains implementation-only.  Formal measurement
modules require an external target manifest and owner execution authority;
importing this package authorizes no worker or performance claim.
"""

from .public_pyoptix_owner import (
    CONTROL_DTYPE,
    FORMAL_PARTICLE_SHAPE,
    PARTICLE_PARAM_DTYPE,
    ParticleDeviceStatusError,
    ParticleExactCoreCompletion,
    ParticleExecutionCounters,
    ParticleExecutionResult,
    ParticleOracleMismatch,
    ParticleProblemShape,
    PrevalidatedParticleExecutionInput,
    FormalPublicPyOptixParticleOwner,
    PublicPyOptixParticleOwner,
    PublicPyOptixRuntime,
    prevalidate_formal_particle_execution_input,
    prepare_formal_particle_owner,
)

__all__ = [
    "CONTROL_DTYPE",
    "FORMAL_PARTICLE_SHAPE",
    "PARTICLE_PARAM_DTYPE",
    "ParticleDeviceStatusError",
    "ParticleExactCoreCompletion",
    "ParticleExecutionCounters",
    "ParticleExecutionResult",
    "ParticleOracleMismatch",
    "ParticleProblemShape",
    "PrevalidatedParticleExecutionInput",
    "FormalPublicPyOptixParticleOwner",
    "PublicPyOptixParticleOwner",
    "PublicPyOptixRuntime",
    "prevalidate_formal_particle_execution_input",
    "prepare_formal_particle_owner",
]
