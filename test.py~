from socket import * #using sockets for now, will implement lower level if needed 
import time
import _thread as thread

def main():
    slist=start_up()
    thread.start_new_thread (gencmds,(slist,))
    time.sleep(1)
    shut_down(slist)
    print(slist)
def start_up():
    slist=[]
    iplist=['128.180.134.200','128.180.132.15','128.180.135.18'] 
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
    while len(slist)<len(iplist):
        s=socket(AF_INET,SOCK_STREAM)
        flag=True
        while flag:
            try:
                s.bind((gethostname(),PORT_NUMBER))
                flag=False
            except:
                PORT_NUMBER+=1
        s.listen(1)
        print(s)
        conn,addr=s.accept()
        slist.append(s)
    return slist

def shut_down(slist):
    for s in slist:
        slist.remove(s)
        s.close()
def get():
    pass
def put():
    pass
def parse():
    pass
def gencmds(slist):
    for s in slist:
        try:
            print(s.getpeername())
        except:
            print(s.getsockname())
    pass

main()
