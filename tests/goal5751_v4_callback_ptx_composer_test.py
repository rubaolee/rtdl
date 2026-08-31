from __future__ import annotations

import dataclasses
import unittest

from rtdsl.v4_callback_poc import DeviceFunctionArtifact
from rtdsl.v4_callback_ptx_composer import (
    CallbackPtxCompositionError,
    compose_callback_ptx,
)


def leaf(role: str, symbol: str, *, suffix: str = "") -> DeviceFunctionArtifact:
    ptx = f""".version 8.0
.target sm_61
.address_size 64
.common .global .align 8 .b8 __NumbaEnv_{role}[8];
.visible .func {symbol}() {{
    ret;
}}
{suffix}"""
    import hashlib
    return DeviceFunctionArtifact(
        schema="rtdl.v4.formal_device_function_artifact.v1",
        role=role,
        abi_name=symbol,
        compute_capability=(6, 1),
        numeric_mode="strict",
        generated_source_sha256="1" * 64,
        ir_sha256="2" * 64,
        ptx=ptx,
        ptx_sha256=hashlib.sha256(ptx.encode()).hexdigest(),
        ptx_version="8.0",
        ptx_target="sm_61",
        external_symbols=(),
        numba_version="0.65.1",
        python_version="3.12.3",
        nonce_word=1,
    )


def wrapper(symbols: list[str]) -> str:
    externs = "".join(
        f".extern .func {symbol}\n(\n);\n" for symbol in symbols
    )
    return f""".version 8.0
.target sm_61
.address_size 64
{externs}.visible .func wrapper_entry() {{
    ret;
}}
"""


class Goal5751CallbackPtxComposerTest(unittest.TestCase):
    def setUp(self):
        self.roles = ["bounds", "make_ray", "intersection", "any_hit", "closest_hit", "miss", "finalize"]
        self.symbols = {role: f"rtdl_v4_{role}_abc" for role in self.roles}
        self.leaves = [leaf(role, self.symbols[role]) for role in self.roles]

    def compose(self, **changes):
        return compose_callback_ptx(
            changes.get("wrapper", wrapper(list(self.symbols.values()))),
            changes.get("leaves", self.leaves),
            exact_symbols_by_role=changes.get("symbols", self.symbols),
        )

    def test_seven_exact_leaves_compose_deterministically(self):
        result = self.compose()
        self.assertEqual(result, self.compose())
        self.assertEqual(len(result.leaf_bindings), 7)
        self.assertEqual(len(result.stripped_wrapper_externs), 7)
        self.assertEqual(len(result.stripped_numba_environments), 7)
        for symbol in self.symbols.values():
            self.assertEqual(result.ptx.count(f".func {symbol}"), 1)
            self.assertNotIn(f".extern .func {symbol}", result.ptx)

    def test_target_or_digest_drift_fails_closed(self):
        bad_target = dataclasses.replace(
            self.leaves[0],
            ptx=self.leaves[0].ptx.replace("sm_61", "sm_89"),
        )
        import hashlib
        bad_target = dataclasses.replace(
            bad_target, ptx_sha256=hashlib.sha256(bad_target.ptx.encode()).hexdigest()
        )
        with self.assertRaises(CallbackPtxCompositionError) as target:
            self.compose(leaves=[bad_target] + self.leaves[1:])
        self.assertEqual(target.exception.code, "target_identity")
        with self.assertRaises(CallbackPtxCompositionError) as digest:
            self.compose(leaves=[dataclasses.replace(self.leaves[0], ptx_sha256="0" * 64)] + self.leaves[1:])
        self.assertEqual(digest.exception.code, "leaf_digest")

    def test_unknown_or_ambiguous_wrapper_extern_fails_closed(self):
        unknown = wrapper(list(self.symbols.values()) + ["evil"])
        with self.assertRaises(CallbackPtxCompositionError) as caught:
            self.compose(wrapper=unknown)
        self.assertEqual(caught.exception.code, "wrapper_extern_identity")
        ambiguous = wrapper(list(self.symbols.values())).replace(
            self.symbols[self.roles[0]],
            self.symbols[self.roles[0]] + self.symbols[self.roles[1]],
            1,
        )
        with self.assertRaises(CallbackPtxCompositionError):
            self.compose(wrapper=ambiguous)

    def test_duplicate_or_cross_leaf_symbol_fails_closed(self):
        with self.assertRaises(CallbackPtxCompositionError) as duplicate:
            self.compose(symbols={**self.symbols, self.roles[1]: self.symbols[self.roles[0]]})
        self.assertEqual(duplicate.exception.code, "symbol_set")
        extra = self.leaves[0].ptx + f"// {self.symbols[self.roles[1]]}\n"
        import hashlib
        cross = dataclasses.replace(
            self.leaves[0], ptx=extra, ptx_sha256=hashlib.sha256(extra.encode()).hexdigest()
        )
        with self.assertRaises(CallbackPtxCompositionError) as caught:
            self.compose(leaves=[cross] + self.leaves[1:])
        self.assertEqual(caught.exception.code, "cross_leaf_symbol")

    def test_external_or_referenced_numba_environment_fails_closed(self):
        external = leaf("bounds", self.symbols["bounds"], suffix=".extern .func evil;\n")
        with self.assertRaises(CallbackPtxCompositionError) as caught:
            self.compose(leaves=[external] + self.leaves[1:])
        self.assertEqual(caught.exception.code, "leaf_external_dependency")
        text = self.leaves[0].ptx + "// __NumbaEnv_bounds\n"
        import hashlib
        referenced = dataclasses.replace(
            self.leaves[0], ptx=text, ptx_sha256=hashlib.sha256(text.encode()).hexdigest()
        )
        with self.assertRaises(CallbackPtxCompositionError) as env:
            self.compose(leaves=[referenced] + self.leaves[1:])
        self.assertEqual(env.exception.code, "referenced_numba_environment")

    def test_missing_role_or_symbol_binding_fails_closed(self):
        with self.assertRaises(CallbackPtxCompositionError) as missing:
            self.compose(leaves=self.leaves[:-1])
        self.assertEqual(missing.exception.code, "role_set")
        stale = dataclasses.replace(self.leaves[0], abi_name="stale")
        with self.assertRaises(CallbackPtxCompositionError) as binding:
            self.compose(leaves=[stale] + self.leaves[1:])
        self.assertEqual(binding.exception.code, "artifact_symbol_binding")


if __name__ == "__main__":
    unittest.main()
