import os
import unittest
from unittest import mock

import rtdsl as rt


class Goal709EmbreeThreadingContractTest(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("RTDL_EMBREE_THREADS", None)
        rt.configure_embree(threads=None)

    def test_default_thread_config_is_auto(self):
        os.environ.pop("RTDL_EMBREE_THREADS", None)
        rt.configure_embree(threads=None)
        with mock.patch("rtdsl.embree_runtime.os.cpu_count", return_value=32):
            config = rt.embree_thread_config()
        self.assertEqual(config.requested, "auto")
        self.assertEqual(config.effective_threads, 32)
        self.assertEqual(config.source, "default")
        self.assertTrue(config.auto)

    def test_env_thread_config(self):
        os.environ["RTDL_EMBREE_THREADS"] = "8"
        rt.configure_embree(threads=None)
        config = rt.embree_thread_config()
        self.assertEqual(config.requested, "8")
        self.assertEqual(config.effective_threads, 8)
        self.assertEqual(config.source, "env")
        self.assertFalse(config.auto)

    def test_api_override_wins_over_env_and_can_clear(self):
        os.environ["RTDL_EMBREE_THREADS"] = "8"
        config = rt.configure_embree(threads=4)
        self.assertEqual(config.requested, "4")
        self.assertEqual(config.effective_threads, 4)
        self.assertEqual(config.source, "api")

        cleared = rt.configure_embree(threads=None)
        self.assertEqual(cleared.requested, "8")
        self.assertEqual(cleared.source, "env")

    def test_auto_api_uses_cpu_count(self):
        with mock.patch("rtdsl.embree_runtime.os.cpu_count", return_value=16):
            config = rt.configure_embree(threads="auto")
        self.assertEqual(config.requested, "auto")
        self.assertEqual(config.effective_threads, 16)
        self.assertEqual(config.source, "api")
        self.assertTrue(config.auto)

    def test_invalid_thread_values_fail_clearly(self):
        for value in ("0", "-1", "many", 0, -2):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "positive integer or 'auto'"):
                    rt.configure_embree(threads=value)

    def test_public_api_exports_thread_config(self):
        self.assertTrue(hasattr(rt, "EmbreeThreadConfig"))
        self.assertTrue(hasattr(rt, "configure_embree"))
        self.assertTrue(hasattr(rt, "embree_thread_config"))


if __name__ == "__main__":
    unittest.main()
