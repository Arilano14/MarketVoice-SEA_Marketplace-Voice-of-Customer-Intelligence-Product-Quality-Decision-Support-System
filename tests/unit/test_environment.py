"""
Environment Smoke Tests.
Validates path resolution, config loading, and directory structure using Python unittest.
"""

import sys
import unittest
from pathlib import Path

# Ensure src/ is in sys.path for direct module import without editable install
SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from marketvoice.utils.config import get_project_root, load_project_settings


class TestEnvironmentSmoke(unittest.TestCase):

    def test_project_root_exists(self):
        root = get_project_root()
        self.assertTrue(root.exists())
        self.assertTrue((root / "pyproject.toml").exists())
        self.assertTrue((root / "README.md").exists())

    def test_load_project_settings(self):
        settings = load_project_settings()
        self.assertIsInstance(settings, dict)
        self.assertIn("project", settings)
        self.assertEqual(settings["project"]["name"], "MarketVoice SEA")

    def test_directory_structure_exists(self):
        root = get_project_root()
        expected_subdirs = [
            "config",
            "data/raw",
            "data/interim",
            "data/processed",
            "data/metadata",
            "docs/governance",
            "docs/requirements",
            "docs/engineering",
            "src/marketvoice",
            "tests",
            "reports/validation",
        ]
        for d in expected_subdirs:
            subdir = root / d
            self.assertTrue(subdir.exists(), f"Missing required directory: {d}")
            self.assertTrue(subdir.is_dir())


if __name__ == "__main__":
    unittest.main()
