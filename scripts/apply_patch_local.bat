@echo off
setlocal
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  python "%~dp0apply_patch_helper.py" %*
  exit /b %ERRORLEVEL%
)
py -3 "%~dp0apply_patch_helper.py" %*
exit /b %ERRORLEVEL%
