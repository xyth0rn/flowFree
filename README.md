# flowFree

## Flow Free Game
https://play.google.com/store/apps/details?id=com.bigduckgames.flow&hl=zh_TW&gl=US

## Usage
work with python2

### [1] edit "game" in flowFree.py
![alt text](https://github.com/xyth0rn/flowFree/blob/main/flowFree_1.jpg)
```
game = [1, 0, 0, 0, 2, \
        0, 0, 0, 0, 0, \
        0, 3, 4, 0, 0, \
        0, 0, 1, 0, 0, \
        4, 3, 2, 0, 0 ]
Note:
 0 = space
```
### [2] python flowFree.py
```
AAAAB
DDDAB
DCDAB
DCAAB
DCBBB

A⇨⇨⇩B
⇩⇦⇦⇩⇩
⇩CD⇩⇩
⇩⇩A⇦⇩
DCB⇦⇦

A══╗B
╔═╗║║
║CD║║
║║A╝║
DCB═╝
```
![alt text](https://github.com/xyth0rn/flowFree/blob/main/flowFree_2.jpg)

### [3] options
The flowFree.py has a built-in SAT-Solver base on "DPLL-based SAT solvers by Will Klieber".
There is a option to speed up program by replace built-in SAT-Solver with pycosat:
```
    # option 1: fast (need to import pycosat)
    # sol_lst = pycosat.solve(flowFree_CNFs)

    # option 2: slow 
    solution = IsSatisfiable(flowFree_CNFs, [])
    sol_lst = sorted(solution, key=abs)
```

## Awards
第59屆全國中小學科展: 探究精神獎
https://www.ntsec.edu.tw/Science-Content.aspx?cat=15422&a=6821&fld=&key=&isd=1&icop=10&p=4&sid=15827

## Contributors
黃仲璿,林立宸

## Reference
A SAT-based Sudoku Solver by Tjark Weber

DPLL-based SAT solvers by Will Klieber
