from socket import * #using sockets for now, will implement lower level if needed 
import time
import _thread as thread
import sys

def main(): 
    slist=start_up()
    time.sleep(1)
    thread.start_new_thread(gencmds,(slist,))
    print(get_ip_address())
    for s in slist:
        thread.start_new_thread(listen,(s,))
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
def get(k):
    pass
def put(k,v):
    x=get(k)
    pass
def lock(k):
    pass
def unlock(k):
    pass
def parse(msg):
    
    pass
def gencmds(slist):
    for s in slist:
        ip=get_ip_address()
        msg="hi  from "+ip
        for i in range(1,1000):
            msg=msg+"a"
        emsg=msg.encode('utf-8')
        length=len(emsg)
        elength=int_to_bytes(length)
        print(elength,length)
        print('t',len(elength))
        s.send(elength)
        s.send(emsg)

def listen(s):
    l=int_from_bytes(s.recv(1))
    print(l)
    emsg=s.recv(l)
    msg=emsg.decode('utf-8')
    print(msg)

def get_ip_address():#using google to obtain real ip, google most reliable host I know.
    s = socket(AF_INET,SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def int_to_bytes(x):#convert int to bytes to send
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes): #recieved bytes to int
    return int.from_bytes(xbytes, 'big')


main()
