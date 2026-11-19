#!/usr/bin/env python3
"""Read and prepare the changelog section for one release.

`prepare` folds the current changelog into a `### vVERSION` section and
clears `### Unreleased`. `show` prints that section. The deploy topic uses
both, and the release workflow uses `show` as the GitHub release body.
"""

import re
import sys
from pathlib import Path

HEADING = re.compile(r"^###\s+\S")
VERSION_HEADING = re.compile(r"^###\s+v?(\d+\.\d+\.\d+)\s*$")
UNRELEASED_HEADING = re.compile(r"^###\s+Unreleased\s*$", re.IGNORECASE)
BULLET = re.compile(r"^\s*[-*]\s+\S")


def parse_sections(text):
    preamble = []
    sections = []
    current = None
    for line in text.splitlines():
        if HEADING.match(line):
            current = [line, []]
            sections.append(current)
            continue
        if current is None:
            preamble.append(line)
        else:
            current[1].append(line)
    return preamble, sections


def section_version(heading):
    match = VERSION_HEADING.match(heading)
    return match.group(1) if match else None


def bullets(body):
    return [line for line in body if BULLET.match(line)]


def trim_edges(lines):
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def render_section(heading, body):
    body = trim_edges(body)
    if not body:
        return heading
    return heading + "\n\n" + "\n".join(body)


def render_document(preamble, sections):
    parts = []
    preamble_text = "\n".join(trim_edges(preamble))
    if preamble_text:
        parts.append(preamble_text)
    parts.extend(render_section(heading, body) for heading, body in sections)
    return "\n\n".join(parts).rstrip() + "\n"


def choose_version_section(sections, version):
    matches = [(index, body) for index, (heading, body) in enumerate(sections) if section_version(heading) == version]
    if not matches:
        return None, []
    for index, body in matches:
        if bullets(body):
            return index, body
    return matches[0]


def show_notes(text, version):
    _, sections = parse_sections(text)
    _, body = choose_version_section(sections, version)
    if not bullets(body):
        raise SystemExit(f"No changelog entries for {version}")
    return render_section(f"### v{version}", body) + "\n"


def prepare_notes(text, version):
    preamble, sections = parse_sections(text)
    version_index, version_body = choose_version_section(sections, version)
    unreleased_indexes = [index for index, (heading, _) in enumerate(sections) if UNRELEASED_HEADING.match(heading)]
    unreleased_body = sections[unreleased_indexes[0]][1] if unreleased_indexes else []

    if not bullets(version_body) and bullets(unreleased_body):
        version_body = unreleased_body

    if not bullets(version_body):
        raise SystemExit(f"No changelog entries for {version}")

    drop = set(unreleased_indexes)
    if version_index is not None:
        drop.add(version_index)
        drop.update(index for index, (heading, _) in enumerate(sections) if section_version(heading) == version)
    rest = [section for index, section in enumerate(sections) if index not in drop]
    prepared = [
        ("### Unreleased", []),
        (f"### v{version}", trim_edges(version_body)),
        *rest,
    ]
    return render_document(preamble, prepared), render_section(f"### v{version}", version_body) + "\n"


def main(argv):
    if len(argv) < 3 or argv[1] not in {"show", "prepare"}:
        raise SystemExit("usage: release_notes.py show|prepare VERSION [CHANGELOG]")
    command = argv[1]
    version = argv[2][1:] if argv[2].startswith("v") else argv[2]
    path = Path(argv[3] if len(argv) > 3 else "CHANGELOG.md")
    text = path.read_text()
    if command == "show":
        sys.stdout.write(show_notes(text, version))
        return
    updated, _notes = prepare_notes(text, version)
    path.write_text(updated)


if __name__ == "__main__":
    main(sys.argv)
