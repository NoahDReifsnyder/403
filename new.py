import json
iplist=['172.31.47.97','172.31.37.86','172.31.43.198','172.31.36.171']
num=100
keyrange=100
data={"ip":iplist,"ops":num,"keyrange":keyrange}
with open('config.txt', 'w') as outfile:
    json.dump(data, outfile)
