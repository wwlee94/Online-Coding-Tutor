#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
from flask import Flask , render_template, session , request, redirect, url_for
from flask_socketio import SocketIO, emit
import datetime
app = Flask(__name__)
app.secret_key = "secret"
# app.config.update(
#     PERMANENT_SESSION_LIFETIME = 5)
socketio = SocketIO(app)
#visualize code to json
import sv_logger
import json

#subprocess / flag
import subprocess
from time import sleep
from fcntl import fcntl,F_GETFL,F_SETFL
from os import O_NONBLOCK,read

# 에러 처리
import errno

# 유저 세션 번호
user_no = 0
p = re.compile(".py[(]\d+[)]") #pdb current line 번호를 알기 위함
p_num = re.compile('\d+')      # .py(숫자) 형태로 뽑은 패턴에서 숫자만 빼냄

#filepath의 .py를 실행하고 반환값을 json으로 변환
def execute_return_json(filepath):
    script = []
    def my_finalizer(output_lst):
        script.append(output_lst)
        #print 출력을 output_json에 쓴다? error
        #print -> output_json
    #ignore_id=True -> id = 99999 고정
    sv_logger.exec_script_str(open(filepath).read(),my_finalizer,False)
    output_json = json.dumps(script)
    return output_json

#서버 초기 설정
@app.before_request
def before_request():
    global user_no #user_no를 전역변수로 선언
# 	app.permanent_session_lifetime = timedelta(minutes=5) #세션 기간 5분으로 설정
    if 'session' in session and 'user-id' in session:
        pass
    else:
        session['session'] = os.urandom(24)
        session['username'] = 'user_'+str(user_no)
        session['debug_str'] = []
        user_no += 1
#redirect로 온 데이터 보여줘야함..
@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form # {url:url,data: data} -> data를 가져온것
        print(data['bno'])
        print(data['content'])
        contents = data['content']
        return render_template('index.html',content = contents)
    else:
        return render_template('index.html',content = "false")
@app.route('/test')
def test():
    return render_template('loading-page.html')

#python 코드 예제 리눅스 파일 조회 후 반환
@app.route('/example')
def example():
    file_info = []
    path=os.path.join("/home/ubuntu/sv_flask/app/example/python/")
    file_list = os.listdir(path)
# 	file_list_py = [file for file in file_list if file.endswith('.py')]
    file_list_py = []
    for file in file_list:
        filepath = ""
        content = ""
        count = 0
        filepath = path + file
        if file.endswith('.py'):
            #파일 내용 읽기
            fid = open(filepath,'r')
            lines = fid.readlines()
            for line in lines:
                if count == 1: info = line
                content = content + line
                count += 1
            fid.close()
            #파일 크기 읽기
            size = os.path.getsize(filepath)
            #파일 수정일 읽기
            mtime = os.path.getmtime(filepath)
            mtime = datetime.datetime.fromtimestamp(mtime)
            mtime = mtime.ctime()
            file_list_py.append({'file':file,'info':info,'size':size,
                              'mtime':mtime,'content':content})
    print (file_list_py)
    return render_template('example.html',file_list_py = file_list_py)

@socketio.on('connect')
def connect():
    emit("after connect", {'data': 'Connected'})
    print("Connect !!")

#사용자가 브라우저를 종료하면 시간 지나서 disconnect -> 세션도 비움 -> 해당 세션id의 파일도 삭제
@socketio.on('disconnect')
def disconnect():
    filepath = os.path.join("/home/ubuntu/sv_flask/app/userfile",session['username']+'.py')
    if os.path.isfile(filepath):
        os.remove(filepath)

    print (session['username']+" Session Clear !!")
    session.clear()
    print ("Disconnected !!")

#stop 버튼 클릭시
@socketio.on('stop_request')
def stop(message):
    session['debug_str']=[]
    print ("Session['debug_str'] Clear !!")
    print (message['data'])

#viz_request -> visualize 버튼 클릭시 요청 -> 내부 정보를 json으로 반환
@socketio.on('viz_request')
def vizualize_request(message):
    string = message['data'] #unicode로 받아짐..!!!! 중요!!
    string = string.encode('latin-1').decode('utf-8') #라틴에서 utf-8로..
    python_v = check_version(message['version'])
    print (string)
    print (python_v)
    print ("viz_request : python compile !!")
    try:
        if not (os.path.isdir('/home/ubuntu/sv_flask/app/userfile')):
            os.makedirs(os.path.join('/home/ubuntu/sv_flask/app/userfile'))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create Directory!!")
            raise
    filepath = os.path.join("/home/ubuntu/sv_flask/app/userfile",session['username']+'.py')
    fid = open(filepath,"w")
    if os.path.isfile(filepath):
        fid.write(string)
    fid.close()
    cmd = [python_v,'/home/ubuntu/sv_flask/app/userfile/'+session['username']+'.py']
    fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    #data = fd_popen.read().strip()
    #fd_popen.close()
    out , err = fd_popen.communicate()
    print (out)
    print ("visualize data")
    if err == "":
        viz_data = execute_return_json(cmd[1])
        print (viz_data)
        emit("viz_response", {'data': viz_data})
    elif err != "":
        print (err)
        emit("viz_response", {'data': err})

#run_request -> Run 버튼 클릭시 .py 컴파일 후 결과값 리턴
@socketio.on('run_request')
def run_request(message):
    string = message['data'] #unicode로 받아짐..!!!! 중요!!
    string = string.encode('latin-1').decode('utf-8') #라틴에서 utf-8로..
    python_v = check_version(message['version'])
    print ("run_request : python compile !!")
    try:
        if not (os.path.isdir('/home/ubuntu/sv_flask/app/userfile')):
            os.makedirs(os.path.join('/home/ubuntu/sv_flask/app/userfile'))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create Directory!!")
            raise
    filepath = os.path.join("/home/ubuntu/sv_flask/app/userfile",session['username']+'.py')
    fid = open(filepath,"w")
    if os.path.isfile(filepath):
        fid.write(string)
    fid.close()
    cmd = [python_v,'/home/ubuntu/sv_flask/app/userfile/'+session['username']+'.py']
    fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    #data = fd_popen.read().strip()
    #fd_popen.close()
    out , err = fd_popen.communicate()
    if err == "":
        print (out)
        out = out.strip()
        out = python_version(python_v) + out #sys.version -> python version
        emit("run_response", {'data': out})
    elif err != "":
        print (err)
        emit("run_response", {'data': err})

#debug_request -> Debug버튼 클릭시 서버에서 PDB 실행
@socketio.on('debug_request')
def debug_request(message):
    string = message['data'] #unicode로 받아짐..!!!! 중요!!
    string = string.encode('latin-1').decode('utf-8') #라틴에서 utf-8로..
    session['debug_str']=[]
    python_v = check_version(message['version'])
    print (string)
    print ("debug_request : python debug !!")
    try:
        if not (os.path.isdir('/home/ubuntu/sv_flask/app/userfile')):
            os.makedirs(os.path.join('/home/ubuntu/sv_flask/app/userfile'))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create Directory!!")
            raise
    filepath = os.path.join("/home/ubuntu/sv_flask/app/userfile",session['username']+'.py')
    fid = open(filepath,"w")
    if os.path.isfile(filepath):
        fid.write(string)
    fid.close()
    cmd = [python_v,'-m','pdb','/home/ubuntu/sv_flask/app/userfile/'+session['username']+'.py']
    fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    #fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    #data = fd_popen.read().strip()
    #fd_popen.close()
    out , err = fd_popen.communicate()
    out = out.strip()

    line_stack = []  # 현재까지 디버그된 py파일의 라인 정보 스택
    #.py 패턴을 찾아 라인 정보를 가져옴
    findall = p.findall(out)
    print (findall)
    for e in findall:
        string = p_num.search(e)
        line_stack.append(string.group())
    if(len(line_stack)!=0):
        linenum = line_stack[-1] #마지막 원소 접근 -> -1
    else:
        linenum = '-1'

    if out != "":
        out = python_version(python_v) + out #sys.version -> python version
        print (out)
        emit("debug_response", {'success': out, 'linenum':linenum })
    if err != "":
        print (err)
        emit("debug_response", {'fail': err})

#Debug 버튼 클릭 이후 PDB 커맨드 입력창에 커맨드 입력시 -> 입력큐를 만들어 PDB출력값 반환
#pdb를 popen으로 열고 readline() 호출하면 block됨
#따라서 입력큐를 만들어 출력 ex) session['debug_str'] = ['s','s']
@socketio.on('debug_input_request')
def debug_input_request(message):
    session_clear = False
    python_v = check_version(message['version'])
    session['debug_str'].append(str(message['data']))
    print (message['data'])
    print ("debug_input_request : python debug_input !!")
    # #세션  출력 (테스트)
    # for i in session:
    #     if i == 'debug_str':  #session['debug_str'] 인 것만 빼냄
    #         print "i :", session[i]

    cmd = [python_v,'-m','pdb','/home/ubuntu/sv_flask/app/userfile/'+session['username']+'.py']
    fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
# 비동기로 설정하는 법?
# # set the O_NONBLOCK flag of p.stdout file descriptor:
# flags = fcntl(p.stdout, F_GETFL) # get current p.stdout flags
# fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)

    inst_stack = [] # 현재까지 디버그된 명령어 스택
    line_stack = [] # 현재까지 디버그된 라인 정보 스택

    for i in session:
        if i == 'debug_str':
            for s in session[i]:
                print (s)
                inst_stack.append(s+"\n")     #명령어 스택에 입력한 문자열 추가
    fd_popen.stdin.writelines(inst_stack)     #pdb subprocess에 입력값 주기!

    result_out, result_err = fd_popen.communicate() #단계 종료

    if message['data'] == 'q' or message['data']=='quit':
        session_clear = True
        print ("Session['debug_str'] Clear !!")
        result_out = result_out + "PDB DEBUGGER Exit!!"

    if result_out != "":
        version = python_version(python_v)
        #version=파이썬버전 / result_out=pdb 결과
        result_out = version + result_out
        #(Pdb) 뒤에 줄바꿈 추가하기위함
        result_out = pdb_line_break(result_out,session['debug_str'])
        result_out = result_out.strip()      #첫번째,마지막 줄바꿈 없앰
        print (result_out)

        #진행 상태가 finished된 상태인지 검사
        finish_state = check_pdb_finished(result_out)

        #.py 패턴을 찾아 라인 정보를 가져옴
        findall = p.findall(result_out)
        print (findall)
        for e in findall:
            string = p_num.search(e)
            line_stack.append(string.group())
        if(len(line_stack)!=0):
            linenum = line_stack[-1] #마지막 원소 접근 -> -1
        else:
            linenum = '-1'

        #사용자로부터 q,quit 입력이 들어왔었으면 -> session_clear True 이니
        #debug_str 세션 비우고 완전종료
        if session_clear == True:
            session['debug_str']=[]
            session_clear = False
            #linnum = -1로 view에서 breakpoint 모두 제거
            linenum = '-1'
            # 종료 alert 설정 on
            finish_state = 0

        emit("debug_input_response", {'data': result_out, 'linenum' : linenum ,
                                      'finish' : finish_state})
    if result_err != "":
        # BdbQuit 네트워크 통신으로 작업할 경우 무조건 뜸
        if re.search('BdbQuit',result_err):
            session['debug_str']=[]
            session_clear = False
            linenum = '-1'
            finish_state = 0
            cmd = [python_v,'-m','pdb','/home/ubuntu/sv_flask/app/userfile/'+session['username']+'.py']
            fd_popen = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            result_out, result_err = fd_popen.communicate() #단계 종료
            version = python_version(python_v)
            result_out = version + 'Debugging Exit ! program will be restarted.\n' + result_out
            emit("debug_input_response", {'data': result_out, "finish" : finish_state })
        else:
            result_err = result_err + "Press any key!!"
            emit("debug_input_response", {'data': result_err})
#check_version으로 python,python3 인지 체크후 대입
#popen으로 version 출력값 구함
def python_version(version):
    fd_popen = subprocess.Popen([version,'/home/ubuntu/sv_flask/app/version.py'],stdout=subprocess.PIPE)
    out = fd_popen.communicate()[0]
    return out
def check_version(str):
    if str in "python 2.7":
        return "python"
    elif str in "python 3.6":
        return "python3"
#콘솔 결과값에 (pdb) 뒤에 줄바꿈 추가함수
def pdb_line_break(str,set_list):
    count = 0
    start = 0 #str pointer
    pdb_str = "(Pdb)"
    while True:
        #찾고자 하는 문자열이 없고 or 사용자 입력큐 list의 크기가 count보다 작거나 같을때 종료
        if str.find(pdb_str,start) == -1 or len(set_list) <= count:
            break
        #찾고자 하는 문자열이 존재하면
        elif str.find(pdb_str,start) != -1:
            pointer = str.find(pdb_str,start)
            pointer += 5 #반환값이 '(' <- 위치 따라서 +5하면 ')' <-를 가리킴
            str = str[:pointer] + " " + set_list[count] +"\n" + str[pointer:]    #str에서 pointer 위치 이전를 선택 / pointer 위치 이후를 선택
            start = pointer
            count += 1
    return str
#결과값에 The program finished and will be restarted -> 종료문구 있는 지 체크 -> 있으면 종료
def check_pdb_finished(str):
    p = re.compile("The program finished and will be restarted")
    string = p.search(str)
    if(string):
        return 1
    else:
        return -1
if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=5000,debug=True)
