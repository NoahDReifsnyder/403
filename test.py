#Working Model
from socket import * #using sockets for now, will implement lower level if needed 
import time
from datetime import datetime
from queue import Queue
from threading import Thread,Lock
import _thread as thread
import sys
from random import randint
#iplist=['10.0.0.173','10.0.0.224','10.0.0.39']
save='128.180.133.83'
iplist=['128.180.135.45','128.180.132.69','128.180.132.176']
num=100
keyrange=5
mylocks={}#list of keys I HOLD LOCKS FOR
remlocks={}#list of locked by outside 
gotlist={}#list of return k,v pairs from get requests.
faillist={}#to count failed gets
MSGID=0
IDLOC=Lock()
PUTLOC=Lock()
SOCLOCL={}
putcount=1
mydata={}
finlist=[]
def finlen():
    global finlist
    return len(finlist)
def myd():
    global mydata
    print(mydata)
def getput(b):
    global putcount
    global PUTLOC
    PUTLOC.acquire()
    if not b:
        nput=putcount-1
    else:
        nput=putcount
        putcount+=1
    PUTLOC.release()
    return nput
def iplen():
    global iplist
    return len(iplist)-1
def getid():
    global MSGID
    global IDLOC
    IDLOC.acquire()
    id=MSGID
    MSGID+=1
    IDLOC.release()
    return id
def main(): 
    slist=start_up()
    thread.start_new_thread(gencmds,(slist,))
    for s in slist:
        thread.start_new_thread(listen,(s,))
    while finlen()<(iplen()+1):
        print(finlen(),iplen()+1)
        time.sleep(5)
        pass
def start_up():
    global iplist
    global SOCLOCL
    global remlocks
    slist=[] 
#list of ip's for my network.Creating connections based on this list. Probably will be read in from a file                      
#I don't have static ip's so will need to update each time I move until I set it up on a AWS
    PORT_NUMBER=5000 #starting port, will iterate up as needed for more connections.
#when we create, we send out requests to connect to all other nodes, then we wait for new nodes to ask us for connection.                            
    n=10 #number of nodes, plus a few extra for safety
    partition={}
    for ip in iplist:
        i=PORT_NUMBER
        flag=True
        while i < PORT_NUMBER+n and flag:
            s=socket(AF_INET,SOCK_STREAM)
            try:
                s.connect((ip,i))
                print("connect on",ip)
                slist.append(s)
                flag=False
            except:
                i+=1
    s=socket(AF_INET,SOCK_STREAM)
    flag=True
    while flag:
        try:
            s.bind((get_ip_address(),PORT_NUMBER))
            flag=False
        except:
            PORT_NUMBER+=1
    s.listen(0)
    while len(slist)<(len(iplist)-1):
        conn,addr=s.accept()
        print("connect on",addr)
        slist.append(conn)
    for s in slist:
        remlocks[s]=[]
        SOCLOCL[s]=Lock()
    remlocks[0]=[]
    return slist

#Protocols
############################
def get(k,slist):
    global faillist
    global gotlist
    id=getid()
    msg="GET"+str(k)
    for s in slist:
        send(s,msg,id)
    id=str(id)
    while not id in faillist or not faillist[id]==iplen():
        #print(id, faillist,gotlist)
        if id in gotlist:
            return gotlist.pop(id)
    return None

def got(k,s,id):
    global mydata
    v='\xff'#denotes not found
    k=str(k)
    if k in mydata:
        v=str(mydata[k])
    msg="GOT"+k+"_"+v
    send(s,msg,id)
    pass
def put(k,v,slist):
    global mydata
    x=get(k,slist)
    k=str(k)
    b=k not in mydata
    print(x,b)
    if not x:
        if k not in mydata:
            mydata[k]=v
            return getput(True)
    return getput(False)
def lock(k,slist):
    global remlocks
    k=str(k)
    for s in remlocks:
        while k in remlocks[s]:
            pass
    #remlocks[0].append(k)
    msg="LCK"+str(k)
    id=getid()
    for s in slist:
        send(s,msg,id)
def locked(k,s,id):
    global remlocks
    global LOCLOC
    for soc in remlocks:
        while k in remlocks[soc]:
            pass
    remlocks[s].append(k)
    msg="LKD"+str(k)
    #print(remlocks)
    send(s,msg,id)
    return id
def unlock(k,slist):
    global mylocks
    global remlocks
    id=getid()
    k=str(k)
    while k in mylocks:
        mylocks.pop(k)
    #remlocks[0].remove(k)
    msg="ULK"+str(k)
    for s in slist:
        send(s,msg,id)
    pass
def done(slist):
    msg="FIN"
    id=getid()
    for s in slist:
        send(s,msg,id)
############################
def parse(mssg,s):
    global mylocks
    global locks
    global gotlist
    global faillist
    global mydata
    global finlist
    #print(mssg.encode('utf-8'))
    #print("Got:",mssg)
    try:
        msg,id=mssg.split("\x00")
    except ValueError:
        print("Error:",mssg)
        time.sleep(10)
    type=msg[:3]
    rest=msg[3:]
    k=None
    v=None
    try:
        k,v=rest.split("_")
    except ValueError:
        k=rest
        v=None

    if type=="GET":
        got(k,s,id)
        pass
    elif type=="GOT":
        if v=="\xff":
            if id not in faillist:
                faillist[id]=0
            faillist[id]+=1
        else:
            gotlist[id]=v
        pass
    elif type=="LCK":
        locked(k,s,id)
        pass
    elif type=="LKD":
        if k not in mylocks:
            mylocks[k]=0
        mylocks[k]+=1
        pass
    elif type=="ULK":
        #print(remlocks)
        if k in remlocks[s]:
            remlocks[s].remove(k)
        #print(remlocks)
        pass
    elif type=="FIN":
        print("GET FIN")
        finlist.append(s)

def wait(key,slist,id):
    global mylocks
    global remlocks
    key=str(key)
    while not key in mylocks or not mylocks[key]==iplen():
        pass
def gencmds(slist):
    print('doing commands')
    global num
    global keyrange
    global remlocks
    global mylocks
    for i in range(0,num):
        a=randint(1,2)
        key=randint(0,keyrange)
        if key in mylocks:
            mylocks.pop(key)
        value=randint(0,1000000)
        #print("SCommand:",i,key,remlocks,mylocks)
        id=lock(key,slist)
        #print("LCommand:",i)
        wait(key,slist,id)
        #print("WCommand:",i)
        if a==1:
            #print("put",key,value)
            c=put(key,value,slist)
            print("Put:",c,mydata)
        else:
            #print("get",key)
            value=get(key,slist)
        unlock(key,slist)
        #print("ECommand:",i)
        print("Command",i,"of",num)
    while True:
        #myd()
        #print('here')
        time.sleep(5)
def send(s,msg,id):
    global SOCLOCL
    msg=msg+"\x00"+str(id) #char/x00 splits msg and id
    emsg=msg.encode('utf-8')
    #print("Sending",emsg,msg)
    length=len(emsg)
    elength=int_to_bytes(length)
    SOCLOCL[s].acquire()
    s.send(elength)
    s.send(emsg)
    SOCLOCL[s].release()

def listen(s):
    while True:
        l=int_from_bytes(s.recv(1))
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
        #print("Got:",emsg,msg)
        thread.start_new_thread(parse,(msg,s,))

def get_ip_address():#using google to obtain real ip, google most reliable host I know.
    s = socket(AF_INET,SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def int_to_bytes(x):#convert int to bytes to send
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes): #recieved bytes to int
    return int.from_bytes(xbytes, 'big')
main()
