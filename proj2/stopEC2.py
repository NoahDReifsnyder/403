import json
import subprocess
import sys
id=[]
type="stop-instances"
cmd=["aws","ec2","describe-instances"]
a=subprocess.check_output(cmd)
data=json.loads(a)
a=data["Reservations"][0]["Instances"]
for b in a:
    id.append(b["InstanceId"])
cmd=["aws","ec2",type,"--instance-ids"]
for i in id:
    cmd.append(i)
subprocess.check_output(cmd)
