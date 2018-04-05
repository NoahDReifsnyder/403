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
###############################
slist=[]
outfile=open("out.txt","w")
###############################
IDLOC=Lock()
MSGID=0
LTL=[]
def start_up():
    print("starting")
    global slist
    global LTL
    PORT_NUMBER=5000
    for ip in iplist:
        s=socket(AF_INET,SOCK_STREAM)
        for i in range(0,100):
            try:
                s.connect((ip,PORT_NUMBER+i))
                slist.append(s)
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
        slist.append(conn)
        t=Thread(target=listen, args=(conn,))
        t.start()
        LTL.append(t)
    s.close()

def listen(s):
    print("listening on "+str(s))
    while True:
        l=int_from_bytes(s.recv(1))
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
        msg,id=msg.split("/x00")
        if msg=="CLS":
            break
        if len(msg)>0:
            pass
        else:
            break
def done():
    msg="CLS"
    send(msg,slist)
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
    print("this is command:",i)
    a=randint(0,100)
    if a<=60:
        get()
    elif a>80:
        put()
    else:
        putmult(3)

def put():
    key=randint(0,keyrange)
    value=randint(0,100000000)
    msg="PUT"+str(key)+"_"+str(value)
    send(msg,slist)
def get():    
    key=randint(0,keyrange)
    msg="GET"+str(key)
    send(msg,slist)
    
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
    #gencmds()
    #print(slist)
    done()
    closeall()
def send(msg,socs):
    msg=msg+"/x00"+getid()
    emsg=msg.encode('utf-8')
    length=len(emsg)
    elength=int_to_bytes(length)
    for s in socs:
        s.send(elength)
        s.send(emsg)
def closeall():
    for s in slist:
        s.close()
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
main()
