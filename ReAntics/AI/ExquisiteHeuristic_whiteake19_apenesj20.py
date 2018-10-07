import random
import sys
sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
from random import shuffle

##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course. 
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "ExquisiteHeuristic")
        self.depth_limit = 3
        self.me = 0
        self.move = None
        self.nextMove = None
        self.prunedMoves = 0

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        self.me = currentState.whoseTurn
        # rotate to the next move
        self.move = self.nextMove
        # set number of pruned nodes to zero
        self.prunedMoves = 0
        # if the list of moves is empty or move holds an enemy move, do minimax()
        if self.move is None or self.move["minmax"] == -1:
            root = {"move": None, "state": currentState, "value": 0, "min": -1000, "max": 1000, "parent": None, "depth": 0,
                    "minmax": 1, "next-move": None}
            # root has no move associated with it so automatically update self.move to minimax["next-move"]
            self.move = self.minimax(root, 0)["next-move"]
            # if minimax returns no moves, do an end move
            if self.move is None:
                self.nextMove = None  # done so the code at the start of getMove work
                return Move(END, None, None)
            else:
                self.nextMove = self.move["next-move"]
        else:
            # so move is not None AND move is our move
            self.nextMove = self.move["next-move"]
        if self.prunedMoves != 0:
            print("Pruned ", self.prunedMoves, " moves")
        return self.move["move"]

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # registerWin
    #
    # This agent doens't learn
    # however we need to reset global variables
    #
    def registerWin(self, hasWon):
        self.move = None
        self.nextMove = None 
        pass

    ##
    # evaluateState
    #
    # This agent evaluates the state and returns a double between -1.0 and 1.0
    #
    def evaluateState(self, currentState):
        me = self.me
        if getWinner(currentState) == 1:
            return 1
        elif getWinner(currentState) == 0:
            return -1
        # Get the different inventories
        myInventory = currentState.inventories[me]
        enemyInventory = currentState.inventories[1-me]
        neutralInventory = currentState.inventories[2]
        ourAnts = getAntList(currentState, me, types=(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
        ourQueen = getAntList(currentState, me, types=(QUEEN,))
        if len(ourQueen) == 1:
            ourAnthillCoords = myInventory.getAnthill().coords
            queenAroundAnthill = max(approxDist(ourQueen[0].coords, ourAnthillCoords),2)
        if len(ourAnts) == 4:
            return -1
        workers = getAntList(currentState, me, types=(WORKER, WORKER))
        if len(workers) == 1:
            worker = 1
        else:
            worker = 0
        # worker = min(len(workers), 1) # One or zero, we only want one worker
        rSoldiers = getAntList(currentState, me, types=(R_SOLDIER, R_SOLDIER))
        rSoldier = min(len(rSoldiers), 1) # One or zero, we only want one ranged soldier
        # If we have an r soldier make sure it attacks a worker or goes to the opponent's anthill
        rSoldierDistance = 20
        if rSoldier:
            enemyWorkers = getAntList(currentState, 1-me, types=(WORKER, WORKER))
            if enemyWorkers:
                rSoldierDistance = approxDist(rSoldiers[0].coords, enemyWorkers[0].coords)
            else: 
                queen = getAntList(currentState, 1-me, types=(QUEEN,))
                if len(queen) == 1:
                    enemyQueenCoords = queen[0].coords
                    rSoldierDistance = abs(approxDist(rSoldiers[0].coords, enemyQueenCoords)-3)
                else:
                    return 1
                    #enemyAnthillCoords = enemyInventory.getAnthill().coords
                    #rSoldierDistance = abs(approxDist(rSoldiers[0].coords, enemyAnthillCoords)-3)
        # Make sure the worker goes to get food and gets it back to the anthill (or tunnel)
        foodDistance = 20
        # Incentivize carrying food
        carrying = 0
        if worker:
            if workers[0].carrying:
                carrying = 1
            constrs = neutralInventory.constrs
            foodCoords = (0,0)
            if carrying == 0: # Compute distance to food if not carrying
                for construction in constrs:
                    if construction.type == FOOD:
                        foodCoords = construction.coords
                        newDistance = approxDist(workers[0].coords, foodCoords)
                        if newDistance <= foodDistance:
                            foodDistance = newDistance
                # foodDistance = max(approxDist(workers[0].coords, foodCoords),1)
            else:  # Compute distance to tunnel if carrying
                myTunnelCoords = myInventory.getTunnels()[0].coords
                foodDistance = approxDist(workers[0].coords, myTunnelCoords)
        # Get the other used parameters
        queenList = getAntList(currentState, 1-me, types = (QUEEN, QUEEN))
        enemyQueenHealth = 0
        if queenList:
            enemyQueenHealth = queenList[0].health
        ourFoodNumber = myInventory.foodCount
        enemyAntNumber = len(enemyInventory.ants)
        enemyFoodNumber = enemyInventory.foodCount
        ourPoints = 5*worker + 4*rSoldier + 2*ourFoodNumber + carrying \
            + 1/(rSoldierDistance+1) + 0.5/(foodDistance+1) + 0.25/(queenAroundAnthill)
        enemyPoints = 3*enemyFoodNumber + 2*enemyAntNumber + enemyQueenHealth
        # This makes sure the value is always between -1 and 1
        value = (ourPoints - enemyPoints) / (ourPoints + enemyPoints) 
        # If the AI wins the value should be 1, otherwise it should be -1
        return value

    ##
    # expandNode
    #
    # This function takes a node (dictionary) as input finds all the legal moves from that state
    # and creates a list of new node with states resulting from each of those nodes and returns that list
    #
    def expandNode(self, node):
        moves = listAllLegalMoves(node["state"])
        states = []
        for move in moves:
            newNode = {"move":move}
            newNode["state"] = getNextStateAdversarial(node["state"], newNode["move"])
            newNode["value"] = 0
            newNode["min"] = node["min"]
            newNode["max"] = node["max"]
            newNode["parent"] = node
            newNode["depth"] = node["depth"]+1
            if move.moveType == END:
                newNode["minmax"] = -1 * node["minmax"]
            else:
                newNode["minmax"] = node["minmax"]
            newNode["next-move"] = None
            states.append(newNode)
        return states

    ##
    # evalListNodes
    #
    # This function takes a list of nodes and takes the average of the values accossiated with
    # each and returns that average value
    #
    def evalListNodes(self, nodes):
        if nodes and len(nodes) > 1:
            randomNode = nodes[0]
            if randomNode["minmax"] == 1:
                bestNodeValue = -1
                for node in nodes:
                    if node["value"] >= bestNodeValue:
                        bestNodeValue = node["value"]
            elif randomNode["minmax"] == -1:
                bestNodeValue = 1
                for node in nodes:
                    if node["value"] <= bestNodeValue:
                        bestNodeValue = node["value"]
            return bestNodeValue
        elif nodes:
            return nodes[0]["value"]
        else:
            return -1


    ##
    # minimax
    #
    # This function preforms minimax search
    # It takes a node and the depth
    # The nodes are expanded until the depth limit is reached
    # Then the values of the nodes are averaged and propagated up
    # The move from the node with the best value at depth 0 is returned as the best move to make
    #
    def minimax(self, node, depth):
        newNodes = self.expandNode(node)
        shuffle(newNodes)
        # create counter
        counter = 0
        # it is depth + 1 since we just expanded the node and are
        # now evaluating nodes at depth + 1
        if depth+1 < self.depth_limit:
            # if the next set of nodes are inside the depth limit,
            for n in newNodes:
                # increment counter
                counter += 1
                # update the bounds of each newNode since a previous newNode could have updated node's bounds
                n["min"] = node["min"]
                n["max"] = node["max"]
                # minimax updates the min and max bounds of the parent node, not the children
                if node["minmax"] == 1:                   
                    temp = node["min"]  # used so we don't do minimax() twice
                    node["min"] = max(self.minimax(n, depth+1), node["min"])
                    # if the value was updated, update the next-move value to n
                    if temp != node["min"]:
                        node["next-move"] = n
                        # if the bounds cross each other, prune remaining nodes
                    if node["min"] > node["max"] or node["min"] == 1:
                        # updated global variable
                        self.prunedMoves += len(newNodes) - counter
                        if depth == 0:
                            return node
                        else: 
                            return node["min"]
                else:
                    temp = node["max"]
                    node["max"] = min(self.minimax(n, depth+1), node["max"])
                    if temp != node["max"]:
                        node["next-move"] = n
                    if node["min"] > node["max"]:
                        self.prunedMoves += len(newNodes) - counter
                        if depth == 0:
                            return node
                        else:
                            return node["max"]
        else:
            # else find the best value for min/max
            for n in newNodes:
                # increment counter
                counter += 1
                if node["minmax"] == 1:
                    temp = node["min"]
                    node["min"] = max(self.evaluateState(n["state"]), node["min"])
                    # if the bounds cross each other, prune remaining nodes
                    if node["min"] > node["max"]:
                        self.prunedMoves += len(newNodes) - counter
                        return node["min"]
                    # if the value was updated, update the next-move value to n
                    if temp != node["min"]:
                        node["next-move"] = n
                    if node["min"] == 1:
                        return node["min"]
                else:
                    temp = node["max"]
                    node["max"] = min(self.evaluateState(n["state"]), node["max"])
                    if node["min"] > node["max"]:
                        self.prunedMoves += len(newNodes) - counter
                        return node["max"]
                    # if the value was updated, update the next-move value to n
                    if temp != node["max"]:
                        node["next-move"] = n
        # evaluation = self.evalListNodes(newNodes) NOT NEEDED, minimax() now evaluates nodes
        if depth > 0:
            if node["minmax"] == 1:
                return node["min"]
            else:
                return node["max"]
        else:
            # shuffle(newNodes)
            # sortedNodes = sorted(newNodes, key=lambda k: k["value"])
            # return sortedNodes[len(sortedNodes)-1]["move"]

            # when we've finished minimax, return the root node with all the updated values
            return node

################
#  UNIT TESTS  #
################


ai = AIPlayer(0)

# create general state to modify
testState = GameState.getBasicState()
# make it an average game state
# add food to (3,3), (6,3), (6,6), (3,6)
testState.inventories[NEUTRAL].constrs.append(Construction((3, 3), FOOD))
testState.inventories[NEUTRAL].constrs.append(Construction((6, 3), FOOD))
testState.inventories[NEUTRAL].constrs.append(Construction((6, 6), FOOD))
testState.inventories[NEUTRAL].constrs.append(Construction((3, 6), FOOD))
# add worker next to food (2,3)
testState.inventories[0].ants.append(Ant((2, 3), WORKER, 0))
# make an enemy worker on opposite side
testState.inventories[1].ants.append(Ant((7, 6), WORKER, 1))
# add another friendly worker to look more like AI
testState.inventories[0].ants.append(Ant((7, 3), WORKER, 0))
# move queen so she doesn't stand on anthill and cause evaluateList() to return -1.0
queenMove = Move(MOVE_ANT, [(0, 0), (1, 0)])
testState = getNextState(testState, queenMove)

# EVALUATE STATE TESTS
# (1) Will worker move onto food?
# get state with ant on food
foodMove = Move(MOVE_ANT, [(7, 3), (6, 3)], None)
foodState = getNextState(testState, foodMove)
# if moving worker onto food is considered worse than not, ERROR
if ai.evaluateState(foodState) < ai.evaluateState(testState):
    print("ERROR: Ant will not move onto food")

# (2) Will game make new ants?
# update foodCounts
testState.inventories[0].foodCount = 2
testState.inventories[1].foodCount = 2
# use food to build Soldier
soldierBuild = Move(BUILD, None, SOLDIER)
buildState = getNextState(testState, soldierBuild)
# unit test not applicable with heuristic
# if ai.evaluateState(buildState) < ai.evaluateState(testState):
#     print("ERROR: AI will not build soldier")

# (3) Will game move non-workers towards enemy queen?
soldierMove = Move(MOVE_ANT, [(0,0),(0,1),(0,2)])
attackState = getNextState(buildState, soldierMove)
if ai.evaluateState(attackState) < ai.evaluateState(buildState):
    print("ERROR: AI will not attack queen")

# minimax TESTS
# (1) Does reaching depth limit return an integer?
testNode = {"move": None, "state": testState, "value": 0, "min": -1000, "max": 1000, "parent": None, "depth": 3,
            "minmax": 1, "next-move": None}
if not isinstance(ai.minimax(testNode, testNode["depth"]), float):
    print("ERROR: minimax() doesn't test depth limit properly")

# EVALLISTNODES TESTS
# (1) Does sending an empty list cause a DivideByZeroError?
try:
    ai.evalListNodes([])
except:
    print("ERROR: evalListNodes() cannot handle empty list input")

# EXPAND NODE TESTS
# (1) Does expanding a node return more nodes?
testNode = {"move": None, "state": testState, "value": 0, "min": -1000, "max": 1000, "parent": None, "depth": 0,
            "minmax": 1, "next-move": None}
if len(ai.expandNode(testNode)) == 0:
    print("ERROR: expandNode returns empty list")