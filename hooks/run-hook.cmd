: << 'CMDBLOCK'
@echo off
REM Cross-platform wrapper for hook scripts.

if "%~1"=="" (
    exit /b 0
)

set "HOOK_DIR=%~dp0"

if not exist "%HOOK_DIR%%~1" (
    exit /b 0
)

if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

exit /b 0
CMDBLOCK

case "$0" in
  */*) SCRIPT_DIR="${0%/*}" ;;
  *) SCRIPT_DIR="." ;;
esac

SCRIPT_NAME="${1:-}"
[ -n "$SCRIPT_NAME" ] || exit 0
shift
SCRIPT_PATH="${SCRIPT_DIR}/${SCRIPT_NAME}"
[ -r "$SCRIPT_PATH" ] || exit 0

find_bash() {
  if [ -n "${BASH:-}" ] && [ -x "$BASH" ]; then
    printf '%s\n' "$BASH"
    return 0
  fi

  for candidate in /usr/bin/bash /bin/bash /usr/local/bin/bash; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  command -v bash 2>/dev/null || return 1
}

BASH_BIN="$(find_bash 2>/dev/null || true)"
[ -n "$BASH_BIN" ] || exit 0
exec "$BASH_BIN" "$SCRIPT_PATH" "$@"
