#include <nvrtc.h>

int main(void) {
    nvrtcProgram program = (nvrtcProgram)0;
    return (int)nvrtcCreateProgram(
        &program, "extern \"C\" __global__ void kat() {}", "kat.cu",
        0, (const char* const*)0, (const char* const*)0);
}
