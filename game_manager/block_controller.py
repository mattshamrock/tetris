#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy
import re

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

   

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        #print("=================================================>")

        # pprint.pprint(GameStatus, width = 61, compact = True)
        
        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        self.CurrentShape_index = GameStatus["block_info"]["currentShape"]["index"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_index = GameStatus["block_info"]["nextShape"]["index"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        self.Elapsed_Time = GameStatus["judge_info"]["elapsed_time"]
        self.Game_Time = GameStatus["judge_info"]["game_time"]

        # search best nextMove -->
        strategy = None
        LatestEvalValue = -100000
        # search with current block Shape
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)

                # evaluate board
                EvalValue = self.calcEvaluationValueSample(board, self.board_backboard)
                # update best move
                if EvalValue > LatestEvalValue:
                    strategy = (direction0, x0, 1, 1)
                    LatestEvalValue = EvalValue

                ###test
                ###for direction1 in NextShapeDirectionRange:
                ###  x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                ###  for x1 in range(x1Min, x1Max):
                ###        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                ###        EvalValue = self.calcEvaluationValueSample(board2)
                ###        if EvalValue > LatestEvalValue:
                ###            strategy = (direction0, x0, 1, 1)
                ###            LatestEvalValue = EvalValue
        # search best nextMove <--

        #print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        #print(nextMove)
        #print("###### SAMPLE CODE ######")
        selectedBoard = self.getBoard(self.board_backboard, self.CurrentShape_class, strategy[0], strategy[1])
        EvalValue = self.calcEvaluationValueSample(selectedBoard, self.board_backboard,prt = True)

        return nextMove

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board

    def calcEvaluationValueSample(self, board, board_backboard, prt = False):
        
        
        # obtain data for MaxY and Dead Y in current board 
        width = self.board_data_width #10
        height = self.board_data_height #22
        
        CurBlockMaxY = [0] * width
        CurHoleCandidates = [0] * width
        CurDeadY = [0] * height

        for y in range(height - 1, 0, -1): 
            for x in range(width):
                if board_backboard[y * self.board_data_width + x] == self.ShapeNone_index: #0
                    CurHoleCandidates[x] += 1  # just candidates in each column..
                else: #block
                    CurBlockMaxY[x] = height - y
                    if CurHoleCandidates[x] > 0:
                        for z in range(CurHoleCandidates[x]):
                            CurDeadY[y+1+z] = 1
                            CurHoleCandidates[x] = 0                # reset

        # obtain data in current board for minY
        LowestX = ""

        if min(CurBlockMaxY) == CurBlockMaxY[0]:
            LowestX = "Left"
        elif min(CurBlockMaxY) == CurBlockMaxY[width-1]:
            LowestX = "Right"
        else:
            LowestX = "Mid"

        
        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of lines with hole(s).
        nDeadY = 0
        ## absolute differencial value of MaxY
        absDy = 0
        absDyforLowerEdgeY = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        DeadY = [0] * height

        ### check board
        # each y line
        for y in range(height - 1, 0, -1): #range(start,end,progress)
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width): #range(10)=ten times starting in zero
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index: #ただの0
                    # hole
                    hasHole = True
                else:
                    # block
                    hasBlock = True
            if hasBlock == True and hasHole == False:
                # filled with block
                fullLines += 1
            elif hasBlock == False and hasHole == True:
                pass
            else:
                for x in range(width): #range(10)=ten times starting in zero
                    if board[y * self.board_data_width + x] == self.ShapeNone_index: #ただの0
                    #hole
                        holeCandidates[x] += 1  # just candidates in each column..
                    else:
                        #block
                        BlockMaxY[x] = height - y - fullLines    # update BlockMaxY
                        if holeCandidates[x] > 0:
                            holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                            for z in range(holeCandidates[x]):
                                DeadY[y+1+z] = 1
                            holeCandidates[x] = 0                # reset

        # nDeadY
   
        for y in DeadY:
            nDeadY += abs(y)

        #sortedMaxY
        SortedMaxY = sorted(BlockMaxY) #sort the list in ascending order to get min and second min Y

        #adjust FullLines to feasible value
        CurDeadYinRange = CurDeadY[height-1-3-min(CurBlockMaxY) : height-min(CurBlockMaxY)]
        nCurDeadYinRange = 0
        for z in CurDeadYinRange:
            nCurDeadYinRange += abs(z)
        adjFullLines = fullLines + nCurDeadYinRange

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(width - 1):
            val = (BlockMaxY[i] - BlockMaxY[i+1]) 
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)
     
        ### absolute differencial value of Lower Edge Y
        ### MaxY to keep low
        lowerDy = 0        
        keepLow = 0        

        if CurBlockMaxY[0] <= CurBlockMaxY[width-1]:
            lowerDy = BlockMaxDy[0]
            keepLow = BlockMaxY[0]
        else:
            lowerDy = BlockMaxDy[width - 1 - 1]
            keepLow = BlockMaxY[width - 1]
        absDyforLowerEdgeY = abs(lowerDy)

        # Define chasm as a gap requires I shape
        Chasm = 0
        if LowestX == "Left":
            for x in range (1 , width-2 , 1):
                if BlockMaxDy[x] >= 3:
                    if BlockMaxDy[x+1] <= -3:
                        Chasm = 1
            if BlockMaxDy[width-2] >= 3:
                Chasm = 1
            
        else:
            for x in range (0 , width-3 , 1):
                if BlockMaxDy[x] >= 3:
                    if BlockMaxDy[x+1] <= -3:
                        Chasm = 1
            if BlockMaxDy[width-3] >= 3:
                Chasm = 1
            

        #evaluate fitness of the next shape

        NextShapeCapable = False
        mpBlockMaxDy = map(str, BlockMaxDy)
        joinBlockMaxDy = "," + ",".join(mpBlockMaxDy)  #convert maxY list into arrayed string
        Capablearray = "" #reset

        if self.NextShape_index == 1:     
            Capablearray = r',3|-3|,4|-4|,5|-5|,6|-6|,7|-7|,8|-8|,9|-9|10|-10|11|-11|12|-12'
        elif self.NextShape_index == 2:
            Capablearray = r'0|,2|-1,0'
        elif self.NextShape_index == 3:
            Capablearray = r'0|-2|0,1'
        elif self.NextShape_index == 4:
            Capablearray = r'0,0|,1|-1|,1,-1'
        elif self.NextShape_index == 5:
            Capablearray = r'0'
        elif self.NextShape_index == 6:
            Capablearray = r'0,-1|,1'
        elif self.NextShape_index == 7:
            Capablearray = r'1,0|-1'

        if re.search(Capablearray,joinBlockMaxDy): #whether maxDY has Capable array for the NextShape
            NextShapeCapable = True
        else:
            pass   

        # only for level 1: avoid trap
        if self.CurrentShape_index == 2:
            if joinBlockMaxDy == ",-3,-1,0,1,0,-2,0,2,1":
              NextShapeCapable = False

        #if self.CurrentShape_index == 5:
         #   if joinBlockMaxDy == ",-9,0,1,1,0,0,1,0,1":
          #      NextShapeCapable = False
        
        if self.CurrentShape_index == 2:
            if joinBlockMaxDy == ",0,-1,1,0,-1,0,-1,0,1":
              NextShapeCapable = False

    

        # calc Evaluation Value
        score = 0
        if self.Elapsed_Time / self.Game_Time > 0.95:
            score = score + NextShapeCapable * 40.0
            score = score + (adjFullLines**2-adjFullLines*1.0) * 50.0           
            score = score - nDeadY * 200.0               
            score = score - Chasm * 180.0
            score = score - (absDy-absDyforLowerEdgeY) * 5.0       
            score = score - (max(BlockMaxY)-min(BlockMaxY)) * 12.0
            score = score - keepLow * 5.0

        else:    
            score = score + NextShapeCapable * 40.0
            score = score + (adjFullLines**2-adjFullLines*3.4) * 50.0           
            score = score - nDeadY * 200.0               
            score = score - Chasm * 180.0
            score = score - (absDy-absDyforLowerEdgeY) * 5.0       
            score = score - (max(BlockMaxY)-SortedMaxY[1]) * 12.0
            score = score - (max(BlockMaxY)-SortedMaxY[2]) * 1.0
            score = score - keepLow * 15.0


#        if prt == True: #88行目のEvalValueのみでprintしたい＝Trueにする。88行目のEvalValueはStrategyで確定されたdirectionx, x0の時のboardを持ってきている
 #           path = '..\\tetris\\game_manager\\block_controller_log.txt'
  #          with open (path, mode ="a") as f:
   #             for y in range(height):
    #                f.write("\n")
     #               for x in range(width):
      #                  boardElmt = board[y*width+x] 
       #                 f.write(str(boardElmt).replace("0","_")+" ")  
#
 #               f.write("\n" + "\n" + \
  #              "CurrentShape_index = " + str(self.CurrentShape_index) +"\n" + \
   #             "score = " + str(score) + "\n" + \
    #            "LowestX = " + str(LowestX) + "\n" + \
     #           "keepLow = " + str(keepLow) + "\n" + \
      #          "NextShapeCapable = " + str(NextShapeCapable) +"\n" + \
       #         "joinBlockMaxDy = " + str(joinBlockMaxDy) +"\n" + \
        #        "fullLines = " + str(fullLines) +"\n" + \
         #       "DeadY = " + str(DeadY) +"\n" + \
          #      "nDeadY = " + str(nDeadY) +"\n" + \
           #     "CurDeadY = " + str(CurDeadY) +"\n" + \
            #    "CurDeadYinRange = " + str(CurDeadYinRange) +"\n" + \
             #   "nCurDeadYinRange = " + str(nCurDeadYinRange) +"\n" + \
                #"adjFullLines = " + str(adjFullLines) +"\n" + \
               # "Chasm = " + str(Chasm) +"\n" + \
              #  "(absDy-absDyforLowerEdgeY) = " + str(absDy-absDyforLowerEdgeY) +"\n" + \
             #   "max(BlockMaxY) = " + str(max(BlockMaxY)) +"\n" + \
            #    "Time_Remain = " + str(self.Game_Time - self.Elapsed_Time) +"\n" + \
           #     "CurBlockMaxY = " + str(CurBlockMaxY) +"\n" + \
          #      "BlockMaxY = " + str(BlockMaxY) +"\n" + \
         #       "SortedMaxY[1] = " +str(SortedMaxY[1]) +"\n" + \
        #        "BlockMaxDy = " + str(BlockMaxDy) +"\n")
                

        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
 
        return score

BLOCK_CONTROLLER = Block_Controller()
