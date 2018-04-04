import sys

t="hello"
r=open("MWD.py","r")
t=r.read()
actions=[]
methods=[]
flag="a"
for set in t.split("a=1"):
    if ":" in set:
        print(set)
        if flag=="a":
            actions.append(set)
        else:
            methods.append(set)
    if "declare_operators" in set:
        flag="m"


a=open("a.py","w")
m=open("m.py","w")
for act in actions:
    a.write(act)
for met in methods:
    m.write(met)
#print(actions)
