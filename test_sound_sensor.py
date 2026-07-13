import subprocess
import sys
import unittest
from pathlib import Path


class SoundSensorCliTests(unittest.TestCase):
    def test_help_runs_without_gpio_backend_failure(self) -> None:
        repo_root = Path(__file__).resolve().parent
        result = subprocess.run(
            [sys.executable, "sound_sensor.py", "--help"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIn("Monitor a digital sound sensor", result.stdout)


if __name__ == "__main__":
    unittest.main()
