# md-fixup (Rust)

Rust implementation of the markdown linter/formatter. This version compiles to a single binary with no runtime dependencies.

## Building

```bash
cd rust
cargo build --release
```

The binary will be at `target/release/md-fixup`.

## Installation

You can install it system-wide with:

```bash
cargo install --path .
```

Or copy the binary from `target/release/md-fixup` to a directory in your PATH.

## Usage

Same as the Python version:

```bash
# Process a file (outputs to stdout)
./target/release/md-fixup file.md

# Overwrite files in place
./target/release/md-fixup --overwrite file.md

# Process multiple files
./target/release/md-fixup --width 80 file1.md file2.md

# Skip specific rules
./target/release/md-fixup --skip 2,3 file.md
./target/release/md-fixup --skip wrap,end-newline file.md
```

## Differences from Python Version

- Compiles to a single binary (no Python interpreter needed)
- Faster execution
- Same functionality and behavior
- All 25 linting rules are implemented

## Development

```bash
# Check for compilation errors
cargo check

# Run tests (if any are added)
cargo test

# Build optimized release binary
cargo build --release
```
