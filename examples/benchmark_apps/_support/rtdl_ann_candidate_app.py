from __future__ import annotations

from examples.benchmark_apps._support._repo_bootstrap import ensure_repo_src_on_path

ensure_repo_src_on_path()

from rtdsl._example_support.rtdl_ann_candidate_app import *  # noqa: F401,F403
