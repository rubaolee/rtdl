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
