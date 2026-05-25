from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.gpu_rmq import rtdl_gpu_rmq_benchmark_app as app  # noqa: E402


AUTHOR_REPO = "https://github.com/lakreis/GPU-RMQ.git"
AUTHOR_COMMIT = "86fed1c170b7e41e8ec44e461f7220f87f492893"
DEFAULT_REPO_DIR = ROOT / "scratch" / "external" / "GPU-RMQ"
DEFAULT_CSV = ROOT / "scratch" / "gpu_rmq_author_baseline.csv"
DEFAULT_AUX_DIR = ROOT / "scratch" / "gpu_rmq_author_saved_inputs"


def _run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, timeout: int = 1800) -> dict[str, Any]:
    started = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "command": command,
        "cwd": str(cwd) if cwd else None,
        "returncode": started.returncode,
        "stdout": started.stdout,
        "stderr": started.stderr,
    }


def clone_commands(repo_dir: Path) -> list[list[str]]:
    return [
        ["git", "clone", AUTHOR_REPO, str(repo_dir)],
        ["git", "-C", str(repo_dir), "checkout", AUTHOR_COMMIT],
    ]


def build_commands(repo_dir: Path, *, optix_home: str, is_long: int = 0, cg_size_log: int = 3, cg_amount_log: int = 2) -> list[list[str]]:
    return [
        [
            "cmake",
            "-S",
            str(repo_dir),
            "-B",
            str(repo_dir / "build"),
            f"-DOPTIX_HOME={optix_home}",
            f"-DIS_LONG={is_long}",
            f"-DXXX_CG_SIZE_LOG={cg_size_log}",
            f"-DXXX_CG_AMOUNT_LOG={cg_amount_log}",
        ],
        ["cmake", "--build", str(repo_dir / "build"), "-j"],
    ]


def author_run_command(
    repo_dir: Path,
    *,
    n: int,
    q: int,
    lr: int,
    alg: int,
    log_bs: int,
    reps: int,
    seed: int,
    dev: int,
    nt: int,
    csv_path: Path,
    check_mode: str,
    save_input_data: bool,
) -> list[str]:
    command = [
        str(repo_dir / "build" / "rtxrmq"),
        str(n),
        str(q),
        str(lr),
        str(alg),
        "--log_bs",
        str(log_bs),
        "--reps",
        str(reps),
        "--dev",
        str(dev),
        "--nt",
        str(nt),
        "--seed",
        str(seed),
        f"--save-time={csv_path}",
    ]
    if check_mode == "check":
        command.append("--check")
    elif check_mode == "trivial":
        command.append("--trivialCheck")
    elif check_mode == "rand":
        command.append("--randTrivialCheck")
    elif check_mode != "none":
        raise ValueError(f"unsupported check mode: {check_mode}")
    if save_input_data:
        command.append("--save-input-data")
    return command


def patch_aux_dir(repo_dir: Path, aux_dir: Path) -> dict[str, Any]:
    main_cu = repo_dir / "src" / "main.cu"
    text = main_cu.read_text(encoding="utf-8")
    old = 'std::string directory_save_aux_data = "write/your/path/here";'
    new = f'std::string directory_save_aux_data = "{str(aux_dir).rstrip("/")}/";'
    if old not in text and new not in text:
        raise RuntimeError("could not find directory_save_aux_data assignment in authors main.cu")
    if old in text:
        main_cu.write_text(text.replace(old, new), encoding="utf-8")
        changed = True
    else:
        changed = False
    aux_dir.mkdir(parents=True, exist_ok=True)
    return {"file": str(main_cu), "aux_dir": str(aux_dir), "changed": changed}


def plan_payload(args: argparse.Namespace) -> dict[str, Any]:
    repo_dir = Path(args.repo_dir)
    return {
        "goal": "goal2595_gpu_rmq_author_runner",
        "author_repo": AUTHOR_REPO,
        "author_commit": AUTHOR_COMMIT,
        "repo_dir": str(repo_dir),
        "claim_boundary": app.CLAIM_BOUNDARY,
        "clone_commands": clone_commands(repo_dir),
        "build_commands": build_commands(
            repo_dir,
            optix_home=args.optix_home,
            is_long=args.is_long,
            cg_size_log=args.cg_size_log,
            cg_amount_log=args.cg_amount_log,
        ),
        "smoke_matrix": [
            author_run_command(
                repo_dir,
                n=args.n,
                q=args.q,
                lr=lr,
                alg=alg,
                log_bs=args.log_bs,
                reps=args.reps,
                seed=args.seed,
                dev=args.dev,
                nt=args.nt,
                csv_path=Path(args.csv_path),
                check_mode=args.check_mode,
                save_input_data=args.save_input_data,
            )
            for lr in args.lr
            for alg in args.alg
        ],
        "paper_workloads": app.AUTHOR_PAPER_WORKLOADS,
        "note": "Use action run-matrix on a CUDA/OptiX pod after clone/build and optional patch-aux-dir.",
    }


def ensure_repo(repo_dir: Path, *, dry_run: bool) -> dict[str, Any]:
    if repo_dir.exists():
        return {"status": "exists", "repo_dir": str(repo_dir)}
    commands = clone_commands(repo_dir)
    if dry_run:
        return {"status": "dry_run", "commands": commands}
    results = [_run(command, timeout=1800) for command in commands]
    return {"status": "ran", "results": results}


def build_repo(args: argparse.Namespace) -> dict[str, Any]:
    repo_dir = Path(args.repo_dir)
    commands = build_commands(
        repo_dir,
        optix_home=args.optix_home,
        is_long=args.is_long,
        cg_size_log=args.cg_size_log,
        cg_amount_log=args.cg_amount_log,
    )
    if args.dry_run:
        return {"status": "dry_run", "commands": commands}
    env = os.environ.copy()
    results = [_run(command, env=env, timeout=args.timeout) for command in commands]
    return {"status": "ran", "results": results}


def run_matrix(args: argparse.Namespace) -> dict[str, Any]:
    repo_dir = Path(args.repo_dir)
    csv_path = Path(args.csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    commands = [
        author_run_command(
            repo_dir,
            n=args.n,
            q=args.q,
            lr=lr,
            alg=alg,
            log_bs=args.log_bs,
            reps=args.reps,
            seed=args.seed,
            dev=args.dev,
            nt=args.nt,
            csv_path=csv_path,
            check_mode=args.check_mode,
            save_input_data=args.save_input_data,
        )
        for lr in args.lr
        for alg in args.alg
    ]
    if args.dry_run:
        return {"status": "dry_run", "commands": commands}
    env = os.environ.copy()
    results = [_run(command, env=env, timeout=args.timeout) for command in commands]
    parsed_csv = app.author_time_csv_payload(csv_path) if csv_path.exists() else None
    return {"status": "ran", "results": results, "csv": parsed_csv}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GPU-RMQ authors-code runner packet.")
    parser.add_argument("--action", choices=("plan", "clone", "patch-aux-dir", "build", "run-matrix"), default="plan")
    parser.add_argument("--repo-dir", default=str(DEFAULT_REPO_DIR))
    parser.add_argument("--optix-home", default="${OPTIX_HOME}")
    parser.add_argument("--csv-path", default=str(DEFAULT_CSV))
    parser.add_argument("--aux-dir", default=str(DEFAULT_AUX_DIR))
    parser.add_argument("--n", type=int, default=1 << 20)
    parser.add_argument("--q", type=int, default=1 << 16)
    parser.add_argument("--lr", type=int, action="append", default=None)
    parser.add_argument("--alg", type=int, action="append", default=None)
    parser.add_argument("--log-bs", type=int, default=6)
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--seed", type=int, default=27722)
    parser.add_argument("--dev", type=int, default=0)
    parser.add_argument("--nt", type=int, default=1)
    parser.add_argument("--check-mode", choices=("none", "check", "trivial", "rand"), default="rand")
    parser.add_argument("--save-input-data", action="store_true")
    parser.add_argument("--is-long", type=int, choices=(0, 1), default=0)
    parser.add_argument("--cg-size-log", type=int, default=3)
    parser.add_argument("--cg-amount-log", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.lr is None:
        args.lr = [-3]
    if args.alg is None:
        args.alg = [2, 5, 16, 20]

    if args.action == "plan":
        payload = plan_payload(args)
    elif args.action == "clone":
        payload = ensure_repo(Path(args.repo_dir), dry_run=args.dry_run)
    elif args.action == "patch-aux-dir":
        payload = {"status": "dry_run", "repo_dir": args.repo_dir, "aux_dir": args.aux_dir} if args.dry_run else patch_aux_dir(Path(args.repo_dir), Path(args.aux_dir))
    elif args.action == "build":
        payload = build_repo(args)
    elif args.action == "run-matrix":
        if shutil.which("nvidia-smi") is None and not args.dry_run:
            payload = {"status": "blocked", "reason": "nvidia-smi not found; use a CUDA/OptiX pod or pass --dry-run"}
        else:
            payload = run_matrix(args)
    else:
        raise ValueError(args.action)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
