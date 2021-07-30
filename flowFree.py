from copy import copy, deepcopy
# import pycosat

def FindUnitClauses(ClauseList):
    UnitClauses = []
    for clause in ClauseList:
        if len(clause) == 1:
            if clause[0] not in UnitClauses:
                UnitClauses += clause
    return UnitClauses

def AssignLit(ClauseList, lit): # Unit propagation
    ClauseList = deepcopy(ClauseList)
    for clause in copy(ClauseList):
        if lit in clause: ClauseList.remove(clause)
        if -lit in clause: clause.remove(-lit)
    return ClauseList

def IsSatisfiable(ClauseList, Solution):
    # Unit propagation
    while True:
        UnitClauses = FindUnitClauses(ClauseList)
        if len(UnitClauses) == 0:
            break
        for UC in UnitClauses:
            # print "UC =>", UC
            ClauseList = AssignLit(ClauseList,UC)
            Solution += [UC]

    # Test if no unsatisfied clauses remain
    if len(ClauseList) == 0: return Solution
    # Test for presense of empty clause
    if [] in ClauseList: 
        # print "No solution in this branch"
        # print " "
        return []
    # Split on an arbitrarily decided literal
    DecLit = ClauseList[0][0]
    # print "DecLit =>", DecLit
    return ( IsSatisfiable(AssignLit(ClauseList,DecLit), Solution+[DecLit]) or
        IsSatisfiable(AssignLit(ClauseList,-DecLit), Solution+[-DecLit]) )

def xyVar(n, dMax, x, y, d):
    return dMax*(n*y + x) + d

def mVar(dMax, m, d):
    return dMax*m + d

def get_flowFree_CNFs(game):
    m = len(game)
    n = int(m**0.5)

    # find end points
    dColor = 0        # number of colors per cell
    dMax = 0        # dMax(number of colors per cell + 4 directions per cell)    
    CNFs = []        # clauses
    TPs = []        # terminal points (begin & end points)
    BPs = []        # begin ponits
    BP_idx = []        # begin points' index
    BP_color = []    # begin ponits color list
    CP_idx = []        # connect points' index
    nEP_idx = []    # not end points' index

    # determine BPs, BP_color, CP_idx, dMax
    dColor = max(game)        # find max number of colors
    dMax = dColor + 4            # plus 4 direction +1=up, +2=down, +3=left, +4=right
    for i in range(0, m):
        if game[i] != 0:
            TPs += [mVar(dMax,i,game[i])]
        if ((game[i] != 0) & (game[i] not in BP_color)):
            BPs += [mVar(dMax,i,game[i])]
            BP_idx += [i]
            BP_color += [game[i]]
        if game[i] == 0:
            CP_idx += [i]
    nEP_idx = BP_idx + CP_idx
    nEP_idx.sort()

    # [1-0] assige initial colors to begin & end cells
    for i in range(0, m):
        if game[i] != 0:
            CNFs += [[mVar(dMax,i,game[i])]]

    # [1-1]
    # at least one color per cell
    for idx in range(0, m):
        CNF = []
        for d in range(1, dColor+1):
            CNF += [mVar(dMax, idx, d)]
        CNFs += [CNF]
    # at least one direction per nEPs
    for idx in nEP_idx:
        CNF = []
        for d in range(dColor+1, dMax+1):
            CNF += [mVar(dMax, idx, d)]
        CNFs += [CNF]

    # [1-2]
    # no more than one color per cell
    for idx in range(0, m):
        for d in range(1, dColor):
            for k in range(d+1, dColor+1):
                CNFs += [[-mVar(dMax,idx,d), -mVar(dMax,idx,k)]]
    # no more than one direction per nEPs
    for idx in nEP_idx:
        for d in range(dColor+1, dMax):
            for k in range(d+1, dMax+1):
                CNFs += [[-mVar(dMax,idx,d), -mVar(dMax,idx,k)]]

    # [2] every TPs cell has "only one" neighbor with same color
    for TP in TPs:
        NBs = []    # neighbors
        dCell = (TP-1)%dMax + 1
        xCell = ((TP-1)/dMax)%n
        yCell = (TP-1)/(n*dMax)
        # 2-1 find the neighbors
        # xyVar(n, dMax, x, y, d) = dMax*(n*y + x) + d
        if xCell > 0 :    # has a left neighbor
            NBs += [xyVar(n, dMax, xCell-1, yCell, dCell)]
        if xCell < n-1 :    # has a right neighbor
            NBs += [xyVar(n, dMax, xCell+1, yCell, dCell)]
        if yCell > 0 :    # has a up neighbor
            NBs += [xyVar(n, dMax, xCell, yCell-1, dCell)]
        if yCell < n-1 :    # has a down neighbor
            NBs += [xyVar(n, dMax, xCell, yCell+1, dCell)]
        # 2-2 at least one neighbor with same color
        CNFs += [NBs]
        # 2-3 only one neighbor with same color
        for j in range(0, len(NBs)-1):
            for k in range(j+1, len(NBs)):
                CNFs += [[-NBs[j], -NBs[k]]]

    # [3] every nEPs cell has same color with its next ponit
    # -(dir1 & cell1_color1 & -cell2_color1) => (-dir1 | -cell1_color1 | cell2_color1)
    for idx in nEP_idx:
        x = idx%n
        y = idx/n
        for z in range(1, dColor+1):
            # direction up
            if y  > 0:
                CNFs += [[-xyVar(n,dMax,x,y,dColor+1), -xyVar(n,dMax,x,y,z), xyVar(n,dMax,x,y-1,z)]]
            # direction down
            if y < n-1:
                CNFs += [[-xyVar(n,dMax,x,y,dColor+2), -xyVar(n,dMax,x,y,z), xyVar(n,dMax,x,y+1,z)]]
            # direction left
            if x > 0:
                CNFs += [[-xyVar(n,dMax,x,y,dColor+3), -xyVar(n,dMax,x,y,z), xyVar(n,dMax,x-1,y,z)]]
            # direction right
            if x < n-1:
                CNFs += [[-xyVar(n,dMax,x,y,dColor+4), -xyVar(n,dMax,x,y,z), xyVar(n,dMax,x+1,y,z)]]

    # [4] no direction conflicts
    # -(dir1 & dir2) => (-dir1 | -dir2)
    # next cell is up=1
    for x in range(0, n):
        for y in range(1, n):
            CNFs += [[-xyVar(n,dMax,x,y,dColor+1), -xyVar(n,dMax,x,y-1,dColor+2)]]
    # next cell is down=2
    for x in range(0, n):
        for y in range(0, n-1):
            CNFs += [[-xyVar(n,dMax,x,y,dColor+2), -xyVar(n,dMax,x,y+1,dColor+1)]]
    # next cell is left=3
    for x in range(1, n):
        for y in range(0, n):
            CNFs += [[-xyVar(n,dMax,x,y,dColor+3), -xyVar(n,dMax,x-1,y,dColor+4)]]
    # next cell is right=4
    for x in range(0, n-1):
        for y in range(0, n):
            CNFs += [[-xyVar(n,dMax,x,y,dColor+4), -xyVar(n,dMax,x+1,y,dColor+3)]]

    # [5] no outbound direction
    for i in range(0, n):
        # no up @ y=0
        CNFs += [[-xyVar(n,dMax,  i,  0,dColor+1)]]
        # no down @ y=n-1
        CNFs += [[-xyVar(n,dMax,  i,n-1,dColor+2)]]
        # no left @ x=0
        CNFs += [[-xyVar(n,dMax,  0,  i,dColor+3)]]
        # no right @ x=n-1
        CNFs += [[-xyVar(n,dMax,n-1,  i,dColor+4)]]

    # [6] neoghbor's flow
    for idx in range(0, m):
        NBs = []        # neighbors
        xCell = idx%n
        yCell = idx/n
        # [6-1] find the neighbors flowed into this cell 
        if yCell > 0 :        # has a up neighbor (flow down d=+2)
            NBs += [mVar(dMax,idx-n,dColor+2)]
        if yCell < n-1 :    # has a down neighbor (flow up d=+1)
            NBs += [mVar(dMax,idx+n,dColor+1)]
        if xCell > 0 :        # has a left neighbor (flow right d=+4)
            NBs += [mVar(dMax,idx-1,dColor+4)]
        if xCell < n-1 :    # has a right neighbor (flow left d=+3)
            NBs += [mVar(dMax,idx+1,dColor+3)]

        # [6-2] no flow into BPs: -a
        if idx in BP_idx:
            for NB in NBs:
                CNFs += [[-NB]]
        # [6-3] at least one flow into nBPs: (a | b | c | d)
        if idx not in BP_idx:
            CNFs += [NBs]
        # [6-4] no two flow into one cell: -(a & b) = (-a | -b)
        for i in range(0, len(NBs)-1):
            for j in range(i+1, len(NBs)):
                CNFs += [[-NBs[i], -NBs[j]]]

    return CNFs, n, dMax


def print_flowFree(game_lst, dMax, n):
    letter = ['-','A','B','C','D','E','F','G','H','I','J','K','L', \
        'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    for y in range(0, n):
        rowLine = ''
        for x in range(0, n):
            for d in range(0, dMax-4):
                if game_lst[dMax*(n*y+x)+d] > 0 :
                    rowLine = rowLine + letter[game_lst[dMax*(n*y+x)+d] % dMax]
        print(rowLine)

def print_flowArrow(game_lst, sol_lst, dMax, n):
    letter = ['-','A','B','C','D','E','F','G','H','I','J','K','L', \
        'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    arL = u'\u21E6'
    arT = u'\u21E7'
    arR = u'\u21E8'
    arD = u'\u21E9'    
    arrow = [arR,arL,arD,arT,arR]
    for y in range(0, n):
        rowLine = ''
        for x in range(0, n):
            if game_lst[n*y+x] > 0:
                rowLine = rowLine + letter[game_lst[n*y+x]]
            else:
                for d in range(dMax-4, dMax):
                    if sol_lst[dMax*(n*y+x)+d] > 0 :
                        mod = sol_lst[dMax*(n*y+x)+d]%dMax
                        if mod == 0:
                            rowLine = rowLine + arrow[mod]
                        else:
                            rowLine = rowLine + arrow[dMax-mod]
        print(rowLine)


def print_flowLine(game_lst, sol_lst, dMax, n):
    letter = ['-','A','B','C','D','E','F','G','H','I','J','K','L', \
        'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    # get directions
    # 1:up, 2:dwon, 3:left, 4:right
    dir_lst = []
    asc_lst = []
    for y in range(0, n):
        for x in range(0, n):
            asc_lst += [0]
            dir = 0
            for d in range(dMax-4, dMax):
                if sol_lst[dMax*(n*y+x)+d] > 0 :
                    mod = sol_lst[dMax*(n*y+x)+d]%dMax
                    if mod == 0:
                        mod = dMax
                    dir = 4-(dMax-mod)
                    dir_lst += [dir]
            if dir == 0:
                dir_lst += [dir]

    dir0 = u'\u2550'
    dir1 = u'\u2551'
    dir2 = u'\u2554'
    dir3 = u'\u2557'
    dir4 = u'\u255a'
    dir5 = u'\u255d'
    dir_table = [dir0,dir1,dir2,dir3,dir4,dir5]

    for y in range(0, n-1):
        for x in range(0, n):
            if dir_lst[n*y+x] == 2: # down
                if dir_lst[n*(y+1)+x] == 3: # left
                    asc_lst[n*(y+1)+x] = 5
                if dir_lst[n*(y+1)+x] == 4: # right
                    asc_lst[n*(y+1)+x] = 4
                if dir_lst[n*(y+1)+x] == 2: # down
                    asc_lst[n*(y+1)+x] = 1
    for y in range(1, n):
        for x in range(0, n):
            if dir_lst[n*y+x] == 1: # up
                if dir_lst[n*(y-1)+x] == 3: # left
                    asc_lst[n*(y-1)+x] = 3
                if dir_lst[n*(y-1)+x] == 4: # right
                    asc_lst[n*(y-1)+x] = 2
                if dir_lst[n*(y-1)+x] == 1: # up
                    asc_lst[n*(y-1)+x] = 1
    for y in range(0, n):
        for x in range(0, n-1):
            if dir_lst[n*y+x] == 4: # right
                if dir_lst[n*y+x+1] == 1: # up
                    asc_lst[n*y+x+1] = 5
                if dir_lst[n*y+x+1] == 2: # down
                    asc_lst[n*y+x+1] = 3
                if dir_lst[n*y+x+1] == 4: # right
                    asc_lst[n*y+x+1] = 0
    for y in range(0, n):
        for x in range(1, n):
            if dir_lst[n*y+x] == 3: # left
                if dir_lst[n*y+x-1] == 1: # up
                    asc_lst[n*y+x-1] = 4
                if dir_lst[n*y+x-1] == 2: # down
                    asc_lst[n*y+x-1] = 2
                if dir_lst[n*y+x-1] == 3: # left
                    asc_lst[n*y+x-1] = 0

    for y in range(0, n):
        rowLine = ''
        for x in range(0, n):
            if game_lst[n*y+x] > 0:
                rowLine = rowLine + letter[game_lst[n*y+x]]
            else:
                rowLine = rowLine + dir_table[asc_lst[n*y+x]]
        print(rowLine)


if __name__ == '__main__':
    # only support nxn square game

    """
    # 5x5 ok
    game = [1, 0, 0, 0, 2, \
            0, 0, 0, 0, 0, \
            0, 3, 4, 0, 0, \
            0, 0, 1, 0, 0, \
            4, 3, 2, 0, 0 ]

    # 6x6 ok
    game = [1, 0, 2, 0, 0, 0, \
            3, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 1, 2, \
            0, 0, 0, 3, 4, 5, \
            0, 5, 0, 0, 0, 0, \
            4, 0, 0, 0, 0, 0 ]

    # 7x7 ok
    game = [0, 0, 0, 0, 0, 0, 1, \
            0, 2, 0, 0, 0, 0, 3, \
            0, 0, 0, 0, 0, 0, 4, \
            0, 0, 3, 5, 6, 0, 0, \
            0, 0, 2, 0, 0, 0, 0, \
            0, 6, 0, 0, 0, 0, 0, \
            0, 0, 0, 1, 5, 4, 0  ]

    # 8x8 ok
    game = [0, 0, 0, 0, 1, 2, 1, 0, \
            0, 0, 0, 0, 3, 0, 4, 0, \
            0, 0, 5, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 2, 4, 0, \
            0, 0, 5, 6, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 7, 0, 0, \
            0, 6, 7, 3, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0  ]
    # 9x9 ok
    game = [0, 0, 0, 0, 0, 0, 1, 2, 3, \
            0, 4, 0, 0, 0, 0, 0, 0, 0, \
            5, 0, 0, 1, 0, 0, 0, 0, 0, \
            0, 0, 0, 2, 0, 0, 0, 0, 0, \
            0, 3, 0, 0, 0, 0, 0, 6, 0, \
            0, 0, 0, 0, 7, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 8, 0, 8, \
            0, 0, 0, 5, 0, 0, 7, 6, 9, \
            4, 0, 0, 0, 0, 9, 0, 0, 0  ]
    # 14x14 ok
    game = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, \
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 0, 0, \
            0, 2, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 6, 0, 0, 0, 0, 0, 7, 0, 0, 0, 8, 0, 0, \
            9, 0, 0, 0, 0, 0, 0,10, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0,11,10,12, 0, 3, 0, 0, 0, 0, \
            0, 0, 0, 0, 0,13,11, 0,14,12, 0, 0, 0, 0, \
            0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0,13, 0, 0,15, 5, 9, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 4, 0, 0, \
            0, 0, 0, 0, 0, 0, 0,14,15, 0, 0, 0, 0, 0  ]
    # 15x15 ok
    game = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, \
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 0, 0, \
            0, 2, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 6, 0, 0, 0, 0, 0, 7, 0, 0, 0, 8, 0, 0, \
            9, 0, 0, 0, 0, 0, 0,10, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0,11,10,12, 0, 3, 0, 0, 0, 0, \
            0, 0, 0, 0, 0,13,11, 0,14,12, 0, 0, 0, 0, \
            0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            0, 0,13, 0, 0,15, 5, 9, 0, 0, 0, 0, 0, 0, \
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 4, 0, 0, \
            0, 0, 0, 0, 0, 0, 0,14,15, 0, 0, 0, 0, 0  ]
    """
    game = [1, 0, 0, 0, 2, \
            0, 0, 0, 0, 0, \
            0, 3, 4, 0, 0, \
            0, 0, 1, 0, 0, \
            4, 3, 2, 0, 0 ]

            
    flowFree_CNFs, n, dMax = get_flowFree_CNFs(game)

    # option 1: fast (need to import pycosat)
    # sol_lst = pycosat.solve(flowFree_CNFs)

    # option 2: slow 
    solution = IsSatisfiable(flowFree_CNFs, [])
    sol_lst = sorted(solution, key=abs)
    
    print_flowFree(sol_lst, dMax, n)
    print('')
    print_flowArrow(game, sol_lst, dMax, n)
    print('')
    print_flowLine(game, sol_lst, dMax, n)