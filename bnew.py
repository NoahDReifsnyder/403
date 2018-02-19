#Working Model
from socket import * #using sockets for now, will implement lower level if needed 
import json
import time
from datetime import datetime
from queue import Queue
from threading import Thread,Lock
import _thread as thread
import sys
from random import randint
#############
iplist=None
ops=None
keyrange=None
#to be read from file
#############
mylocks={}#list of keys I HOLD LOCKS FOR 
gotlist={}#list of return k,v pairs from get requests.
faillist={}#to count failed gets
MSGID=0#message identifiers, unique
IDLOC=Lock()#lock to ensure uniqueness for msgid
PUTLOC=Lock()#lock ot esnure uniquenss for putcount
LOCLOCL={}#list of keys and their corresponding locks
SOCLOCL={}#locks for sockets to ensure one read/write at a time
putcount=1#count of puts
mydata={}#internall knowledge
idlist=[]#list of valid message ids
finlist=[]#sockets that are done sending messages
slist=[]#list of sockets
newlist={}#new connections
savelist={}#saving data on closing connection
#globals
###########
def LLS(k):
    global LOCLOCL
    k=str(k)
    if k not in LOCLOCL:
        LOCLOCL[k]=Lock()

def finlen():
    global finlist
    return len(finlist)

def myd():
    global mydata
    print(mydata)

def getput(b):
    global PUTLOC
    global putcount
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
    global IDLOC
    global MSGID
    IDLOC.acquire()
    id=MSGID
    MSGID+=1
    IDLOC.release()
    return id

def readfile():
    global iplist
    global ops
    global keyrange
    data=None
    with open('config.txt','r') as f:
        data=json.load(f)
    iplist=data["ip"]
    ops=data["ops"]
    keyrange=data["keyrange"]

def main(): 
    global slist
    readfile()
    start_up()
    thread.start_new_thread(gencmds,())
    while finlen()<(iplen()+1):
        time.sleep(1)#just for a cleaner run

def start_up():
    global slist 
#list of ip's for my network.Creating connections based on this list. Probably will be read in from a file                      
#I don't have static ip's so will need to update each time I move until I set it up on a AWS
    PORT_NUMBER=5000 #starting port, will iterate up as needed for more connections.
#when we create, we send out requests to connect to all other nodes, then we wait for new nodes to ask us for connection.               
    partition={}#test
    for ip in iplist:
        s=socket(AF_INET,SOCK_STREAM)
        try:
            s.connect((ip,PORT_NUMBER))
            print("connect on",ip)
            slist.append(s)
            SOCLOCL[s]=Lock()
            thread.start_new_thread(listen,(s,))
        except:
            pass
    s=socket(AF_INET,SOCK_STREAM)
    flag=True
    while flag:
        try:
            s.bind((get_ip_address(),PORT_NUMBER))
            print(PORT_NUMBER)
            flag=False
        except:
            time.sleep(1)
            pass
    s.listen(0)
    while len(slist)<(len(iplist)-1):
        conn,addr=s.accept()
        print("connect on",addr[0])
        slist.append(conn)
        SOCLOCL[conn]=Lock()
        thread.start_new_thread(listen,(conn,))
    thread.start_new_thread(cons,(PORT_NUMBER,s,))
    return

def cons(PORT_NUMBER,s):#if new nodes join
    while True:
        conn,addr=s.accept()
        print("connect on",addr)
        addr=addr[0]
        thread.start_new_thread(new,(addr,conn,))
def new(addr,s):
    global newlist
    id=getid()
    addr=str(addr)
    SOCLOCL[s]=Lock()
    msg="ADR"
    for ip in iplist:
        msg+=ip+","
    msg+=addr
    print(msg)
    send(s,msg,id)
    msg="NEW"+addr
    newlist[addr]=0
    for soc in slist:
        send(soc,msg,id)
    while newlist[addr]<iplen():
        pass
    iplist.append(addr)
    slist.append(s)
    listen(s)

def conn(ip):
    PORT_NUMBER=5000
    s=socket(AF_INET,SOCK_STREAM)
    try:
        s.connect((ip,PORT_NUMBER))
        print("connect on",ip)
        slist.append(s)
        SOCLOCL[s]=Lock()
        thread.start_new_thread(listen,(s,))
    except:
        print("failure")

#Protocols
############################
def add(k,s,id):
    while k not in newlist:
        pass
    msg="ADD"+k
    send(s,msg,id)

def adr(k):
    for ip in k.split(","):
        ip=str(ip)
        if ip not in iplist:
            iplist.append(ip)
            if not ip==get_ip_address():
                print('diff')
                conn(ip)

def get(k):
    global slist
    global mydata
    global faillist
    global gotlist
    id=getid()
    k=str(k)
    msg="GET"+str(k)
    if k in mydata:
        return mydata[k]
    for s in slist:
        send(s,msg,id)
    id=str(id)
    length=iplen()
    while not id in faillist or not faillist[id]==length:
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

def put(k,v):
    global mydata
    x=get(k)
    k=str(k)
    b=k not in mydata
    if not x:
        if k not in mydata:
            mydata[k]=v
            return getput(True)
    return getput(False)

def lock(k):
    global slist
    global LOCLOCL
    global mylocks
    k=str(k)
    LLS(k)
    LOCLOCL[k].acquire()
    while k in mylocks:
        pass
    mylocks[k]=0
    LOCLOCL[k].release()
    msg="LCK"+str(k)
    id=getid()
    idlist.append(str(id))
    for s in slist:
        send(s,msg,id)
    return id

def locked(k,s,id):
    global LOCLOCL
    global mylocks
    LLS(k)
    LOCLOCL[k].acquire()
    while k in mylocks:
        pass
    msg="LKD"+str(k)
    send(s,msg,id)
    LOCLOCL[k].release()

def unlock(k):
    global mylocks
    k=str(k)
    if k in mylocks:
        mylocks.pop(k)

def done():
    global slist
    global finlist
    print("Done")
    msg="FIN"
    id=getid()
    for s in slist:
        send(s,msg,id)
    finlist.append("0")

def helper(key):
    id=lock(key)
    wait(key,id)

def close():
    global slist
    global mydata
    global mylocks
    id=getid()
    n=len(slist)
    msg="CLS"
    for s in slist:
        send(s,msg,id)
    i=0
    tl=[]
    print(mydata.keys())
    for key in mydata:
        t=Thread(target=helper,args=(key,))
        tl.append(t)
        t.start()
    for t in tl:
        t.join()
    for key in mydata:
        id=getid()
        msg="PUT"+str(key)+"_"+str(mydata[key])
        print(key,mydata[key])
        send(slist[i],msg,id)
        i+=1
        if i==n:
            i=0
    mydata={}
    mylocks={}
    iplist=[]
    slist=[]
    done()
############################
def parse(mssg,s):
    global mydata
    try:
        msg,id=mssg.split("\x00")
    except ValueError:
        print("Error:",mssg)#corrupted message
        return
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
    elif type=="PUT":
        mydata[k]=v
        print(k,mydata[k])
    elif type=="LCK":
        locked(k,s,id)
    elif type=="LKD":
        if id in idlist:#currently requested lock (time outs)
            mylocks[str(k)]+=1
    elif type=="NEW":
        add(k,s,id)
        pass
    elif type=="ADD":
        newlist[k]+=1
        print(newlist)
        pass
    elif type=="ADR":
        adr(k)
    elif type=="CLS":
        slist.remove(s)
        iplist.remove(str(s.getpeername()[0]))
    elif type=="FIN":
        finlist.append(s)

def wait(key,id):
    key=str(key)
    dt=datetime.now()
    while not mylocks[key]==iplen():
        tn=datetime.now()
        td=tn-dt
        ts=td.total_seconds()
        if ts>1:
            #print('stuck2',mylocks,key) #lock on keys, threads interfeering in to
            a=randint(1,2)
            if a==1:#random chance to give up lock
                idlist.remove(str(id))
                mylocks.pop(key)
                id=lock(key)
                
            dt=datetime.now()

def cmds(i):
    dt=datetime.now()
    a=randint(1,100)
    key=randint(0,keyrange)
    while key in mylocks:
        #print('stuck')
        pass#currently, can't support keeping lock for multiple actions at once, need to reacquire
    value=randint(0,1000000)
    id=lock(key)
    wait(key,id) 
    if a>60:
        c=put(key,value)
        print("Put:",key,c)
    elif a==1:
        close()
    else:
        value=get(key)
        print("Get:",key,value)
    unlock(key)
    #print("Command",i,"of",num)
    td=((datetime.now())-dt).total_seconds()
    return td
    
def gencmds():
    global mydata
    global putcount
    print('doing commands')
    tl=0
    dt=datetime.now()
    for i in range(0,ops):
        if '0' in finlist:
            break
        td=cmds(i)
        tl+=td
    td=datetime.now()-dt
    td=td.total_seconds()
    tp=ops/td
    lt=tl/ops
    print("latency:",lt)
    print("throughput:",tp)
    print("data:",mydata,len(mydata))
    print("puts:",putcount)
    if '0' not in finlist:
        done()

def send(s,msg,id):
    global SOCLOCL
    msg=msg+"\x00"+str(id) #char/x00 splits msg and id
    emsg=msg.encode('utf-8')
    length=len(emsg)
    elength=int_to_bytes(length)
    SOCLOCL[s].acquire()
    s.send(elength)
    s.send(emsg)
    SOCLOCL[s].release()

def listen(s):
    print(s)
    while True:
        l=int_from_bytes(s.recv(1))
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
        if len(msg)>0:
            thread.start_new_thread(parse,(msg,s,))
        else:
            pass
def get_ip_address():#using google to obtain real ip, google most reliable host I know.
    s = socket(AF_INET,SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def int_to_bytes(x):#convert int to bytes to send
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes): #recieved bytes to int 
    return int.from_bytes(xbytes, 'big')

main()#program is loaded, start running
