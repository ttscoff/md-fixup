#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_notes.py"
spec = importlib.util.spec_from_file_location("release_notes", SCRIPT)
release_notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_notes)


SAMPLE = """### Unreleased

#### NEW

- Handwritten note

### v0.1.42

#### FIXED

- Failing formatting tests

### v0.1.41

#### FIXED

- Failing cargo test
"""

PREPENDED = """### 0.1.43

2026-11-19 07:39

#### NEW

- **Link definitions** can follow the block where each link first appears

### Unreleased

#### NEW

- **Link definitions** can follow the block where each link first appears

### v0.1.42

#### FIXED

- Failing formatting tests
"""


class TestReleaseNotes(unittest.TestCase):
    def test_show_reads_v_prefixed_section_only(self):
        notes = release_notes.show_notes(SAMPLE, "0.1.42")
        self.assertIn("### v0.1.42", notes)
        self.assertIn("- Failing formatting tests", notes)
        self.assertNotIn("0.1.41", notes)
        self.assertNotIn("Handwritten", notes)

    def test_prepare_keeps_generated_section_and_clears_unreleased(self):
        updated, notes = release_notes.prepare_notes(PREPENDED, "0.1.43")
        self.assertTrue(updated.startswith("### Unreleased\n\n### v0.1.43\n"))
        self.assertEqual(updated.split("### v0.1.42")[0].count("Link definitions"), 1)
        self.assertIn("#### NEW", notes)
        self.assertNotIn("### Unreleased", notes)
        self.assertIn("### v0.1.42", updated)

    def test_prepare_promotes_unreleased_when_version_is_missing(self):
        updated, notes = release_notes.prepare_notes(SAMPLE, "0.1.43")
        self.assertIn("- Handwritten note", notes)
        self.assertIn("### v0.1.43", updated)
        self.assertNotIn("Handwritten note", updated.split("### v0.1.43", 1)[0])

    def test_prepare_rejects_an_empty_release(self):
        text = "### Unreleased\n\n### v0.1.42\n\n#### FIXED\n\n- Old\n"
        with self.assertRaises(SystemExit):
            release_notes.prepare_notes(text, "0.1.43")


if __name__ == "__main__":
    unittest.main()
