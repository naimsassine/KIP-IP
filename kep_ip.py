#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Sassine Naim
# ID: 000 440091

from pyomo.environ import *

# naming convention
patient = lambda i: "p_{{{}}}".format(i)
donor = lambda i: "d_{{{}}}".format(i)


#insert any auxiliary code

# function that takes a dictionary and returns a list of its keys
def getKeysList(dict):
    return list(dict.keys())

# function that takes a dictionary and returns a list of its values
def getValuesList(dict):
    return list(dict.values())

# function that takes as input a list, which should be the list of arcs and
# returns all the arcs that end with the node 'n'
def rightCompFix(list, n):
    list_to_return = []
    for i in list :
        if i[1] == n :
            list_to_return.append(i)
    return list_to_return


# function that takes as input a list, which should be the list of arcs and
# returns all the arcs that start with the node 'n'
def leftCompFix(list, n):
    list_to_return = []
    for i in list :
        if i[0] == n :
            list_to_return.append(i)
    return list_to_return

# I use the function below to detemrine the successors of a node
# It usually takes as input the leftCompFix(arcs, node)
def succDeU(list):
    list_to_return = []
    for i in list :
        list_to_return.append(i[1])
    return list_to_return

# I use the function below to detemrine the predecessors of a node
# It usually takes as input the rightCompFix(arcs, node)
def precedDeU(list):
    list_to_return = []
    for i in list :
        list_to_return.append(i[0])
    return list_to_return

# function that takes as input a feasible solution x, the set of nodes,
# and returns a dictionary with the adjacency points of every node
# this function is used in the DFS
def calcul_adj(x, node_set):
    adj = dict()
    for i in node_set:
        adj.update({ i : succDeU(leftCompFix(x, i))})
    return adj

# DFS method implemented in a function that is used to determine
# the different cycles of a graph
def dfs(adj,node,visited,cycle,start):
  if (visited[node]):
    if (node == start):
        return None
  visited[node] = True;
  cycle.append(node)
  for child in adj[node]:
    dfs(adj,child,visited, cycle,start)
  visited[node] = False

# function that takes as input a feasible solution and set of nodes,
# and returns the different cycles found in this feasible solution
def find_cycles(x, nodes):
    all_cycles = []
    visited = {}
    for j in nodes:
        visited.update({ j : False})
    for i in nodes :
        sous_cycle = []
        cycle = []
        adj = calcul_adj(x,nodes) # dici vient le problème
        start = i
        if not not adj[i]:
            dfs(adj,start,visited,cycle,start)
            cycle.append(cycle[0])
            for k in range(len(cycle)-1) :
                sous_cycle.append((cycle[k], cycle[k+1]))
            all_cycles.append(sous_cycle)
    return all_cycles

# the cycles returned by find_cycles can have sometimes duplicates or, empty lists ...
# this function just cleans the totality of the cycles to get it in the wanted form
# I could have coded this function in the find_cycles function, but it was getting a bit
# long and heavy, so I decited to separate it
def cycles_cleaning(w, cycles):
    x_c = w.copy()
    for k in x_c :
        x_c[k] = 0
    for i in range(len(cycles)) :
        removable = False
        for j in range(len(cycles[i])) :
            if (x_c[cycles[i][j]] == 1):
                removable = True
            else :
                x_c[cycles[i][j]] = 1
        if removable :
            cycles[i].clear()
    return ([i for i in cycles if i != []])

# this function takes as argument a dict of the feasible or optimal
# solution x, and the total number of couples (pi,di)
# and returns the solution under the format that is demanded by the assistant
def dict_to_sol_format(x,n):
    solution = []
    for arc in x :
        if arc[0] >= n : # its patient donnor
            solution.append((patient(arc[0]-n), donor(arc[1])))
        else : # its donner patient
            solution.append((donor(arc[0]), patient(arc[1]-n)))
    return(solution)

# function that takes as input a filename, typically "small.csv" or normal or large
# and outputs :
# n the number of patient-donor pairs (p_i, d_i),
# M the maximum number of exchanges per cycle of transplants.
# w a dictionary with every arc and its cost
# node_set, the set of nodes
# arc_set, the set of arcs
def scanDocument(filename):
    w = dict()
    file = open(filename, "r")
    initLine = file.readline().split(";")
    n, M = int(initLine[0]), int(initLine[2])
    lines = file.readlines()
    for line in lines :
        values = line.split(";")
        w.update({(int(values[0]), int(values[1]) + n): float(values[2])})
    for index in range(n):
        w.update({(index + n, index): 0})
    node_set = list(range(0,2*int(n)))
    arc_set = getKeysList(w)
    return w, n, M, node_set, arc_set



def solve(args):
    verbose = args.verbose
    if not args.cycle_limit:
        w, n, M, node_set, arc_set = scanDocument(args.instance)

        m = pyomo.environ.ConcreteModel()

        # Create sets
        m.node_set = pyomo.environ.Set( initialize=node_set )
        m.arc_set = pyomo.environ.Set( initialize=arc_set , dimen=2)

        # Create variables
        m.X = pyomo.environ.Var(m.arc_set, domain=pyomo.environ.Binary)


        # Create objective
        def obj_rule(m):
            return sum(m.X[e] * w[e] for e in arc_set)
        m.OBJ = pyomo.environ.Objective(rule=obj_rule, sense=pyomo.environ.maximize)



        def flow_bal_rule(m,u):
            succs = succDeU(leftCompFix(arc_set, u))
            preds = precedDeU(rightCompFix(arc_set, u))
            return sum(m.X[(u,v)] for v in succs) - sum(m.X[(v2,u)] for v2 in preds) == 0

        m.FlowBal = pyomo.environ.Constraint(m.node_set, rule=flow_bal_rule)


        pyomo.environ.SolverFactory('glpk').solve(m)

        if(verbose) : m.pprint()

        x = [] # list that will store the taken arcs
        for p in m.arc_set:
            if m.X[p].value == 1.0:
                x.append(p)




    else :
        w, n, M, node_set, arc_set = scanDocument(args.instance)

        loop_again = True
        g_cycle = []
        p_cycle = []


        while (loop_again):

            m = pyomo.environ.ConcreteModel()

            # Create sets
            m.node_set = pyomo.environ.Set( initialize=node_set )
            m.arc_set = pyomo.environ.Set( initialize=arc_set , dimen=2)

            # Create variables
            m.X = pyomo.environ.Var(m.arc_set, domain=pyomo.environ.Binary)

            m.cycle_num = pyomo.environ.Set(initialize = g_cycle)


            # Create objective
            def obj_rule(m):
                return sum(m.X[e] * w[e] for e in arc_set)
            m.OBJ = pyomo.environ.Objective(rule=obj_rule, sense=pyomo.environ.maximize)




            def flow_bal_rule(m,u):
                succs = succDeU(leftCompFix(arc_set, u))
                preds = precedDeU(rightCompFix(arc_set, u))
                return sum(m.X[(u,v)] for v in succs) - sum(m.X[(v2,u)] for v2 in preds) == 0

            m.FlowBal = pyomo.environ.Constraint(m.node_set, rule=flow_bal_rule)


            def cycle_rule(m,c):
                cycle = p_cycle[c]
                return sum(m.X[uv] for uv in cycle) <= len(p_cycle[c])-1

            m.CycleRule = pyomo.environ.Constraint(m.cycle_num, rule=cycle_rule)


            pyomo.environ.SolverFactory('glpk').solve(m)


            x = [] # list that will store the taken arcs
            for p in m.arc_set:
                if m.X[p].value == 1.0:
                    x.append(p)

            argument = find_cycles(x, node_set)
            cycles_found = cycles_cleaning(w,argument)
            found_cycleM = False
            for cycle in cycles_found:
                if len(cycle)>2*M and not(cycle in p_cycle):
                    found_cycleM = True
                    p_cycle.append(cycle)
                    g_cycle.append(p_cycle.index(cycle))

            loop_again = found_cycleM
    if(verbose) : m.pprint()
    return(dict_to_sol_format(x,n))


