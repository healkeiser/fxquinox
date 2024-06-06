@echo off

@REM Setup environment
set USD_ASSET_RESOLVER=%SERVER_ROOT%/Projects/Code/fxquinox/plugins/usd/usdAssetResolver
set TF_DEBUG=AR_RESOLVER_INIT
set PATH=%SERVER_ROOT%/Projects/Code/fxquinox/plugins/usd/usdAssetResolver/cachedResolver/lib;%PATH%
set PXR_PLUGINPATH_NAME=%SERVER_ROOT%/Projects/Code/fxquinox/plugins/usd/usdAssetResolver/cachedResolver/resources;%PXR_PLUGINPATH_NAME%
set PYTHONPATH=%SERVER_ROOT%/Projects/Code/fxquinox/plugins/usd/usdAssetResolver/cachedResolver/lib/python;%PYTHONPATH%
set AR_CACHEDRESOLVER_ENV_EXPOSE_RELATIVE_PATH_IDENTIFIERS=1

@REM echo      USD_ASSET_RESOLVER: %USD_ASSET_RESOLVER%
@REM echo                TF_DEBUG: %TF_DEBUG%
@REM echo                    PATH: %PATH%
@REM echo     PXR_PLUGINPATH_NAME: %PXR_PLUGINPATH_NAME%
@REM echo              PYTHONPATH: %PYTHONPATH%

@REM Launch Houdini
"C:/PROGRA~1/SIDEEF~1/HOUDIN~1.547/bin/houdini"
