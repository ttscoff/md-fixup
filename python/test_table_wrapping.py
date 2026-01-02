#!/usr/bin/env python3
"""Test that tables are not broken by wrapping"""

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


class TestTableWrapping(unittest.TestCase):
    """Test that tables are not broken by text wrapping"""

    def test_table_not_wrapped(self):
        """Test that table rows are not wrapped even with narrow width"""
        content = """| Very long column header | Short | Another header |
| --- | --- | --- |
| Cell with very long content that should not wrap | Data | More data |
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            # Use narrow width to ensure wrapping would happen for regular text
            md_fixup.process_file(f.name, 20, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Table should be preserved - each row should be on a single line
        lines = output.split('\n')
        table_lines = [line for line in lines if '|' in line and line.strip()]

        # All table lines should be single lines (not wrapped)
        for line in table_lines:
            # Count pipes - should be consistent (table structure preserved)
            pipe_count = line.count('|')
            self.assertGreater(pipe_count, 0, f"Table line should contain pipes: {line}")
            # Line should not have been broken into multiple lines
            # (if it was wrapped, we'd see the content split across lines)

        # Verify the long content is still intact
        self.assertIn("Very long column header", output)
        self.assertIn("Cell with very long content that should not wrap", output)

    def test_table_with_paragraph_after(self):
        """Test that tables don't break and following paragraphs can still wrap"""
        content = """| Header 1 | Header 2 |
| --- | --- |
| Data 1 | Data 2 |

This is a very long paragraph that should be wrapped when the width is narrow enough to trigger wrapping behavior.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            md_fixup.process_file(f.name, 40, overwrite=True)
            with open(f.name, 'r') as result:
                output = result.read()
            os.unlink(f.name)

        # Table should be intact (normalization may add spacing)
        self.assertIn("Header 1", output)
        self.assertIn("Header 2", output)
        self.assertIn("Data 1", output)
        self.assertIn("Data 2", output)
        # Verify table structure is preserved (pipes present)
        table_lines = [line for line in output.split('\n') if '|' in line and line.strip()]
        self.assertGreaterEqual(len(table_lines), 3, "Should have at least header, separator, and data row")

        # Paragraph after table should be wrapped
        # (we just check it's there, wrapping is tested elsewhere)
        self.assertIn("This is a very long paragraph", output)


if __name__ == '__main__':
    unittest.main()
