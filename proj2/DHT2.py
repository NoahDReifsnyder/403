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
closeable=None
NPut=1
###############################
slist={}
outfile=open("out.txt","w")
###############################
IDLOC=Lock()
MSGID=0
LTL=[]
SOCLOCL={}
waitList={}
waitListL=Lock()
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
    print("listening on "+str(s))
    while True:
        l=int_from_bytes(s.recv(1))
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
        if len(msg)==0:
            break
        try:
            msg,id=msg.split("/x00")
        except:
            print("error:",msg,len(msg))
        if msg=="CLS":
            break
        parse(msg,id)
def parse(msg,id,s):
    type=msg[:3]
    rest=msg[3:]
    k=None
    v=None
    try:
        k,v=rest.split("_")
        print(k,v,id,casehandler[type])
        casehandler[type](k,v,s,id) 
    except ValueError:
        k=rest
        print(k,id,casehandler[type])
        casehandler[type](k,s,id)
    
def done():
    msg="CLS"
    id=getid()
    send(msg,-1,id)
    for t in LTL:
        t.join()
    
def gencmds():
    tlist=[]
    for i in range(0,ops):
        t=Thread(target=cmds,args=(i,))
        t.start()
        tlist.append(t)
    for t in tlist:
        t.join()
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
    print("\n\n\n\n\n\n\n\n\n\nThis is the output for node",priv_ip,pub_ip)
    readfile()
    start_up()
    gencmds()
    #print(slist)
    done()
    closeall()
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
    parse(msg,id,sendself)
    pass
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
    global closeable
    data=None
    with open('config.txt','r') as f:
        data=json.load(f)
        iplist=data["ip"]
        ops=data["ops"]
        keyrange=data["keyrange"]
        closeable=data["closeable"]
            
def getid():
    global IDLOC
    global MSGID
    IDLOC.acquire()
    id=MSGID
    MSGID=MSGID+1
    IDLOC.release()
    return str(id)


def put():#handles none,sends put
    key=randint(0,keyrange)
    value=randint(0,100000000)
    id=getid()
    msg="PUT"+str(key)+"_"+str(value)
    lock(key,id)
    send(msg,key,id)
def get():#handles none, sends get    
    key=randint(0,keyrange)
    id=getid()
    msg="GET"+str(key)
    send(msg,key,id)
def lock(k,id):#handles none, sends lck
    msg="LCK"+str(k)
    send(msg,k,id)
def unlock(k):#handles none, sends ulk
    pass
def puth(k,v,s,id):#handles put, sends nothing
    pass
def geth(k,s,id):#handles get,sends got
    pass
def lckh(k,s,id):#handles lck, sends lkd,nlk
    pass
def ulkh(k,s,id):#handles ulk, sends nothing
    pass
def goth(v,s,id):#handles got, sends nothig
    pass
def lkdh(k,s,id):#handles lkd, sends nothing
    pass
def nlkh(k,s,id):#handles nlk, sends nothing
    pass
#send put get lck ulk got lkd nlk
#hand put get lck ulk got lkd nlk
casehandler={"PUT":puth,"GET":geth,"LCK":lckh,"ULK":ulkh,"GOT":goth,"LKD":lkdh,"NLK":nlkh}
def print(*string):
    for s in string:
        outfile.write(str(s))
        outfile.write(" ")
    outfile.write('\n')
main()
