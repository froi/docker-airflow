#!/usr/bin/python

import sys
import subprocess
import string
import time

args = sys.argv

command = args[1]

executors = {
    'local': 'LocalExecutor',
    'sequential': 'SequentialExecutor',
    'celery': 'CeleryExecutor'
}

containers = {
    'webserver': 'webserver_1',
    'scheduler': 'scheduler_1',
    'fmeengine': 'fmeengine_1'
}


# Garbage Collect
def garbage_collect():
    # Clean up as part of this gig
    #subprocess.call('docker rm -v $(docker ps -a -q -f status=exited)', shell=True)
    #subprocess.call('docker rmi $(docker images -f "dangling=true" -q)', shell=True)
    #subprocess.call('docker volume rm $(docker volume ls -qf dangling=true)', shell=True)
    subprocess.call('./docker-cleanup.sh', shell=True)


def kill_all_containers():
    subprocess.call('docker kill $(docker ps -q)', shell=True)






if command == 'start' or command == 'up' or command == 'stop' or command == 'down':
    try:
        compose_type = args[2]
    except:
        compose_type = raw_input('Enter Executor (' + ', '.join(executors.keys(
        )) + '): ')

    # Stop no matter what.
    tmpl = string.Template("Stopping $composeType executor.")
    print(tmpl.substitute(composeType=compose_type))

    subprocess.call(
        "docker-compose -f docker-compose-" + executors[compose_type] +
        ".yml down",
        shell=True)

    if command == 'up' or command == 'start':
        tmpl = string.Template("Starting $composeType executor.")
        print(tmpl.substitute(composeType=compose_type))
        subprocess.call(
            "docker-compose -f docker-compose-" + executors[compose_type] +
            ".yml up -d",
            shell=True)

elif command == 'ssh':
    try:
        cname = args[2]
    except:
        cname = raw_input('Enter Container Type (' + ', '.join(containers.keys(
        )) + '): ')

    tmpl = string.Template("Opening connection to local $cname container")
    print(tmpl.substitute(cname=cname))
    subprocess.call("docker exec -it dockerairflow_" \
    + containers[cname] + " /bin/bash", shell=True)

elif command == 'jupyter':
    port = "8888"
    url = "http://127.0.0.1:" + port
    c_call = "docker exec -itd dockerairflow_" + containers['webserver']
    print('Starting Jupyter NB within the webserver environment on ' + url)
    subprocess.call(c_call + " pkill -f jupyter", shell=True)
    subprocess.call(
            c_call + " jupyter notebook --no-browser --port " + port +
        " --ip=0.0.0.0 --NotebookApp.token=''",
        shell=True)
    try:
        import webbrowser
        time.sleep(2)
        webbrowser.open(url, new=2)
    except ImportError:
        pass

elif command == 'pull_latest_image':
    print("Pulling latest from docker hub")
    subprocess.call('docker pull mrmaksimize/airflow:latest', shell=True)

elif command == 'rebuild_image':
    print("DID YOU REMOVE THE IMAGE FIRST???")
    subprocess.call(
        "docker build --rm --no-cache -t mrmaksimize/airflow .", shell=True)

elif command == 'remove_image':
    image_id = args[2]
    subprocess.call('docker rmi -f ' + image_id, shell=True)

elif command == 'kill_all_containers':
    kill_all_containers()
    garbage_collect()

elif command == 'garbage_collect':
    garbage_collect()

elif command == 'setup':
    menv = args[2] or 'mac'
    subprocess.call('rm -rf .env && cp ' + menv + '.env .env')
