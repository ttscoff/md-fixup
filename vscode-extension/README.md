# Markdown Fixup VS Code Extension

VS Code extension for formatting markdown files using [md-fixup](https://github.com/yourusername/md-fixup).

## Features

- **Format Document Command**: Run "Markdown Fixup: Format Document" from the command palette (Cmd+Shift+P / Ctrl+Shift+P)
- **Format on Save**: Automatically format markdown files when you save them
- **Integrated Formatter**: Works with VS Code's built-in format document command (Shift+Option+F / Shift+Alt+F)
- **Configurable**: Customize wrap width, skip rules, and executable path

## Installation

1. Install the `md-fixup` binary:
   - **Rust version** (recommended): `cargo install --path rust/` or download from releases
   - **Python version**: Make `python/md-fixup.py` executable and add to PATH

2. Install this extension:
   - Open VS Code
   - Go to Extensions (Cmd+Shift+X / Ctrl+Shift+X)
   - Search for "Markdown Fixup"
   - Click Install

## Configuration

Add these settings to your VS Code settings (`.vscode/settings.json` or User Settings):

```json
{
  "md-fixup.enable": true,
  "md-fixup.fixupOnSave": false,
  "md-fixup.path": "",
  "md-fixup.width": 60,
  "md-fixup.skipRules": []
}
```

### Settings

- **`md-fixup.enable`**: Enable/disable the extension (default: `true`)
- **`md-fixup.fixupOnSave`**: Automatically format on save (default: `false`)
- **`md-fixup.path`**: Path to md-fixup executable. Leave empty to auto-detect from PATH
- **`md-fixup.width`**: Wrap width for text formatting (default: `60`, set to `0` to disable wrapping)
- **`md-fixup.skipRules`**: Array of rules to skip (e.g., `["wrap", "end-newline"]`)

### Example: Skip wrapping but keep other rules

```json
{
  "md-fixup.width": 0,
  "md-fixup.skipRules": ["wrap"]
}
```

## Usage

### Command Palette

1. Open a markdown file
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "Markdown Fixup: Format Document"
4. Press Enter

### Format on Save

Enable format on save in your settings:

```json
{
  "md-fixup.fixupOnSave": true
}
```

### Standard Format Command

The extension also registers as a standard formatter, so you can use:
- `Shift+Option+F` (Mac) or `Shift+Alt+F` (Windows/Linux)
- Right-click → "Format Document"

## Development

To build and test the extension:

```bash
cd vscode-extension
npm install
npm run compile
```

Then press `F5` in VS Code to open a new window with the extension loaded.

## Requirements

- VS Code 1.74.0 or higher
- `md-fixup` binary installed and accessible in PATH (or set `md-fixup.path`)

## License

MIT
