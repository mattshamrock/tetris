import sys
import subprocess
import copy

def receive_shapelist(n):
    shapelist = []
    for i in range(n):
        xi = str(input())
        shapelist.append(xi)
    shapelist.reverse()

    return shapelist


def foundlist_init(n,shapelist):
    foundlist = [[False for i in range(10)] for i in range(n)]
    for i in range(n):
        for j in range(len(shapelist[i])):
            foundlist[i][j] = True if shapelist[i][j] == "0" else False

    return foundlist

def x_with_block_init(n, foundlist):
    x_with_block = [[] for i in range(n)]
    for row in range(n):
        for x in range(len(foundlist[row])):
            if foundlist[row][x] == False:
                x_with_block[row].append(x)
        random.shuffle(x_with_block[row])

    return x_with_block

def remove_if_deadend(key_order, foundlist, row, test_xs, x1,x2):
    if foundlist[row].count(False) != 0:
        key_order[row].remove(test_xs)
        foundlist[row][x1], foundlist[row][x2] = False, False

    return key_order, foundlist

def remove_if_deadend_2(key_order, foundlist, row, test_xs_xs, leftoverX, x3):
    if foundlist[row + 1].count(False) != 0:
        key_order[row].remove(test_xs_xs)
        foundlist[row][leftoverX], foundlist[row + 1][x3] = False, False

    return key_order, foundlist

def bruteforce(x_with_block, key_order, foundlist, row):
    if row == len(shapelist):
        return key_order

    for t1 in range(len(x_with_block[row])):
        for t2 in range(t1+1,len(x_with_block[row])):
            x1 = min(x_with_block[row][t1],x_with_block[row][t2])
            x2 = max(x_with_block[row][t1],x_with_block[row][t2])
            test_xs = "xs_"+ str(x1) + str(shapelist[row][x1]) + str(x2) + str(shapelist[row][x2])
            if lib.artdict[test_xs] != False and foundlist[row][x1] == False and foundlist[row][x2] == False:
                foundlist[row][x1], foundlist[row][x2] = True,True
                key_order[row].append(test_xs)

                if foundlist[row].count(False) == 0:
                    key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = row + 1)

                    key_order, foundlist = remove_if_deadend(key_order = key_order, foundlist = foundlist, row = row, test_xs = test_xs, x1 = x1, x2 = x2)


                elif foundlist[row].count(False) == 1:
                    leftoverX = foundlist[row].index(False)
                    
                    for t3 in range(len(x_with_block[row+1])):
                        x3 = x_with_block[row + 1][t3]
                        test_xs_xs = "xs_" + str(leftoverX) + str(shapelist[row][leftoverX]) + "_" + str(x3) + str(shapelist[row + 1][x3])
                        if lib.artdict[test_xs_xs] != False and foundlist[row + 1][x3] == False:
                            foundlist[row][leftoverX], foundlist[row + 1][x3] = True, True
                            key_order[row].append(test_xs_xs)
                            key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = row + 1)

                            key_order, foundlist = remove_if_deadend_2(key_order = key_order, foundlist = foundlist, row = row, test_xs_xs = test_xs_xs, leftoverX = leftoverX, x3 = x3)


                else:
                    key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = row)

                    key_order, foundlist = remove_if_deadend(key_order = key_order, foundlist = foundlist, row = row, test_xs = test_xs, x1 = x1, x2 = x2)


    return key_order

def rearrange(shapelist, key_order, n):
    key_order_copy = copy.deepcopy(key_order)
    for row in range(1, n):
        for xs in range(len(key_order[row])):
            test = key_order[row][xs]
            if test.count("_") == 1:
                x1,x2 = int(test[3]),int(test[5])
                if shapelist[row - 1][x1] == "0" or shapelist[row - 1][x2] == "0":
                    key_order_copy[row].remove(test)
                    key_order_copy[row].append(test)

    for row in range(1, n):
        for xs in range(len(key_order[row])):
            test = key_order[row][xs]
            if test[5] == "_":
                key_order_copy[row].remove(test)
                key_order_copy[row].append(test)

    return key_order_copy

def check_blocknumber(foundlist):
    zero = 0
    for l in foundlist:
        zero += l.count(False)
    if zero % 2 == 1:
        print(zero)
        print("This art has an odd number of blocks")
        sys.exit()


import art_lib as lib
import random
import time

print("number of rows:")
n = int(input())
print("shapes in 10 digits:")
shapelist = receive_shapelist(n = n)

print("----------------------------")
for pr in shapelist:
    print(pr)

foundlist = foundlist_init(n = n, shapelist = shapelist)
for pr in foundlist:
    print(pr)

check_blocknumber(foundlist = foundlist)

x_with_block = x_with_block_init(n = n, foundlist=foundlist)

key_order = [[] for i in range(n)] 
key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = 0)
key_order = rearrange(shapelist = shapelist, key_order = key_order, n = n)


path = '..\\tetris\\game_manager\\log_art.txt'

for pr in key_order:
    print("'" +"', '".join(map(str,pr))+"'")
    with open (path, mode ="a") as f:
        f.write("'" +"', '".join(map(str,pr))+"'" +"\n")


for row in key_order:
    for xs in row:
        output = lib.artdict[xs]
        print(", ".join(map(str,output))+ ",")
        with open (path, mode ="a") as f:
            f.write(", ".join(map(str,output))+ "," +"\n")

with open (path, mode ="a") as f:
    f.write("======================================================" +"\n")
