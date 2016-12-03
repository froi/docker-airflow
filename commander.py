#!/usr/bin/python

import sys
import subprocess
import string
import time

args = sys.argv

command = args[1]

executors = {
    'local': 'LocalExecutor',
    'sequential': 'SequentialExecutor'
}

containers = {
    'webserver': 'webserver_1',
    'scheduler': 'scheduler_1',
    'fmeengine': 'fmeengine_1'
}

def run_compose(direction='up', compose_type='sequential'):
    executor = executors[compose_type]
    tmpl = string.Template("Starting $ex_name executor.")
    print(tmpl.substitute(ex_name=executor))
    bash_tmpl = string.Template("docker-compose -f docker-compose-$ex_name.yml $op -d")
    subprocess.call(bash_tmpl.substitute(ex_name=executor, op=direction), shell=True)

def get_compose_type():
    try:
        compose_type = args[2]
    except:
        compose_type = raw_input('Enter Executor (' + ', '.join(executors.keys()) + '): ')

    return compose_type

if command == 'start':
    run_compose('up', get_compose_type())

elif command == 'stop':
    run_compose('down', get_compose_type())

elif command == 'restart':
    run_compose('down', get_compose_type())
    run_compose('up', get_compose_type())

elif command == 'ssh':
    try:
        cname = args[2]
    except:
        cname = raw_input('Enter Container Type (' + ', '.join(containers.keys()) + '): ')

    tmpl = string.Template("Opening connection to local $cname container")
    print(tmpl.substitute(cname = cname))
    subprocess.call("docker exec -it dockerairflow_" \
    + containers[cname] + " /bin/bash", shell=True)

elif command == 'jupyter':
    port = "8888"
    url = "http://127.0.0.1:" + port
    c_call = "docker exec -itd dockerairflow_" + containers['webserver']
    print('Starting Jupyter NB within the webserver environment on ' + url)
    subprocess.call(c_call + " pkill -f jupyter", shell=True)
    subprocess.call(c_call + " jupyter notebook --no-browser --port " + port + " --ip=0.0.0.0", shell=True)
    try:
        import webbrowser
        time.sleep(2)
        webbrowser.open(url, new=2)
    except ImportError:
        pass

elif command == 'rebuild_image':
    print("DID YOU REMOVE THE IMAGE FIRST???")
    subprocess.call("docker build --rm --no-cache -t mrmaksimize/airflow .", shell=True)

elif command == 'remove_image':
    image_id = args[2]
    subprocess.call('docker rmi -f ' + image_id, shell=True)

elif command == 'setup':
    menv = args[2] or 'mac'
    subprocess.call('rm -rf .env && cp ' + menv + '.env .env')
