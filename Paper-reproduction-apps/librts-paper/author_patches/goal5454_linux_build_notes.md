# Goal5454 Local Linux Build Adaptation

This adaptation changes build compatibility only. It does not change LibRTS
query semantics, result collection, data, or timing code.

Environment:

```text
host = lestat@192.168.1.20
GPU = NVIDIA GeForce GTX 1070
CUDA = 12.0
OptiX = /home/lestat/vendor/optix-dev
author commit = 52509e8022abeab722f5a9a89d1917e8b481defe
```

Required adaptations:

1. apply `goal5454_gtx1070_sm61.patch` with
   `git apply --unidiff-zero goal5454_gtx1070_sm61.patch` because the pinned
   repository defaults to CUDA architecture 75 while the GTX 1070 is
   architecture 61;
2. use GCC/G++ 12 as the CUDA host compiler;
3. provide gflags 2.2.2 in a user prefix and a discoverable Boost serialization
   library;
4. for Ubuntu 24.04 GCC-12 headers with CUDA 12.0, define the following header
   guards during host compilation:

```text
__AVX512FP16INTRIN_H_INCLUDED
__AVX512FP16VLINTRIN_H_INCLUDED
_AMXTILEINTRIN_H_INCLUDED
_AMXINT8INTRIN_H_INCLUDED
_AMXBF16INTRIN_H_INCLUDED
```

These flags only suppress unsupported host intrinsic headers that the tiny
example does not use. They are local-Linux compatibility evidence, not a paper
performance configuration and not an RTDL core change.
