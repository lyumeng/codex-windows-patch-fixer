# Codex Windows Patch Fixer

[English](#codex-windows-patch-fixer) | [中文](#中文说明)

---

## Codex Windows Patch Fixer

A minimal Codex skill to fix Windows `git apply`/`apply_patch` failures in sandboxed environments.

### Problem
On Windows, Codex's built-in `apply_patch` often fails due to:
- WindowsApps sandbox ACL errors (`Access is denied`, `CreateProcessAsUserW failed: 5`)
- `.bat` wrapper mangling multiline arguments in PowerShell
- Sandbox creating directories with incorrect ACLs for subsequent writes

### Solution
Copy `local-apply-patch-fallback/` to `~/.codex/skills/`. 

The skill runs a Python helper (`scripts/apply_patch_local.bat`) with no sandbox, reading patches from stdin and bypassing all Windows-specific launch issues.

### Requirements
- **Python 3** must be available.
- For Windows, place in `%USERPROFILE%\.codex\skills\local-apply-patch-fallback\`.


### Install
```powershell
# PowerShell
Copy-Item -Recurse local-apply-patch-fallback $env:USERPROFILE\.codex\skills\
```
Or manually copy the folder.

### Uninstall
Delete `~/.codex/skills/local-apply-patch-fallback/`.

---

<a id="中文说明"></a>

# Codex Windows 补丁修复器

一个精简的 Codex 技能，专门解决 Windows 上 `apply_patch` 在沙盒环境中的失败问题。

### 问题
Codex 在 Windows 上内置补丁工具常因以下原因失败：
- WindowsApps 沙盒 ACL 错误（`Access is denied`、`CreateProcessAsUserW failed: 5`）
- `.bat` 包装器在 PowerShell 中损坏多行参数
- 沙盒创建目录后继承 ACL 不完整，后续写入失败

### 解决方案
将 `local-apply-patch-fallback/` 文件夹复制到 `~/.codex/skills/`，然后对 Codex 说：

```
Use the local-apply-patch-fallback skill to apply this patch.
```

技能通过 Python 脚本（`scripts/apply_patch_local.bat`）以当前用户权限运行，从 stdin 读取补丁，避开 Windows 的启动限制。

### 依赖
需要系统中已安装 **Python 3**。
Windows 下目标位置：`%USERPROFILE%\.codex\skills\local-apply-patch-fallback\`。


### 安装
```powershell
# PowerShell
Copy-Item -Recurse local-apply-patch-fallback $env:USERPROFILE\.codex\skills\
```
或手动复制文件夹到~/.codex/skills/文件夹。

### 移除
删除 `~/.codex/skills/local-apply-patch-fallback/`。

---

MIT License. See [LICENSE](LICENSE).
