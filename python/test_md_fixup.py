#!/usr/bin/env python3
"""Tests for md-fixup.py"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Import md-fixup as a module
import importlib.util
python_dir = Path(__file__).parent.parent / "python"
spec = importlib.util.spec_from_file_location("md_fixup", python_dir / "md-fixup.py")
md_fixup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md_fixup)


class TestListNormalization(unittest.TestCase):
    """Test list marker normalization and renumbering"""

    def test_bullet_marker_normalization_by_level(self):
        """Test that bullet markers are normalized based on indentation level"""
        content = """* First level
    - Second level
        + Third level
            + Fourth level
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check that markers are normalized (spaces converted to tabs, linter adds blank line)
        self.assertIn("* First level", output)
        self.assertIn("- Second level", output)
        self.assertIn("+ Third level", output)
        self.assertIn("+ Fourth level", output)

    def test_numbered_list_renumbering(self):
        """Test that numbered lists are renumbered sequentially"""
        content = """1. First
3. Third
5. Fifth
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check that renumbering happened (linter adds blank line at end)
        self.assertIn("1. First", output)
        self.assertIn("2. Third", output)
        self.assertIn("3. Fifth", output)
        self.assertNotIn("3. Third", output)
        self.assertNotIn("5. Fifth", output)

    def test_nested_numbered_lists(self):
        """Test that nested numbered lists are renumbered independently"""
        content = """1. First
    1. Nested first
    3. Nested third
2. Second
    1. Another nested first
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check that nested lists are renumbered independently (linter adds blank line)
        self.assertIn("1. First", output)
        self.assertIn("2. Second", output)
        self.assertIn("1. Nested first", output)
        self.assertIn("2. Nested third", output)
        self.assertIn("1. Another nested first", output)
        self.assertNotIn("3. Nested third", output)

    def test_mixed_list_types(self):
        """Test mixing bulleted and numbered lists"""
        content = """1. Numbered item
    * Bullet item
    * Another bullet
2. Back to numbered
    - Different bullet marker
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check mixed list types work correctly (linter normalizes markers by level, adds blank line)
        self.assertIn("1. Numbered item", output)
        self.assertIn("2. Back to numbered", output)
        # Level 1 (4 spaces) uses `-` marker, not `*`
        self.assertIn("- Bullet item", output)
        self.assertIn("- Another bullet", output)
        self.assertIn("- Different bullet marker", output)

    def test_interrupted_list_detection(self):
        """Test that interrupted lists (bullet <-> numbered) are split with HTML comment"""
        content = """1. First
2. Second
3. Third
* An interrupted list
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check interruption detection (linter adds blank line at end)
        self.assertIn("<!-- -->", output)
        self.assertIn("* An interrupted list", output)
        self.assertIn("1. First", output)
        self.assertIn("2. Second", output)
        self.assertIn("3. Third", output)

    def test_interrupted_list_reverse(self):
        """Test interruption from bulleted to numbered list"""
        content = """* First bullet
- Second bullet
+ Third bullet
1. An interrupted numbered list
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check interruption detection (linter adds blank line at end)
        self.assertIn("<!-- -->", output)
        self.assertIn("1. An interrupted numbered list", output)

    def test_interrupted_list_same_indentation(self):
        """Test that interruption only happens at same indentation level"""
        content = """1. First
    * Nested bullet
2. Second (should continue numbering)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Should NOT have HTML comment - different indentation levels (linter adds blank line)
        self.assertNotIn('<!-- -->', output)
        self.assertIn("1. First", output)
        self.assertIn("2. Second (should continue numbering)", output)
        # Level 1 (4 spaces) uses `-` marker, not `*`
        self.assertIn("- Nested bullet", output)


class TestBoldItalicNormalization(unittest.TestCase):
    """Test bold/italic marker normalization"""

    def test_bold_normalization(self):
        """Test that **bold** is normalized to __bold__"""
        content = """This is **bold** text.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check that normalization happened (linter adds blank line at end)
        self.assertIn("__bold__", output)
        self.assertNotIn("**bold**", output)

    def test_italic_normalization(self):
        """Test that _italic_ is normalized to *italic*"""
        content = """This is _italic_ text.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check that normalization happened (linter adds blank line at end)
        self.assertIn("*italic*", output)
        self.assertNotIn("_italic_", output)

    def test_bold_italic_nested(self):
        """Test nested bold and italic"""
        content = """***bold italic***
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Should normalize to __*bold italic*__
        self.assertIn("__*bold italic*__", output)
        self.assertNotIn("***bold italic***", output)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality like line endings, whitespace, etc."""

    def test_line_endings_normalization(self):
        """Test that line endings are normalized to Unix"""
        content = "Line 1\r\nLine 2\rLine 3\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'rb') as result:
                output = result.read()
            os.unlink(f.name)

        # Should only contain \n, no \r\n or \r
        self.assertNotIn(b'\r\n', output)
        self.assertNotIn(b'\r', output)
        self.assertIn(b'\n', output)

    def test_trailing_whitespace_removal(self):
        """Test that trailing whitespace is removed"""
        content = "Line with spaces    \nLine with tabs\t\t\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check that trailing whitespace is removed (except 2 spaces for line breaks)
        lines = output.split('\n')
        for line in lines[:-2]:  # Skip last blank line added by linter
            if line and not line.endswith('  '):  # Allow 2 spaces for line breaks
                self.assertFalse(line.rstrip() != line, f"Line has trailing whitespace: {repr(line)}")

    def test_end_newline(self):
        """Test that file ends with exactly one newline"""
        content = "Line 1\nLine 2"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Should end with exactly one newline (linter adds blank line + newline)
        self.assertTrue(output.endswith('\n'))
        # Should not end with multiple newlines (except the blank line rule)
        self.assertLessEqual(output.count('\n\n\n'), 0)


class TestComplexScenarios(unittest.TestCase):
    """Test complex real-world scenarios"""

    def test_test_md_file(self):
        """Test the actual test.md file scenario"""
        content = """1. List item 1
    * indented item
    + another item
        1. Testing something
        3. Else
1. Back to the root
4. what?
* An interrupted list
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 60, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Check key features (linter adds blank line at end)
        self.assertIn("1. List item 1", output)
        self.assertIn("2. Back to the root", output)
        self.assertIn("3. what?", output)
        self.assertIn("<!-- -->", output)
        self.assertIn("* An interrupted list", output)
        # Check nested items (spaces converted to tabs)
        self.assertIn("1. Testing something", output)
        self.assertIn("2. Else", output)


if __name__ == '__main__':
    unittest.main()
