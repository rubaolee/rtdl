# Host Enablement Report: 192.168.1.20 Embree Setup

Date: 2026-04-02
Host: `192.168.1.20`
User: `lestat`

## Purpose

This report records the work performed to make `192.168.1.20` available for RTDL Embree-based development and testing.

## Initial State

The host was reachable over the local network and accepted SSH connections, but it was not ready for RTDL/Embree work.

Verified initial properties:

- OS: Ubuntu 24.04.4 LTS
- Architecture: `x86_64`
- SSH reachable on port `22`
- Present:
  - `gcc`
  - `g++`
  - `make`
  - `python3`
  - `pkg-config`
- Missing:
  - `cmake`
  - `pip3`
  - Embree runtime/development packages

## Packages Installed

Installed with `apt`:

```sh
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  cmake python3-pip libembree-dev embree-tools git
```

Relevant installed package versions:

- `cmake` 3.28.3
- `pip3` 24.0
- `libembree-dev` 4.3.0+dfsg-2
- `libembree4-4` 4.3.0+dfsg-2
- `embree-tools` 4.3.0+dfsg-2

## Embree Verification

### Library/headers

Verified that the host now contains:

- header: `/usr/include/embree4/rtcore.h`
- library: `/usr/lib/x86_64-linux-gnu/libembree4.so`

### Important packaging note

Ubuntu's `libembree-dev` package on this host does **not** provide a working `pkg-config` entry named `embree4`. The following check failed:

```sh
pkg-config --modversion embree4
```

However, the headers and shared library are installed correctly, and direct compilation/linking works.

### Native smoke test

Compiled and ran a minimal C++ program that creates and releases an Embree device:

```cpp
#include <embree4/rtcore.h>
#include <iostream>
int main() {
  RTCDevice device = rtcNewDevice(nullptr);
  if (!device) {
    std::cerr << "rtcNewDevice failed\n";
    return 1;
  }
  rtcReleaseDevice(device);
  std::cout << "embree_smoke_ok\n";
  return 0;
}
```

Compile command used on the host:

```sh
c++ -std=c++17 -I/usr/include /tmp/embree_smoke.cpp \
  -L/usr/lib/x86_64-linux-gnu -lembree4 -o /tmp/embree_smoke
```

Observed result:

```text
embree_smoke_ok
```

This confirms that Embree is usable on the machine.

### Native repository validation program

Added a stronger native validation program in the RTDL repository:

- `apps/embree_remote_validation.cpp`

This program does more than create a device. It:

1. creates an Embree device and scene
2. allocates one triangle geometry
3. commits the geometry and scene
4. shoots a ray from `(0.25, 0.25, 1.0)` toward `-Z`
5. verifies that the ray hits the triangle at:
   - `geomID = 0`
   - `primID = 0`
   - `tfar = 1.0`
   - barycentric coordinates `u = 0.25`, `v = 0.25`

Compile command used on the host:

```sh
c++ -std=c++17 -O2 -Wall -Wextra -I/usr/include \
  apps/embree_remote_validation.cpp \
  -L/usr/lib/x86_64-linux-gnu -lembree4 \
  -o /tmp/embree_remote_validation_test
```

Observed result on `192.168.1.20`:

```text
embree_validation_ok geomID=0 primID=0 tfar=1 u=0.25 v=0.25
```

This confirms that the host can not only load Embree, but also build a scene and execute a basic intersection query successfully.

## RTDL Workspace Preparation

Prepared a working RTDL checkout on the host:

```sh
mkdir -p ~/work
cd ~/work
git clone https://github.com/rubaolee/rtdl.git rtdl_python_only
cd rtdl_python_only
git checkout main
git pull --ff-only
```

## RTDL Verification

Ran:

```sh
make build
```

Observed result:

- `make build` passed on `192.168.1.20`
- the Python-hosted RTDL plan-lowering path executed successfully

Representative build output:

```text
mkdir -p build
PYTHONPATH=src:. python3 -c "import rtdsl as rt; ... [rt.lower_to_execution_plan(...) ...]"
```

## Final Status

`192.168.1.20` is now available for RTDL Embree-based work.

Current readiness:

- network reachable: yes
- SSH accessible: yes
- compiler toolchain: yes
- `cmake`: yes
- `pip3`: yes
- Embree installed: yes
- native Embree smoke test: yes
- native Embree triangle-hit validation program: yes
- RTDL repo cloned: yes
- RTDL `make build`: yes

## Remaining Caveat

The only notable caveat found in this enablement round is:

- Ubuntu's Embree package on this machine does not expose a working `pkg-config embree4` entry

So native builds that assume:

```sh
pkg-config --cflags --libs embree4
```

may need to be adapted on this host to use explicit include/library paths unless a local pkg-config shim is added later.

## Conclusion

The host is now suitable for Embree-based RTDL development and validation work. It is not a GPU/OptiX machine, but it is ready as a Linux `x86_64` Embree development target.
