### Unreleased

### v0.1.43

2026-11-19 07:54

#### NEW

- **Link definitions** can follow the block where each link first appears
- Added changelog

#### IMPROVED

- Include changelog in GitHub releases

### v0.1.42

#### FIXED

- Failing formatting tests

### v0.1.41

#### FIXED

- Failing cargo test
- Failing Homebrew forumla update

### v0.1.39

#### CHANGED

- `--init-config` now writes `include: all` with `inline-links` and `hr-stars` skipped instead of listing every rule under `include`
- Legacy `skip: all` plus `include: [list]` config pattern remains supported alongside the new `include: all` workflow
- Rule 35 (`hr-stars`) is on by default; use `--skip hr-stars` or config `skip` to disable dash-to-star horizontal rule conversion
- `--init-config` skip list includes only `inline-links` (no longer skips `hr-stars` now that it is enabled by default)

#### NEW

- Support `include: all` in config YAML to enable every lint rule, including opt-in defaults (`inline-links`, `hr-stars`), with optional `skip: [list]` to turn specific rules off
- Add `--include` CLI flag to enable rules by number or keyword (removes them from the skip set; works with config `skip: all` to run only selected rules for one invocation)
- Rule 36 (`rewrap`): when wrap is enabled, consecutive short paragraph lines are joined and reflowed to `--width`; use `--skip rewrap` to only break lines longer than the width

#### IMPROVED

- Python config loading passes through `rules` and `include_all` so opt-in rule defaults respect `include: all`
- Blockquotes at the same `>` nesting depth rewrap together; nested quotes (`>>`) stay separate from outer quotes
- Blockquote prefix detection handles multiple `>` markers so wrap and rewrap use the correct `>` prefix on nested blockquotes
- Hard line breaks (two trailing spaces or a trailing backslash) end a rewrap segment instead of merging across the break
- List continuation lines, definition-list items, and quote-only blank lines are excluded from paragraph rewrap
- Lines containing `|` are not wrapped or rewrapped (tables and similar pipe-containing lines)

#### FIXED

- Rust config files using `skip: all` or `include: all` now load correctly (YAML `all` values were not deserializing)

### v0.1.38

#### FIXED

- Make the Rust codebase pass CI "cargo fmt --check" and "cargo clippy -- -D warnings"

### v0.1.37

#### CHANGED

- Normalize Kramdown IALs to include inner spacing (`{:.tip}` -> `{: .tip }`).

#### NEW

- Normalize Liquid tags so `{%tag%}` becomes `{% tag %}` (skips inline code spans).
- Add optional `hr-stars` rule (off by default) to convert dash-only horizontal rules (`-{3,}`) to `* * * * *` without affecting setext underlines.

#### FIXED

- Avoid misclassifying a leading `---` horizontal rule as YAML frontmatter unless there is a closing fence and YAML-looking `key:` content.
- Prevent inserting a blank line between setext headings and their dash underline when `setext-to-atx` is disabled (fixes issue [#5](https://github.com/ttscoff/md-fixup/issues/5)).
- Prevent link text containing `|` from triggering table normalization (resolves [#4](https://github.com/ttscoff/md-fixup/issues/4)).

### v0.1.36

#### FIXED

- URLs created by "before" timing regex replacements are now properly converted to links-at-end format (fixes issue [#3](https://github.com/ttscoff/md-fixup/issues/3))

### v0.1.35

#### CHANGED

- Normalize Kramdown IALs to the "{: ... }" form and avoid rewriting IAL-like text inside backticked code spans

#### NEW

- Add "liquid-tags" normalization to rewrite "{%tag%}" to "{% tag %}" (including "{%- -%}" variants) while leaving backticked code spans unchanged
- Add "compress-lists" rule to remove unnecessary blank lines between consecutive list items (bulleted and numbered)

#### IMPROVED

- Compress definition lists by removing blank lines before and between consecutive ":\\s+" items (including inside blockquotes)
- Normalize nested blockquote markers by removing spaces between leading ">" characters ("> >" -> ">>")

#### FIXED

- When compress-lists is enabled, avoid forcing extra blank lines before list items or after indented fenced code blocks inside list items

### v0.1.34

#### IMPROVED

- Convert links before wrapping so inline-to-reference conversion does not create unnecessarily short lines

#### FIXED

- Prevent wrapping reference-style link definition lines (e.g. "[1]: https://example.com") so generated definitions remain intact
- Require whitespace after list markers so emphasis like "*This" at paragraph start is not treated as a list item

### v0.1.33

#### CHANGED

- Bump Rust CLI version to 0.1.32

#### NEW

- Apply multi-line replacement patterns to the whole document (still respecting in_code_blocks/in_frontmatter and before/after timing)

#### FIXED

- Make replacements that include newlines or dotall/multiline flags match reliably instead of being silently ignored by line-by-line processing

### v0.1.32

#### CHANGED

- Bump Rust CLI version to 0.1.31

#### FIXED

- Prevent emphasis normalization from affecting underscores in filenames like _my_file_name.md by only normalizing when underscores are at word boundaries
- Rename CLI option from --replacement-file to --replacements-file to match YAML config key naming

### v0.1.31

#### CHANGED

- Bump Rust CLI version to 0.1.30

#### IMPROVED

- Keep words preceding numeric tokens together with them when wrapping so prose with versions like Markd 3. is formatted more naturally

#### FIXED

- Prevent paragraph wrapping from starting lines with number-plus-period tokens that Markdown parsers treat as ordered list items
- Preserve inline code spans when wrapping so text inside backticks is never split across lines and renders without unwanted line breaks

### v0.1.30

#### CHANGED

- Bump Rust CLI version to 0.1.29

#### IMPROVED

- Keep words preceding numeric tokens together with them when wrapping so prose with versions like Markd 3. is formatted more naturally

#### FIXED

- Prevent paragraph wrapping from starting lines with number-plus-period tokens that Markdown parsers treat as ordered list items

### v0.1.29

#### NEW

- Add YAML-driven regex replacement engine with per-pattern before/after timing and context flags for code blocks and frontmatter
- Support replacements and replacements_file options in config to control whether replacements run and where patterns are loaded from
- Add --replacements/--no-replacements and --replacement-file flags to enable or disable replacements and override the replacements file path
- Add tests for syntax highlighting
- Add YAML-driven regex replacement engine with per-pattern before/after timing and context flags for code blocks and frontmatter
- Support replacements and replacements_file options in config to control whether replacements run and where patterns are loaded from
- Add --replacements/--no-replacements and --replacement-file flags to enable or disable replacements and override the replacements file path

#### FIXED

- Wrapped list item continuation lines now use spaces to align with content after list marker instead of tab indentation
- Blank lines after lists are no longer incorrectly removed when followed by non-list content
- Wrapped list item continuation lines now use spaces to align with content after list marker instead of tab indentation
- Blank lines after lists are no longer incorrectly removed when followed by non-list content

### v0.1.28

#### FIXED

- Wrapped list item continuation lines now use spaces to align with content after list marker instead of tab indentation
- Blank lines after lists are no longer incorrectly removed when followed by non-list content

### v0.1.27

#### FIXED

- Text wrapping no longer breaks markdown links [text](url) across lines
- Reference link conversion now works correctly (links were being broken by wrapping before conversion)

### v0.1.26

#### FIXED

- Text wrapping no longer breaks markdown links [text](url) or inline code `code` across lines
- Reference link conversion now works correctly (links were being broken by wrapping before conversion)

### v0.1.25

#### FIXED

- YAML frontmatter no longer gets blank lines added inside it after the opening fence or before the closing fence

### v0.1.24

#### CHANGED

- List item continuation lines now use tab indentation instead of spaces to match list marker indent level

#### FIXED

- Creating regex inside loop
- Paragraphs containing inline code spans now wrap correctly (previously any inline code 20+ chars would skip wrapping entirely)
- List items now wrap properly (regex was failing to match lines with trailing newlines)

### v0.1.23

#### FIXED

- Homebrew formula creation
- Failing lint runs

### v0.1.22

#### FIXED

- Failing tests

### v0.1.21

#### FIXED

- Applied cargo fmt formatting changes to rust/src/main.rs to fix CI formatting check failures. All changes are formatting-only (line breaks, spacing, alignment) with no functional changes.

### v0.1.20

#### CHANGED

- Rust version now orders link definitions with text-based refs first (in document order), then numeric refs

#### NEW

- Rust version now preserves existing reference links with their original IDs (both text-based and numeric)
- Rust version now preserves implicit reference links instead of converting them
- Rust version now avoids numeric ID conflicts when assigning IDs to inline links

#### IMPROVED

- Python version now avoids numeric ID conflicts when existing reference links use numeric IDs
- Python version now preserves existing reference links and implicit links when converting to reference format

### v0.1.5

#### FIXED

- Fixed mangled VERSION constant line in rust/src/main.rs that was preventing compilation (was duplicated and merged incorrectly)
