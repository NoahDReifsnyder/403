from socket import * #using sockets for now, will implement lower level if needed 
import time
from queue import Queue
from threading import Thread
import _thread as thread
import sys
from random import randint
num=5
keyrange=100
mylocks={}#list of keys I HOLD LOCKS FOR
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
    slist=[]
    iplist=['10.0.0.173','10.0.0.224','10.0.0.39'] 
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
    msg="GET"+k
    for s in slist:
        send(s,msg)
def got(v,s):
    msg="GOT"+v
    send(s,msg)
    pass
def put(k,v,slist):
    x=get(k)
    msg="PUT"+k+"_"+v
    pass
def lock(k,slist):
    msg="LCK"+k
    for s in slist:
        send(s,msg)
def locked(k,s):
    msg="LKD"+k
    send(s,msg)
    pass
def unlock(k,slist):
    msg="ULK"+k
    for s in slist:
        send(s,msg)
    pass
############################
def parse(msg):
    global mylocks
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
        got(k)
        pass
    elif type=="GOT":
        gotlist[k]=v
        pass
    elif type=="LCK":
        lkd(k)
        pass
    elif type=="LKD":
        if k not in mylocks:
            mylocks[k]=0
        mylocks[k]+=1
        pass
    elif type=="ULK":
        pass


def wait(key):
    while key not in mylocks:
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
def send(s,msg):
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
        thread.start_new_thread(parse,(msg,))

def get_ip_address():#using google to obtain real ip, google most reliable host I know.
    s = socket(AF_INET,SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def int_to_bytes(x):#convert int to bytes to send
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes): #recieved bytes to int
    return int.from_bytes(xbytes, 'big')


main()
