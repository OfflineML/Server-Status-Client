@echo off
setlocal enabledelayedexpansion

REM Check if one argument is provided
if "%~1"=="" (
    echo Usage: %0 APP_VERSION
    exit /b 1
)

REM Store the APP_VERSION argument in a variable
set "APP_VERSION=%~1"

REM Validate APP_VERSION input
if "%APP_VERSION%"=="" (
    echo Application version is required.
    exit /b 1
)

REM Ask for API_KEY in the command line
set /p "API_KEY=Please enter your Server's API Key: "

REM Validate API_KEY input
if "%API_KEY%"=="" (
    echo API Key is required.
    exit /b 1
)

REM Define variables
set "DOWNLOAD_URL=https://github.com/Tetraa-Group/Server-Status-Client/releases/download/%APP_VERSION%/windows_client.exe"
echo "DOWNLOAD_URL: %DOWNLOAD_URL%"
set "ENDPOINT=https://api.statusrecorder.ziphio.com/server_data"
set "INSTALL_DIR=%ProgramFiles%\Server-Status-Client"
set "SERVICE_NAME=ServerStatusClient"

REM Remove existing installation directory if it exists
if exist "%INSTALL_DIR%" (
    cd /d "%INSTALL_DIR%"
    if exist "windows_client.exe" (
        echo Stopping existing service...
        .\windows_client.exe stop
        echo Removing existing service...
        .\windows_client.exe remove
    )
    cd ..
    echo Removing existing installation directory...
    rmdir /s /q "%INSTALL_DIR%"
)

REM Create installation directory
mkdir "%INSTALL_DIR%"

REM Download the client
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALL_DIR%\windows_client.exe'"

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
.\windows_client.exe install
if %errorlevel% neq 0 (
    echo [31mFailed to install the service.[0m
    exit /b 1
)

REM Start the service
echo Starting the service...
.\windows_client.exe start
if %errorlevel% neq 0 (
    echo [31mFailed to start the service.[0m
    exit /b 1
)

echo [32mService installed and started successfully.[0m


endlocal
