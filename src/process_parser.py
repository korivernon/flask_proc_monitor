import os

import psutil

#this file contains the process parser
#the process parser will parse through the processes

from MetaDBConnect import *
from config import  *

def list_directories(path):
    try:
        # List all entries in the given path
        entries = os.listdir(path)

        # Filter out directories
        directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]

        return directories
    except FileNotFoundError:
        return "The specified path was not found."
    except PermissionError:
        return "Permission denied to access the specified path."
    except OSError as e:
        return f"An error occurred: {e}"

import subprocess
def run_process(command):
    try:
        # Split the command string into arguments
        args = command.split()

        # Run the command
        result = subprocess.run(args, capture_output=True, text=True, check=True)

        # Return the output, error (if any), and exit status
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess
        return e.output, e.stderr, e.returncode

def start_job(job_name):
    command_line = os.path.join(TARGET_DIR,job_name,'start.sh')
    print(f"command line: --> {command_line}")
    command_line = 'bash ' + command_line
    try:
        stdout, stderr, retcode = run_process(command_line)
        print('stdout', stdout)
        print('stderr', stderr)
        print('retcode', retcode)
    except:
        print(traceback.format_exc())
        return False
    return True

def stop_job(job_name):
    command_line = os.path.join(TARGET_DIR,job_name,'stop.sh')
    command_line = 'bash ' + command_line
    try:
        stdout, stderr, retcode = run_process(command_line)
        print('stdout',stdout)
        print('stderr', stderr)
        print('retcode', retcode)
    except:
        print(traceback.format_exc())
        return False
    return True

def fetch_stderr(job_name, target_dir = TARGET_DIR, join_by='<br>'):
    file_path = os.path.join(target_dir, job_name, 'stderr')
    file_name = os.path.join(file_path, get_latest_file(file_path))
    result = tail(file_name)
    return join_by.join(result)

def fetch_stdout(job_name, target_dir = TARGET_DIR, join_by='<br>'):
    file_path = os.path.join(target_dir, job_name, 'stdout')
    file_name = os.path.join(file_path, get_latest_file(file_path))
    result = tail(file_name)
    return join_by.join(result)

def restart_job(job_name):
    stop_job(job_name)
    start_job(job_name)
    return True

def is_script_running(script_name):
    try:
        # Use pgrep to find processes with a name matching the script_name
        # script_name = script_name.replace('trapbookpro','trapbookair')
        print(f'checking script running: {script_name}')
        result = subprocess.run(["pgrep", "-f", script_name], capture_output=True, text=True)

        # Check if the output is empty (no matching processes found)
        if result.stdout:
            return True
        else:
            return False
    except subprocess.SubprocessError as e:
        print(f"An error occurred: {e}")
        return False

def fetch_run_time(pid):
    try:
        result = subprocess.run(["ps", "-o", "etime", "-p", f"$(pgrep {pid})"], capture_output=True, text=True)
        output = result.stdout
        print(f"fetching run time: {result}")
    except:
        print('hit error trying to fetch run time:\n',traceback.format_exc())
        return
    return output

def fetch_pid(process_name = "process_name.exe"):
    for proc in psutil.process_iter(['name','cmdline']):
        if proc.name() == process_name or process_name in proc.cmdline():
            pid = proc.pid
            return pid
    return None

def fetch_process_runtime(process_name):
    # Use pgrep to find the PID of the script with those arguments
    result = subprocess.run(["ps", "-ef", "|",'grep',process_name], capture_output=True, text=True)
    print('result:-->',result)
    pid_string = result.stdout.split()[0]  # Remove any trailing newlines
    print('pidstring: ', pid_string)
    pid = int(pid_string)  # If you need to use the PID as a number
    print('result of fetching pid',pid)
    # pid = pid.decode().strip()  # Convert bytes to string and remove trailing newline
    # Use ps to get the runtime of the process with that PID
    result = subprocess.run(["ps", "-o", "etime", "-p", pid], capture_output=True, text=True)
    output = result.stdout
    return output

def find_procs_to_monitor_and_enrich(group=True):
    all_procs = get_all_procs()
    enriched = []
    for ind, row in all_procs.iterrows():
        row = row.to_dict()
        row['command'] = " ".join(row['command_line'].split(' ')[1:])
        row['running'] = is_script_running(row['command'])
        # row['runtime'] = fetch_process_runtime(row['command'])
        if row['running'] == False and row['active'] == True: # red
            row['flag'] = True
            row['color'] = 'RED'
            row['score'] = -1
            row['START'] = f'<a href="/start/{row["process_name"]}">START</a>'
            row['STOP'] = 'N/A'
            row['RESTART'] = f'<a href="/restart/{row["process_name"]}">RESTART</a>'
        elif row['running'] == True and row['active'] == True:
            row['flag'] = False
            row['color'] = 'GREEN'
            row['score'] = 1
            row['START'] = 'N/A'
            row['STOP'] = f'<a href="/stop/{row["process_name"]}">STOP</a>'
            row['RESTART'] = f'<a href="/restart/{row["process_name"]}">RESTART</a>'
        else:
            row['flag'] = False
            row['color'] = 'GREY'
            row['score'] = 0
            row['STOP'] = 'N/A'
            row['RESTART'] = 'N/A'
            row['START'] = f'<a href="/start/{row["process_name"]}">START</a>'
        row['process_name_'] = row["process_name"]
        row['process_name'] = f'<a href="/more_info/{row["process_name"]}">{row["process_name"]}</a>'

        enriched.append(row)
    enriched_procs = pd.DataFrame(enriched)
    if group:
        segregated = segregate_procs(enriched_procs)
    else:
        return enriched_procs # dataframe
    return segregated

def tail(filepath, lines=100):
    """Tails the last `lines` lines of a file."""
    with open(filepath, 'rb') as f:
        f.seek(-2, 2)  # Jump to the second-last byte.
        while f.read(1) != b'\n':
            if f.tell() == 1:  # Reached the beginning of the file.
                f.seek(0)
                break
            f.seek(-2, 1)

        lines_to_read = lines + 1  # Read one extra line to cover edge cases.
        block_size = 1024
        blocks = []

        while lines_to_read > 0 and f.tell() > 0:
            if f.tell() > block_size:
                f.seek(-block_size, 1)
            blocks.append(f.read(block_size))
            lines_found = blocks[-1].count(b'\n')
            lines_to_read -= lines_found

        blocks.reverse()
        return b''.join(blocks).decode().splitlines()[-lines:]

def get_latest_file(directory):
    """Gets the latest file in a directory."""
    return max(os.listdir(directory), key=lambda f: os.path.getmtime(os.path.join(directory, f)))

def main():
    target_dir = '/Users/trapbookair/Development/scheduling'
    print(fetch_stdout(target_dir=target_dir,job_name='emon_server_runner', join_by='\n'))

if __name__ == '__main__':
    main()