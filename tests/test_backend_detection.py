import importlib.util
import pathlib
import unittest
from unittest import mock

MODULE = pathlib.Path(__file__).parents[1] / "gtock-src/usr/share/gtock/config.py"
SPEC = importlib.util.spec_from_file_location("gtock_config", MODULE)
CONFIG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONFIG)


class CronBackendDetectionTests(unittest.TestCase):
    def setUp(self):
        CONFIG.cron_backend = None
        self.env = mock.patch.dict("os.environ", {}, clear=False)
        self.env.start()
        import os
        os.environ.pop("GTOCK_CRON_BACKEND", None)

    def tearDown(self):
        self.env.stop()
        CONFIG.cron_backend = None

    def test_explicit_override_wins(self):
        with mock.patch.dict("os.environ", {"GTOCK_CRON_BACKEND": "busybox"}), \
             mock.patch.object(CONFIG, "_running_cron_backends", return_value={"cronie"}), \
             mock.patch.object(CONFIG, "_installed_cron_backends", return_value={"fcron"}):
            self.assertEqual(CONFIG.getCronBackend(), "busybox")

    def test_running_and_installed_candidates_follow_priority(self):
        with mock.patch.object(CONFIG, "_running_cron_backends", return_value={"fcron", "busybox"}), \
             mock.patch.object(CONFIG, "_installed_cron_backends", return_value={"cronie", "dcron"}):
            self.assertEqual(CONFIG.getCronBackend(), "cronie")

    def test_fcron_precedes_dcron_and_busybox(self):
        with mock.patch.object(CONFIG, "_running_cron_backends", return_value=set()), \
             mock.patch.object(CONFIG, "_installed_cron_backends", return_value={"fcron", "dcron", "busybox"}):
            self.assertEqual(CONFIG.getCronBackend(), "fcron")

    def test_dcron_precedes_busybox(self):
        with mock.patch.object(CONFIG, "_running_cron_backends", return_value=set()), \
             mock.patch.object(CONFIG, "_installed_cron_backends", return_value={"dcron", "busybox"}):
            self.assertEqual(CONFIG.getCronBackend(), "dcron")

    def test_busybox_fallback(self):
        with mock.patch.object(CONFIG, "_running_cron_backends", return_value=set()), \
             mock.patch.object(CONFIG, "_installed_cron_backends", return_value={"busybox"}):
            self.assertEqual(CONFIG.getCronBackend(), "busybox")

    def test_resource_paths_are_relative_to_installed_module(self):
        import os
        self.assertEqual(CONFIG.gs_dir, os.path.dirname(os.path.realpath(MODULE)))
        self.assertEqual(CONFIG.image_dir, os.path.join(CONFIG.gs_dir, "pixmaps"))
        self.assertEqual(CONFIG.glade_dir, os.path.join(CONFIG.gs_dir, "assets"))
        self.assertTrue(CONFIG.xwrapper_exec.endswith("xwrapper.py"))

    def test_unknown_package_names_do_not_match_cron_substring(self):
        with mock.patch.object(CONFIG.shutil, "which", return_value="/usr/bin/dpkg-query"), \
             mock.patch.object(CONFIG.subprocess, "run", return_value=mock.Mock(stdout="dcron: /usr/bin/crontab", stderr="")):
            self.assertEqual(CONFIG._package_owner("/usr/bin/crontab"), "dcron")


if __name__ == "__main__":
    unittest.main()
