# Codex Windows Patch Fixer

A Pi skill that provides a local fallback for applying patches in OpenAI Codex on Windows, fixing common `apply_patch` failures caused by sandbox ACL restrictions, `.bat` wrapper argument corruption, and WindowsApps permission issues.

## Problem

Codex on Windows frequently fails to apply patches due to several known issues:

| Issue | Root Cause | GitHub Issue |
|-------|-----------|--------------|
| `Access is denied` in WindowsApps install | Sandboxed worker cannot spawn `codex.exe` from `C:\Program Files\WindowsApps\...` (error 5) | [#13965](https://github.com/openai/codex/issues/13965) |
| Multiline patch strings corrupted on PowerShell | `apply_patch.bat` uses `%*` which breaks multiline arguments forwarded to `codex.exe` | [#13840](https://github.com/openai/codex/issues/13840) |
| Sandboxed directory ACL errors | Sandbox creates directories with incorrect inherited ACLs, causing subsequent patch writes to fail | [#14585](https://github.com/openai/codex/issues/14585) |
| UNC / mapped drive paths cause Access Denied | Codex normalizes mapped drive paths to UNC format inconsistently | [#12350](https://github.com/openai/codex/issues/12350) |

## Solution

This skill ships a lightweight Python-based patch helper (`apply_patch_helper.py`) with a Windows `.bat` wrapper (`apply_patch_local.bat`) that:

- **Runs as the current user** — bypasses sandbox ACL restrictions entirely
- **Reads patches from stdin** — no `%*` argument corruption on Windows
- **Uses pure Python file I/O** — no dependency on `codex.exe` or its WindowsApps install path
- **Validates paths** — prevents path traversal outside the project root

## Installation

### As a Pi Agent Skill

Copy this skill directory to your Pi skills folder:

```
Pi skills dir: ~/.pi/agent/skills/codex-windows-patch-fixer/
```

Or use the skill registration method your Pi setup supports.

### Manual Usage

The helper scripts can also be used standalone — see below.

## Usage

### With Pi Agent

Tell the agent to use this skill:

```
Use $local-apply-patch-fallback to apply this patch in the current repository.
```

### Standalone (PowerShell)

```powershell
$patch = @"
*** Begin Patch
*** Add File: hello.txt
+hello
*** End Patch
"@
$patch | .\scripts\apply_patch_local.bat --root (Get-Location)
```

### Standalone (Command Prompt)

```cmd
echo *** Begin Patch > patch.txt
echo *** Add File: hello.txt >> patch.txt
echo +hello >> patch.txt
echo *** End Patch >> patch.txt
type patch.txt | scripts\apply_patch_local.bat --root .
```

### Standalone (Linux / macOS / WSL)

```bash
echo -e '*** Begin Patch\n*** Add File: hello.txt\n+hello\n*** End Patch' | \
    python3 scripts/apply_patch_helper.py --root .
```

## Supported Patch Format

| Operation | Syntax |
|-----------|--------|
| **Add file** | `*** Add File: <path>`<br>`+content line` |
| **Update file** | `*** Update File: <path>`<br>`@@`<br>`-old line`<br>`+new line`<br>` context line` |
| **Delete file** | `*** Delete File: <path>` |

### Example: Update an existing file

```
*** Begin Patch
*** Update File: src/example.py
@@
-def hello():
-    pass
+def hello():
+    print("Hello, world!")
*** End Patch
```

> **Note:** The `-old` lines in an `Update File` block must **exactly match** the current file content (line by line). There is no fuzzy or context-based matching.

## Project Structure

```
codex-windows-patch-fixer/
├── SKILL.md                            # Pi skill definition
├── README.md                           # This file (English)
├── README_zh.md                        # Chinese README
├── LICENSE                             # MIT License
├── agents/
│   └── openai.yaml                     # Pi agent interface config
└── scripts/
    ├── apply_patch_helper.py            # Core Python patch applier
    └── apply_patch_local.bat            # Windows .bat wrapper (falls back to py)
```

## Limitations

- **No fuzzy matching** — update hunks require exact line matching
- **Single hunk only** — multiple `@@` blocks in one `Update File` are not supported
- **No `Move to`** — file rename/move operations are not supported
- **Requires Python 3** — available on virtually all Codex Windows setups

## License

MIT. See [LICENSE](LICENSE) for details.
