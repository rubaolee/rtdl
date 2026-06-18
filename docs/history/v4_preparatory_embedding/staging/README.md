# V4 Preparatory C ABI Staging Inputs

This directory holds archived C ABI staging inputs that are not part of the
V3.0 public release surface.

## Contents

- [include/rtdl/rtdl.h](include/rtdl/rtdl.h): draft C ABI header.
- [packaging/rtdl-c-api.pc](packaging/rtdl-c-api.pc): pkg-config metadata for
  review-only staged bundles.
- [packaging/rtdl-c-api-config.cmake](packaging/rtdl-c-api-config.cmake):
  CMake metadata for review-only staged bundles.

## Boundary

These files remain useful for V4 planning and regression checks, but they do
not make V3.0 an embedding release, SDK release, package-install release,
stable C ABI release, generated-binding release, public true-zero-copy release,
or device-buffer execution release.
