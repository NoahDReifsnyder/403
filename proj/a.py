    
def unstuck(state,agent):
    loc=state.agent[agent]
    if not state.clear[loc]:
        precond={'agent':{agent:loc},'clear':{loc:0}}
        state.clear[loc]=1
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
def move_forward(state, agent, test=0):
    state1=copy.deepcopy(state)
    if (test==0):
        alt=move_backward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.behind and state.clear[state.behind[loc]]:
        precond={'agent':{agent:loc},'behind':{loc:state.behind[loc]},'clear':{loc:1}}
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
def move_backward(state, agent, test=0):
    state1=copy.deepcopy(state)
    if (test == 0):
        alt=move_forward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.infront and state.clear[state.infront[loc]]:
        precond={'agent':{agent:loc},'infront':{loc:state.infront[loc]},'clear':{loc:1}}
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
def move_up(state, agent, test=0):
    state1=copy.deepcopy(state)
    if (test==0):
        alt=move_backward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.below and state.clear[state.below[loc]]:
        state.agent[agent] = state.below[loc]
        precond={'agent':{agent:loc},'below':{loc:state.below[loc]},'clear':{loc:1}}
        if alt:
            if not state.clear[state.infront[loc]]:
                return False
            precond['clear'][state.infront[loc]]=1
            return ([state,state1],precond)
        else:
            return ([state],precond)
    else: return False

#down or forward
def move_down(state, agent, test=0):
    state1=copy.deepcopy(state)
    if (test==0):
        alt=move_forward(state1,agent,1)
    else:
        alt=False
    loc=state.agent[agent]
    if state.agent[agent] in state.above and state.clear[state.above[loc]]:
        state.agent[agent] = state.above[loc]
        precond={'agent':{agent:loc},'above':{loc:state.above[loc]},'clear':{loc:1}}
        if alt:
            precond['clear'][state.behind[loc]]=1
            return ([state,state1],precond)
        else:
            return ([state],precond)
    else: return False
