#include "optix/rtdl_optix_prelude.h"

// Deployment-only RTDL V4 runtime.  The checked .rtdlexe product consumes the
// callback protocol implementation and the shared OptiX/CUDA primitives, but
// none of the historical monolithic workload entrypoints.  Keeping those
// unrelated exports out of this DSO makes content-addressed verification and
// dynamic loading proportional to the deployed language runtime.
namespace {
#include "optix/rtdl_optix_core.cpp"
#include "optix/rtdl_optix_v4_callback_poc.cpp"
} // anonymous namespace

#define RTDL_V4_PRODUCT_ONLY 1
#include "optix/rtdl_optix_api.cpp"
