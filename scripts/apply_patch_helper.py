from __future__ import annotations

import argparse
import sys
from pathlib import Path


class PatchError(Exception):
    pass


PREFIX_ADD = '*** Add File: '
PREFIX_DELETE = '*** Delete File: '
PREFIX_UPDATE = '*** Update File: '


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    return parser.parse_args()


def resolve_path(root: Path, relative_path: str) -> Path:
    target = (root / relative_path).resolve()
    root_resolved = root.resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise PatchError(f'Path outside root: {relative_path}') from exc
    return target


def write_added_file(target: Path, content: list[str]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(''.join(f'{line}\n' for line in content), encoding='utf-8')


def apply_add_file(root: Path, lines: list[str], index: int) -> int:
    path_text = lines[index][len(PREFIX_ADD):]
    content: list[str] = []
    index += 1
    while index < len(lines) and not lines[index].startswith('*** '):
        line = lines[index]
        if not line.startswith('+'):
            raise PatchError(f'Unexpected line in add file block: {line}')
        content.append(line[1:])
        index += 1
    write_added_file(resolve_path(root, path_text), content)
    return index


def apply_delete_file(root: Path, lines: list[str], index: int) -> int:
    target = resolve_path(root, lines[index][len(PREFIX_DELETE):])
    if target.exists():
        target.unlink()
    return index + 1


def apply_update_file(root: Path, lines: list[str], index: int) -> int:
    target = resolve_path(root, lines[index][len(PREFIX_UPDATE):])
    if not target.exists():
        raise PatchError(f'File not found for update: {target.name}')
    index += 1
    if index >= len(lines) or lines[index] != '@@':
        raise PatchError('Expected @@ after update header')
    index += 1
    old_lines: list[str] = []
    new_lines: list[str] = []
    while index < len(lines) and not lines[index].startswith('*** '):
        line = lines[index]
        if line.startswith('-'):
            old_lines.append(line[1:])
        elif line.startswith('+'):
            new_lines.append(line[1:])
        elif line.startswith(' '):
            old_lines.append(line[1:])
            new_lines.append(line[1:])
        else:
            raise PatchError(f'Unexpected line in update block: {line}')
        index += 1
    current = target.read_text(encoding='utf-8').splitlines()
    if current != old_lines:
        raise PatchError(f'Update hunk does not match file: {target.name}')
    target.write_text(''.join(f'{line}\n' for line in new_lines), encoding='utf-8')
    return index


def apply_patch_text(root: Path, patch_text: str) -> None:
    lines = patch_text.splitlines()
    if not lines or lines[0] != '*** Begin Patch':
        raise PatchError('Missing *** Begin Patch marker')
    if lines[-1] != '*** End Patch':
        raise PatchError('Missing *** End Patch marker')

    index = 1
    while index < len(lines) - 1:
        line = lines[index]
        if line.startswith(PREFIX_ADD):
            index = apply_add_file(root, lines, index)
            continue
        if line.startswith(PREFIX_DELETE):
            index = apply_delete_file(root, lines, index)
            continue
        if line.startswith(PREFIX_UPDATE):
            index = apply_update_file(root, lines, index)
            continue
        raise PatchError(f'Unsupported patch operation: {line}')


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    patch_text = sys.stdin.read()
    try:
        apply_patch_text(root, patch_text)
    except PatchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
