### Send a command to all nodes in cluster (defined by cluster file)
### Key file is provided by AWS when setting up node

identity_file="403.pem"
python3 startEC2.py
for server in $(cat cluster); do
    echo $server
    scp -i $identity_file ./DHT2.py ec2-user@$server:~/    
    scp -i $identity_file ./config.txt ec2-user@$server:~/
    echo "file send"
    ssh -i $identity_file ec2-user@$server "if pgrep python3 > /dev/null; then killall python3; fi ; python3 ~/DHT2.py 1>out.txt 2>error.txt &"
    echo "Command sent $server"
done
echo "Done"
for server in $(cat cluster); do
    ssh -i $identity_file ec2-user@$server "while pgrep python3 > /dev/null; do sleep 1; done;"
    echo "command done"
done
for server in $(cat cluster); do
    ssh -i $identity_file ec2-user@$server "cat out.txt"
done
echo "printed"
python3 stopEC2.py
