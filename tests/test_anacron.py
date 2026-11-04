import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).parents[1] / "gtock-src/usr/share/gtock/anacron.py"
SPEC = importlib.util.spec_from_file_location("gtock_anacron", MODULE)
ANACRON = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANACRON)


class AnacronParserTests(unittest.TestCase):
    def test_job(self):
        job = ANACRON.Anacron.parse_job("7 10 weekly /usr/local/bin/backup")
        self.assertEqual(job["period"], "7")
        self.assertEqual(job["delay"], 10)
        self.assertEqual(job["identifier"], "weekly")
        self.assertEqual(job["command"], "/usr/local/bin/backup")

    def test_monthly_alias(self):
        job = ANACRON.Anacron.parse_job("@monthly 15 monthly /usr/local/bin/monthly")
        self.assertEqual(job["period"], "@monthly")

    def test_comments_and_environment_are_not_jobs(self):
        self.assertIsNone(ANACRON.Anacron.parse_job("# comment"))
        self.assertIsNone(ANACRON.Anacron.parse_job("MAILTO=root"))

    def test_invalid_period_is_not_job(self):
        self.assertIsNone(ANACRON.Anacron.parse_job("0 5 invalid /bin/true"))

    def test_format_rejects_newline(self):
        with self.assertRaises(ValueError):
            ANACRON.Anacron._format_job("1", 5, "daily", "/bin/true\n/bin/false")


if __name__ == "__main__":
    unittest.main()
