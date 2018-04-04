
def find_cost(start,end,n):
    sCol=(start-1)%n
    sRow=(start-1)//n
    eCol=(end-1)%n
    eRow=(end-1)//n
    dist=abs(eCol-sCol)+abs(eRow-sRow)
    return dist
     
def achieve_goal(state, agent, end, n, tFlag=0):
    start=state.agent[agent]
    if not state.clear[start]:
        return [('unstuck',agent),('achieve_goal',agent, end, n)]
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

def light_all(state, agent, n):
    build=[]
    for b in state.lit:
        if state.lit[b]==0:
            build.append(('achieve_goal',agent,state.beacons[b],n))
            build.append(('light',agent,b))
        elif state.lit[b]==2:
            build.append(('relight',b))
    return build
