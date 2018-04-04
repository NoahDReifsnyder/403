\#!/bin/bash
### Send a command to all nodes in cluster (defined by cluster file)
### Key file is provided by AWS when setting up node

identity_file="First.pem"

for server in $(cat cluster); do
    echo $server
    scp -i $identity_file ./DHT2.py ubuntu@$server:~/403/proj2/    
    scp -i $identity_file ./config.txt ubuntu@$server:~/403/proj2/
    echo "file send"
    ssh -i $identity_file ubuntu@$server "if pgrep python3 > /dev/null; then killall python3; fi ; python3 ~/403/proj2/DHT2.py 1>out.txt &"
    echo "Command sent $server"
done
echo "Done"
for server in $(cat cluster); do
    ssh -i $identity_file ubuntu@$server "while pgrep python3 > /dev/null; do sleep 1; done; cat out.txt"
done
