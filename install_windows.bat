@echo off
setlocal enabledelayedexpansion

REM Check if two arguments are provided
if "%~2"=="" (
    echo Usage: %0 <APP_VERSION> <API_KEY>
    exit /b 1
)

REM Store the arguments in variables
set "APP_VERSION=%~1"
set "API_KEY=%~2"

REM Validate inputs
if "%APP_VERSION%"=="" (
    echo [31mApplication version is required.[0m
    exit /b 1
)
if "%API_KEY%"=="" (
    echo [31mAPI Key is required.[0m
    exit /b 1
)

REM Define variables
set "DOWNLOAD_URL=https://github.com/Tetraa-Group/Server-Status-Client/releases/download/%APP_VERSION%/client.exe"
echo "DOWNLOAD_URL: %DOWNLOAD_URL%"
set "ENDPOINT=https://api.statusrecorder.ziphio.com/server_data"
set "INSTALL_DIR=%ProgramFiles%\Server-Status-Client"
set "SERVICE_NAME=ServerStatusClient"

REM Remove existing installation directory if it exists
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

REM Create installation directory
mkdir "%INSTALL_DIR%"

REM Download the client
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALL_DIR%\client.exe'"

REM Create api_configs.json file
echo {> "%INSTALL_DIR%\api_configs.json"
echo     "version": "%APP_VERSION%",>> "%INSTALL_DIR%\api_configs.json"
echo     "api_key": "%API_KEY%",>> "%INSTALL_DIR%\api_configs.json"
echo     "endpoint": "%ENDPOINT%">> "%INSTALL_DIR%\api_configs.json"
echo }>> "%INSTALL_DIR%\api_configs.json"

REM Install and start the service
REM Change to the installation directory
cd /d "%INSTALL_DIR%"

REM Install the service
echo Installing the service...
.\client.exe install
if %errorlevel% neq 0 (
    echo [31mFailed to install the service.[0m
    exit /b 1
)

REM Start the service
echo Starting the service...
.\client.exe start
if %errorlevel% neq 0 (
    echo [31mFailed to start the service.[0m
    exit /b 1
)

echo [32mService installed and started successfully.[0m


endlocal
