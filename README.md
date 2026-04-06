# Codex Windows Patch Fixer

[中文说明](#中文说明) | [English](#codex-windows-patch-fixer)

A Codex skill that provides a local fallback for applying patches on Windows, fixing common `apply_patch` failures caused by sandbox ACL restrictions, `.bat` wrapper argument corruption, and WindowsApps permission issues.

## Problem

Codex on Windows frequently fails to apply patches due to several known issues:

| Issue | Root Cause | GitHub Issue |
|-------|-----------|--------------|
| `Access is denied` in WindowsApps | Sandboxed worker cannot spawn `codex.exe` from `C:\Program Files\WindowsApps\...` (error 5) | [#13965](https://github.com/openai/codex/issues/13965) |
| Multiline patches corrupted in PowerShell | `apply_patch.bat` uses `%*` which breaks multiline argument forwarding | [#13840](https://github.com/openai/codex/issues/13840) |
| Sandboxed directory ACL errors | Incorrect inherited ACLs on newly created directories cause subsequent writes to fail | [#14585](https://github.com/openai/codex/issues/14585) |
| UNC / mapped drive Access Denied | Codex normalizes mapped drive paths to UNC format inconsistently | [#12350](https://github.com/openai/codex/issues/12350) |

## Solution

This skill ships a lightweight Python-based patch helper (`apply_patch_helper.py`) with a Windows `.bat` wrapper (`apply_patch_local.bat`) that:

- **Runs as the current user** — bypasses sandbox ACL restrictions
- **Reads patches from stdin** — no `%*` argument corruption
- **Uses pure Python file I/O** — no dependency on `codex.exe` or its WindowsApps install path
- **Validates paths** — prevents path traversal outside the project root

## Installation

Copy the `local-apply-patch-fallback/` folder into your Codex skills directory:

```
~/.codex/skills/local-apply-patch-fallback/
```

For example, in PowerShell:

```powershell
git clone https://github.com/lyumeng/codex-windows-patch-fixer.git
Copy-Item -Recurse codex-windows-patch-fixer/local-apply-patch-fallback $env:USERPROFILE\.codex\skills\
```

## Usage

### With Codex Skills

Once installed, tell Codex to use this skill when the built-in `apply_patch` fails:

```
Use the local-apply-patch-fallback skill to apply this patch.
```

### Standalone (PowerShell)

```powershell
$patch = @"
*** Begin Patch
*** Add File: hello.txt
+hello
*** End Patch
"@
$patch | .\apply_patch_local.bat --root (Get-Location)
```

### Standalone (Linux / macOS / WSL)

```bash
echo -e '*** Begin Patch\n*** Add File: hello.txt\n+hello\n*** End Patch' | \
    python3 apply_patch_helper.py --root .
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
├── LICENSE
├── README.md                       # This file
└── local-apply-patch-fallback/     # ← Copy THIS folder to ~/.codex/skills/
    ├── SKILL.md                    # Codex skill definition
    ├── agents/
    │   └── openai.yaml
    └── scripts/
        ├── apply_patch_helper.py   # Core Python patch applier
        └── apply_patch_local.bat   # Windows .bat wrapper (auto-falls back to py)
```

## Limitations

- **No fuzzy matching** — update hunks require exact line matching
- **Single hunk only** — multiple `@@` blocks in one `Update File` are not supported
- **No `Move to`** — file rename/move operations are not supported
- **Requires Python 3** — available on all systems where Codex runs

## License

MIT. See [LICENSE](LICENSE) for details.

---

<a id="中文说明"></a>

# 🇨🇳 中文说明

一个 Codex 技能（Skill），为 Windows 上的 `apply_patch` 提供本地回退方案，绕过沙盒 ACL 权限限制、`.bat` 包装器参数截断、WindowsApps 权限等问题。

## 问题背景

| 问题 | 根因 |
|------|------|
| `Access is denied` | 沙盒无法从 WindowsApps 路径启动 `codex.exe` |
| 多行补丁损坏 | `.bat` 包装器的 `%*` 截断多行参数 |
| 目录 ACL 错误 | 沙盒创建目录时 ACL 继承不完整 |
| UNC/映射盘路径失败 | 映射盘与 UNC 格式之间规范化不一致 |

## 安装

将 `local-apply-patch-fallback/` 文件夹复制到 Codex 技能目录：

```
~/.codex/skills/local-apply-patch-fallback/
```

PowerShell 示例：

```powershell
git clone https://github.com/lyumeng/codex-windows-patch-fixer.git
Copy-Item -Recurse codex-windows-patch-fixer\local-apply-patch-fallback $env:USERPROFILE\.codex\skills\
```

## 使用方法

安装后，在 `apply_patch` 失败时通过以下方式调用：

### 搭配 Codex Skills

```
Use the local-apply-patch-fallback skill to apply this patch.
```

### 独立使用（PowerShell）

```powershell
$patch = @"
*** Begin Patch
*** Add File: hello.txt
+hello
*** End Patch
"@
$patch | .\apply_patch_local.bat --root (Get-Location)
```

### 独立使用（WSL / Linux / macOS）

```bash
echo -e '*** Begin Patch\n*** Add File: hello.txt\n+hello\n*** End Patch' | \
    python3 apply_patch_helper.py --root .
```

## 支持的补丁格式

| 操作 | 语法 |
|------|------|
| **新增文件** | `*** Add File: <路径>` → `+内容行` |
| **更新文件** | `*** Update File: <路径>` → `@@` → `-旧行` / `+新行` / ` 上下文` |
| **删除文件** | `*** Delete File: <路径>` |

> **注意：** `Update File` 中的旧行必须与文件当前内容**逐行精确匹配**，不支持模糊匹配。

## 目录结构

```
local-apply-patch-fallback/           # ← 复制到 ~/.codex/skills/ 的完整内容
├── SKILL.md                          # Codex 技能定义
├── agents/
│   └── openai.yaml                   # Agent 接口配置
└── scripts/
    ├── apply_patch_helper.py         # 核心 Python 补丁应用脚本
    └── apply_patch_local.bat         # Windows .bat 包装器（自动回退到 py）
```

## 局限性

- 不支持模糊匹配（需精确行匹配）
- 不支持多个 `@@` 块（单个 hunk）
- 不支持 `Move to`（文件重命名/移动）
- 需要 Python 3

## 许可证

MIT 协议
