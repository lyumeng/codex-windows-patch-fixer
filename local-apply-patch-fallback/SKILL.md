---
name: local-apply-patch-fallback
description: Local fallback for repository patching when file edits are needed but the built-in apply_patch tool is unavailable, especially on Windows environments that fail with Access is denied, codex.exe launch errors, or empty apply_patch failures. Use when Codex needs to apply Claude-style patch text in the current repository without copying helper scripts into the repo.
---

# Local Apply Patch Fallback

Use the bundled helper in this skill to apply patch text directly to the current repository when the built-in `apply_patch` path is broken.

## Workflow

1. Resolve the target root. Default to the current repository or current working directory.
2. Resolve `scripts/apply_patch_local.bat` relative to this skill directory. On non-Windows shells, call `scripts/apply_patch_helper.py` directly with Python.
3. Build a patch using the supported subset and send it on stdin.
4. Check exit code and stderr. Non-zero means the patch was not applied.
5. Verify file contents or run project tests after the patch.

## Supported Patch Subset

- `*** Begin Patch`
- `*** Add File: <path>`
- `*** Update File: <path>` with a single `@@` hunk and exact old/new lines
- `*** Delete File: <path>`
- `*** End Patch`

## PowerShell Example

```powershell
$patch = @"
*** Begin Patch
*** Add File: hello.txt
+hello
*** End Patch
"@
$patch | & 'C:\Users\admin\.codex\skills\local-apply-patch-fallback\scripts\apply_patch_local.bat' --root (Get-Location)
```

## Guardrails

- Do not treat this skill as a global replacement for the built-in developer tool. Use it as a fallback workflow.
- Do not copy the bundled scripts into the target repository unless the user explicitly asks for repo-local installation.
- The helper rejects paths that escape `--root`.
- If the patch requires unsupported features such as `Move to`, multiple hunks, or fuzzy context matching, stop using this helper and edit files another way.

## Bundled Scripts

- `scripts/apply_patch_local.bat`: Windows wrapper that invokes the Python helper.
- `scripts/apply_patch_helper.py`: Applies the supported patch subset against `--root`.

