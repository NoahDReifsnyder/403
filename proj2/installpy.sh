### Send a command to all nodes in cluster (defined by cluster file)
### Key file is provided by AWS when setting up node

identity_file="403.pem"

for server in $(cat cluster); do
    echo $server
    ssh -i $identity_file ec2-user@$server "python3 -v"
done
