#-*- coding:utf-8 -*-
import os
import sys
import subprocess
import docker # Docker SDK for Python
'''
    1. user_file_path : docker_container에서 실행될 파일 경로와 이름
    -> (MOUNT { HOST : ~/sv_flask/app/userfile, DOCKER_CONTAINER : /usr/src/app) }
    2. language : 컴파일할 언어 종류
    3. image_name : docker로 build한 이미지 이름
    4. mem_limit : 메모리 제한 크기 (Default : 64 메가)
    5. cpu_shares : CPU 자원 제한 크기 (Default : CPU 1개 할당)

    cf) IO 접근 제한 : READ_ONLY (읽기만 가능)
'''

# docker container 실행
def run(language, user_file_path, image_name = "buildtest", mem_limit = "64m", cpu_shares = "1024"):

    # # 파라미터 가져오기
    # user_file_path = sys.argv[1]
    print("image_name = '" + image_name +"'")
    print("language = '" + language +"'")
    print("user_file_path = '" + user_file_path +"'")
    print("mem_limit = '" + mem_limit +"'")
    print("cpu_shares = '" + cpu_shares +"'")

    client = docker.from_env()

    # 컨테이너 실행
    # 설정한 메모리 이상으로 메모리를 사용하면 컨테이너는 자동적으로 종료
    cmd = language + " " + user_file_path
    container = client.containers.run(image=image_name, command = cmd, detach = True,
                            volumes= {'/home/ubuntu/sv_flask/app/userfile/':{'bind': '/usr/src/app', 'mode': 'ro'}},
                            mem_limit = "64m", cpu_shares = 1024)
    id = container.short_id
    print("Container ID : " + id)

    # 컨테이너 생성 후 stop
    print("kill Container")
    container.kill()

    print("stop Container")
    container.stop(timeout = 5)
    exit_code = container.wait()

    stat_code = exit_code['StatusCode'] # 에러 코드
    exc_msg = exit_code['Error'] # 에러 메시지

    result = {}
    if stat_code == 0:
        result['state'] = 'success'
        stdout = container.logs(stdout=True, stderr=False) # 컨테이너 log 확인
        result['stdout'] = stdout

    elif stat_code == 1:
        result['state'] = 'compile error'
        stderr = container.logs(stdout=False, stderr=True) # 컨테이너 log 확인
        result['stderr'] = stderr

    # elif D['state'] == 'tle':
    #     result['state'] = 'tle'
    #     result['stdout'] = ''
    #     result['stderr'] = 'Running time limit exceeded.'
    elif stat_code == 137:
        result['state'] = 'error'
        result['stdout'] = ''
        result['stderr'] = 'Memory limit exceeded.'
    # elif 'docker' not in D['stderr']:
    #     result['state'] = 'error'
    #     result['stdout'] = D['stdout']
    #     result['stderr'] = D['stderr']
    #     if logger is not None:
    #         logger.info('Exception while running(may due to user): ' + result['stderr'])
    else:
        result['state'] = 'error'
        result['stdout'] = ''
        result['stderr'] = 'Server error.'
        print 'Error while running: ' + result['stderr']

    # 컨테이너 제거
    print("remove Container")
    container.remove()

    return result
