#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import random
import copy
import numpy
import time

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

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
        self.Elapsed_Time = GameStatus["judge_info"]["elapsed_time"]
        t1 = datetime.now()

        # print GameStatus
        #print("★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★>")
        #pprint.pprint(GameStatus, width = 61, compact = True)

        #Get current dy 
        field_board = GameStatus["field_info"]["backboard"]
        pprint.pprint(field_board, width = 31, compact = True)
        cur_board = [0,22,22,22,22,22,22,22,22,22,22,0]
        for x in range(10):
            for y in range(22):
                xy = y*10 + x
                if field_board[xy] == 0:
                    cur_board[x+1] -= 1
                else:
                    break
        print("cur_board : ",cur_board)
        cur_dy = [0,0,0,0,0,0,0,0,0,0,0]
        for i in range(11):
            cur_dy[i] = cur_board[i+1] - cur_board[i]
        print("cur_dy : ",cur_dy)

        #[0:"trial_id", 1:shapeindex, 2:direction, 3:Xcoord, 4:"y/n", 5:hldindex, 6:EvalValue, 7:nHoles, 8:nLines] 6:dyList
        test_cond = [["00000",0,0,0,"n",None,-100,0,0],
                    ["10000",0,0,0,"n",None,-100,0,0],
                    ["20000",0,0,0,"n",None,-100,0,0],
                    ["30000",0,0,0,"n",None,-100,0,0],
                    ["40000",0,0,0,"n",None,-100,0,0],
                    ["50000",0,0,0,"n",None,-100,0,0],
                    ["dy"]]

        #===== round 0 ===================================================
        Round = 0
        scenario0 =[]
        #get lowest Y to calc deleted rows
        lowY = min(cur_board[1:11])

        #get info for each test case
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element0"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element0"]["direction_range"]
        hld_index = GameStatus["block_info"]["holdShape"]["index"]
        hld_direction = GameStatus["block_info"]["holdShape"]["direction_range"]
        trial_id = 1

        #===== non-hold ===============
        HoldYN = "n"
        for direction in directions_rnd:
            # for each possible ref. point (x) 
            for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(cur_dy)         
                test_cond = self.getTestCase(trial_id = trial_id,
                                        test_cond = test_cond,
                                        Round = Round,
                                        test_dy = before_dy,
                                        shapeindex = index_rnd,
                                        direction = direction,
                                        Xcoord = test_Xcoord,
                                        HoldYN = HoldYN,
                                        hld_index = hld_index,
                                        lowY = lowY)

                scenario0.append(copy.copy(test_cond))
                trial_id += 1

        #===== hold ===============
        HoldYN = "y"
        if hld_index == None:
            #use copy func to keep cur_ independent of test_
            before_dy = copy.copy(cur_dy)         
            test_cond = self.getTestCase(trial_id = trial_id,
                                    test_cond = test_cond,
                                    Round = Round,
                                    test_dy = before_dy,
                                    shapeindex = 0,
                                    direction = 0,
                                    Xcoord = 0,
                                    HoldYN = HoldYN,
                                    hld_index = index_rnd,
                                    lowY = lowY)

            scenario0.append(copy.copy(test_cond))
            trial_id += 1

        elif hld_index != index_rnd: 
            for direction in hld_direction:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(cur_dy)               
                    test_cond = self.getTestCase(trial_id = trial_id,
                                            test_cond = test_cond,
                                            Round = Round,
                                            test_dy = before_dy,
                                            shapeindex = hld_index,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = index_rnd,
                                            lowY = lowY)

                    scenario0.append(copy.copy(test_cond))
                    trial_id += 1
        else:
            pass
        scenario0.sort(reverse = True, key = lambda x:x[Round][6])

        #===== round 1 ===================================================
        Round = 1
        scenario1 = []
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element1"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element1"]["direction_range"]

        for eachsce in scenario0:
            #get lowest Y to calc deleted rows
            lowY = 99
            testlowY = 0
            for i in range(10):
                testlowY += eachsce[6][i]
                lowY = min(lowY, testlowY)

            #get info for each test case
            hld_index = eachsce[Round-1][5]
            if hld_index != None:
                hld_direction = self.dir_range[hld_index]

            trial_id = 1

            #===== non-hold ===============
            HoldYN = "n"
            for direction in directions_rnd:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(eachsce[6]) 
                    test_cond = self.getTestCase(trial_id = trial_id,
                                            test_cond = copy.copy(eachsce),
                                            Round = Round,
                                            test_dy = before_dy,
                                            shapeindex = index_rnd,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = hld_index,
                                            lowY = lowY)
                    scenario1.append(copy.copy(test_cond))
                    trial_id += 1

            #===== hold ===============
            HoldYN = "y"
            if hld_index == None:
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(eachsce[6])         
                test_cond = self.getTestCase(trial_id = trial_id,
                                        test_cond = copy.copy(eachsce),
                                        Round = Round,
                                        test_dy = before_dy,
                                        shapeindex = 0,
                                        direction = 0,
                                        Xcoord = 0,
                                        HoldYN = HoldYN,
                                        hld_index = index_rnd,
                                        lowY = lowY)

                scenario1.append(copy.copy(test_cond))
                trial_id += 1
            
            elif hld_index != index_rnd: 
                for direction in hld_direction:
                    # for each possible ref. point (x) 
                    for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                        #use copy func to keep cur_ independent of test_
                        before_dy = copy.copy(eachsce[6])                 
                        test_cond = self.getTestCase(trial_id = trial_id,
                                                test_cond = copy.copy(eachsce),
                                                Round = Round,
                                                test_dy = before_dy,
                                                shapeindex = hld_index,
                                                direction = direction,
                                                Xcoord = test_Xcoord,
                                                HoldYN = HoldYN,
                                                hld_index = index_rnd,
                                                lowY = lowY)

                        scenario1.append(copy.copy(test_cond))
                        trial_id += 1
            else:
                pass
            
        scenario1.sort(reverse = True, key = lambda x:x[Round][6])


        #===== round 2 ===================================================
        Round = 2
        scenario2 = []
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element2"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element2"]["direction_range"]
        cases = min(150, len(scenario1))

        for eachsce in scenario1[0:cases]:
            #get lowest Y to calc deleted rows
            lowY = 99
            testlowY = 0
            for i in range(10):
                testlowY += eachsce[6][i]
                lowY = min(lowY, testlowY)

            #get info for each test case
            hld_index = eachsce[Round-1][5]
            if hld_index != None:
                hld_direction = self.dir_range[hld_index]

            trial_id = 1

            #===== non-hold ===============
            HoldYN = "n"
            for direction in directions_rnd:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(eachsce[6]) 
                    test_cond = self.getTestCase(trial_id = trial_id,
                                            test_cond = copy.copy(eachsce),
                                            Round = Round,
                                            test_dy = before_dy,
                                            shapeindex = index_rnd,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = hld_index,
                                            lowY = lowY)
                    scenario2.append(copy.copy(test_cond))
                    trial_id += 1

            #===== hold ===============
            HoldYN = "y"
            if hld_index == None:
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(eachsce[6])         
                test_cond = self.getTestCase(trial_id = trial_id,
                                        test_cond = copy.copy(eachsce),
                                        Round = Round,
                                        test_dy = before_dy,
                                        shapeindex = 0,
                                        direction = 0,
                                        Xcoord = 0,
                                        HoldYN = HoldYN,
                                        hld_index = index_rnd,
                                        lowY = lowY)

                scenario2.append(copy.copy(test_cond))
                trial_id += 1
            
            elif hld_index != index_rnd: 
                for direction in hld_direction:
                    # for each possible ref. point (x) 
                    for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                        #use copy func to keep cur_ independent of test_
                        before_dy = copy.copy(eachsce[6])                 
                        test_cond = self.getTestCase(trial_id = trial_id,
                                                test_cond = copy.copy(eachsce),
                                                Round = Round,
                                                test_dy = before_dy,
                                                shapeindex = hld_index,
                                                direction = direction,
                                                Xcoord = test_Xcoord,
                                                HoldYN = HoldYN,
                                                hld_index = index_rnd,
                                                lowY = lowY)

                        scenario2.append(copy.copy(test_cond))
                        trial_id += 1
            else:
                pass
          
        scenario2.sort(reverse = True, key = lambda x:x[Round][6])



        #===== round 3 ===================================================
        Round = 3
        scenario3 = []
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element3"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element3"]["direction_range"]
        cases = min(150, len(scenario2))

        for eachsce in scenario2[0:cases]:
            #get lowest Y to calc deleted rows
            lowY = 99
            testlowY = 0
            for i in range(10):
                testlowY += eachsce[6][i]
                lowY = min(lowY, testlowY)

            #get info for each test case
            hld_index = eachsce[Round-1][5]
            if hld_index != None:
                hld_direction = self.dir_range[hld_index]

            trial_id = 1

            #===== non-hold ===============
            HoldYN = "n"
            for direction in directions_rnd:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(eachsce[6]) 
                    test_cond = self.getTestCase(trial_id = trial_id,
                                            test_cond = copy.copy(eachsce),
                                            Round = Round,
                                            test_dy = before_dy,
                                            shapeindex = index_rnd,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = hld_index,
                                            lowY = lowY)
                    scenario3.append(copy.copy(test_cond))
                    trial_id += 1

            #===== hold ===============
            HoldYN = "y"
            if hld_index == None:
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(eachsce[6])         
                test_cond = self.getTestCase(trial_id = trial_id,
                                        test_cond = copy.copy(eachsce),
                                        Round = Round,
                                        test_dy = before_dy,
                                        shapeindex = 0,
                                        direction = 0,
                                        Xcoord = 0,
                                        HoldYN = HoldYN,
                                        hld_index = index_rnd,
                                        lowY = lowY)

                scenario3.append(copy.copy(test_cond))
                trial_id += 1
            
            elif hld_index != index_rnd: 
                for direction in hld_direction:
                    # for each possible ref. point (x) 
                    for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                        #use copy func to keep cur_ independent of test_
                        before_dy = copy.copy(eachsce[6])                 
                        test_cond = self.getTestCase(trial_id = trial_id,
                                                test_cond = copy.copy(eachsce),
                                                Round = Round,
                                                test_dy = before_dy,
                                                shapeindex = hld_index,
                                                direction = direction,
                                                Xcoord = test_Xcoord,
                                                HoldYN = HoldYN,
                                                hld_index = index_rnd,
                                                lowY = lowY)

                        scenario3.append(copy.copy(test_cond))
                        trial_id += 1
            else:
                pass
          
        scenario3.sort(reverse = True, key = lambda x:x[Round][6])


        #===== round 4 ===================================================
        Round = 4
        scenario4 = []
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element4"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element4"]["direction_range"]
        cases = min(150, len(scenario3))

        for eachsce in scenario3[0:cases]:
            #get lowest Y to calc deleted rows
            lowY = 99
            testlowY = 0
            for i in range(10):
                testlowY += eachsce[6][i]
                lowY = min(lowY, testlowY)

            #get info for each test case
            hld_index = eachsce[Round-1][5]
            if hld_index != None:
                hld_direction = self.dir_range[hld_index]

            trial_id = 1

            #===== non-hold ===============
            HoldYN = "n"
            for direction in directions_rnd:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(eachsce[6]) 
                    test_cond = self.getTestCase(trial_id = trial_id,
                                            test_cond = copy.copy(eachsce),
                                            Round = Round,
                                            test_dy = before_dy,
                                            shapeindex = index_rnd,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = hld_index,
                                            lowY = lowY)
                    scenario4.append(copy.copy(test_cond))
                    trial_id += 1

            #===== hold ===============
            HoldYN = "y"
            if hld_index == None:
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(eachsce[6])         
                test_cond = self.getTestCase(trial_id = trial_id,
                                        test_cond = copy.copy(eachsce),
                                        Round = Round,
                                        test_dy = before_dy,
                                        shapeindex = 0,
                                        direction = 0,
                                        Xcoord = 0,
                                        HoldYN = HoldYN,
                                        hld_index = index_rnd,
                                        lowY = lowY)

                scenario4.append(copy.copy(test_cond))
                trial_id += 1
            
            elif hld_index != index_rnd: 
                for direction in hld_direction:
                    # for each possible ref. point (x) 
                    for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                        #use copy func to keep cur_ independent of test_
                        before_dy = copy.copy(eachsce[6])                 
                        test_cond = self.getTestCase(trial_id = trial_id,
                                                test_cond = copy.copy(eachsce),
                                                Round = Round,
                                                test_dy = before_dy,
                                                shapeindex = hld_index,
                                                direction = direction,
                                                Xcoord = test_Xcoord,
                                                HoldYN = HoldYN,
                                                hld_index = index_rnd,
                                                lowY = lowY)

                        scenario4.append(copy.copy(test_cond))
                        trial_id += 1
            else:
                pass
          
        scenario4.sort(reverse = True, key = lambda x:x[Round][6])


        #===== round 5 ===================================================
        Round = 5
        scenario5 = []
        index_rnd = GameStatus["block_info"]["nextShapeList"]["element5"]["index"]
        directions_rnd = GameStatus["block_info"]["nextShapeList"]["element5"]["direction_range"]
        cases = min(150, len(scenario3))

        for eachsce in scenario4[0:cases]:
            #get lowest Y to calc deleted rows
            lowY = 99
            testlowY = 0
            for i in range(10):
                testlowY += eachsce[6][i]
                lowY = min(lowY, testlowY)

            #get info for each test case
            hld_index = eachsce[Round-1][5]
            if hld_index != None:
                hld_direction = self.dir_range[hld_index]

            trial_id = 1

            #===== non-hold ===============
            HoldYN = "n"
            for direction in directions_rnd:
                # for each possible ref. point (x) 
                for test_Xcoord in range(self.Xrange[index_rnd][direction][0], self.Xrange[index_rnd][direction][1]+1):
                    #use copy func to keep cur_ independent of test_
                    before_dy = copy.copy(eachsce[6]) 
                    test_cond = self.getTestCase(trial_id = trial_id,
                                            test_cond = copy.copy(eachsce),
                                            Round = Round,
                                            test_dy = before_dy,
                                            shapeindex = index_rnd,
                                            direction = direction,
                                            Xcoord = test_Xcoord,
                                            HoldYN = HoldYN,
                                            hld_index = hld_index,
                                            lowY = lowY)
                    scenario5.append(copy.copy(test_cond))
                    trial_id += 1

            #===== hold ===============
            HoldYN = "y"
            if hld_index == None:
                #use copy func to keep cur_ independent of test_
                before_dy = copy.copy(eachsce[6])         
                test_cond = self.getTestCase(trial_id = trial_id,
                                        test_cond = copy.copy(eachsce),
                                        Round = Round,
                                        test_dy = before_dy,
                                        shapeindex = 0,
                                        direction = 0,
                                        Xcoord = 0,
                                        HoldYN = HoldYN,
                                        hld_index = index_rnd,
                                        lowY = lowY)

                scenario5.append(copy.copy(test_cond))
                trial_id += 1
            
            elif hld_index != index_rnd: 
                for direction in hld_direction:
                    # for each possible ref. point (x) 
                    for test_Xcoord in range(self.Xrange[hld_index][direction][0],self.Xrange[hld_index][direction][1]+1):
                        #use copy func to keep cur_ independent of test_
                        before_dy = copy.copy(eachsce[6])                 
                        test_cond = self.getTestCase(trial_id = trial_id,
                                                test_cond = copy.copy(eachsce),
                                                Round = Round,
                                                test_dy = before_dy,
                                                shapeindex = hld_index,
                                                direction = direction,
                                                Xcoord = test_Xcoord,
                                                HoldYN = HoldYN,
                                                hld_index = index_rnd,
                                                lowY = lowY)

                        scenario5.append(copy.copy(test_cond))
                        trial_id += 1
            else:
                pass
          
        scenario5.sort(reverse = True, key = lambda x:x[Round][6])





        #print some of the best 
        i = 0
        for eachsce in scenario5:
            if i <3:
                print(eachsce)
            i += 1
        print("total scenario considered is : ", i)


        bestscenario = scenario5[0]
        print("bestscenario : ", bestscenario)
        # search best nextMove -->
        # random sample
        nextMove["strategy"]["direction"] = bestscenario[0][2]
        nextMove["strategy"]["x"] = bestscenario[0][3]
        nextMove["strategy"]["y_operation"] = 1
        nextMove["strategy"]["y_moveblocknum"] = 1
        nextMove["strategy"]["use_hold_function"] = bestscenario[0][4]
        # search best nextMove <--

        # return nextMove
        print("===", datetime.now() - t1)
        print("nextMove is ",nextMove)
        return nextMove


    def getTestCase(self,test_cond,Round,test_dy,trial_id,shapeindex,direction,Xcoord,HoldYN,hld_index,lowY):
        EvalValue = -999
        nHoles = 0
        nLines = 0
        test_cond[Round] = ["{0:05d}".format(trial_id),
                            shapeindex,
                            direction,
                            Xcoord,
                            HoldYN,
                            hld_index,
                            EvalValue,
                            nHoles,
                            nLines]
       
        #adjust x to where each block actually starts, i.e. the diff btwn ref. point and left edge of the block
        refpoint = self.Xrange[test_cond[Round][1]][test_cond[Round][2]][0]
        adjx = 0 - refpoint
        #add dy for each cur_dy to see what comes
        index = 0
        for test_adddy in self.dy_add[test_cond[Round][1]][test_cond[Round][2]]:
            test_dy[test_cond[Round][3]+adjx+index] += test_adddy
            index += 1

        #difference from ideal dy
        dy_dif = []
        #in relative height, stating left side as 0 
        index = 0
        for dyideal in self.dy_ideal[test_cond[Round][1]][test_cond[Round][2]]:
            dy_dif.append(test_dy[test_cond[Round][3]+adjx + 1 + index] - dyideal)
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
                test_dy[test_cond[Round][3] + adjx + i] += max_ydif
                nHoles += max_ydif
            #adjust for the rest of dy_dif
            else:
                test_dy[test_cond[Round][3] + adjx + i] -= dy_dif[i-1]
                nHoles += (max_ydif -y_dif[i])
                #adjust the right side
                if i == len(y_dif)-1:
                    test_dy[test_cond[Round][3] + adjx + i + 1] -= max_ydif - y_dif[-1]
        test_cond[Round][7] = nHoles
      
        test_cond[6] = test_dy
        #calc fullLines
        absY = [test_dy[0],0,0,0,0,0,0,0,0,0]
        for i in range(1,10):
            absY[i] = absY[i-1] + test_dy[i]
        new_lowY = min(absY)
        fullLines = max((new_lowY - lowY - nHoles),0)
        test_cond[Round][8] = fullLines

        #===== evaluate test_dy ============================
        score = 0

        #calc absdy. include both edges of the board
        absdy = 0
        for i in range(1,10):
            absdy += abs(test_dy[i])
        score += absdy * -1

        #calc gap
        gap = 0
        for i in range(1,9):
            if abs(test_dy[i]) >=3:
                gap += 1
        score += gap * -1000
        

        #Find the lowest x.
        lowest = "mid"
        if new_lowY == absY[0]:
            lowest = "right"
        if new_lowY == absY[9]:
            lowest = "left"
        for i in range(1,8):
            if new_lowY == absY[i]:
                lowest = "mid"
        
        #make eigher side the single lowest, even it costs 2 line del.
        #but it should not make holes
        if lowest == "mid":
            score += -500

        #holding shape 1 is good. but not better than 4 fulllines
        if hld_index == 1:
            score += 6000

        #evaluation for nHoles is cumuative
        nHoles_cml = nHoles
        if Round != 0:
            for rnd in range(Round + 1):
                nHoles_cml += test_cond[rnd][7]

        score += nHoles_cml * -10000

        #evaluation for fullLines is cumulative
        if self.Elapsed_Time >= 175:
            fulLscore = [0,100, 500 , 1000, 10000]
        else:
            fulLscore = [0,-5000,-1000,-500,10000]
        for rnd in range(Round + 1):
            score += fulLscore[test_cond[rnd][8]]


        test_cond[Round][6] = score
        return test_cond





BLOCK_CONTROLLER = Block_Controller()
               
