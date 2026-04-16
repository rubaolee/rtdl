import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def vulkan_available() -> bool:
    try:
        version = rt.vulkan_version()
    except Exception:
        return False
    return bool(version)
