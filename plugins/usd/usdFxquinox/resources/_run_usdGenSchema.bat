@echo off

REM Set paths to Houdini programs, and the USD file
set HOUDINI_VERSION=20.0.547
set USD_PLUGIN_NAME=usdFxquinox
set HYTHON_PATH="%ProgramFiles%\Side Effects Software\Houdini %HOUDINI_VERSION%\bin\hython.exe"
set USDGENSCHEMA_PATH="%ProgramFiles%\Side Effects Software\Houdini %HOUDINI_VERSION%\bin\usdGenSchema"
set SCHEMA_PATH=%~dp0%USD_PLUGIN_NAME%\schema.usda
set DESTINATION_PATH=%~dp0

echo Running usdGenSchema for %USD_PLUGIN_NAME%:
echo           Hython: %HYTHON_PATH%
echo       USD plugin: %USD_PLUGIN_NAME%
echo     UsdGenSchema: %USDGENSCHEMA_PATH%
echo           Schema: %SCHEMA_PATH%
echo             Dest: %DESTINATION_PATH%
echo.

REM Run the command `hython usdGenSchema 'path/to/schema.usda' 'destination/path'`
%HYTHON_PATH% %USDGENSCHEMA_PATH% %SCHEMA_PATH% %DESTINATION_PATH%

pause