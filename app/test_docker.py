import sys
sys.path.append('/home/ubuntu/sv_flask/app/docker')
import docker_container

result = docker_container.run("python3", "./user_0.py")
print("result")
print(result)
