#!/usr/bin/env python3
"""Mechanically replace RTDL's eager compatibility exports with PEP 562 loads.

The historical package initializer contains thousands of one-line re-exports.
Importing ``rtdsl.v4`` therefore imported the entire historical system before
Python could load the narrow V4 module.  This tool preserves the exact public
aliases, ``__all__``, wrapper functions, version, and curated ``__dir__`` while
turning only the top-level re-export statements into an identity table.

The rewrite is deliberately structural and fail closed: any new top-level
statement kind must be handled explicitly before this tool may update the file.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import tempfile


def _module_name(node: ast.ImportFrom, imported_name: str) -> tuple[str, str | None]:
    prefix = "." * node.level
    if node.module is None:
        return prefix + imported_name, None
    return prefix + node.module, imported_name


def render_lazy_initializer(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    exports: dict[str, tuple[str, str | None]] = {}
    preserved: list[str] = []
    seen_version = False

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__" and node.level == 0:
                continue
            if any(alias.name == "*" for alias in node.names):
                raise RuntimeError("star imports are not safe to lazy-rewrite")
            for alias in node.names:
                public_name = alias.asname or alias.name
                exports[public_name] = _module_name(node, alias.name)
            continue
        if isinstance(node, ast.Assign):
            names = {
                target.id for target in node.targets
                if isinstance(target, ast.Name)
            }
            if names == {"__version__"}:
                seen_version = True
            elif names not in ({"__all__"}, {"_CONTRACT_FIRST_DIR_EXPORTS"}):
                raise RuntimeError(f"unhandled package assignment at line {node.lineno}: {names}")
        elif not isinstance(node, ast.FunctionDef):
            raise RuntimeError(
                f"unhandled top-level node {type(node).__name__} at line {node.lineno}")
        if node.end_lineno is None:
            raise RuntimeError(f"missing end line for node at {node.lineno}")
        preserved.append("".join(lines[node.lineno - 1:node.end_lineno]).rstrip() + "\n")

    if not seen_version or not exports:
        raise RuntimeError("initializer lacks version or re-export rows")

    rows = []
    for name, (module, attribute) in sorted(exports.items()):
        rows.append(f"    {name!r}: ({module!r}, {attribute!r}),")
    header = '''\
"""RTDL package compatibility surface with lazy historical re-exports.

The narrow ``rtdsl.v4`` package no longer imports every historical backend and
experiment module.  Existing ``from rtdsl import NAME`` callers retain the
same alias and load it on first access.
"""

from __future__ import annotations

import importlib as _importlib


'''
    lazy = "_LAZY_EXPORTS = {\n" + "\n".join(rows) + "\n}\n\n\n"
    loader = '''\
def __getattr__(name: str):
    binding = _LAZY_EXPORTS.get(name)
    if binding is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = binding
    module = _importlib.import_module(module_name, __name__)
    value = module if attribute is None else getattr(module, attribute)
    globals()[name] = value
    return value


'''
    return header + lazy + loader + "\n".join(preserved)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()
    if args.in_place == (args.output is not None):
        raise ValueError("select exactly one of --in-place or --output")
    source_path = args.input.resolve()
    rendered = render_lazy_initializer(source_path.read_text(encoding="utf-8"))
    compile(rendered, str(source_path), "exec")
    if args.in_place:
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", newline="\n", delete=False,
                dir=source_path.parent, prefix=".rtdsl-init-", suffix=".tmp") as stream:
            stream.write(rendered)
            temporary = Path(stream.name)
        temporary.replace(source_path)
    else:
        output = args.output.resolve()
        if output.exists():
            raise FileExistsError(output)
        output.write_text(rendered, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
