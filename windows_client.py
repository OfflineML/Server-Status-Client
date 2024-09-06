import os
import socket
import threading
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
from client import run_client


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
        client_thread = threading.Thread(target=run_client, args=())
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
