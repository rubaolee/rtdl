#include <fcntl.h>
#include <nvrtc.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void rtdl_goal5801_nvrtc_forbidden(const char* symbol) {
    const char* path = getenv("RTDL_GOAL5801_NVRTC_TRAP_LOG");
    if (path && path[0] != '\0') {
        const int fd = open(path, O_WRONLY | O_CREAT | O_APPEND, 0600);
        if (fd >= 0) {
            (void)write(fd, symbol, strlen(symbol));
            (void)write(fd, "\n", 1u);
            (void)close(fd);
        }
    }
    _exit(97);
}

nvrtcResult nvrtcCreateProgram(nvrtcProgram* program, const char* source,
        const char* name, int header_count, const char* const* headers,
        const char* const* include_names) {
    (void)program; (void)source; (void)name; (void)header_count;
    (void)headers; (void)include_names;
    rtdl_goal5801_nvrtc_forbidden("nvrtcCreateProgram");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

nvrtcResult nvrtcCompileProgram(nvrtcProgram program, int option_count,
        const char* const* options) {
    (void)program; (void)option_count; (void)options;
    rtdl_goal5801_nvrtc_forbidden("nvrtcCompileProgram");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

nvrtcResult nvrtcGetProgramLogSize(nvrtcProgram program, size_t* size) {
    (void)program; (void)size;
    rtdl_goal5801_nvrtc_forbidden("nvrtcGetProgramLogSize");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

nvrtcResult nvrtcGetProgramLog(nvrtcProgram program, char* log) {
    (void)program; (void)log;
    rtdl_goal5801_nvrtc_forbidden("nvrtcGetProgramLog");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

nvrtcResult nvrtcGetPTXSize(nvrtcProgram program, size_t* size) {
    (void)program; (void)size;
    rtdl_goal5801_nvrtc_forbidden("nvrtcGetPTXSize");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

nvrtcResult nvrtcGetPTX(nvrtcProgram program, char* ptx) {
    (void)program; (void)ptx;
    rtdl_goal5801_nvrtc_forbidden("nvrtcGetPTX");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

nvrtcResult nvrtcDestroyProgram(nvrtcProgram* program) {
    (void)program;
    rtdl_goal5801_nvrtc_forbidden("nvrtcDestroyProgram");
    return NVRTC_ERROR_INTERNAL_ERROR;
}

const char* nvrtcGetErrorString(nvrtcResult result) {
    (void)result;
    rtdl_goal5801_nvrtc_forbidden("nvrtcGetErrorString");
    return "forbidden";
}
