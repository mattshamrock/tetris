#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import random
import copy
import numpy
import time

class Block_Controller(object):

    Xrange = [[[0,0]],
            [[0,9],[2,8]],
            [[0,8],[1,8],[1,9],[1,8]],
            [[1,9],[1,8],[0,8],[1,8]],
            [[0,8],[1,8],[1,9],[1,8]],
            [[0,8]],
            [[1,8],[0,8]],
            [[1,8],[0,8]]]

    dy_add = [[[0]],
        [[4,-4],[1,0,0,0,-1]],
        [[3,-2,-1],[2,-1,0,-1],[1,2,-3],[1,0,1,-2]],
        [[1,2,-3],[2,-1,0,-1],[3,-2,-1],[1,0,1,-2]],
        [[3,-2,-1],[1,1,-1,-1],[1,2,-3],[1,1,-1,-1]],
        [[2,0,-2]],
        [[1,1,-1,-1],[2,0,-2]],
        [[1,1,-1,-1],[2,0,-2]]]

    dy_ideal = [[[]],
        [[],[0,0,0]],
        [[-2],[0,0],[0],[0,1]],
        [[2],[-1,0],[0],[0,0]],
        [[-1],[0,0],[1],[1,-1]],
        [[0]],
        [[1,0],[-1]],
        [[0,-1],[1]]]

    dir_range = [[0],
                [0,1],
                [0,1,2,3],
                [0,1,2,3],
                [0,1,2,3],
                [0],
                [0,1],
                [0,1]]

    # GetNextMove is main function.
    # input
    #    GameStatus : this data include all field status, 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : this data include next shape position and the other,
    #               if return None, do nothing to nextMove.


    def GetNextMove(self, nextMove, GameStatus):
        t1 = datetime.now()

        # print GameStatus
        #pprint.pprint(GameStatus, width = 61, compact = True)

        #Get current dy 
        field_board = GameStatus["field_info"]["backboard"]
        #pprint.pprint(field_board, width = 31, compact = True)

        cur_board = [0,22,22,22,22,22,22,22,22,22,22,0]
        for x in range(10):
            for y in range(22):
                xy = y*10 + x
                if field_board[xy] == 0:
                    cur_board[x+1] -= 1
                else:
                    break
        #print("cur_board : ",cur_board)
        cur_dy = [0,0,0,0,0,0,0,0,0,0,0]
        for i in range(11):
            cur_dy[i] = cur_board[i+1] - cur_board[i]
        #print("cur_dy : ",cur_dy)
           

        """
        #★★★★★★★★★★★★★★★★ to be deleted　★★★★★★★★★★★★★★★★★★★★★★★★
        path = '..\\tetris\\game_manager\\log_board.txt'
        with open (path, mode ="a") as f:
            f.write("\n")
            f.write("block_number : " + str(self.block_number))
            for y in range(22):
                f.write("\n")
                for x in range(10):
                    boardElmt = field_board[y*10+x] 
                    f.write(str(boardElmt).replace("0","_")+" "
                    )  

            f.write("\n" + "cur_board : " + str(cur_board) + "\n")
            f.write(str(cur_dy) + "\n")
        #★★★★★★★★★★★★★★★★ to be deleted　★★★★★★★★★★★★★★★★★★★★★★★★
        """

        #[0:shapeindex, 1:direction, 2:Xcoord, 3:"y/n", 4:hldindex, 5:EvalValue, 6:nHoles, 7:nLines] 1:dyList
        self.test_cond = [[0,0,0,"n",None,-999999,0,0],["dy"]]

        #get lowest Y to calc deleted rows
        self.lowY = min(cur_board[1:11])

        #get info for each test case
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element0"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element0"]["direction_range"]
        hld_index = GameStatus["block_info"]["holdShape"]["index"]
        hld_direction = GameStatus["block_info"]["holdShape"]["direction_range"]


        bestscenario = [[0,0,0,"n",None,-999999,0,0],["dy"]]

        #===== non-hold ===============
        HoldYN = "n"
        for direction in directions_rnd:
            # for each possible ref. point (x) 
            for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(cur_dy)         
                self.test_cond = self.getTestCase(
                                        test_dy = before_dy,
                                        shapeindex = index_rnd,
                                        direction = direction,
                                        Xcoord = test_Xcoord,
                                        HoldYN = HoldYN,
                                        hld_index = hld_index
                                                                )
                if self.test_cond[0][5] >= bestscenario[0][5]:
                    bestscenario = copy.copy(self.test_cond)

        #===== hold ===============
        HoldYN = "y"
        if hld_index == None:
            #use copy func to keep cur_ independent of test_
            before_dy = copy.copy(cur_dy)         
            self.test_cond = self.getTestCase(
                                    test_dy = before_dy,
                                    shapeindex = 0,
                                    direction = 0,
                                    Xcoord = 0,
                                    HoldYN = HoldYN,
                                    hld_index = index_rnd,
                                                )
            if self.test_cond[0][5] >= bestscenario[0][5]:
                bestscenario = copy.copy(self.test_cond)

        elif hld_index != index_rnd: 
            for direction in hld_direction:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(cur_dy)               
                    self.test_cond = self.getTestCase(
                                            test_dy = before_dy,
                                            shapeindex = hld_index,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = index_rnd,
                                                            )

                    if self.test_cond[0][5] >= bestscenario[0][5]:
                        bestscenario = copy.copy(self.test_cond)

  
        #print("bestscenario : ", bestscenario)
        # search best nextMove -->
        nextMove["strategy"]["direction"] = bestscenario[0][1]
        nextMove["strategy"]["x"] = bestscenario[0][2]
        nextMove["strategy"]["y_operation"] = 1
        nextMove["strategy"]["y_moveblocknum"] = 1
        nextMove["strategy"]["use_hold_function"] = bestscenario[0][3]
        # search best nextMove <--
        """
        #★★★★★★★★★★★★★★★★ to be deleted　★★★★★★★★★★★★★★★★★★★★★★★★
       
        path = '..\\tetris\\game_manager\\log_board.txt'
        with open (path, mode ="a") as f:
            f.write(str(bestscenario[6])+str(bestscenario[0])+str(bestscenario[1])+str(bestscenario[2])+str(bestscenario[3])+str(bestscenario[4])+str(bestscenario[5]) + "\n")
            f.write(str(scenario5[1][6])+str(scenario5[1][0])+str(scenario5[1][1])+str(scenario5[1][2])+str(scenario5[1][3])+str(scenario5[1][4])+str(scenario5[1][5])+ "\n")
            f.write(str(scenario5[2][6])+str(scenario5[2][0])+str(scenario5[2][1])+str(scenario5[2][2])+str(scenario5[2][3])+str(scenario5[2][4])+str(scenario5[2][5])+ "\n")
       
       
        path = '..\\tetris\\game_manager\\log_time.txt'
        self.RDseed = GameStatus["debug_info"]["random_seed"]
        with open (path, mode ="a") as f:
            f.write("\n")
            f.write(str(self.RDseed)+ " ★★★784 ===," + str(datetime.now() - t1) + " ,___ total scenario : " +str(lengths))
        #★★★★★★★★★★★★★★★★ to be deleted　★★★★★★★★★★★★★★★★★★★★★★★★
        """
        # return nextMove
        #print("===", datetime.now() - t1, ",___ total scenario : ", lengths)

        #print("nextMove is ",nextMove)
        return nextMove


    def getTestCase(self,test_dy,shapeindex,direction,Xcoord,HoldYN,hld_index):
        EvalValue = -999
        nHoles = 0
        nLines = 0
        self.test_cond[0] = [
                            shapeindex,
                            direction,
                            Xcoord,
                            HoldYN,
                            hld_index,
                            EvalValue,
                            nHoles,
                            nLines]
       
        #adjust x to where each block actually starts, i.e. the diff btwn ref. point and left edge of the block
        refpoint = self.Xrange[shapeindex][direction][0]
        adjx = 0 - refpoint
        #add dy for each cur_dy to see what comes
        index = 0
        for test_adddy in self.dy_add[shapeindex][direction]:
            test_dy[Xcoord + adjx + index] += test_adddy
            index += 1

        #difference from ideal dy
        dy_dif = []
        #in relative height, stating left side as 0 
        index = 0
        for dyideal in self.dy_ideal[shapeindex][direction]:
            dy_dif.append(test_dy[Xcoord + adjx + 1 + index] - dyideal)
            index += 1               
        
        #in absolute height, to get dy_dif for left edge of the block and to get nHoles                 
        y_dif = [0]
        index = 0
        for i in dy_dif:
            y_dif.append(i + y_dif[index])
            index += 1

        max_ydif = max(y_dif)
        adj_dydif = 1 - refpoint
        """
        print("---------------------------------------")
        print("dy_dif : ",dy_dif," y_dif : ",y_dif)
        print(" test_dy : ",test_dy," max_ydif : " , max_ydif)
        """
        #adjust for y_dif and count nHoles
        nHoles = 0
        for i in range (len(y_dif)):
            #adjust the left side 
            if i == 0:
                test_dy[Xcoord + adjx + i] += max_ydif
                nHoles += max_ydif
            #adjust for the rest of dy_dif
            else:
                test_dy[Xcoord + adjx + i] -= dy_dif[i-1]
                nHoles += (max_ydif -y_dif[i])
                #adjust the right side
                if i == len(y_dif)-1:
                    test_dy[Xcoord + adjx + i + 1] -= max_ydif - y_dif[-1]
        """
        self.test_cond[0][6] = nHoles
        """
        """
        self.test_cond[1] = test_dy
        """
        #calc fullLines
        absY = [test_dy[0],0,0,0,0,0,0,0,0,0]
        for i in range(1,10):
            absY[i] = absY[i-1] + test_dy[i]
        new_lowY = min(absY)
        fullLines = max((new_lowY - self.lowY - nHoles),0) #subtract nHoles to avoid making massive holes to inappropriately judge as fulllines
        """
        self.test_cond[0][7] = fullLines
        """
        #===== evaluate test_dy ============================
       
        #calc absdy. exclude either edges of the board, but only to the height of the other.
        absdy = 0
        for i in range(0,11):
            absdy += abs(test_dy[i])
              
        #calc gap
        gap = 0
        deepgap = 0
        for i in range(1,10):
            if abs(test_dy[i]) >=5:
                deepgap += 1
            elif abs(test_dy[i]) >=3:
                gap += 1

        
        new_maxY = max(absY) - fullLines
        
        sc_absdy = -1
        sc_deepgap = -50000
        sc_gap = -1000
        sc_newmaxY = -50

        fulLscore = [0, -405, 100 , 100000, 300000]
        if new_maxY >= 10:       
            fulLscore = [0, 100, 1000 , 100000, 300000]
        sc_nHoles = -5000
        sc_hldOne = 200

        #calc score
        #evaluation for fullLines is cumulative

        #make eigher side the single lowest, even it costs 2 line del.
        #but it should not make holes

        #holding shape 1 is good. but not better than 4 fulllines

        score = 0
        score += fulLscore[fullLines]
        score += absdy * sc_absdy
        score += deepgap * sc_deepgap
        score += gap * sc_gap
        score += nHoles * sc_nHoles
        score += new_maxY * sc_newmaxY

        if hld_index == 1:
            score += sc_hldOne

        self.test_cond[0][5] = score

        return self.test_cond


BLOCK_CONTROLLER = Block_Controller()
               
