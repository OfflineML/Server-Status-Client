@echo off
setlocal enabledelayedexpansion

REM Check if required arguments are provided
if "%~2"=="" (
    echo [31mAPI Key is not provided, copy the API key from the server-card and paste it at the end of the command.[0m
    exit /b 1
)

REM Define variables
set "API_KEY=%~2"
set "APP_VERSION=%~1"
set "DOWNLOAD_URL=https://github.com/Tetraa-Group/Server-Status-Client/releases/download/%APP_VERSION%/server_status_client.exe"
set "ENDPOINT=https://api.statusrecorder.ziphio.com/server_data"
set "INSTALL_DIR=%ProgramFiles%\Server-Status-Client"
set "SERVICE_NAME=ServerStatusClient"

REM Remove existing installation directory if it exists
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

REM Create installation directory
mkdir "%INSTALL_DIR%"

REM Download the client
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALL_DIR%\server_status_client.exe'"

REM Create api_configs.json file
echo {> "%INSTALL_DIR%\api_configs.json"
echo     "version": "%APP_VERSION%",>> "%INSTALL_DIR%\api_configs.json"
echo     "api_key": "%API_KEY%",>> "%INSTALL_DIR%\api_configs.json"
echo     "endpoint": "%ENDPOINT%">> "%INSTALL_DIR%\api_configs.json"
echo }>> "%INSTALL_DIR%\api_configs.json"

REM Install and start the service
sc create %SERVICE_NAME% binPath= "%INSTALL_DIR%\server_status_client.exe" start= auto
sc description %SERVICE_NAME% "Server Status Client background service"
sc start %SERVICE_NAME%

echo Server Status Client has been installed and started as a service.
echo.
echo To manage the Server Status Client service:
echo   Start the service:   sc start %SERVICE_NAME%
echo   Stop the service:    sc stop %SERVICE_NAME%
echo   Restart the service: sc stop %SERVICE_NAME% ^& sc start %SERVICE_NAME%
echo   Check status:        sc query %SERVICE_NAME%
echo.
echo The service is configured to start automatically on system boot.
echo You can view the logs in the Windows Event Viewer.

endlocal
