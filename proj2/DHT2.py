from socket import *
import requests
import json
import time
from datetime import datetime
from queue import Queue
from threading import Thread,Lock
import _thread as thread
import sys
from random import randint
import requests

###############################
iplist=None
ops=None
keyrange=None
closeable=None
###############################
slist=[]
outfile=open("out.txt","w")
MYIP = requests.get('https://api.ipify.org').text
###############################
IDLOC=Lock()
MSGID=0
def start_up():
    for ip in iplist:
        VCLOCK[ip]=0
    print("starting")
    global slist
    PORT_NUMBER=5000
    for ip in iplist:
        s=socket(AF_INET,SOCK_STREAM)
        for i in range(0,100):
            try:
                s.connect((ip,PORT_NUMBER+i))
                slist.append(s)
                t=Thread(target=listen, args=(s,))
                t.start()
                #t.join()
                break
            except:
                continue
    s=socket(AF_INET,SOCK_STREAM)
    for i in range (0,100):
        try:
            s.bind((get_ip_address(),PORT_NUMBER+i))
            break
        except:
            continue
    s.listen(1)
    while slistlen()<iplistlen():
        conn,addr=s.accept()
        slist.append(conn)
        t=Thread(target=listen, args=(conn,))
        t.start()
        #t.join()
    s.close()

def listen(s):
    print("listening on "+str(s))
    '''while False:
        l=int_from_bytes(s.recv(1))
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
        if len(msg)>0:
            pass
        else:
            break'''

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
    send(msg)
def get():    
    key=randint(0,keyrange)
    msg="GET"+str(key)
    send(msg)
    
def putmult(num):#need to parrellel this
    for i in range(num):
        tlist=[]
        t=Thread(target=put)
        tlist.append(t)
        t.start()
    for t in tlist:
        t.join()
def main():
    print("\n\n\n\n\n\n\n\n\n\nThis is the output for node "+MYIP)
    readfile()
    start_up()
    gencmds()
    #print(slist)
    closeall()
def send(msg):
    msg=msg+"/x00"+getid()
    print(msg)
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
    with open('/home/ubuntu/403/proj2/config.txt','r') as f:
        data=json.load(f)
        iplist=data["ip"]
        ops=data["ops"]
        keyrange=data["keyrange"]
        closeable=data["closeable"]
def get_ip_address():#using google to obtain real ip, google most reliable host I know.
    s = socket(AF_INET,SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
            
def getid():
    global IDLOC
    global MSGID
    IDLOC.acquire()
    id=MSGID
    MSGID=MSGID+1
    IDLOC.release()
    return str(id)                                
main()
