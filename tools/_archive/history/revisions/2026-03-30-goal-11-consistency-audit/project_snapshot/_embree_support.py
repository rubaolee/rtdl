import rtdsl as rt


def embree_available() -> bool:
    try:
        rt.embree_version()
    except Exception:
        return False
    return True
