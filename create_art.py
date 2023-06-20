import sys
import subprocess

def create_art(curfoundflag, Rnd):
    global finishflag
    if finishflag == True:
        pass
    else:
        rnd = Rnd
        rnd += 1
        if rnd > searchround:
            leftoverX, leftovershape = None,None
            retryflag = False
            if False in curfoundflag:
                leftoverX = curfoundflag.index(False)
                leftovershape = eachline[leftoverX]
                if int(leftovershape) == 1:
                    retryflag = True
            if retryflag == False:
                finishflag = True
                print(num,eachline,order,"left : xs_"+ str(leftoverX)+ str(leftovershape))

        else:
            foundflag = curfoundflag
            for x1 in range(10):
                if foundflag[x1] != True:
                    for x2 in range(x1+1,10):
                        if foundflag[x2] != True and finishflag != True:
                            test_lib = "xs_" + str(x1) + str(eachline[x1]) + str(x2) + str(eachline[x2])  
                            if lib.artdict[test_lib] != False:
                                order.append(test_lib)
                                foundflag[x1] = True
                                foundflag[x2] = True
                                create_art(curfoundflag = foundflag, Rnd = rnd)
                                order.pop(-1)
                                foundflag[x1] = False
                                foundflag[x2] = False         

import art_lib as lib

searchround = 4
print("number of rows:")
n = int(input())
print("shapes in 10 digits:")

shapelist = []
for i in range(n):
    xi = str(input())
    shapelist.append(xi)
shapelist.reverse()

num = 0
for eachline in shapelist:
    num += 1
    foundflag = [False,False,False,False,False,False,False,False,False,False]
    for digit in range(10):
        if eachline[digit] == "0":
            foundflag[digit] = True

    rnd = 0
    order = []
    global finishflag
    finishflag = False
    ans = create_art(curfoundflag = foundflag, Rnd = rnd)
    if finishflag == False:
        print(num, "not found")

