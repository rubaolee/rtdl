#ifndef _AMXTILEINTRIN_H_INCLUDED
#define _AMXTILEINTRIN_H_INCLUDED

/*
 * Build-only compatibility shim for CUDA 12.0's host parser on GCC 12/13.
 * The author PIP sources do not use Intel AMX tile intrinsics, but Boost's
 * transitive immintrin.h include pulls them in and nvcc 12.0 cannot parse the
 * GCC builtins. Keeping this header empty removes an unused host-only surface.
 */

#endif
