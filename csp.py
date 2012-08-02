# to run: python csp.py <name of file>

# items: list of items
# bags: list of bags
# fitting_limit: fitting limit ([0]: lower limit bound; [1]: upper limit bound)
# constraint_matrices: constraint_matrix for each pair of constrained variables (dict of 2-d dicts)
# the keys in constraint matrices are represented as 'item1,item2'
# nodes are represented as 'item-bag'

# ran without errors for all 20 txt files in this folder.

import sys
import time
from collections import defaultdict
from optparse import OptionParser

usage = "usage: %prog [FILEPATH] <[OPTIONS]>"
parser = OptionParser(usage=usage)
#parser.add_option("-f", "--file", dest="filename", default="test_1.txt", help="CSP FILE to read from", metavar="FILE")
parser.add_option("-m", "--mrv", action="store_true", dest="mrv", default=False, help="Use MRV optimization")
parser.add_option("-l", "--lcv", action="store_const", const='lcv', dest="tiebreak", default=None, help="Use LCV")
parser.add_option("-d", "--degree", action="store_const", const='degree', dest="tiebreak", default=None, help="Use Degree heuristics")
parser.add_option("-c", "--fc", action="store_true", dest="fc", default=False, help="Use forward checking")
parser.add_option("-a", "--ac3", action="store_true", dest="ac3", default=False, help="Use AC-3 checking")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Enables trace of how to solve the problem.")
(options, args) = parser.parse_args()

counter = 0

#item class -- remember these are the variables
class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = int(weight)
        # domain attribute is not set in constructor, but is set later on


#bag class -- remember these are the values
class Bag:
    def __init__(self, name, cap):
        self.name = name
        self.capacity = int(cap)


#function for getting an object from a list by the objects name
def getByName(alist, name):
    for l in alist:
        if l.name == name:
            return l
    return None


def checkNodes(nodes):
    bag_list = set([])
    for node in nodes:
        bag_list.add(node.split('-')[1])

    for bag in bags:
        if bag.name not in bag_list:
            # print bag.name + ' not in ' + str(bag_list)
            return False

    return True


def checkAC3(nodes):
    variables = defaultdict(list)
    for node in nodes:
        nlist = node.split('-')
        variables[nlist[0]].append(nlist[1])

    arcs = [key.split(',') for key in constraint_matrices]
    arcs = arcs + [arc[::-1] for arc in arcs]

    # print 'entered checkAC3()'
    # print 'arcs: ' + str(arcs)
    # print 'variables: ' + str(variables)

    def arcReduce(arc):
        # print 'ar(' + str(arc) + ') -- '
        removed_any = False
        for value_x in variables[arc[0]][:]:
            node_x = arc[0] + '-' + value_x
            ncc = False
            for value_y in variables[arc[1]][:]:
                node_y = arc[1] + '-' + value_y
                if nodesCanCoexist(node_x, node_y):
                    ncc = True

            if ncc:
                return

            variables[arc[0]].remove(value_x)
            # print '    -- Removed value ' + value_x + ' from variable ' + arc[0]
            removed_any = True

        return removed_any

    queue = arcs
    while queue:
        arc = queue.pop(0)
        if arcReduce(arc):
            for key in variables:
                if not variables[key]:
                    return False

            queue.extend(filter(lambda an_arc: an_arc[1] == arc[0], arcs))

    ret_nodes = []
    for key in variables:
        for value in variables[key]:
            ret_nodes.append(key + '-' + value)

    return ret_nodes


#function for checking whether a path is valid. Set final to true if you're checking the solution
def checkPath(path, final=False):
    # print 'cp: ' + str(path)
    #get bag info
    bag_dict = defaultdict(list)
    for node in path:
        nlist = node.split('-')
        item_name = nlist[0]
        item = getByName(items, item_name)
        bag_name = nlist[1]
        bag = getByName(bags, bag_name)
        bag_dict[bag].append(item.weight)
    # print bag_dict

    #check fitting limits and capacity
    for bag in bag_dict:
        if len(fitting_limit) > 0:
            if len(bag_dict[bag]) > fitting_limit[1]:
                return False

            if final & (len(bag_dict[bag]) < fitting_limit[0]):
                # print 'invalid: bag capacity = ' + str(len(bag_dict[bag]))
                return False

        bag_sum = sum(bag_dict[bag])
        bag_cap = float(bag.capacity)
        bag_frac = bag_sum / bag_cap

        if bag.capacity < sum(bag_dict[bag]):
            return False

        if final & (bag_frac < 0.9):
            # print 'invalid: ' + str(bag_sum) + ' / ' + str(bag_cap) + " = " + str(bag_frac)
            return False

    #check binary constraints
    for cm in constraint_matrices:
        cmlist = cm.split(',')
        item1 = cmlist[0]
        item2 = cmlist[1]
        # print 'item1: ' + item1 + ' | item2: ' + item2
        bag1, bag2 = None, None
        for node in path:
            nlist = node.split('-')
            item_name = nlist[0]
            bag_name = nlist[1]
            # print 'item_name: ' + item_name + ' | bag_name: ' + bag_name
            if item_name == item1:
                bag1 = bag_name
            elif item_name == item2:
                bag2 = bag_name

        if (bag1 is not None) & (bag2 is not None):
            valid = constraint_matrices[cm][bag1][bag2]
            # print "valid: " + str(valid)
            if not valid:
                return False

    return True


#get the key for the constraint matrix of 2 items
def getConstraintKey(item1, item2):
    for pair in constraint_matrices:
        cmlist = pair.split(',')
        if (item1 in cmlist) & (item2 in cmlist):
            return pair

    return None


#check whether 2 nodes aren't allowed due to binary constraints
def nodesCanCoexist(node1, node2):
    # print 'ncc -- node1: ' + node1 + ' | node2: ' + node2
    n1_list = node1.split('-')
    n1_item = n1_list[0]
    n1_bag = n1_list[1]
    n2_list = node2.split('-')
    n2_item = n2_list[0]
    n2_bag = n2_list[1]

    ckey = getConstraintKey(n1_item, n2_item)
    # print ckey
    if ckey is None:
        return True

    if n1_item != ckey.split(',')[0]:
        n1_item, n2_item = n2_item, n1_item
        n1_bag, n2_bag = n2_bag, n1_bag

    return constraint_matrices[ckey][n1_bag][n2_bag]


#generate the new node list based on the given new_node
def generateNewNodes(nodes, new_node, fc=False, curPath=[]):
    # print str(nodes) + new_node
    ret_nodes = filter(lambda node: node.split('-')[0] != new_node.split('-')[0], nodes)

    if fc:
        for node in ret_nodes:
            if not nodesCanCoexist(node, new_node):
                # print 'Removed ' + node + '. Clashes with ' + new_node
                ret_nodes.remove(node)

        # for node in ret_nodes:
        #     if not checkPath(curPath + [new_node, node]):
        #         ret_nodes.remove(node)

    return ret_nodes


#generate the new node list using MRV
def generateMRVNodes(nodes, tiebreak='test'):
    item_dict = defaultdict(list)
    for node in nodes:
        item_dict[node.split('-')[0]].append(node)

    if tiebreak:
        for key in item_dict:
            # print item_dict[key]
            item_dict[key] = tiebreaker(tiebreak, item_dict[key], nodes)
            # print item_dict[key]

    ret_list = []
    sorted_keys = sorted(item_dict, key=lambda key: len(item_dict[key]))
    for key in sorted_keys:
        ret_list.extend(item_dict[key])

    return ret_list


#if there is a tie for the MRV, it uses LCV or degree heuristics
def tiebreaker(tiebreak, node_subset, nodes):
    #sanity check
    if (tiebreak != 'lcv' and tiebreak != 'degree'):
        return node_subset

    nodes = filter(lambda node: node not in node_subset, nodes)
    const_list = {}
    for item in node_subset:
        constraints = 0
        for othernode in nodes:
            if (nodesCanCoexist(item, othernode) == False):
                constraints += 1
        if (tiebreak == 'degree'):
            constraints *= -1
        const_list[item] = constraints
        #print item, (" : "), constraints
    if (len(const_list) != len(node_subset)):
        print "SOMETHING IS WRONG!!!!!!!"
    res_list = sorted(const_list, key=lambda key: const_list[key])
    return res_list


#the main implementation of backtracking
def backtrack(nodes, path, fc=False, mrv=False, tiebreak='test', ac3=False):
    if not checkPath(path):
        return False

    if not checkNodes(nodes + path):
        return False

    # print 'path: ' + str(path)
    # print 'nodes: ' + str(nodes)

    if ac3:
        new_nodes = checkAC3(nodes + path)
        if not new_nodes:
            return False
        new_nodes = filter(lambda node: node not in path, new_nodes)
    else:
        new_nodes = nodes
    # print 'ar returned ' + str(new_nodes)

    if len(nodes) == 0:
        return path

    for i, node in enumerate(new_nodes[:]):
        new_nodes = generateNewNodes(new_nodes[:], node, fc=fc)
        if options.verbose:
            print 'trying node ' + node + ' on path ' + str(path)

        if mrv:
            new_nodes = generateMRVNodes(new_nodes, tiebreak)
        solution = backtrack(new_nodes, path + [node], fc=fc, mrv=mrv, tiebreak=tiebreak)
        global counter
        counter += 1
        if len(path) == 0:
            print str((i * 100.0) / len(nodes)) + '% of search complete'
        if solution:
            if checkPath(solution, True):
                if options.verbose:
                    print 'found solution'
                return solution

    return False
    if options.verbose:
        print 'go back up'


try:
    filename = sys.argv[1]
except IndexError:
    filename = 'test_1.txt'

# parse the file and store a list of lines for each section of data in lines_dict
f = open(filename)
flist = f.readlines()
lines_dict = defaultdict(list)
i = -1
for line in flist:
    if '#####' in line:
        i += 1
        continue
    lines_dict[i].append(line)

# for key in lines_dict:
#     print key

#initialize items
items = []
for line in lines_dict[0]:
    ilist = line.split()
    items.append(Item(ilist[0], ilist[1]))

if options.verbose:
    for item in items:
        print 'item: ' + item.name + ' -- ' + str(item.weight)

#initialize bags
bags = []
for line in lines_dict[1]:
    blist = line.split()
    bags.append(Bag(blist[0], blist[1]))

if options.verbose:
    for bag in bags:
        print 'bag: ' + bag.name + ' -- ' + str(bag.capacity)

#get fitting limits
try:
    fitting_limit = [int(x) for x in lines_dict[2][0].split()]
except IndexError:
    fitting_limit = []
# print 'fitting limit: ' + str(fitting_limit)

#start measuring time
timestamp = time.time()

#set the domain of each item
for item in items:
    item.domain = bags

#change the domain of each item depending on their inclusive unary constraint
for line in lines_dict[3]:
    iuclist = line.split()
    item = getByName(items, iuclist.pop(0))
    item.domain = filter(lambda x: x.name in iuclist, item.domain)

#change the domain of each item depending on their exclusive unary constraint
for line in lines_dict[4]:
    euclist = line.split()
    item = getByName(items, euclist.pop(0))
    item.domain = filter(lambda x: x.name not in euclist, item.domain)

if options.verbose:
    for item in items:
        print item.name + ': ' + str(map(lambda item: item.name, item.domain))

constraint_matrices = {}
#create constraint matrices for binary equals
for line in lines_dict[5]:
    belist = line.split()
    item1 = getByName(items, belist[0])
    item2 = getByName(items, belist[1])
    cons_name = ','.join(belist)

    constraint_matrices[cons_name] = defaultdict(dict)

    for b1 in bags:
        for b2 in bags:
            if b1 is not b2:
                constraint_matrices[cons_name][b1.name][b2.name] = False
                continue
            if (b1 in item1.domain) & (b2 in item2.domain):
                constraint_matrices[cons_name][b1.name][b2.name] = True
            else:
                constraint_matrices[cons_name][b1.name][b2.name] = False

#create constraint matrices for binary not equals
for line in lines_dict[6]:
    bnelist = line.split()
    item1 = getByName(items, bnelist[0])
    item2 = getByName(items, bnelist[1])
    cons_name = ','.join(bnelist)

    if cons_name not in constraint_matrices.keys():
        constraint_matrices[cons_name] = defaultdict(dict)
        already_set = False
    else:
        already_set = True

    for b1 in bags:
        for b2 in bags:
            if b1 is b2:
                constraint_matrices[cons_name][b1.name][b2.name] = False
                continue
            if (b1 in item1.domain) & (b2 in item2.domain):
                constraint_matrices[cons_name][b1.name][b2.name] = True
            else:
                constraint_matrices[cons_name][b1.name][b2.name] = False

#create constraint matrices for mutual exclusive
for line in lines_dict[7]:
    melist = line.split()
    item1 = getByName(items, melist[0])
    item2 = getByName(items, melist[1])
    bag1 = getByName(bags, melist[2])
    bag2 = getByName(bags, melist[3])
    cons_name = ','.join(melist[:2])

    if cons_name not in constraint_matrices.keys():
        constraint_matrices[cons_name] = defaultdict(dict)
        already_set = False
    else:
        already_set = True

    for b1 in bags:
        for b2 in bags:
            if ((b1 is bag1) & (b2 is bag2)) | ((b1 is bag2) & (b2 is bag1)):
                constraint_matrices[cons_name][b1.name][b2.name] = False
                continue
            if (b1 in item1.domain) & (b2 in item2.domain):
                if already_set:
                    continue
                constraint_matrices[cons_name][b1.name][b2.name] = True
            else:
                constraint_matrices[cons_name][b1.name][b2.name] = False

if options.verbose:
    for key in constraint_matrices:
        print 'matrix for ' + key + ': ' + str(constraint_matrices[key])

initial_nodes = []
for item in items:
    initial_nodes.extend([item.name + '-' + str(value.name) for value in item.domain])

if options.mrv:
    initial_nodes = generateMRVNodes(initial_nodes)

if options.verbose:
    print 'initial nodes: ' + str(initial_nodes)
#print 'gnn test: ' + str(generateNewNodes(initial_nodes, initial_nodes[0]))
# print 'mrv test: ' + str(generateMRVNodes(initial_nodes, 'lcv'))

solution = backtrack(initial_nodes, [], options.fc, options.mrv, options.tiebreak, options.ac3)
timestamp = time.time() - timestamp
timehour = int(timestamp / 3600)
timestamp -= timehour * 3600
timemin = int(timestamp / 60)
timestamp -= timemin * 60
timesec = timestamp
print "time: %dh %dm %fs" % (timehour, timemin, timesec)
print "Consistency Checks happened : ", counter, " times."
if not solution:
    print "This problem has no solution"
    sys.exit()

bag_dict = defaultdict(list)
for node in solution:
    nlist = node.split('-')
    item_name = nlist[0]
    bag_name = nlist[1]
    bag_dict[bag_name].append(item_name)

print 'The solution is '  # + str(bag_dict)
for key in bag_dict:
    blist = bag_dict[key]
    print "bag-" + key + ": " + str(blist)
    weight_sum = sum([getByName(items, item).weight for item in blist])
    capacity = getByName(bags, key).capacity
    percent = (100.0 * weight_sum) / capacity
    print "percent filled: " + str(weight_sum) + ' / ' + str(capacity) + ' = ' + str(percent) + '%'
