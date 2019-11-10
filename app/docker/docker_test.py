# import subprocess
# output=subprocess.check_output(['docker','ps'],universal_newlines=True)
# x=output.split('\n')
# for i in x:
#   if i.__contains__("inspiring_sinoussi"):
#       container_id=i[:12]
# container_id_with_path=container_id+":/tmp"
# subprocess.call(["docker", "cp", "./test.py", container_id_with_path])
#

## first access method
# import subprocess
# file = "-c print('hello')\nprint('world')"
# cmd = ('docker run python:3.6.4-jessie python '+file).split()
# p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
# out, err = p.communicate()
# print(out)

import subprocess
import docker
import os
client = docker.from_env()
# fid = open('./test.py',"w")
# if os.path.isfile('./test.py'):
#     fid.write("print('hello')")
# fid.close()
stdout = client.containers.run(image="python:3.6.4-jessie",command="echo hello world", remove=True)
print(stdout)
