import json
import subprocess
import sys
import time
cmd=["aws","ssm","describe-instance-information","--output","json","--query","InstanceInformationList[*]"]
a=subprocess.check_output(cmd)
if isinstance(a,bytes):
    a=a.decode('utf-8')
data=json.loads(a)
print(data)
