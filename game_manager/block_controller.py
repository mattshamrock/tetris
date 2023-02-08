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
        self.block_number = GameStatus["judge_info"]["block_index"]
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
        self.maxY = max(cur_board)

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
        cases = min(180, len(scenario1))

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
        cases = min(180, len(scenario2))

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
        cases = min(180, len(scenario3))

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
        cases = min(180, len(scenario4))

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
        lengths = len(scenario0)+len(scenario1)+len(scenario2)+len(scenario3)+len(scenario4)+len(scenario5)


        if self.block_number >= 179:
            bestscenario =  scenario0[0]
        elif self.block_number >= 178:
            bestscenario =  scenario1[0]
        elif self.block_number >= 177:
            bestscenario =  scenario2[0]
        elif self.block_number >= 176:
            bestscenario =  scenario3[0]
        elif self.block_number >= 175:
            bestscenario =  scenario4[0]
        else:
            bestscenario = scenario5[0]   
        
        #print("bestscenario : ", bestscenario)
        # search best nextMove -->
        nextMove["strategy"]["direction"] = bestscenario[0][2]
        nextMove["strategy"]["x"] = bestscenario[0][3]
        nextMove["strategy"]["y_operation"] = 1
        nextMove["strategy"]["y_moveblocknum"] = 1
        nextMove["strategy"]["use_hold_function"] = bestscenario[0][4]
        # search best nextMove <--

        """
        #★★★★★★★★★★★★★★★★ to be deleted　★★★★★★★★★★★★★★★★★★★★★★★★
        path = '..\\tetris\\game_manager\\log_board.txt'
        with open (path, mode ="a") as f:
            f.write("\n")
            f.write(str(bestscenario[6])+str(bestscenario[0])+str(bestscenario[1])+str(bestscenario[2])+str(bestscenario[3])+str(bestscenario[4])+str(bestscenario[5]) + "\n")
            f.write(str(scenario5[1][6])+str(scenario5[1][0])+str(scenario5[1][1])+str(scenario5[1][2])+str(scenario5[1][3])+str(scenario5[1][4])+str(scenario5[1][5])+ "\n")
            f.write(str(scenario5[2][6])+str(scenario5[2][0])+str(scenario5[2][1])+str(scenario5[2][2])+str(scenario5[2][3])+str(scenario5[2][4])+str(scenario5[2][5])+ "\n")

        path = '..\\tetris\\game_manager\\log_time.txt'
        self.RDseed = GameStatus["debug_info"]["random_seed"]
        with open (path, mode ="a") as f:
            f.write("\n")
            f.write(str(self.RDseed)+ "=== " + str(datetime.now() - t1) + " ___ total scenario : " +str(lengths))
        #★★★★★★★★★★★★★★★★ to be deleted　★★★★★★★★★★★★★★★★★★★★★★★★
        """
        
        # return nextMove
        #print("===", datetime.now() - t1, "___ total scenario : ", lengths)

        #print("nextMove is ",nextMove)
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
      
        #evaluation for nHoles is cumuative
        nHoles_cml = 0
        for rnd in range(Round + 1):
            nHoles_cml += test_cond[rnd][7]

        test_cond[6] = test_dy
        #calc fullLines
        absY = [test_dy[0],0,0,0,0,0,0,0,0,0]
        for i in range(1,10):
            absY[i] = absY[i-1] + test_dy[i]
        new_lowY = min(absY)
        fullLines = max((new_lowY - lowY - nHoles_cml),0) #subtract cml to avoid making massive holes to inappropriately judge as fulllines
        test_cond[Round][8] = fullLines

        #===== evaluate test_dy ============================

       
        #Find the lowest x.
        lowest = "mid"
        if new_lowY == absY[0]:
            lowest = "left"
        if new_lowY == absY[9]:
            lowest = "right"
        for i in range(1,9):
            if new_lowY == absY[i]:
                lowest = "mid"

        #calc absdy. exclude either edges of the board
        absdy = 0
        for i in range(0,11):
            absdy += abs(test_dy[i])
        if lowest == "left":
            absdy -= abs(test_dy[0])
        if lowest == "right":
            absdy -= abs(test_dy[10])

        #calc gap
        gap = 0
        deepgap = 0
        for i in range(2,9):
            if abs(test_dy[i]) >=5:
                deepgap += 1
            elif abs(test_dy[i]) >=3:
                gap += 1
        
        if lowest == "right":
            if abs(test_dy[1]) >= 5:
                deepgap += 1
            elif abs(test_dy[1]) >=3:
                gap += 1

        if lowest == "left":
            if abs(test_dy[9]) >= 5:
                deepgap += 1
            elif abs(test_dy[9]) >=3:
                gap += 1

        if lowest == "mid":
            if abs(test_dy[1]) >= 5 or abs(test_dy[9]) >= 5:
                deepgap += 1
            elif abs(test_dy[1]) >=3 or abs(test_dy[9]) >=3:
                gap += 1

       
        sc_absdy = -1
        sc_deepgap = -3000
        sc_gap = -1000

        if self.block_number >= 177:
            fulLscore = [0, 1000, 4000, 10000, 20000]
            sc_nHoles_cml = -50
            sc_mid = -50
            sc_hldOne = 100

        elif self.block_number >= 175  or self.maxY >= 10:
            fulLscore = [0, -100, 3000, 10000, 20000]
            sc_nHoles_cml = -800
            sc_mid = -100
            sc_hldOne = 100

        else:
            fulLscore = [0,-5000,-2000,-300,10000]
            sc_nHoles_cml = -10000
            sc_mid = -1000
            sc_hldOne = 2000

        #calc score
        score = 0
        for rnd in range(Round + 1):
            score += fulLscore[test_cond[rnd][8]]
        score += absdy * sc_absdy
        score += deepgap * sc_deepgap
        score += gap * sc_gap
        score += nHoles_cml * sc_nHoles_cml
        if lowest == "mid":
            score += sc_mid
        if hld_index == 1:
            score += sc_hldOne


        #evaluation for fullLines is cumulative

        #make eigher side the single lowest, even it costs 2 line del.
        #but it should not make holes

        #holding shape 1 is good. but not better than 4 fulllines


        test_cond[Round][6] = score
        return test_cond




BLOCK_CONTROLLER = Block_Controller()
               
