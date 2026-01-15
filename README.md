[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# md-fixup

A comprehensive markdown linter and formatter that normalizes formatting and wraps text. Available in both Python and Rust implementations.

## Features

md-fixup performs 33 different normalization and formatting rules:

1. Normalizes line endings to Unix
2. Trims trailing whitespace (preserves exactly 2 spaces for line breaks)
3. Collapses multiple blank lines (max 1 consecutive, except in code blocks) and compresses definition lists (`:\s+`)
4. Normalizes headline spacing (exactly 1 space after #)
5. Ensures blank line after headline
6. Ensures blank line before code block
7. Ensures blank line after code block
8. Ensures blank line before list
9. Ensures blank line after list
10. Ensures blank line before horizontal rule
11. Ensures blank line after horizontal rule
12. Converts list indentation spaces to tabs consistently
13. Normalizes list marker spacing
14. Wraps text at specified width (preserving links, code spans, fenced blocks)
15. Ensures exactly one blank line at end of file
16. Normalizes IAL (Inline Attribute List) spacing for both Kramdown and Pandoc styles
17. Normalizes fenced code block language identifier spacing
18. Normalizes reference-style link definition spacing
19. Normalizes task list checkbox (lowercase x)
20. Normalizes blockquote spacing
21. Normalizes display math block spacing (handles multi-line, preserves currency)
22. Normalizes table formatting (aligns columns, handles relaxed and headerless tables)
23. Normalizes emoji names (spellcheck and correct typos using fuzzy matching)
24. Normalizes typography (curly quotes to straight, en/em dashes, ellipses, guillemets)
25. Normalizes bold/italic markers (bold: always __, italic: always *). Intra-word underscores (e.g., in filenames like `_my_file_name.md`) are preserved and not converted to emphasis markers.
26. Normalizes list markers (renumber ordered lists, standardize bullet markers by level)
27. Resets ordered lists to start at 1 (if disabled, preserves starting number)
28. Converts links to numeric reference links
29. Places link definitions at the end of the document
30. Converts links to inline format (overrides numeric reference links)
31. Normalizes Liquid tag spacing (`{%tag%}` -> `{% tag %}`)
32. Normalizes blockquote marker chains (removes spaces between leading `>` markers, e.g. `> >` -> `>>`)
33. Compresses list spacing by removing unnecessary blank lines between list items (bulleted and numbered)

**Definition lists:** md-fixup compresses definition lists by removing blank lines before and between consecutive definition items (`:\s+`). This also works inside blockquotes (removing quote-only blank lines like `>` between definition items). This behavior is part of rule `3` (`blank-lines`).


Table cleanup algorithm by [Dr. Drang](https://leancrew.com/).

## Installation

### Homebrew

Install using Homebrew:

```bash
brew tap ttscoff/thelab
brew install md-fixup
```

### Python Version (legacy)

The Python version requires Python 3 and has no external dependencies (uses only standard library).

**Note:** The Python implementation is frozen at version `0.1.28` and will not receive new features going forward. There is no longer full feature parity between the Python script and the Rust/binary version, and the rest of this README and all option/feature documentation describe the Rust version only. The Python script remains available for existing workflows that depend on it, but new projects should prefer the Rust binary.

```bash
# Make the script executable
chmod +x python/md-fixup.py

# Optionally, create a symlink or add to PATH
ln -s $(pwd)/python/md-fixup.py /usr/local/bin/md-fixup
```

### Rust Version

The Rust version compiles to a single binary with no runtime dependencies.

```bash
cd rust
cargo build --release
```

The binary will be at `target/release/md-fixup`. You can install it system-wide:

```bash
# Install using cargo
cargo install --path rust/

# Or manually copy the binary
cp rust/target/release/md-fixup /usr/local/bin/md-fixup
```

## Usage

The Rust binary is the primary implementation, and the options and examples in this section describe the Rust version. The legacy Python script shares most of the same flags but may not support newer features added after `0.1.28`.

```bash
# Process a file (outputs to stdout)
md-fixup file.md

# Overwrite files in place
md-fixup --overwrite file.md

# Set wrap width
md-fixup --width 80 file.md

# Process multiple files
md-fixup --width 72 file1.md file2.md *.md

# Skip specific rules (by number or keyword)
md-fixup --skip 2,3 file.md
md-fixup --skip wrap,end-newline file.md

# Process all .md files in current directory (if no files specified)
md-fixup

# Read file paths from stdin
find . -name "*.md" | md-fixup --width 100
```

### Available Rules

Rules can be skipped using either their number or keyword:

- `1` / `line-endings` - Normalize line endings to Unix
- `2` / `trailing` - Trim trailing whitespace
- `3` / `blank-lines` - Collapse multiple blank lines (also compresses definition lists, `:\s+`)
- `4` / `header-spacing` - Normalize headline spacing
- `5` / `header-newline` - Ensure blank line after headline
- `6` / `code-before` - Ensure blank line before code block
- `7` / `code-after` - Ensure blank line after code block
- `8` / `list-before` - Ensure blank line before list
- `9` / `list-after` - Ensure blank line after list
- `10` / `rule-before` - Ensure blank line before horizontal rule
- `11` / `rule-after` - Ensure blank line after horizontal rule
- `12` / `list-tabs` - Convert list indentation spaces to tabs
- `13` / `list-marker` - Normalize list marker spacing
- `14` / `wrap` - Wrap text at specified width
- `15` / `end-newline` - Ensure exactly one blank line at end of file
- `16` / `ial-spacing` - Normalize IAL spacing
- `17` / `code-lang-spacing` - Normalize fenced code block language identifier spacing
- `18` / `ref-link-spacing` - Normalize reference-style link definition spacing
- `19` / `task-checkbox` - Normalize task list checkbox
- `20` / `blockquote-spacing` - Normalize blockquote spacing
- `21` / `math-spacing` - Normalize display math block spacing (including surrounding newlines)
- `22` / `table-format` - Normalize table formatting
- `23` / `emoji-spellcheck` - Normalize emoji names
- `24` / `typography` - Normalize typography (sub-keywords: `em-dash`, `guillemet`)
- `25` / `bold-italic` - Normalize bold/italic markers (preserves intra-word underscores in filenames like `_my_file_name.md`)
- `26` / `list-markers` - Normalize list markers (renumber ordered lists, standardize bullet markers by level)
- `27` / `list-reset` - Reset ordered lists to start at 1 (if disabled, preserves starting number)
- `28` / `reference-links` - Convert links to numeric reference links
- `29` / `links-at-end` - Place link definitions at the end of the document (if skipped and reference-links enabled, places at beginning)
- `30` / `inline-links` - Convert links to inline format (overrides reference-links if enabled)
- `31` / `liquid-tags` - Normalize Liquid tag spacing
- `32` / `blockquote-markers` - Normalize blockquote marker chains (remove spaces between `>` markers)
- `33` / `compress-lists` - Compress list spacing by removing unnecessary blank lines between list items

Group keywords (expand to multiple rules):

- `code-block-newlines` - Skip all code block newline rules (equivalent to skipping `6` and `7`)
- `display-math-newlines` - Skip display math newline handling (equivalent to skipping `21`)

## Configuration File

You can create a configuration file to set default options. The config file is located at:
- `$XDG_CONFIG_HOME/md-fixup/config.yml` (or `config.yaml`)
- `~/.config/md-fixup/config.yml` (fallback if `XDG_CONFIG_HOME` is not set)

### Initializing the Config File

To create an initial config file with all rules enabled by name, use:

```bash
md-fixup --init-config
```

This creates `~/.config/md-fixup/config.yml` with all rules listed, making it easy to edit and disable specific rules.

**Note:** If no config file exists and you run `md-fixup` interactively (from a terminal), it will automatically create the initial config file for you. This only happens when running interactively to avoid creating files during background/automated runs.

The configuration file is a YAML file with the following structure:

```yaml
width: 60
overwrite: false
rules:
  skip: all
  include:
    - line-endings
    - blank-lines
```

Or to skip specific rules:

```yaml
width: 80
overwrite: true
rules:
  skip:
    - line-endings
    - blank-lines
    - wrap
```

**Configuration merging:**
- Command-line arguments always override config file settings
- Rules specified in `--skip` are merged with config file rules (CLI takes precedence)
- The `skip: all` pattern starts with all rules disabled, then includes only the specified rules
- Group keywords (`code-block-newlines`, `display-math-newlines`) work in config files

### Custom regex replacements

md-fixup can also run user-defined regex search/replace patterns as part of a fixup pass. Patterns are defined in a YAML file and can be scoped to run before or after the built-in rules, and optionally inside code blocks or YAML frontmatter.

Replacements are enabled by default if a replacements file exists in one of these locations (in order of precedence):

- `.md-fixup-replacements` in the current directory
- The path set in `replacements_file:` in the config file
- `~/.config/md-fixup/replacements.yml` (or `$XDG_CONFIG_HOME/md-fixup/replacements.yml`)

You can control replacements via the config file:

```yaml
width: 80
overwrite: true
replacements: true                 # enable/disable replacements (default: true if a file exists)
replacements_file: ~/my-replacements.yml
rules:
  skip:
    - wrap
```

The replacements file itself is also YAML, with this structure:

```yaml
replacements:
  - name: "fix-double-spaces"
    pattern: "  +"
    replacement: " "
    # Optional fields (defaults shown):
    timing: after          # "before" or "after" built-in rules
    in_code_blocks: false
    in_frontmatter: false

  - name: "swap-version"
    pattern: '(\\d+)\\.(\\d+)'
    replacement: '$2.$1'
    timing: before
```

Each replacement:

- **name**: Human-readable identifier for logging and debugging
- **pattern**: A Rust `regex` pattern (supports capture groups)
- **replacement**: The replacement string (supports `$1`, `$2`, etc. for capture groups)
- **timing**: When to run the replacement (`before` or `after` the built-in rules)
- **in_code_blocks**: If `true`, pattern is allowed to run inside fenced code blocks
- **in_frontmatter**: If `true`, pattern is allowed to run inside YAML frontmatter

**YAML quoting and escaping tips:**
- Prefer **single quotes** for `pattern:` when your regex includes backslashes (common with `\[` `\]` `\d` `\s`, etc.). Single-quoted YAML strings do not treat backslashes as escapes, so the regex reaches the engine unchanged.
- If you use **double quotes** for `pattern:`, you often need to **double-escape backslashes** (e.g. write `\\d+` instead of `\d+`) because YAML will interpret backslashes inside double-quoted strings.
- In **double-quoted YAML strings**, some sequences like `\|` are not valid YAML escapes and can cause parse errors. Either remove the backslash (often you do not need it) or use single quotes.

Example (BBCode-style tags, multi-line, and anchors):

```yaml
replacements:
  - name: "subhead"
    pattern: '(?m)^\[b\](.*?)\[/b\]'
    replacement: '## $1'
    timing: before

  - name: "quote"
    pattern: '(?s)\[quote\]\n(.*?)\[/quote\]'
    replacement: '> $1'
    timing: before
```

Multi-line patterns are supported. If your `pattern` includes `\n` or uses inline flags like `(?s)`/`(?m)`, it will be applied to the whole document (still respecting `in_code_blocks` and `in_frontmatter`). If you use `^`/`$` and want them to match line starts/ends within the document, include `(?m)` in the pattern.

You can override config and defaults on the command line:

- `--replacements` / `--no-replacements` – force-enable or disable replacements
- `--replacements-file FILE` – use a specific replacements YAML file for this run

## Examples

```bash
# Format a single file in place
md-fixup --overwrite README.md

# Format with custom width, skipping wrapping
md-fixup --width 100 --skip wrap file.md

# Format multiple files, preserving em dashes
md-fixup --skip typography,em-dash *.md

# Process all markdown files in a project
find . -name "*.md" -not -path "./.git/*" | md-fixup --overwrite

# Run with a specific replacements file
md-fixup --replacements-file ./replacements.yml --overwrite file.md
```

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
