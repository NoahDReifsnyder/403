#attempt to re-write and clean up treehop py-planner

stateList={}
def seek_plan(state,t,goals):#current state, task to decompose, and goal list
    global stateList
    if t.action in operators:
        #current task is an action
        stringState=string_state(state)#used to id states
        if stringState in stateList:#if found, link and stop planning
            t.find=1
            t.fNode=stateList[stringState]
            return False
        else:
            stateList[stringState]=t#if not found, add to list
        operator=operators[t.action]
        opreturn=operator(copy.deepcopy(state),*t.cond)#gets possible resulting states
        precond=opreturn[1]
        newstates=opreturn[0]
        newstate=newstates[0]#plan off first state, replan on rest
        for x in range(1,len(newstates)):
            t.states[x-1]=newstates[x]
            pass
        pass
    elif t.action in methods:
        #current task is a method
        for method in methods[t.action]:
            subtasks=method(state,*t.cond)#decompose method
            for s in subtasks:#decompose subtasks
                p=PlanNode(s[0],s[1:])
                t.children=t.children+[p]
                state=seek_plan(state,p,goals)
                if not state:#Planner fails recursivly, unreachable goal or found state
                    return False
        return state
    else:
        return False
