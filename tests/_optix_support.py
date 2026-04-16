import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def optix_available() -> bool:
    try:
        rt.optix_version()
    except Exception:
        return False
    return True
