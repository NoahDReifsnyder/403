from socket import * #using sockets for now, will implement lower level if needed 
import time
from queue import Queue
from threading import Thread,Lock
import _thread as thread
import sys
from random import randint
iplist=['10.0.0.173','10.0.0.224','10.0.0.39']
num=5
keyrange=100
mylocks={}#list of keys I HOLD LOCKS FOR
remlocks=[]#list of locked by outside 
gotlist={}#list of return k,v pairs from get requests.
faillist={}#to count failed gets
MSGID=0
IDLOC=Lock()
mydata={}
def iplen():
    global iplist
    return len(iplist)
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
    time.sleep(1)
    thread.start_new_thread(gencmds,(slist,))
    print(get_ip_address())
    '''for s in slist:
        thread.start_new_thread(listen,(s,))
    '''
    time.sleep(5)
    shut_down(slist)
def start_up():
    global iplist
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
    return slist

def shut_down(slist):
    for s in slist:
        s.close()
        slist.remove(s)
#Protocols
############################
def get(k,slist):
    id=getid()
    msg="GET"+k
    for s in slist:
        send(s,msg,id)
    while id not in faillist or not faillist[id]==iplen():
        if id in gotlist:
            return gotlist.pop(id)
    return None

def got(k,s,id):
    global mydata
    v='\xff'#denotes not found
    if k in mydata:
        v=mydata[k]
    msg="GOT"+k+"_"+v
    send(s,msg,id)
    pass
def put(k,v,slist):
    global mydata
    x=get(k)
    if not x:
        mydata[k]=v
        return True
    return False
def lock(k,slist):
    msg="LCK"+k
    id=getid()
    for s in slist:
        send(s,msg,id)
def locked(k,s,id):
    global remlocks
    while k in remlocks or k in mylocks:
        pass
    remlocks.append(k)
    msg="LKD"+k
    send(s,msg,id)
    pass
def unlock(k,slist):
    global mylocks
    id=getid()
    mylocks.pop(k)
    msg="ULK"+k
    for s in slist:
        send(s,msg,id)
    pass
############################
def parse(mssg,s):
    global mylocks
    global locks
    global gotlist
    global faillist
    msg,id=mssg.split("\x00")
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
        got(k,id)
        pass
    elif type=="GOT":
        if v=="/xff":
            if v not in faillist:
                faillist[v]=0
            faillist[v]+=1
        else:
            gotlist[id]=v
        pass
    elif type=="LCK":
        locked(k,s)
        pass
    elif type=="LKD":
        if k not in mylocks:
            mylocks[k]=0
        mylocks[k]+=1
        pass
    elif type=="ULK":
        remlocks.remove(k)
        pass


def wait(key):
    global mylocks
    while not mylocks[k]==iplen():
        pass

def gencmds(slist):
    global num
    global keyrange
    for i in range(0,num):
        a=randint(1,2)
        key=randint(0,keyrange)
        value=randint(0,1000000)
        lock(key,slist)
        wait(key)
        if a==1:
            put(key,value,slist)
        else:
            get(key,slist)
        unluck(key,slist)
def send(s,msg,id):
    msg=msg+"\x00"+id #char/x00 splits msg and id
    emsg=msg.encode('utf-8')
    length=len(emsg)
    elength=int_to_bytes(length)
    s.send(elength)
    s.send(emsg)

def listen(s):
    while True:
        l=int_from_bytes(s.recv(1))
        emsg=s.recv(l)
        msg=emsg.decode('utf-8')
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
