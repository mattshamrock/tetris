import sys
import subprocess
import copy
import numpy
import time


board_init = [
        [9,9,9,9,9,9,9,9,9,9,9,9],
        [9,0,0,0,0,0,0,0,0,0,0,9],
        [9,0,0,0,0,0,0,0,0,0,0,9],
        [9,0,0,0,0,0,0,0,0,0,0,9],
        [9,9,9,9,9,9,9,9,9,9,9,9],
        ]

range_y = len(board_init)-1

refpoint_relative = [[0],
                    [[[0,-1],[0,1],[0,2]],[[-2,0],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[1,1]],[[-1,0],[1,0],[-1,1]],[[-1,-1],[0,-1],[0,1]],[[1,-1],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[-1,1]],[[-1,-1],[-1,0],[1,0]],[[0,-1],[1,-1],[0,1]],[[-1,0],[1,0],[1,1]]],
                    [[[0,-1],[1,0],[0,1]],[[0,1],[-1,0],[1,0]],[[0,-1],[-1,0],[0,1]],[[0,-1],[-1,0],[1,0]]],
                    [[[0,-1],[1,-1],[1,0]]],
                    [[[0,-1],[1,-1],[-1,0]],[[0,-1],[1,0],[1,1]]],
                    [[[-1,-1],[0,-1],[1,0]],[[1,-1],[1,0],[0,1]]]
                    ]

dot_relative = [[0],
                [[-10, 0, 10, 20], [-2, -1, 0, 1]],
                 [[-10, 0, 10, 11], [-1, 0, 1, 9], [-11, -10, 0, 10], [-9, -1, 0, 1]],
                 [[-10, 0, 9, 10], [-11, -1, 0, 1], [-10, -9, 0, 10], [-1, 0, 1, 11]],
                 [[-10, 0, 1, 10], [-1, 0, 1, 10], [-10, -1, 0, 10], [-10, -1, 0, 1]], 
                 [[-10, -9, 0, 1]], 
                 [[-10, -9, -1, 0], [-10, 0, 1, 11]],
                 [[-11, -10, 0, 1], [-9, 0, 1, 10]]
                ]


adj_zero_init = [0 for i in range(30)]

blockorder = [6,7,4,2,3,1,5]

def search_filledboard(board):
    board[4][x1+1] = 0
    board[0][x2+1] = 0
    testboards = fit_shapes(board = board)

    for testboard in testboards:
        notfoundflag = False
        adj_zero = adj_zero_from_testboard(board = testboard)

        rnd = 1
        for block in range(6):
            adj = []
            rnd += 1
            testboard, adj_zero, adj = fill_most_isolated(rnd = rnd, testboard = testboard, adj_zero = adj_zero, adj = adj)
            if adj == []:
                notfoundflag = True
                continue

            for j in range(3):
                testboard, adj_zero, adj = fill_isolated_from_adj(rnd = rnd, testboard = testboard, adj_zero = adj_zero, adj = adj)        
                if adj == [] and j != 2:
                    notfoundflag = True
                    break
        if notfoundflag == False:
            return testboard

    return False

       
def check_bottom(currentboard):
    check = False
    if currentboard[4][x1+1] == 1 and currentboard[4].count(1) == 1:
        check = True
    return check

def check_top(currentboard):
    check = False
    if currentboard[0][x2+1] == 8 and currentboard[0].count(8) == 1:
        check = True
    return check

def check_sides(currentboard):
    for i in range(len(currentboard)):
        if currentboard[i][0] != 9:
            return False
        if currentboard[i][len(currentboard[i])-1] != 9:
            return False
    return True

def check_1and8(currentboard):
    one,eight = 0,0
    for y in range(len(currentboard)):
        for x in range(len(currentboard[y])):
            dot = currentboard[y][x]
            if dot == 1:
                one += 1
            if dot == 8:
                eight += 1
    if one == 4 and eight == 4:
        return True
    else:
        return False

def fit_shapes(board):
    testboards = find_shape1(board = board)
    testboards = find_shape2(boards = testboards)
    return testboards


def find_shape1(board):
    applicable_board = []
    for x in range(x1,x1+3):
        for rotate in refpoint_relative[shape1]:
            testboard = copy.deepcopy(board)
            for dot in rotate:
                # 2 if shapeindex == 1
                testboard[3][x] = 1
                testboard[min(len(testboard)-1,3 + dot[1])][min(len(board[0])-1, x + dot[0])] = 1
            contflag1 = check_sides(currentboard = testboard)
            contflag2 = check_bottom(currentboard = testboard)
            if contflag1 == True and contflag2 == True:
                applicable_board.append(testboard)
                
    return applicable_board

def find_shape2(boards):
    applicable_board = []
    for testboard_ in boards:
        for x in range(x2,x2+3):
            for rotate in refpoint_relative[shape2]:
                testboard = copy.deepcopy(testboard_)
                for dot in rotate:
                    # 2 if shapeindex == 1
                    testboard[1][x] = 8
                    testboard[1 + dot[1]][min(len(board[0])-1, x + dot[0])] = 8
                contflag1 = check_sides(currentboard = testboard)
                contflag2 = check_top(currentboard = testboard)
                contflag3 = check_1and8(currentboard = testboard)                
                if contflag1 == True and contflag2 == True and contflag3 == True:
                    applicable_board.append(testboard)

    return applicable_board

def adj_zero_from_testboard(board):
    adj_zero = copy.deepcopy(adj_zero_init)
    for dot_ in range(len(adj_zero)):
        xaxis = dot_ % 10 + 1
        yaxis = dot_ // 10 + 1
        if board[yaxis][xaxis] != 0:
            adj_zero[dot_] = 9
        else:
            NSWE = [(0,1),(0,-1),(1,0),(-1,0)]
            for nswe in NSWE:
                if board[yaxis + nswe[0]][xaxis + nswe[1]] == 0:
                    adj_zero[dot_] += 1
    return adj_zero


def fill_most_isolated(rnd,testboard,adj_zero, adj):
    isolated = 0
    count = 0
    testdot_ = 4
    endflag = False
    for eachdot_ in adj_zero:
        if testdot_ >= eachdot_ :
            testdot_ = eachdot_
            isolated = count
        count += 1

    testboard = fill_testboard(rnd = rnd, testboard = testboard, isolated = isolated)
    adj_zero,adj = fill_adj_and_adj_zero(isolated = isolated, adj_zero = adj_zero, adj = adj)

    return testboard, adj_zero, adj

def fill_isolated_from_adj(rnd,testboard,adj_zero, adj):
    isolated = 0
    testdot_ = 4
    for eachdot_ in adj:
        if testdot_ >= adj_zero[eachdot_] :
            testdot_ = adj_zero[eachdot_]
            isolated = eachdot_
    adj.remove(isolated)

    testboard = fill_testboard(rnd = rnd, testboard = testboard, isolated = isolated)
    adj_zero,adj = fill_adj_and_adj_zero(isolated = isolated, adj_zero = adj_zero, adj = adj)

    return testboard, adj_zero, adj


def fill_testboard(rnd, testboard, isolated):
    xaxis = isolated % 10 + 1
    yaxis = isolated // 10 + 1
    testboard[yaxis][xaxis] = rnd
    return testboard

def fill_adj_and_adj_zero(isolated, adj_zero, adj):
    adj_zero[isolated] = 9
    adj = set(adj)
    if isolated % 10 != 9 and adj_zero[isolated + 1] != 9:
        adj_zero[isolated + 1] -= 1
        adj.add(isolated + 1)
    if isolated % 10 != 0 and adj_zero[isolated - 1] != 9:
        adj_zero[isolated - 1] -= 1
        adj.add(isolated - 1)
    if isolated // 10 != 2 and adj_zero[isolated + 10] != 9:
        adj_zero[isolated + 10] -= 1
        adj.add(isolated + 10)
    if isolated // 10 != 0 and adj_zero[isolated - 10] != 9:
        adj_zero[isolated - 10] -= 1
        adj.add(isolated - 10)
    adj = list(adj)
    adj.sort()
    return adj_zero,adj

def find_constraint(board):
    constraint = [set() for i in range(10)]
    for x in range(10):
        prior = set()
        for y in range(4): 
            prior.add(board[4-y][x+1])
            constraint[board[4-y][x+1]] = constraint[board[4-y][x+1]].union(prior)
    for s in range(len(constraint)):
        constraint[s].discard(s)
        constraint[s].discard(9)
    return constraint

def find_shapeorder(board,constraint):
    used = [False for i in range(9)]
    x_order = [1,10,2,9,3,8,4,7,5,6]
    shapeorder = []
    while used.count(False) > 0:
        for x in x_order:
            revisit = False
            for y in range(4):
                shape = board[4 - y][x]
                if used[shape-1] == False and constraint[shape] == set():
                    shapeorder.append(shape)
                    used[shape-1] = True
                    for s in range(len(constraint)):
                        constraint[s].discard(shape)
                    revisit = True

                if revisit == True:
                    continue
            if revisit == True:
                continue
    shapeorder.remove(9)
    return shapeorder

def find_dotorder(board,shapeorder):
    dotorder = [[] for i in range(8)]
    for y in range(5):
        for x in range(len(board[y])):
            shape = board[y][x]
            if shape != 9:
                dotorder[shape-1].append((y*10 + x - 1))
    dotorder = [sorted(each) for each in dotorder ]
    ans = []
    for shape in shapeorder:
        ans.append(dotorder[shape-1])
    return ans

def convert_json_format(dot):
    flag = False
    while flag == False:
        dot4 = dot[0:4]
        ans = []
        for shape in range(len(dot_relative)):
            for rotate in range(len(dot_relative[shape])):
                if dot_relative[shape][rotate] == dot4:
                    ans.append(shape)
                    ans.append(rotate)
                    ans.append((dot[4]-dot[0]) % 10)
                    ans.append(1)
                    return ans
        for i in range(4):
            dot[i] -= 1 
        if min(dot) <= -13:
            flag = True

def adjust_dotorder_for_smallest(dotorder):
    for i in range(len(dotorder)):
        smallest = min(dotorder[i])
        for j in range(4):
            dotorder[i][j] = dotorder[i][j] - smallest
        dotorder[i].append(smallest)
    return dotorder


def search_artlib(board):
    board = search_filledboard(board = board)
    if board != False:
        if board[0].count(0) > 0:
            time.sleep(15)
        """
        for pr in board:
            print(pr)
        """
        constraint = find_constraint(board = board)
        shapeorder = find_shapeorder(board = board, constraint = constraint)
        dotorder = find_dotorder(board = board, shapeorder = shapeorder)
        dotorfer = adjust_dotorder_for_smallest(dotorder = dotorder)

        output = []
        for dot in dotorder:
            ans = convert_json_format(dot)
            output.append(ans)
        return output

    else:
        return False


def merge_artlib():
    if key in artdict.keys():
        with open (path, mode ="a") as f:
            f.write('"'+ key + '":' + str(artdict[key]) + "\n")
    else:
        with open (path, mode ="a") as f:
            f.write('"'+ key + '":' + "False," + "\n")

def writeNone():
    with open (path, mode ="a") as f:
        f.write('"xs_' + str(x1)+str(shape1)+"_"+str(x2)+str(shape2)+ '":' + "False," + "\n")

#"""
import art_lib as lib
artdict = lib.artdict
maxblock = 8
block = 0
path = '..\\tetris\\game_manager\\log_art.txt'
for x1 in range(10):
    for x2 in range(10):
        for shape1 in blockorder:
            for shape2 in blockorder:
                key = "xs_" + str(x1)+str(shape1)+"_"+str(x2)+str(shape2)
                print(key)
                if artdict[key] == False:
                    board = copy.deepcopy(board_init)
                    ans = search_artlib(board = board)
                    print(ans)
                    with open (path, mode ="a") as f:
                        f.write('"'+ key + '":' + str(ans) + ","+"\n")
                else:
                    with open (path, mode ="a") as f:
                        f.write('"'+ key + '":' + str(artdict[key]) + ","+"\n")

print("All done")
#"""

"""
x1 = 9
shape1 = 6
x2 = 0
shape2 = 6
board = copy.deepcopy(board_init)
ans = search_artlib(board = board)
print(ans)
"""