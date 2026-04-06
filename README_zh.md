# Codex Windows 补丁修复器

一个 Pi 技能（Skill），为 OpenAI Codex 在 Windows 上提供本地补丁应用回退方案，解决常见的 `apply_patch` 失败问题（沙盒 ACL 权限限制、`.bat` 包装器参数截断、WindowsApps 权限问题等）。

## 问题背景

Codex 在 Windows 上频繁出现补丁应用失败，主要原因如下：

| 问题 | 根因 | GitHub Issue |
|------|------|-------------|
| `Access is denied`（WindowsApps 安装路径） | 沙盒工作进程无法从 `C:\Program Files\WindowsApps\...` 启动 `codex.exe`（系统错误 5） | [#13965](https://github.com/openai/codex/issues/13965) |
| PowerShell 多行补丁字符串损坏 | `apply_patch.bat` 使用 `%*` 转发参数，破坏多行内容 | [#13840](https://github.com/openai/codex/issues/13840) |
| 沙盒目录 ACL 错误 | 沙盒创建新目录时 ACL 继承不完整，导致后续写入失败 | [#14585](https://github.com/openai/codex/issues/14585) |
| UNC / 映射盘路径导致拒绝访问 | Codex 在映射盘和 UNC 路径之间规范化不一致 | [#12350](https://github.com/openai/codex/issues/12350) |

## 解决方案

本技能提供了一个轻量级 Python 补丁应用工具（`apply_patch_helper.py`）和 Windows `.bat` 包装器（`apply_patch_local.bat`），可以：

- **以当前用户身份运行** — 完全绕过沙盒 ACL 限制
- **通过 stdin 读取补丁** — 避免 Windows 下 `%*` 参数截断问题
- **纯 Python 文件 I/O** — 不依赖 `codex.exe` 及其 WindowsApps 安装路径
- **路径合法性校验** — 防止路径遍历攻击

## 安装

### 作为 Pi 技能安装

将本目录复制到 Pi 的技能目录：

```
Pi 技能目录: ~/.pi/agent/skills/codex-windows-patch-fixer/
```

或使用你 Pi 安装方式所支持的技能注册方法。

### 单独使用

脚本也可以脱离 Pi 独立运行——见下方使用说明。

## 使用方法

### 搭配 Pi Agent

告诉 Agent 使用本技能：

```
Use $local-apply-patch-fallback to apply this patch in the current repository.
```

### 独立使用（PowerShell）

```powershell
$patch = @"
*** Begin Patch
*** Add File: hello.txt
+hello
*** End Patch
"@
$patch | .\scripts\apply_patch_local.bat --root (Get-Location)
```

### 独立使用（命令提示符）

```cmd
echo *** Begin Patch > patch.txt
echo *** Add File: hello.txt >> patch.txt
echo +hello >> patch.txt
echo *** End Patch >> patch.txt
type patch.txt | scripts\apply_patch_local.bat --root .
```

### 独立使用（Linux / macOS / WSL）

```bash
echo -e '*** Begin Patch\n*** Add File: hello.txt\n+hello\n*** End Patch' | \
    python3 scripts/apply_patch_helper.py --root .
```

## 支持的补丁格式

| 操作 | 语法 |
|------|------|
| **新增文件** | `*** Add File: <路径>`<br>`+内容行` |
| **更新文件** | `*** Update File: <路径>`<br>`@@`<br>`-旧行`<br>`+新行`<br>` 上下文行` |
| **删除文件** | `*** Delete File: <路径>` |

### 示例：更新已有文件

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

> **注意：** `Update File` 中的 `-旧行` 必须与文件当前内容**逐行精确匹配**。不支持模糊匹配。

## 目录结构

```
codex-windows-patch-fixer/
├── SKILL.md                            # Pi 技能定义
├── README.md                           # 英文说明
├── README_zh.md                        # 本文档（中文）
├── LICENSE                             # MIT 许可证
├── agents/
│   └── openai.yaml                     # Pi Agent 接口配置
└── scripts/
    ├── apply_patch_helper.py            # 核心 Python 补丁应用脚本
    └── apply_patch_local.bat            # Windows .bat 包装器（自动回退到 py）
```

## 局限性

- **不支持模糊匹配** — 更新操作要求行级精确匹配
- **只支持单个 hunk** — 不支持 `Update File` 内多个 `@@` 块
- **不支持 `Move to`** — 不支持文件重命名或移动操作
- **需要 Python 3** — 所有配置了 Codex 的 Windows 环境均应满足

## 许可证

MIT。详见 [LICENSE](LICENSE)。
