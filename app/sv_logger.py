#-*- coding:utf-8 -*-
#무한루프 방지
MAX_EXECUTED_LINES = 200

def set_max_executed_lines(m):
    global MAX_EXECUTED_LINES
    MAX_EXECUTED_LINES = m

import sys
import bdb # 가장 중요한 import
import os
import re
import traceback

import cStringIO
import sv_encoder

import collections

IGNORE_VARS = set(('__stdout__', '__builtins__', '__name__', '__exception__','__doc__', '__package__'))

#stdout 값 출력 -> frame의 globals 변수의 __stdout__ 값 가져옴
#trace_entry의 6번째(마지막) value
def get_user_stdout(frame):
    my_user_stdout = frame.f_globals['__stdout__']
    return my_user_stdout.getvalue()

#global 변수 가져오는데 ignore_vars 제외한 dict를 반환
def get_user_globals(frame):
    d = filter_var_dict(frame.f_globals)
    # also filter out __return__ for globals only, but NOT for locals
    if '__return__' in d:
        del d['__return__']
    return d

#local 변수 가져오기 ignore_vars 제외한 dict 반환
def get_user_locals(frame):
    return filter_var_dict(frame.f_locals)

def filter_var_dict(d):
    ret = collections.OrderedDict()
    for (k,v) in d.items():
        if k not in IGNORE_VARS:
            ret[k] = v
    return ret

#bdb.Bdb를 상속 받은 PGLogger
class PGLogger(bdb.Bdb):
    #생성자
    def __init__(self, finalizer_func, ignore_id=False):
        bdb.Bdb.__init__(self)
        self.mainpyfile=''
        self._wait_for_mainpyfile = 0

        self.finalizer_func = finalizer_func

        self.trace = []

        self.ignore_id = ignore_id

    def reset(self):
        bdb.Bdb.reset(self)
        self.forget()

    def forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None
    #그 이유는 a.setdata(4, 2)처럼 호출하면 setdata 메서드의 첫 번째 매개변수 self에는
    #setdata메서드를 호출한 객체 a가 자동으로 전달
    def setup(self,f,t):
        self.forget()
        self.stack, self.curindex = self.get_stack(f,t)
        self.curframe = self.stack[self.curindex][0]

    #Override Bdb 함수 -> 여러 event가 발생할때 각각 자동호출됨!
    #when there is the possibility that a break might be necessary
    #anywhere inside the called function.
    def user_call(self, frame, argument_list):
        if self._wait_for_mainpyfile:
            return
        if self.stop_here(frame):
            #해당 exception이 일어났을 때 interaction실행
            self.interaction(frame, None, 'call')
    #when either stop_here() or break_here()
    def user_line(self, frame):
        """This function is called when we stop or break at this line."""
        if self._wait_for_mainpyfile:
            #canonic( 파일명 ) 표준 형식으로 파일 이름을 얻는 보조 방법.
            #즉, 대소 문자를 구분하지 않는 파일 시스템의 경우 절대 경로로 대괄호를 제거합니다
            #frame.f_lineno -> 현재 프레임의 라인정보
            # 파일이름이 <string>으로 시작하지 않으면 바로 종료때림
            if (self.canonic(frame.f_code.co_filename) != "<string>" or
                frame.f_lineno <= 0):
                return

            self._wait_for_mainpyfile = 0
        #해당 exception이 일어났을 때 interaction실행
        self.interaction(frame, None, 'step_line')
    #when stop_here()
    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        #frame의 로컬 변수 __return__ 값을 변경
        frame.f_locals['__return__'] = return_value
         #해당 exception이 일어났을 때 interaction실행
        self.interaction(frame, None, 'return')
    #when stop_here()
    def user_exception(self, frame, exc_info):
        exc_type, exc_value, exc_traceback = exc_info
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""
        #frame의 로컬 변수 __exception__ 값을 변경
        frame.f_locals['__exception__'] = exc_type, exc_value
        if type(exc_type) == type(''):
            exc_type_name = exc_type
        else:
            exc_type_name = exc_type.__name__
        #해당 exception이 일어났을 때 interaction실행
        self.interaction(frame, exc_traceback, 'exception')

    #interaction 함수!!
    def interaction(self, frame, traceback, event_type):
        #위의 setup 함수 불림
        self.setup(frame, traceback)
        #현재 index에 위치한 stack 정보 가져옴
        tos = self.stack[self.curindex]
        top_frame = tos[0]
        lineno = tos[1] #trace_entry의 첫번째 value,
        #event_type -> trace_entry의 두번째 value
        #func_name = tos[0].f_code.co_name -> trace_entry의 세번째 value

        if self.canonic(top_frame.f_code.co_filename) != '<string>':
            return
        # also don't trace inside of the magic "constructor" code
        if top_frame.f_code.co_name == '__new__':
            return
        # or __repr__, which is often called when running print statements
        if top_frame.f_code.co_name == '__repr__':
            return

        #local 변수 list
        encoded_stack_locals = [] #trace_entry의 5번째 value

        i = self.curindex
        while True:
            cur_frame = self.stack[i][0]
            cur_name = cur_frame.f_code.co_name
            if cur_name == '<module>':
                break

            if cur_name == '<lambda>':
                cur_name = 'lambda on line' + str(cur_frame.f_code.co_firstlineno)
            elif cur_name =='':
                cur_name = 'unnamed function'

            encoded_locals = collections.OrderedDict()
            for (k,v) in get_user_locals(cur_frame).iteritems():
                #__module 제외하고
                if k != '__module__':
                    encoded_locals[k] = sv_encoder.encode(v, self.ignore_id)

            encoded_stack_locals.append((cur_name,encoded_locals))
            i -= 1
        #while문 종료
        #global 변수
#         print(get_user_globals(tos[0]))
#         print(tos[0].f_globals)
        encoded_globals = collections.OrderedDict() # trace_entry의 4번째 value
        for (k,v) in get_user_globals(tos[0]).iteritems():
            #sv_encoder -> (1,2) 이런 형식을 ('LIST',addr,val1,val2) 식으로 만듬
            encoded_globals[k] = sv_encoder.encode(v, self.ignore_id)

        trace_entry = collections.OrderedDict()
        trace_entry['line'] = lineno
        trace_entry['event'] = event_type
        trace_entry['func_name'] = tos[0].f_code.co_name
        trace_entry['_globals'] = encoded_globals
        trace_entry['stack_locals'] = encoded_stack_locals
        trace_entry['stdout'] = get_user_stdout(tos[0])

#         trace_entry = dict(line=lineno,
#                          event=event_type,
#                          func_name=tos[0].f_code.co_name,
#                          _globals=encoded_globals,
#                          stack_locals=encoded_stack_locals,
#                          stdout=get_user_stdout(tos[0]))

        #event_type이 예외처리 이면 예외 메시지 추가해준것
        if event_type == 'exception':
            exc = frame.f_locals['__exception__']
            trace_entry['exception_msg'] = exc[0].__name__ + ': ' + str(exc[1])

        #trace -> trace_entry의 배열에 event_type이 발생할때마다 추가추가!!
        self.trace.append(trace_entry)

        if len(self.trace) >= MAX_EXECUTED_LINES:
            self.trace.append(dict(event='instruction_limit_reached',
                                  exception_msg=' (stopped after) '+str(MAX_EXECUTED_LINES)+' steps to prevent possible infinite while loop'))
            sys.exit(0) # 실행 종료

        #초기화
        self.forget()
        #interaction 끝
        # 예제 소스코드 bdb실행함수
    def _runscript(self, script_str):
        # 실행되면 1로 세팅 -> user_line에서 검사후 0으로 바뀌어짐
        self._wait_for_mainpyfile = 1

        #sandbox? 아직 구현 못함

        user_builtins = collections.OrderedDict()
        for (k,v) in __builtins__.iteritems():
            # print(k)
            # print(v)
            user_builtins[k] = v

        #StringIO  는 파일처럼 흉내내는 객체 -> 문자열 데이터를 파일로 저장한다음 처리
        #stdout = sys.stdout # 표준 출력 파일 저장해 두기
        #sys.stdout = f = StringIO.StringIO()    # 출력 파일 방향 전환
        #print 'Sample output'
        #sys.stdout = stdout # 표준 출력 복구
        #s = f.getvalue()    # 내부 문자열 가져오기
        #print s
        user_stdout = cStringIO.StringIO()
        sys.stdout = user_stdout

        user_globals = {"__name__" : "__main__",
                       "__builtins__" : user_builtins,
                       "__stdout__" : user_stdout}

        try:
            # bdp를 실행시킨것
            self.run(script_str, user_globals, user_globals)
        except SystemExit:
            raise bdb.BdbQuit
#         #다른 어떤 오류가 발생할때
#         except Exception:
#             trace_back = sys.exc_info()
#             trace_entry = collections.OrderedDict()
#             trace_entry['line'] = format(trace_back[2].tb_lineno)
#             trace_entry['event'] = 'uncaught_exception'
#             trace_entry['exception_type'] = str(trace_back[0])
#             trace_entry['message'] = str(trace_back[1])
#             trace_entry['filename'] = __file__
#             self.trace.append(trace_entry)

# #             trace_entry = dict(event='uncaught_exception')

# #             self.trace.append(trace_entry)
# #             self.finalize()
#             return

    #최종 검사 단계 -> 라인수 초과되진 않았는지 검사
    def finalize(self):
        '''
        필자는 "인터프리터의 출력"을 통해, 콘솔이나 터미널 창에 출력되는 출력을 의미합니다
        (예 : print ()로 생성 된 출력).
        파이썬에 의해 생성 된 모든 콘솔 출력은 프로그램의
        출력 스트림 sys.stdout (일반 출력) 에 기록됩니다.
        이것들은 파일과 같은 객체입니다.
        '''
        sys.stdout = sys.__stdout__
        assert len(self.trace) <= (MAX_EXECUTED_LINES + 1)

        # filter all entries after 'return' from '<module>', since they
        res = []
        for e in self.trace:
            res.append(e)
            # 종료
            if e['event'] == 'return' and e['func_name'] == '<module>':
                break

        self.trace = res

        #모든 과정의 가장 마지막에 실행됨
        self.finalizer_func(self.trace)
#PGLogger 끝

#Main 메소드!! 실행 핵심 메소드
#finalizer_func는 자신이 원하는 함수로 ex) 결과값을 출력한다던지 or 리턴값으로 결과를 내보낸다던지
# script_str -> 예제 소스코드 등등
def exec_script_str(script_str,finalizer_func,ignore_id=False):
    logger = PGLogger(finalizer_func,ignore_id)
    sv_encoder.cur_small_id = 1
    sv_encoder.real_to_small_IDs = collections.OrderedDict()
    logger._runscript(script_str)
    logger.finalize()

#얘는 로그 찍기 위한 pretty prrint 임
#실제로 서버 파일인 app.py에선 이 함수 안씀 -> 따로 구현
def exec_file_and_pretty_print(mainpyfile):
    import pprint

    if not os.path.exists(mainpyfile):
        print ('Error:', mainpyfile, 'does not exist')
        sys.exit(1)

    def pretty_print(output_lst):
        for e in output_lst:
            pprint.pprint(e)

    #print str(open(mainpyfile).read())
    output_lst = exec_script_str(open(mainpyfile).read(), pretty_print)

if __name__ == '__main__':
    import pg_logger
    pg_logger.exec_file_and_pretty_print(sys.argv[1])
