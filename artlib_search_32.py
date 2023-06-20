import sys
import subprocess
import copy
import numpy
import time


board = [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [9,9,9,9,9,9,9,9,9,9],
        ]

range_y = len(board)-1

refpoint_relative = [[0],
                    [[[0,-1],[0,1],[0,2]],[[-2,0],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[1,1]],[[-1,0],[1,0],[-1,1]],[[-1,-1],[0,-1],[0,1]],[[1,-1],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[-1,1]],[[-1,-1],[-1,0],[1,0]],[[0,-1],[1,-1],[0,1]],[[-1,0],[1,0],[1,1]]],
                    [[[0,-1],[1,0],[0,1]],[[0,1],[-1,0],[1,0]],[[0,-1],[-1,0],[0,1]],[[0,-1],[-1,0],[1,0]]],
                    [[[0,-1],[1,-1],[1,0]]],
                    [[[0,-1],[1,-1],[-1,0]],[[0,-1],[1,0],[1,1]]],
                    [[[-1,-1],[0,-1],[1,0]],[[1,-1],[1,0],[0,1]]]
                    ]

Xrange = [[0],
        [[0,10],[2,9]],
        [[0,9],[1,9],[1,10],[1,9]],
        [[1,10],[1,9],[0,9],[1,9]],
        [[0,9],[1,9],[1,10],[1,9]],
        [[0,9]],
        [[1,9],[0,9]],
        [[1,9],[0,9]]
            ]

status = [[[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1]],
board,  board,  board,  board,  board,  board, board,  board,  board ]

blockorder = [6,7,4,2,3,1,5]


def dfs(currentboard,Block,foundflag):
    if foundflag == True:
        pass
    else:
        block = Block
        block += 1
        if block > maxblock:
            printflag1, printflag2 = True, True
            
            printflag1 = CheckTwoBlocks(currentboard = status[maxblock])
            printflag2 = CheckClearRows(currentboard = status[maxblock])

            if printflag1 == True and printflag2 == True:
                path = '..\\tetris\\game_manager\\log_art.txt'
                with open (path, mode ="a") as f:
                    f.write("xs_" + str(x1)+str(shape1)+str(x2)+str(shape2)+ " = " + str(status[0])+ "\n")            
                foundflag = True
                """
                for i in range(range_y+1):
                    with open (path, mode ="a") as f:
                        f.write(str(status[maxblock][i])+ "\n")
                """
        else:
            for shape in blockorder:
                for rotate in range(len(refpoint_relative[shape])):
                    for Xgrid in range(Xrange[shape][rotate][0],Xrange[shape][rotate][1]):
                        for Ygrid in range(2,range_y+1):
                            newboard = copy.deepcopy(currentboard)
                            refpoint = [Xgrid,Ygrid]
                            
                            gridref = newboard[refpoint[1]][refpoint[0]] 
                            grid0 = newboard[refpoint[1] + refpoint_relative[shape][rotate][0][1]][refpoint[0] +  refpoint_relative[shape][rotate][0][0]]
                            grid1 = newboard[refpoint[1] + refpoint_relative[shape][rotate][1][1]][refpoint[0] +  refpoint_relative[shape][rotate][1][0]]
                            grid2 = newboard[refpoint[1] + refpoint_relative[shape][rotate][2][1]][refpoint[0] +  refpoint_relative[shape][rotate][2][0]]
                            if gridref == 0 and grid0 == 0 and grid1 == 0 and grid2 == 0:
                                pass
                            else:
                                refpoint = [refpoint[0],refpoint[1]-1]

                                newboard[refpoint[1]][refpoint[0]] = shape
                                for add_grid in range(3):
                                    newboard[refpoint[1] + refpoint_relative[shape][rotate][add_grid][1]][refpoint[0] +  refpoint_relative[shape][rotate][add_grid][0]] = shape

                                clearedboard = clearFullLines(currentboard = newboard)

                                status[0][block-1][0] = shape
                                status[0][block-1][1] = rotate
                                status[0][block-1][2] = Xgrid
                                status[block] = clearedboard

                                contflag1,contflag2,contflag3 = True,True,True
                                contflag1 = CheckBottomRow(currentboard = status[block])
                                contflag2 = CheckTopRow(currentboard = status[block])
                                contflag3 = CheckHoles(currentboard = status[block])

                                if contflag1 == True and contflag2== True and contflag3 == True:
                                    dfs(currentboard = status[block],Block = block,foundflag = foundflag)
                                    status[0][block-1] = [0,0,0,1]
                                        
                                else:
                                    break
                                break

def CheckBottomRow(currentboard):
    check = False
    BottomRow = currentboard[range_y - 1]
    i = 0
    for eachgrid in BottomRow:
        if eachgrid != 0:
            if (i == x1 and eachgrid == shape1) or (i == x2 and eachgrid == shape2):
                check = True
            else:
                check = False
                break
        i += 1
    return check


def CheckTwoBlocks(currentboard):
    check = True
    board = currentboard
    Y = range_y -1 
    for X in range(10):
        TestShape = board[Y][X]
        if X == x1:
            if TestShape != shape1:
                check = False 
        elif X == x2:
            if TestShape != shape2:
                check = False 
        else:
            if TestShape != 0:
                check = False
    return check

def CheckTopRow(currentboard):
    check = True
    for num in range(3):
        TopRow = currentboard[num]
        for eachgrid in TopRow:
            if eachgrid != 0:
                check = False
                break
    return check

def clearFullLines(currentboard):
    board = currentboard
    for i in range(range_y):
        row = board[i]
        if row.count(0) == 0:
            for j in range(i,0,-1):
                board[j] = board[j-1]
            board[0] = [0,0,0,0,0,0,0,0,0,0]
            
    return board

def CheckHoles(currentboard):
    check = True
    board = currentboard
    for X in range(10):
        holecandidate = False
        for Y in range(range_y - 2,0,-1):
            if board[Y][X] == 0:
                holecandidate = True
            else:
                if holecandidate == True:
                    check = False
                    break

    return check

def CheckClearRows(currentboard):
    check = True
    for num in range(6):
        TopRow = currentboard[num]
        for eachgrid in TopRow:
            if eachgrid != 0:
                check = False
                break
    return check


maxblock = 8
block = 0
x1, shape1, x2, shape2 = 2,4,6,4
foundflag = False

ans = dfs(currentboard = status[1],Block = block, foundflag = foundflag)
print("done")
