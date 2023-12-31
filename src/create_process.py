import os
import plistlib
from config import *
from MetaDBConnect import *

start = '''
export wd=/Users/trapbookpro/Development/scheduling/{PROCESS_NAME}
export plst={PLIST}
export fn=$wd/$plst

export launchDir=/Library/LaunchDaemons
export launchLocation=/Library/LaunchDaemons/$plst
echo "Launch Location: $fn"
echo 'kara' | sudo -S  cp $fn $launchDir

ls -l $launchLocation
echo "Submitting $plst to launchd"
echo 'kara' | sudo -S  chown root:wheel $launchLocation
echo 'kara' | sudo -S  chmod 644 $launchLocation

echo 'kara' | sudo -S  launchctl load $launchLocation
sudo launchctl bootstrap system $fn
'''

stop = '''
export wd=/Users/trapbookpro/Development/scheduling/{PROCESS_NAME}
export plst={PLIST}
export fn=$wd/$plst

export launchLocation=/Library/LaunchDaemons/$plst
echo "Booting out of Launch Location: $launchLocation"

echo 'kara' | sudo -S launchctl unload $launchLocation
echo 'kara' | sudo -S launchctl bootout system $launchLocation

echo "Removing .plist: $launchLocation"
echo 'kara' | sudo -S rm -f $launchLocation
ls -l $launchLocation
echo "Successfully booted out: $plst"
'''

def write_dict_to_plist(data_dict, process_name, target_dir=TARGET_DIR):
    """Writes a dictionary to a plist file."""
    working_dir = os.path.join(target_dir,process_name )
    filename = f"com.trapbookpro.{process_name.replace('_','.')}.plist"
    os.mkdir(working_dir)
    os.mkdir(os.path.join(working_dir,'stderr'))
    os.mkdir(os.path.join(working_dir,'stdout'))

    create_trigger_files(process_name,target_dir)

    filename = os.path.join(working_dir,filename)

    with open(filename, 'wb') as plist_file:
        plistlib.dump(data_dict, plist_file)


def create_trigger_files(process_name, target_dir=TARGET_DIR):
    plist = f"com.trapbookpro.{process_name.replace('_', '.')}.plist"
    working_dir = os.path.join(target_dir, process_name)
    start_contents = start.format(PLIST=plist, PROCESS_NAME=process_name)
    with open(os.path.join(working_dir, 'start.sh'), 'w') as start_file:
        start_file.writelines(start_contents)

    stop_contents = stop.format(PLIST=plist, PROCESS_NAME=process_name)
    with open(os.path.join(working_dir, 'stop.sh'), 'w') as start_file:
        start_file.writelines(stop_contents)

def create_plist(command_line,process_name, target_dir=TARGET_DIR, run_at_load=True, active=True):
    program_arguments = command_line.split(" ")
    plist_name = f"com.trapbookpro.{process_name.replace('_','.')}.plist"
    # Example usage:
    my_dict = {
        "ProgramArguments": program_arguments,
        "Label": plist_name,
        "WorkingDirectory": os.path.join(target_dir,process_name),
        "StandardOutPath": os.path.join(target_dir, 'stdout' ,f'{process_name}.log'),
        "StandardErrorPath": os.path.join(target_dir, 'stderr', f'{process_name}.log')
    }
    if run_at_load:
        my_dict['RunAtLoad'] = run_at_load
    return my_dict

def create_process_and_dir(command_line,process_name, project_name, target_dir=TARGET_DIR, run_at_load=True, active=True):
    data_dict = create_plist(command_line,process_name, target_dir, run_at_load)
    write_dict_to_plist(data_dict, process_name,target_dir)

    argv = command_line.split(" ")
    conn = MetadataDBConnect()
    with conn:
        conn.insert_process(process_name=process_name,
                            script_path=argv[1],
                            command_line=command_line,
                            plist=f"com.trapbookpro.{process_name.replace('_','.')}",
                            run_at_load=run_at_load,
                            active=active,
                            project_name=project_name)

def main():
    target_dir = '/Users/trapbookair/Development/scheduling'
    # create_trigger_files('test_process', target_dir=target_dir)
    create_process_and_dir(
        command_line='/opt/homebrew/bin/python3 /Users/trapbookair/Development/etrade-monitor/emon_main.py -vo',
        process_name='vol_outliers',
        project_name='EMON',
        target_dir=target_dir,
        run_at_load=False,
        active=False
    )

if __name__ == '__main__':
    main()