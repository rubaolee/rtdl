"""Discovery-visible wrapper for Goal5769 authority attacks."""

try:
    from tests.goal5769_pre_pod_admission_test import *  # noqa: F401,F403
except ImportError:
    from goal5769_pre_pod_admission_test import *  # noqa: F401,F403
