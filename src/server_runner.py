import os
import subprocess
from app import launch

def start_server():
    parent_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(parent_path, 'app.py')
    pidfilename = os.path.join(parent_path ,'server.pid')
    if os.path.exists(pidfilename):
        print("already running server")
        try:
            print("attempting to stop the server")
            stop_server()
        except:
            print("error restarting")
            return
    if not os.path.exists(pidfilename):
        print(pidfilename ,'does not exist. starting server.')
        process = subprocess.Popen(['python3', path, '&'], shell=False)
        if not os.path.exists(pidfilename):
            pidfile = open(pidfilename,'w')
            pidfile.write(str(process.pid))
            pidfile.close()
        else:
            print('Stopping server then restarting because pidfile does not exist')
            stop_server()
            launch()
    else:
        print('Launching server because pid file does not exist.')
        launch()

def stop_server():
    parent_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(parent_path, 'app.py')
    pidfilename = os.path.join(parent_path,'server.pid')
    if os.path.exists(pidfilename):
        f = open(pidfilename, 'r')
        pid = f.readline()
        print('killing process with id', pid)
        subprocess.Popen(['kill', pid], shell=False)
        os.remove(pidfilename)
        return
    print('no process running')

if __name__ == '__main__':
    start_server()