#Grid World Domain File With Preconditions Sent To Planner
#Conformant Planning for refuelling
import treehop 
import copy
from collections import defaultdict
Geff=(1,2)
def refuel(state,agent):
    pre=state.fuel[agent]
    state.fuel[agent]=(pre[0]+10,pre[1]+10)
    return ([state],{'fuel':{agent:(0,1)}})

def unstuck(state,agent):
    loc=state.agent[agent]
    if not state.clear[loc]:
        precond={'agent':{agent:loc},'clear':{loc:0}}
        return([state],precond)
    
def relight(state,beacon):
    precond={'lit':{beacon:2}}
    if state.lit[beacon]==2:
        state.lit[beacon]=1
        return([state],precond)
    else:
        return False
def light(state,agent,beacon):
    precond={'lit':{beacon:0},'agent':{agent: state.beacons[beacon]}}
    if not state.lit[beacon]:
        if state.agent[agent]==state.beacons[beacon]:
            state.lit[beacon]=1
            return([state],precond)
    else:
        return ([state],precond)

#forward or up
def move_forward(state, agent, test=1):
    prev=state.fuel[agent]
    eff=Geff
    state.fuel[agent]=(prev[0]-eff[1],prev[1]-eff[0])
    state1=copy.deepcopy(state)
    if (test==0):
        alt=move_backward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.behind and state.clear[state.behind[loc]]:
        precond={'agent':{agent:loc},'behind':{loc:state.behind[loc]},'clear':{loc:1},'fuel':{agent:eff}}
        state.agent[agent] = state.behind[loc]
        if alt:
            if not state.clear[state.infront[loc]]:
                return False
            precond['clear'][state.infront[loc]]=1
            return ([state,state1],precond)
        else:
            return ([state], precond)
    else: return False

#backward or down
def move_backward(state, agent, test=1):
    prev=state.fuel[agent]
    eff=Geff
    state.fuel[agent]=(prev[0]-eff[1],prev[1]-eff[0])
    state1=copy.deepcopy(state)
    if (test == 0):
        alt=move_forward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.infront and state.clear[state.infront[loc]]:
        precond={'agent':{agent:loc},'infront':{loc:state.infront[loc]},'clear':{loc:1},'fuel':{agent:eff}}
        state.agent[agent] = state.infront[loc]
        if alt:
            if not state.clear[state.behind[loc]]:
                return False
            precond['clear'][state.behind[loc]]=1
            return ([state,state1],precond)
        else:
            return ([state], precond)
    else: return False

#up or backward
def move_up(state, agent, test=1):
    prev=state.fuel[agent]
    eff=Geff
    state.fuel[agent]=(prev[0]-eff[1],prev[1]-eff[0])
    state1=copy.deepcopy(state)
    if (test==0):
        alt=move_backward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.below and state.clear[state.below[loc]]:
        state.agent[agent] = state.below[loc]
        precond={'agent':{agent:loc},'below':{loc:state.below[loc]},'clear':{loc:1},'fuel':{agent:eff}}
        if alt:
            if not state.clear[state.infront[loc]]:
                return False
            precond['clear'][state.infront[loc]]=1
            return ([state,state1],precond)
        else:
            return ([state],precond)
    else: return False

#down or forward
def move_down(state, agent, test=1):
    prev=state.fuel[agent]
    eff=Geff
    state.fuel[agent]=(prev[0]-eff[1],prev[1]-eff[0])
    state1=copy.deepcopy(state)
    if (test==0):
        alt=move_forward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.above and state.clear[state.above[loc]]:
        state.agent[agent] = state.above[loc]
        precond={'agent':{agent:loc},'above':{loc:state.above[loc]},'clear':{loc:1},'fuel':{agent:eff}}
        if alt:
            precond['clear'][state.behind[loc]]=1
            return ([state,state1],precond)
        else:
            return ([state],precond)
    else: return False

treehop.declare_operators(move_forward, move_backward, move_up, move_down, light,relight,unstuck,refuel)

def find_cost(start,end,n):
    sCol=(start-1)%n
    sRow=(start-1)//n
    eCol=(end-1)%n
    eRow=(end-1)//n
    dist=abs(eCol-sCol)+abs(eRow-sRow)
    return dist

        
def achieve_goal(state, agent, end, n, tFlag=0):
    if state.fuel[agent][0]<=2:
        return[('refuel',agent),('achieve_goal',agent, end,n)]
    start=state.agent[agent]
    if not state.clear[start]:
        return [('unstuck',agent)]#,('achieve_goal',agent, end, n)]
    test=copy.deepcopy(state)
    if start==end:
        return []
    state1=copy.deepcopy(state)
    up=move_up(state1,agent)
    if up:
        up=up[0][0].agent[agent]
        up=find_cost(up,end,n)
    else:
        up=n**2
    state1=copy.deepcopy(state)
    down=move_down(state1,agent)
    if down:
        down=down[0][0].agent[agent]
        down=find_cost(down,end,n)
    else:
        down=n**2
    state1=copy.deepcopy(state)
    backward=move_backward(state1,agent)
    if backward:
        backward=backward[0][0].agent[agent]
        backward=find_cost(backward,end,n)
    else:
        backward=n**2
    state1=copy.deepcopy(state)
    forward=move_forward(state1,agent)
    if forward:
        forward=forward[0][0].agent[agent]
        forward=find_cost(forward,end,n)
    else:
        forward=n**2
    m=min(up,down,forward,backward)
    move=0
    if (m==up):
        move='move_up'
    if (m==down):
        move='move_down'
    if (m==forward):
        move='move_forward'
    if (m==backward):
        move='move_backward'
    return[(move,agent),('achieve_goal',agent, end,n)]

treehop.declare_methods('achieve_goal',achieve_goal)

def light_all(state, agent, n):
    build=[]
    for b in state.lit:
        if state.lit[b]==0:
            build.append(('achieve_goal',agent,state.beacons[b],n))
            build.append(('light',agent,b))
        elif state.lit[b]==2:
            build.append(('relight',b))
    return build
treehop.declare_methods('light_all',light_all)

