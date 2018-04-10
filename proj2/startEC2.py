import json
import subprocess
import sys
import time
id=[]
type="start-instances"
cmd=["aws","ec2","describe-instances"]
a=subprocess.check_output(cmd)
if isinstance(a,bytes):
    a=a.decode('utf-8')
data=json.loads(a)
a=data["Reservations"][0]["Instances"]
for b in a:
    id.append(b["InstanceId"])
cmd=["aws","ec2",type,"--instance-ids"]
for i in id:
    cmd.append(i)
while True:
    try:
        subprocess.check_output(cmd)
        print("Starting processes")
        break
    except:
        print("Waiting to start up processes")
flag=True
while flag:
    try:
        cmd=["aws","ec2","describe-instances"]
        a=subprocess.check_output(cmd)
        if isinstance(a,bytes):
            a=a.decode('utf-8')
        data=json.loads(a)
        a=data["Reservations"][0]["Instances"]
        publicDNS=[]
        ip={}
        counter=0
        for b in a:
            publicDNS.append(b["PublicDnsName"])
            ip[b["PublicIpAddress"]]=counter
            counter=counter+1
        flag=False
    except:
        print("Not up yet, taking another pass")
        time.sleep(1)
with open("cluster","w") as f:
    for DNS in publicDNS:
        f.write(DNS)
        f.write(" ")
data={"ip":ip,"ops":100,"keyrange":10,"closeable":False}
with open("config.txt","w") as f:
    json.dump(data,f)
print("All ready to run")
