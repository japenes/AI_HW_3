import random
import sys
import math
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Move import Move
from GameState import *
from AIPlayerUtils import *
from Construction import *
from Inventory import *
from Ant import *
from random import shuffle

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    # Depth limit i means it looks at all the states that are i+1 away from the current state
    # This means that if we set the depth limit to 1 it looks at the current state's (node's)
    # children and grandchildren (so 2 deep)
    @property
    def depthLimit(self):
        return 1    

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "OffIsTheBestDef")


    # Gives an evaluation method the evaluate the current state of the game
    # This method returns a value between -1 and 1, depending on how good the AI is doing
    # For itself, it looks at the following, from most to least important:
    # Having a worker
    # Having a ranged soldier
    # The amount of food
    # The distance between the ranged soldier and one of the enemy's workers, if they have any
    # If they don't have any, the distance between teh ranged soldier and the enemy's anthill
    # The distance between the worker and (some piece of) food, if the worker is not carrying
    # If the worker is carrying, the distance between the worker and the anthill
    # For the enemy, the AI looks at the following, from most to least important:
    # The amount of food
    # The amount of ants
    # The health points of the queen
    def getValue(self, currentState):
        me = currentState.whoseTurn
        # Get the different inventories
        myInventory = currentState.inventories[me]
        enemyInventory = currentState.inventories[1-me]
        neutralInventory = currentState.inventories[2]
        workers = getAntList(currentState, me, types = (WORKER, WORKER))
        worker = min(len(workers), 1) # One or zero, we only want one worker
        rSoldiers = getAntList(currentState, me, types = (R_SOLDIER,R_SOLDIER))
        rSoldier = min(len(rSoldiers), 1) # One or zero, we only want one ranged soldier
        # If we have an r soldier make sure it attacks a worker or goes to the opponent's anthill
        rSoldierDistance = 20
        if rSoldier:
            enemyWorkers = getAntList(currentState, 1-me, types = (WORKER,WORKER))
            if enemyWorkers:
                rSoldierDistance = max(approxDist(rSoldiers[0].coords, enemyWorkers[0].coords),1)
            else: 
                enemyAnthillCoords = enemyInventory.getAnthill().coords
                rSoldierDistance = max(approxDist(rSoldiers[0].coords, enemyAnthillCoords),2)
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
                foodDistance = max(approxDist(workers[0].coords, foodCoords),1)
            else: # Compute distance to anthill if carrying
                myAnthillCoords = myInventory.getAnthill().coords
                foodDistance = max(approxDist(workers[0].coords, myAnthillCoords),1)
        # Get the other used parameters
        queenList = getAntList(currentState, 1-me, types = (QUEEN, QUEEN))
        enemyQueenHealth = 0
        if queenList:
            enemyQueenHealth = queenList[0].health
        ourFoodNumber = myInventory.foodCount
        enemyAntNumber = len(enemyInventory.ants)
        enemyFoodNumber = enemyInventory.foodCount
        ourPoints = 5*worker + 4*rSoldier + 2*ourFoodNumber + carrying \
            + 1/rSoldierDistance + 0.5/foodDistance
        enemyPoints = 3*enemyFoodNumber + 2*enemyAntNumber + enemyQueenHealth
        # This makes sure the value is always between -1 and 1
        value = (ourPoints - enemyPoints) / (ourPoints + enemyPoints) 
        # If the AI wins the value should be 1, otherwise it should be -1
        if getWinner(currentState) == 1:
            return 1
        elif getWinner(currentState) == 0:
            return -1
        return value


    # Evaluates a list of nodes to determine their overall evaluation score
    def getEvaluation(self, nodeList):
        if nodeList:
            averageEval = sum(node['evaluation_of_state'] for node in nodeList) / len(nodeList)
            return averageEval
        else:
            # If we have an empty list it should have a bad evaluation
            return -1


    # Recursive method which returns the move object of the highest evaluated node when depth = 0, 
    # otherwise it will return the evaluation of the complete set of nodes 
    def getBestMove(self, currentState, depth):
        possibleMoves = listAllMovementMoves(currentState) 
        possibleMoves.extend(listAllBuildMoves(currentState))
        nodeList = [] 
        for move in possibleMoves:
            state = getNextStateAdversarial(currentState, move)
            # If depth limit is not reach we should get an evaluation of the children nodes
            if depth < self.depthLimit: 
                evaluation = self.getBestMove(state.fastclone(), depth +1)
            # Otherwise we just evaluate the current node
            else:
                evaluation = self.getValue(state)
            node = {'move_from_parent_node': move, 'state_reached': state.fastclone(), \
                'evaluation_of_state': evaluation, 'depth': depth+1}
            nodeList.append(node)
        # If we are not at depth 0, we should return the overall value of the children nodes
        if depth > 0:
            overallValue = self.getEvaluation(nodeList)      
            return overallValue
        # Otherwise we should pick (one of) the node(s) with the highest evaluation score
        else:
            if nodeList:
                shuffle(nodeList) # If there all multiple best moves we want to pick one at random
                bestNode = max(nodeList, key=lambda x:x['evaluation_of_state'])
                return bestNode['move_from_parent_node']
            else:
                return(Move(END, None, None))


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
        valueBefore = self.getValue(currentState)
        move = self.getBestMove(currentState.fastclone(), 0)
        valueAfter = self.getValue(getNextStateAdversarial(currentState, move))
        # This if statement makes sure we don't make a move that is worse than the current state
        # Otherwise it is better to just end the turn
        if round(valueAfter,2) >= round(valueBefore,2):
            return move
        else:
            return Move(END, None, None)


    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass


# UNIT TEST
# Here we test the methods we wrote for Homework 2

# First we check our getValue function, this function evaluates a state
# Case 1 (simple)
# Check state with AI has only queen as ant and 0 food, with the enemy having a worker ant
# The AI has lost, so function should return -1
basicState = GameState(0,0,0,0).getBasicState()
randomAnt = Ant((0,1), WORKER, 1)
basicState.inventories[1].ants.append(randomAnt)
AIplayer = AIPlayer(1)
value = AIplayer.getValue(basicState)
rightValue = -1
if not math.isclose(value,rightValue):
    print("Error, the getValue function gives the value ", value, \
        "instead of the value ", rightValue, ".")
# Case 2 (complex)
# Check state with queen, one soldier ant and 5 food for the AI
# versus queen and one ant and one food for the opponent 
randomSoldierAnt = Ant((0,1), R_SOLDIER, 1)
basicState.inventories[0].ants.append(randomSoldierAnt)
basicState.inventories[0].foodCount = 5
enemyWorkerAnt = Ant((0,2), WORKER, 1)
basicState.inventories[1].ants.append(enemyWorkerAnt)
basicState.inventories[1].foodCount = 1
value = AIplayer.getValue(basicState)
# This is complicated, but we don't have a worker (which has a coefficient of 5)
# we have a ranged soldier, we have 5 food, distance getween ranged soldier and worker is 1
# and the distance between worker and ant is the maximum (20) because we don;t have a worker
ourPoints = (5*0 + 4*1 + 2*5 + 0 + 1/1 + 0.5/20)
enemyPoints = 3*1 + 2*3 + 10
rightValue = (ourPoints - enemyPoints) / (ourPoints + enemyPoints)
if not math.isclose(value,rightValue):
    print("Error, the getValue function gives the value ", \
        value, "instead of the value ", rightValue, ".")


# Here we check the function that evaluates multiple nodes
# First we create 3 nodes, it should return the average of the 'evaluation_of_state' values,
# which is 0 in this case
node1 = {'move_from_parent_node': [(0,0), (0,1), (1,1)], 'state_reached': basicState, \
    'evaluation_of_state': 0.7, 'depth': 1}
node2 = {'move_from_parent_node': [(0,0), (0,1)], 'state_reached': basicState, \
    'evaluation_of_state': -0.1, 'depth': 1}
node3 = {'move_from_parent_node': [(0,0), (0,1)], 'state_reached': basicState, \
    'evaluation_of_state': -0.6, 'depth': 1}
nodeList = []
nodeList.append(node1)
nodeList.append(node2)
nodeList.append(node3)
rightValue = 0 # Average value of the 3 nodes
value = AIplayer.getEvaluation(nodeList)
if not math.isclose(value,rightValue):
    print("Error, the evaluation function gives the value ", value, \
        "instead of the value ", rightValue, ".")

# Finally we check our rerucsive method, which is called getBestMove
# We look at a specific case in which there is only one move that is clearly the best
# In this case the AI has a ranged soldier which is 4 tiles away from the enemy's only worker
# This means it should return the move wich kills the enemy worker, which is going 1 step closer
basicState = GameState(0,0,0,0).getBasicState()
enemyWorkerAnt = Ant((4,4), WORKER, 1)
randomSoldierAnt = Ant((4,8), R_SOLDIER, 1)
basicState.inventories[0].ants.append(randomSoldierAnt)
basicState.inventories[1].ants.append(enemyWorkerAnt)
AIplayer = AIPlayer(1)
bestMove = AIplayer.getBestMove(basicState,0)
if bestMove.moveType is not MOVE_ANT and bestMove.coordList is not [(4,8),(4,7)]: 
    print("error")



