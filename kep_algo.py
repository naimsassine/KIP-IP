#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Sassine Naim
# ID: 000 440091

from networkx import DiGraph, simple_cycles

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

# function that takes as input a cycle and returns the set of arcs
# that constitute this cycle
def cycle_to_arc(cycle):
    list = []
    for i in range(len(cycle)-1):
	       list.append((cycle[i],cycle[i+1]))

    return (list)

# takes as input the dictionary of arcs and costs, as well as the number of
# (pi,di) pairs, and outputs a feasible solution that I chose
# in this case the feasible solution is just the connection of all the
# (di,pi) and (pi,di) as long as they follow the constraints of the formulation
def feasibleSolution(w,n):
    w_copy = dict()
    for i in list(w.keys()) :
        if i[0] == (i[1]+n) and (i[1],i[0]) in w:
            w_copy.update({(i[0],i[1]): 1})
        elif (i[0]+n) == i[1] and (i[1],i[0]) in w:
            w_copy.update({(i[0],i[1]): 1})
        else :
            w_copy.update({(i[0],i[1]): 0})
    return w_copy

# this function takes as input the dict w with the ars and the costs of each arch
# as well as x, a solution, and calculates the correspong objective value of the
# solution x
def calcul_solution(x,w):
    sum = 0
    for i in x :
        sum = sum + w[i]*x[i]
    return sum

# function that takes as input two dicts, one for the solution x,
# another one x_c and sums both of them
def addition_dict(x,xc):
    xz = dict()
    for i in list(x.keys()):
        for j in list(xc.keys()):
            if i == j:
                if (x[i]+xc[j] < 2):
                    xz.update({i: (x[i]+xc[j])})
                else :
                    xz.update({i: 1})
    return xz

# funtion that takes as input the list of cycles and the graph R
# outputs a list of cost for every cycle
def cost_cycle(cycle, R):
    the_list=[]
    for soucycle in cycle:
        weight = 0
        length = len(soucycle)
        for i in range(length-1):
            weight = weight + R[soucycle[i]][soucycle[i+1]]['weight']
        the_list.append(weight)
    return the_list

# function that construcs the x(C) as mentioned in the Project.pdf
def construction_xc(cycles, cycle_costs, x):
    x_c = x.copy()
    for k in x_c :
        x_c[k] = 0
    found = False
    position = 0
    position = cycle_costs.index(max(cycle_costs))
    if (cycle_costs[position] > 0):
        found = True
    if found == True :
        pc_found = cycles[position]
        arcs_of_cycle = cycle_to_arc(pc_found)
        for i in x_c :
            uv = (i[0],i[1])
            vu = (i[1],i[0])
            if uv in arcs_of_cycle :
                x_c[i] = 1
            elif vu in arcs_of_cycle :
                x_c[i] = -1
            else :
                x_c[i] = 0
    return x_c

# function that returns the forward arcs of a soltion x
def forward_arcs(x):
    f_arcs = []
    for i in list(x.keys()) :
        if x[i] == 0:
            f_arcs.append(i)
    return f_arcs

# function that returns the backward arcs of a soltion x
def backward_arcs(x):
    f_arcs = []
    for i in list(x.keys()) :
        if x[i] == 1:
            f_arcs.append((i[1],i[0]))
    return f_arcs

# this function takes as argument a dict of the feasible or optimal
# solution x, and the total number of couples (pi,di)
# and returns the solution under the format that is demanded by the assistant
def dict_to_sol_format(x,n):
    solution = []
    checkup(x,n)
    for arc in x :
        if x[arc] == 1 :
            if arc[0] >= n : # its patient donnor
                solution.append((patient(arc[0]-n), donor(arc[1])))
            else : # its donner patient
                solution.append((donor(arc[0]), patient(arc[1]-n)))
    return(solution)


# function that takes as input a filename, typically "small.csv" or normal or large
# and outputs :
# n the number of patient-donor pairs (p_i, d_i),
# M the maximum number of exchanges per cycle of transplants.
# w a dictionnary with every arc and its cost
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


def checkup(x, n):
    for arc in x:
        if(x[arc] == 1) and (arc[0] == arc[1]-n):
            x[(arc[1], arc[0])] = 1


def addTheArray(arr, n, array):
    sous_array = []
    for i in range(0, n):
        sous_array.append(arr[i])
    array.append(sous_array)


def generateAllBinaryStrings(n, arr, i, array):

    if i == n:
        addTheArray(arr, n, array)
        return

    arr[i] = -1
    generateAllBinaryStrings(n, arr, i + 1, array)

    arr[i] = 1
    generateAllBinaryStrings(n, arr, i + 1, array)

def keywithmaxval(d):
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]



def solve(args):

    w, n, M, node_set, arc_set = scanDocument(args.instance)



    x = feasibleSolution(w,n)



    # Iteration over the number of times the algorithm needs to be started
    continue_loop = True
    while continue_loop:
        # Positive cycles take over negative cycles
        R1 = DiGraph()
        R1.add_nodes_from(node_set)

        f_arcs1 = forward_arcs(x)
        back_arcs1 = backward_arcs(x)

        for i in back_arcs1 :
            R1.add_edge(i[0],i[1], weight = -w[(i[1],i[0])])
        for i in f_arcs1 :
            R1.add_edge(i[0],i[1], weight = w[i])



        cycles1 = list(simple_cycles(R1))
        for soucycle1 in cycles1 :
            soucycle1.append(soucycle1[0])



        cycle_costs1 = cost_cycle(cycles1, R1)
        x_c1 = construction_xc(cycles1, cycle_costs1, x)



        # negative cycles take over positive ones

        R2 = DiGraph()
        R2.add_nodes_from(node_set)

        f_arcs2 = forward_arcs(x)
        back_arcs2 = backward_arcs(x)


        for i in f_arcs2 :
            R2.add_edge(i[0],i[1], weight = w[i])
        for i in back_arcs2 :
            R2.add_edge(i[0],i[1], weight = -w[(i[1],i[0])])


        cycles2 = list(simple_cycles(R2))
        for soucycle2 in cycles2 :
            soucycle2.append(soucycle2[0])



        cycle_costs2 = cost_cycle(cycles2, R2)
        x_c2 = construction_xc(cycles2, cycle_costs2, x)



        x1 = addition_dict(x,x_c1)
        x2 = addition_dict(x,x_c2)

        solx1 = calcul_solution(x1,w)
        solx2 = calcul_solution(x2,w)
        sol_precedante = calcul_solution(x,w)
        if (sol_precedante == solx1 or sol_precedante == solx2):
            continue_loop = False

        if (solx1>=solx2) :
            x = x1
        if (solx2>solx1) :
            x = x2


    return(dict_to_sol_format(x,n))







# From down here to the end of the code : it's another way to deal with the duplicate arcs coming from the forward_arcs and the back_arcs :
# in the previous method, we just calculate two possibilities : one where in case of duplicate we only take the forward arc cost, and the
# other where we take the backward_arcs costs, and we compare both solutions in terms of maximising the cost function w*x
# Down here, we not only take two solutions, but in case of duplicate arcs, we take all the imaginable solutions, then we repeat the same
# procedure as above. So imagine, there are 3 arcs in common between forward_arcs and backward_arcs, in the case above, we imagine two solutions
# one where we consider, for the duplicate arcs, that they are forward arcs, and one where they are backward arcs
# for the case below, we imagine each posssible solution, that means 2^3 solutions, so for each arc, if its in backward, or in forward arcs


def solveBeta(args):

    w, n, M, node_set, arc_set = scanDocument(args.instance)



    x = feasibleSolution(w,n)



    # Iteration over the number of times the algorithm needs to be started
    continue_loop = True
    while continue_loop:



        f_arcs = forward_arcs(x)
        back_arcs = backward_arcs(x)

        in_common = []
        for i in f_arcs :
            for j in back_arcs :
                if (i == j) :
                    in_common.append(i)
                    f_arcs.remove(i)
                    back_arcs.remove(j)

        lenIC = len(in_common)
        arr = [None] * lenIC
        array = []
        generateAllBinaryStrings(lenIC, arr, 0, array)

        all_graphs = dict()
        if (len(in_common) == 0):
            R = DiGraph()
            R.add_nodes_from(node_set)
            for i in back_arcs :
                R.add_edge(i[0],i[1], weight = -w[(i[1],i[0])])
            for i in f_arcs :
                R.add_edge(i[0],i[1], weight = w[i])
            all_graphs.update({0 : R})
        else :
            for i in range(len(array)):
                R = DiGraph()
                R.add_nodes_from(node_set)
                for j in back_arcs :
                    R.add_edge(j[0],j[1], weight = -w[(j[1],j[0])])
                for j in f_arcs :
                    R.add_edge(j[0],j[1], weight = w[j])
                for k in in_common :
                    if(array[i][in_common.index(k)] == 1) :
                        R.add_edge(k[0],k[1], weight = w[k])
                    else :
                        R.add_edge(k[0],k[1], weight = -w[(k[1],k[0])])
                all_graphs.update({i : R})




        cycles = dict()
        for graph in all_graphs:
            cyclez = list(simple_cycles(all_graphs[graph]))
            cycles.update({graph : cyclez})

        for i in cycles :
            for j in cycles[i] :
                j.append(j[0])

        cycles_costs = dict()
        for graph_num in all_graphs:
            cost = cost_cycle(cycles[graph_num], all_graphs[graph_num])
            cycles_costs.update({graph_num : cost})

        x_c = dict()
        for graph_num in all_graphs :
            xc = construction_xc(cycles[graph_num], cycles_costs[graph_num], x)
            x_c.update({graph_num : xc})

        graph_sol = dict()
        graph_sol_arcs = dict()
        for graph_num in x_c :
            xc = x_c[graph_num]
            new_x = addition_dict(x,xc)
            graph_sol_arcs.update({graph_num : new_x})
            sol = calcul_solution(new_x,w)
            graph_sol.update({graph_num : sol})
        sol_precedante = calcul_solution(x,w)
        graphmax = keywithmaxval(graph_sol)
        x = graph_sol_arcs[graphmax]
        if (sol_precedante == graph_sol[graphmax]):
            continue_loop = False
    return(dict_to_sol_format(x,n))
