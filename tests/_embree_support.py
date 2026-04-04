import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import rtdsl as rt


def embree_available() -> bool:
    try:
        rt.embree_version()
    except Exception:
        return False
    return True
