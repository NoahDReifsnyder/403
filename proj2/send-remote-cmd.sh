#!/bin/bash
### Send a command to all nodes in cluster (defined by cluster file)
### Key file is provided by AWS when setting up node

if [[ $1 = "" ]]; then
echo "Missing cluster file!"
exit
fi

identity_file="First.pem"
for server in $(cat $1); do
    echo $server
    ssh -i $identity_file ubuntu@$server "$2"
    echo "Command sent $server"
done
echo "Done sent command $2"

