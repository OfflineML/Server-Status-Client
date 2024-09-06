import os
import socket
import threading
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
from client import run_client
import win32api
from datetime import datetime


class ServerStatusClient(win32serviceutil.ServiceFramework):
    _svc_name_ = "Server Status Client"
    _svc_display_name_ = "Server Status Client"
    _svc_description_ = "Server Status Client background service    "

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Read configuration
        exe_path = win32api.GetModuleFileName(None)
        if "python" in exe_path.split("\\")[-1].lower():
            exe_path = os.path.abspath(__file__)
        source_dir = os.path.dirname(exe_path)

        # Create a log file
        log_file = os.path.join(source_dir, 'server_status_client.log')
        
        # Function to write log messages
        def write_log(message):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} - {message}\n")
        
        # Log service start
        write_log("Server Status Client service started")
        write_log(f"Source directory: {source_dir}")
        
        # Log configuration details
        config_file = os.path.join(source_dir, 'api_configs.json')
        if os.path.exists(config_file):
            write_log("Configuration file found")
        else:
            write_log("Configuration file not found")
        
        client_thread = threading.Thread(target=run_client, args=(source_dir, write_log,))
        client_thread.start()
        
        while True:
            servicemanager.LogInfoMsg("Service is running")
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if rc == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ServerStatusClient)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ServerStatusClient)

    win32serviceutil.ChangeServiceConfig(
        None,  # No remote machine
        ServerStatusClient._svc_name_,
        startType=win32service.SERVICE_AUTO_START
    )
