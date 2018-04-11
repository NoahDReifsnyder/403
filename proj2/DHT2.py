from socket import *
import json
import time
from datetime import datetime
from queue import Queue
from threading import Thread,Lock
import _thread as thread
import sys
from random import randint
import urllib.request
ts = socket(AF_INET,SOCK_DGRAM)
ts.connect(("8.8.8.8", 80))
priv_ip=ts.getsockname()[0]
ts.close()
pub_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
###############################
iplist=None
ops=None
keyrange=None
NPut=None#how many nodes to store each key on (Put in config file)
###############################
slist={}
outfile=open("out.txt","w")
###############################
IDLOC=Lock()
MSGID=0
LTL=[]
SOCLOCL={}
keyLocs={}
keyLocL=Lock()
gwaitList={}
gwaitListL=Lock()
uwaitList={}
uwaitListL=Lock()
waitList={}
waitListL=Lock()
cls=0
clsL=Lock()
myData={}
def start_up():
    print("starting")
    global slist
    global LTL
    global SOCLOCL
    PORT_NUMBER=5000
    for ip in iplist:
        if ip==pub_ip:
            continue
        s=socket(AF_INET,SOCK_STREAM)
        for i in range(0,100):
            try:
                s.connect((ip,PORT_NUMBER+i))
                num=int(iplist[ip])
                slist[num]=s
                SOCLOCL[s]=Lock()
                t=Thread(target=listen, args=(s,))
                t.start()
                LTL.append(t)
                break
            except:
                continue
    s=socket(AF_INET,SOCK_STREAM)
    for i in range (0,100):
        try:
            s.bind((priv_ip,PORT_NUMBER+i))
            break
        except:
            continue
    s.listen(1)
    while slistlen()<iplistlen():
        conn,addr=s.accept()
        num=int(iplist[addr[0]])
        slist[num]=conn
        SOCLOCL[conn]=Lock()
        t=Thread(target=listen, args=(conn,))
        t.start()
        LTL.append(t)
    
    mynum=int(iplist[pub_ip])
    slist[mynum]=sendself
    s.close()

def listen(s):
    global cls
    print("listening on "+str(s))
    flag=True
    s.settimeout(1)
    while flag:
        try:
            l=int_from_bytes(s.recv(1))
        except:
            if not cls<slistlen():
                flag=False
            continue
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
        if len(msg)==0:
            break
        try:
            msg,id=msg.split("/x00")
        except:
            print("error:",msg,len(msg))
        if msg[:3]=="CLS":
            clsL.acquire()
            cls=cls+1
            clsL.release()
            if not cls<slistlen():
                flag=False
            continue
        thread.start_new_thread(parse,(msg,id,s,))
def parse(msg,id,s):
    type=msg[:3]
    rest=msg[3:]
    k=None
    v=None
    try:
        k,v=rest.split("_")
        #print(k,v,id,casehandler[type],keyLocs)
        casehandler[type](k,v,s,id) 
    except ValueError:
        k=rest
        #print(k,id,casehandler[type],keyLocs)
        casehandler[type](k,s,id)
    
def done():
    msg="CLS"
    id=getid()
    send(msg,-1,id)
    while cls<slistlen():
        #print(cls)
        time.sleep(1)
    print("WERE DONE NOW")
    
def gencmds():
    tlist=[]
    for i in range(0,ops):
        t=Thread(target=cmds,args=(i,))
        t.start()
        #t.join()
        tlist.append(t)
    counter=ops
    for t in tlist:
        t.join()
        #print("JOINED UP BOI",counter)
        counter=counter-1
    print("all cmds done")
def cmds(i):
    #print("this is command:",i)
    a=randint(0,100)
    if a<=60:
        get()
    elif a>80:
        put()
    else:
        putmult(3)
def putmult(num):#need to parrellel this
    for i in range(num):
        tlist=[]
        t=Thread(target=put)
        tlist.append(t)
        t.start()
    for t in tlist:
        t.join()
def main():
    global NPut
    print("\n\n\n\n\n\n\n\n\n\nThis is the output for node",priv_ip,pub_ip)
    readfile()
    if NPut>iplistlen():
        NPut=iplistlen()+1
    print(NPut)
    start_up()
    gencmds()
    time.sleep(1)
    done()
    closeall()
    print("main finished")
def hashf(key):
    if key==-1:
        return slist.keys()
    num=key%slistlen()
    lis=[num]
    while len(lis)<NPut:
        num=num+1
        if num==slistlen():
            num=0
        lis.append(num)
    return lis
def sendself(msg,id):
    global cls
    if msg[:3]=="CLS":
        clsL.acquire()
        cls=cls+1
        clsL.release()
    else:
        thread.start_new_thread(parse,(msg,id,sendself,))
def send(msg,key,id,s=None):
    if not s:
        lis=hashf(key)
        socs=[]
        for n in lis:
            socs.append(slist[n])
    else:
        socs=[s]
    lmsg=msg+"/x00"+str(id)
    emsg=lmsg.encode('utf-8')
    length=len(emsg)
    elength=int_to_bytes(length)
    for s in socs:
        if hasattr(s,'__call__'):
            s(msg,id)
        else:
            SOCLOCL[s].acquire()
            s.send(elength)
            s.send(emsg)
            SOCLOCL[s].release()
def closeall():
    for s in slist:
        if not hasattr(slist[s],'__call__'):
            slist[s].close()
def slistlen():
    return len(slist)
def iplistlen():
    return len(iplist)-1
def int_to_bytes(x):#convert int to bytes to send
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
def int_from_bytes(xbytes): #recieved bytes to int
    return int.from_bytes(xbytes, 'big')
def readfile():
    global iplist
    global ops
    global keyrange
    global NPut
    data=None
    with open('config.txt','r') as f:
        data=json.load(f)
        iplist=data["ip"]
        ops=data["ops"]
        keyrange=data["keyrange"]
        NPut=data["NPut"]
            
def getid():
    global IDLOC
    global MSGID
    IDLOC.acquire()
    id=MSGID
    MSGID=MSGID+1
    id=id*slistlen()
    id=id+iplist[pub_ip]
    IDLOC.release()
    return str(id)


def put():#handles none,sends put
    key=randint(0,keyrange)
    value=randint(0,100000000)
    id=getid()
    msg="PUT"+str(key)+"_"+str(value)
    while not lock(key,id):
        #print(1)
        unlock(key,id)
        id=getid()
        ti=randint(1,10)#Random wait cures livelock
        time.sleep(ti/10)
    send(msg,key,id)
    #print("PUT",key,value)
def get():#handles none, sends get    
    key=randint(0,keyrange)
    id=getid()
    msg="GET"+str(key)
    gwaitListL.acquire()
    gwaitList[id]=None
    gwaitListL.release()
    send(msg,key,id)
    while not gwaitList[id]:
        pass
    v=gwaitList[id]
    gwaitList.pop(id)
    '''if v=="\xff":
        print("Key not yet placed")
    else:
        print("GOT",key,v)'''
def lock(k,id):#handles none, sends lck
    msg="LCK"+str(k)
    waitListL.acquire()
    waitList[id]=0
    waitListL.release()
    send(msg,k,id)
    while id in waitList and waitList[id]<NPut:
        #print(2,id,waitList)
        time.sleep(.1)
    if id in waitList:
        waitList.pop(id)
        return True
    else:
        return False
def unlock(k,id):#handles none, sends ulk
    msg="ULK"+str(k)
    uwaitListL.acquire()
    uwaitList[id]=0
    uwaitListL.release()
    send(msg,k,id)
    while uwaitList[id]<NPut:
        #print(3,id,uwaitList)
        time.sleep(.1) 
    uwaitList.pop(id)
def puth(k,v,s,id):#handles put, sends nothing
    if k in keyLocs and keyLocs[k]==id:
        myData[k]=v
        keyLocs.pop(k)
    else:
        print("BAD PUT BAD PUT")
    pass
def geth(k,s,id):#handles get,sends got
    if k in myData:
        msg="GOT"+str(myData[k])
    else:
        msg="GOT"+"\xff"
    send(msg,k,id,s)
    pass
def lckh(k,s,id):#handles lck, sends lkd,nlk
    keyLocL.acquire()
    if k in keyLocs:
        msg="NLK"+str(k)
        pass
    else:
        msg="LKD"+str(k)
        keyLocs[k]=id
        pass
    keyLocL.release()
    send(msg,k,id,s)
    pass
def ulkh(k,s,id):#handles ulk, sends uld
    msg="ULD"+str(k)
    if k in keyLocs and keyLocs[k]==id:
        keyLocs.pop(k)
    send(msg,k,id,s)
    pass
def uldh(k,s,id):#handles uld, sends nothing
    uwaitListL.acquire()
    uwaitList[id]=uwaitList[id]+1
    uwaitListL.release()
def goth(v,s,id):#handles got, sends nothig
    gwaitListL.acquire()
    if id in gwaitList:
        gwaitList[id]=v
    gwaitListL.release()
    pass
def lkdh(k,s,id):#handles lkd, sends nothing
    waitListL.acquire()
    if id in waitList:
        waitList[id]=waitList[id]+1
    waitListL.release()
    pass
def nlkh(k,s,id):#handles nlk, sends nothing
    waitListL.acquire()
    if id in waitList:
        waitList.pop(id)
    waitListL.release()
    pass
#send put get lck ulk got lkd nlk
#hand put get lck ulk got lkd nlk
casehandler={"PUT":puth,"GET":geth,"LCK":lckh,"ULK":ulkh,"GOT":goth,"LKD":lkdh,"NLK":nlkh,"ULD":uldh}
def print(*string):
    for s in string:
        outfile.write(str(s))
        outfile.write(" ")
    outfile.write('\n')
    outfile.flush()
main()
print("We out")
print(myData)
#outfile.close()
