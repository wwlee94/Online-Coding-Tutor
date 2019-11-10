import subprocess
import docker
import os
client = docker.from_env()
container = client.containers.run(image="buildtest",command="python ./user_0.py", remove=True,
                        volumes= {'/home/ubuntu/sv_flask/app/userfile/':{'bind': '/usr/src/app', 'mode': 'ro'}},
                        detach = True)
print("container stdout")
print(container.logs(stdout=True, stderr=False))
print("container stderr")
print(container.logs(stdout=False, stderr=True))
