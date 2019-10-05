#-*- coding:utf-8 -*-
# Format:
#   * None, int, long, float, str, bool - unchanged -> primitive 타입들
#     (json.dumps encodes these fine verbatim)
#   * compound 타입들 저장 형식은 이렇게
#   * list     - ['LIST', unique_id, elt1, elt2, elt3, ..., eltN]
#   * tuple    - ['TUPLE', unique_id, elt1, elt2, elt3, ..., eltN]
#   * set      - ['SET', unique_id, elt1, elt2, elt3, ..., eltN]
#   * dict     - ['DICT', unique_id, [key1, value1], [key2, value2], ..., [keyN, valueN]]
#   * instance - ['INSTANCE', class name, unique_id, [attr1, value1], [attr2, value2], ..., [attrN, valueN]]
#   * class    - ['CLASS', class name, unique_id, [list of superclass names], [attr1, value1], [attr2, value2], ..., [attrN, valueN]]
#   * circular reference - ['CIRCULAR_REF', unique_id]
#   * other    - [<type name>, unique_id, string representation of object]

import collections

#id(data) 값으로 나온값이 Key  |  cur_small_id -> Value

#cur_small_id의 모음 { my_id : cur_small_id} 형식
real_to_small_IDs = collections.OrderedDict()
#임의 주소 -> compound Type 하나를 선언하면 주소 1 이 된다 가정 그 이후 는 ++
cur_small_id = 1
import re, types
# 정규 표현식 뽑아내기
typeRe = re.compile("<type '(.*)'>")
functionRe = re.compile("<function '(.*)'>")
moduleRe = re.compile("<module '(.*)'>")
#classRe = re.compile("<class '(.*)'>")

def encode(data, ignore_id=False):
    def encode_helper(data,compound_obj_ids):
        #primitive type이면 바로 반환
        if data is None or \
            type(data) in (int,long,float,str,bool):
            return data
        #compound type이면 type 파악 후 재귀
        else:
            #data에 id를 부여 (리얼주소?)
            my_id = id(data)
            # 가상의 id ->1부터 줌
            global cur_small_id
            #encode() 함수 호출시 ignore_id - True 주면 모든 id는 99999
            #현재 주소가 real_to_small_IDs에 존재하는 지 확인
            if my_id not in real_to_small_IDs:
                if  ignore_id:
                    #{"myid" = 99999} 이런식으로 저장
                    real_to_small_IDs[my_id] = 99999
                else:
                    real_to_small_IDs[my_id] = cur_small_id
                cur_small_id += 1
            '''
            #순환 REF
            if my_id in compound_obj_ids:
                return ['CIRCULAR_REF',real_to_small_IDs[my_id]]
            '''

            #new_compound에 기존 compound와 my_id 배열 객체를 결합 (합집합임)
            #compound_obj_ids -> ? {} DICT?
            new_compound_obj_ids = compound_obj_ids.union([my_id])
#             print(new_compound_obj_ids)
            #data의 type을 확인 -> 무조건 compound type -> 주소를 가지는 타입이니
            dataType = type(data)

            my_small_id = real_to_small_IDs[my_id]
#             print(my_small_id)

            # for e in data -> data의 길이만큼 돔, e-> 각 인덱스의 튜플,리스트,셋의 '값'들
            # ret.append(encode_helper(e,new_compound_obj_ids))
            # new_compound_obj_ids -> encode에서 부른 id(data) 값을 추가한것
            if dataType == list:
                ret = ['LIST',my_small_id]
                #자료형과 해당 id를 ret에 저장했으니 그다음은? -> 값을 저장해야함!!
                for e in data: ret.append(encode_helper(e,new_compound_obj_ids))
            elif dataType == tuple:
                ret = ['TUPLE',my_small_id]
                for e in data: ret.append(encode_helper(e,new_compound_obj_ids))
            elif dataType == set:
                ret = ['SET',my_small_id]
                for e in data: ret.append(encode_helper(e,new_compound_obj_ids))
            elif dataType == dict:
                ret = ['DICT',my_small_id]
                #dict의 for문은 이렇게
                for (k,v) in data.iteritems():
                    #locals 값은 띄우지 않는다?
                    if k not in ('__module__','__return__'):
                        ret.append([encode_helper(k,new_compound_obj_ids),encode_helper(v,new_compound_obj_ids)])
            else:
                #함수같은 것들
                typeStr = str(dataType)
                m = typeRe.match(typeStr)

                if not m:
                    m = functionRe.match(typeStr)
                    # if not m:
                    #     m = moduleRe.match(typeStr)

                if m != None:
                    #assert m,dataType
                    #m.group() -> <type 'function'>
                    ret = [m.group(1),my_small_id,str(data)]
                else:
                    ret = ["undefined",my_small_id,"undefined"]
            '''
            #Class , INSTANCE 처리 해야함
            elif dataType in (types.InstanceType,types.ClassType,types.TypeType) or \
               classRe.match(str(dataType)):
                if dataType == types.InstanceType or classRe.match(str(dataType)):
                    ret = ['INSTANCE',data.__class__.__name__,my_small_id]
                else:
                    #__bases__ -> superclass를 출력해줌 e.__name__ -> data의 superclass의 이름
                    superclass_names = [e.__name__ for e in data.__bases__]
                    ret = ['CLASS',data.__name__,my_small_id,superclass_names]

                user_attrs = sorted([e for e in data.__dict__.key()
                                    if e not in ('__doc__','__module__','__return__')])
                for attr in user_attrs:
                    ret.append([encode_helper(attr,new_compound_obj_ids),encode_helper(data.__dict__[attr],new_compound_obj_ids)])'''
#             print(ret)
            return ret
    return encode_helper(data,set())

if __name__=='__main__':

        def test(actual,expected=0):
            import sys
            #라인 번호 가져옴 -> test() 함수가 불린 라인 위치
            linenum = sys._getframe(1).f_lineno
            print ("actual : %s, expected : %s " % (str(actual),str(expected)))
            if(actual == expected):
                msg = "Test on line %s success" % linenum
            else:
                msg = "Test oon line %s fail Expected '%s', but got '%s'." % (linenum,expected,actual)
            print (msg)

        #Primitive Type들은 인자 타입을 확인한 뒤 넣은 그대로 반환함!
        print ("Primitive Type 테스트!!")
        test(encode("hello"),"hello")
        test(encode(123),123)
        test(encode(123.45),123.45)
        test(encode(132432134423143132432134423143),132432134423143132432134423143)
        test(encode(False),False)
        test(encode(None),None)

        #튜플 테스트
        print ("TUPLE 테스트 !!")
        test(encode(((1,2),(2,3))),['TUPLE',1,['TUPLE', 2, 1, 2], ['TUPLE', 3, 2, 3]])

        #DICT 테스트
        print ("DICT 테스트 !!")
        test(encode({1:'mon'}), ['DICT', 4 , [1, 'mon']])

        #함수 테스트
        print ("Method 테스트 !!")
        test(encode(test),['function',5,'test'])
        #더 테스트 해야함
        #range(1,3) 의 반환값 (1,2) 가 나와서 LIST로 나옴
        test(encode(range(1,3)),['range',6,'range(1,3)'])

        print(encode({"stdout": "", "func_name": "<module>", "globals": {"sum": 0, "friends": ["LIST", 1, "Joe", "Bill"], "length": 3, "f": "Joe"}, "stack_locals": [], "line": 7, "event": "step_line"}))
