@echo off
set FXQUINOX_ROOT=%~dp0..
call python -c "from fxquinox.cli._fxcli import _print_ascii_art; _print_ascii_art()" %*
call python -c "from fxquinox.fxcore import run_launcher; run_launcher()" %*
pause