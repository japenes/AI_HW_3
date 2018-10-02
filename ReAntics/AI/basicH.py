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
        super(AIPlayer, self).__init__(inputPlayerId, "basic")
        self.depth_limit = 3
        self.anthillCoords = None
        self.tunnelCoords = None
        self.myFoodCoords = None
        self.maxTunnelDist = 0
        self.maxFoodDist = 0

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
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
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
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
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
        root = {"move": None, "state": currentState, "value": 0, "parent": None, "depth": 0}
        # tree = {"0":[root,]}
        move = self.bfs(root, 0)

        # moves = listAllLegalMoves(currentState)
        # selectedMove = moves[random.randint(0,len(moves) - 1)];
        #
        # #don't do a build move if there are already 3+ ants
        # numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        # while (selectedMove.moveType == BUILD and numAnts >= 3):
        #     selectedMove = moves[random.randint(0,len(moves) - 1)]
        print(move.moveType)
        print(move.coordList)
        print(move.buildType)
        return move

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
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass

    ##
    # evaluateState
    #
    # This agent evaluates the state and returns a double between -1.0 and 1.0
    #
    def evaluateState(self, gs):
        myInv = getCurrPlayerInventory(gs)
        theirInv = getEnemyInv(self, gs)
        me = gs.whoseTurn
        myWorkers = getAntList(gs, me, (WORKER,))
        theirWorkers = getAntList(gs, 1 - me, (WORKER,))
        myQueen = getAntList(gs, me, (QUEEN,))[0]

        # do this once
        if self.maxTunnelDist == 0:
            self.tunnelCoords = getConstrList(gs, me, (TUNNEL,))[0].coords
            self.anthillCoords = getConstrList(gs, me, (ANTHILL,))[0].coords
            print(self.tunnelCoords)
            foods = getConstrList(gs, None, (FOOD,))
            # find the food closest to the tunnel
            bestDistSoFar = 1000  # i.e., infinity
            for food in foods:
                dist = stepsToReach(gs, self.tunnelCoords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFoodCoords = food.coords
                    bestDistSoFar = dist

            print(self.myFoodCoords)

            for i in range(0, 10):
                for j in range(0, 10):
                    tunnelDist = approxDist((i, j), self.tunnelCoords)
                    foodDist = approxDist((i, j), self.myFoodCoords)
                    if (tunnelDist > self.maxTunnelDist):
                        self.maxTunnelDist = tunnelDist
                    if (foodDist > self.maxFoodDist):
                        self.maxFoodDist = foodDist

        # Dont want the queen on the tunnel or the hill
        if myQueen.coords == self.tunnelCoords or myQueen.coords == self.anthillCoords:
            return -1

        # A. The number of ants each player has on the board
        if len(myWorkers) > 2:
            return -1
        if (len(myInv.ants) + len(theirInv.ants)) == 0:
            return -1
        numAntsScore = (len(myInv.ants) - len(theirInv.ants)) / (len(myInv.ants) + len(theirInv.ants))

        myAntScore = 0
        myAntHealth = 0
        myAntCarry = 0
        myAntAttack = 0
        for ant in myInv.ants:
            if ant.type != WORKER:
                if ant.coords == self.anthillCoords:
                    return -1
                for coord in listAttackable(ant.coords):
                    if coord == theirInv.getQueen().coords:
                        myAntAttack += 1
            myAntHealth += ant.health
            if ant.carrying:
                myAntCarry += 1
            if ant.type == WORKER:
                myAntScore += 1
            elif ant.type == QUEEN:
                myAntScore += 4
            elif ant.type == SOLDIER:
                myAntScore += 4
            elif ant.type == DRONE:
                myAntScore += 2
            elif ant.type == R_SOLDIER:
                myAntScore += 3
        theirAntScore = 0
        theirAntHealth = 0
        theirAntCarry = 0
        theirAntAttack = 0
        for ant in theirInv.ants:
            if ant.type != WORKER:
                for coord in listAttackable(ant.coords):
                    if coord == myQueen.coords:
                        theirAntAttack += 1
            theirAntHealth += ant.health
            if ant.carrying:
                theirAntCarry += 1
            if ant.type == WORKER:
                theirAntScore += 1
            elif ant.type == QUEEN:
                theirAntScore += 4
            elif ant.type == SOLDIER:
                theirAntScore += 4
            elif ant.type == DRONE:
                theirAntScore += 2
            elif ant.type == R_SOLDIER:
                theirAntScore += 3

        # B. The types of ants that each player has on the board
        typeAntScore = (myAntScore - theirAntScore) / (myAntScore + theirAntScore)

        # C. The health of ants that each player has on the board
        healthAntScore = (myAntHealth - theirAntHealth) / (myAntHealth + theirAntHealth)

        # D. How much food each player has
        myfoodScore = (myInv.foodCount) / 11
        theirFoodScore = -1 * (theirInv.foodCount / 11)

        # E. How much food the worker ants are carrying
        if len(myWorkers) != 0:
            myCarryScore = myAntCarry / len(myWorkers)
        else:
            myCarryScore = 0
        if len(theirWorkers) != 0:
            theirCarryScore = -1 * (theirAntCarry / len(theirWorkers))
        else:
            theirCarryScore = 1

        # F. How much the respective queens are being “threatened” by enemy ants
        if (myAntAttack + theirAntAttack) == 0:
            attackScore = 0
        else:
            attackScore = (myAntAttack - theirAntAttack) / (myAntAttack + theirAntAttack)

        # G. How well protected the agent’s anthill is

        # H. Carrying workers are close to hill
        depositScore = 0
        # I. Non carrying workers are close to food
        collectScore = 0
        for worker in myWorkers:
            if worker.carrying:
                if approxDist(worker.coords, self.tunnelCoords) == 0:
                    return 1
                depositScore += 1 - (approxDist(worker.coords, self.tunnelCoords) / self.maxTunnelDist)
            else:
                collectScore += 1 - (approxDist(worker.coords, self.myFoodCoords) / self.maxFoodDist)

        print(myfoodScore)

        # total = (numAntsScore + typeAntScore + healthAntScore + 4*myfoodScore + theirFoodScore + 2*myCarryScore + theirCarryScore + attackScore) / 12
        total = (20*myfoodScore + myCarryScore + depositScore + collectScore) / 24
        return total

        # # calculate ant score
        # myAnts = myInv.ants
        # myAntScore = 0
        # for ant in myAnts:
        #     myAntScore += ant.health
        #
        # theirAnts = theirInv.ants
        # theirAntScore = 0
        # for ant in myAnts:
        #     theirAntScore += ant.health
        # antDiff = (myAntScore - theirAntScore) / max(myAntScore, theirAntScore)
        #
        #
        # # calculating food
        #
        # myCarryScore = 0.0
        # foodDistScore = 0.0
        # for worker in myWorkers:
        #     if worker.carrying:
        #         myCarryScore += 1
        # theirWorkers = getAntList(gs, 1 - me, (WORKER,))
        # theirCarryScore = 0.0
        # for worker in theirWorkers:
        #     if worker.carrying:
        #         theirCarryScore += 1
        #         foodDistScore += 1 - (approxDist(worker.coords, self.tunnelCoords) / self.maxTunnelDist)
        #     else:
        #         foodDistScore += 1 - (approxDist(worker.coords, self.myFoodCoords) / self.maxFoodDist)
        # myPotentialFood = myInv.foodCount + myCarryScore
        # theirPotentialFood = theirInv.foodCount + theirCarryScore
        # foodDiff = (myPotentialFood - theirPotentialFood) / 11
        #
        #
        #
        #
        # print((antDiff + foodDiff + foodDistScore) / 3)
        # return (antDiff + foodDiff + foodDistScore) / 3

        # myInv = getCurrPlayerInventory(gs)
        # theirInv = getEnemyInv(self, gs)
        # me = gs.whoseTurn
        # myQueen = getAntList(gs, me, (QUEEN,))[0]
        #
        # #do this once
        # if self.maxTunnelDist == 0:
        #     self.tunnelCoords = getConstrList(gs, me, (TUNNEL,))[0].coords
        #     self.anthillCoords = getConstrList(gs, me, (ANTHILL,))[0].coords
        #     print(self.tunnelCoords)
        #     foods = getConstrList(gs, None, (FOOD,))
        #     #find the food closest to the tunnel
        #     bestDistSoFar = 1000 #i.e., infinity
        #     for food in foods:
        #         dist = stepsToReach(gs, self.tunnelCoords, food.coords)
        #         if (dist < bestDistSoFar):
        #             self.myFoodCoords = food.coords
        #             bestDistSoFar = dist
        #
        #     print(self.myFoodCoords)
        #
        #     for i in range(0,10):
        #         for j in range(0,10):
        #             tunnelDist = approxDist((i,j), self.tunnelCoords)
        #             foodDist = approxDist((i,j), self.myFoodCoords)
        #             if (tunnelDist > self.maxTunnelDist):
        #                 self.maxTunnelDist = tunnelDist
        #             if (foodDist > self.maxFood1Dist):
        #                 self.maxFood1Dist = foodDist
        #
        #
        # #if we have more than two workers, throw out this option
        # myWorkers = getAntList(gs, me, (WORKER,))
        # if len(myWorkers) > 2:
        #     return -1.0
        # else:
        #     myWorkerScore = len(myWorkers) / 2
        #
        # #remove nodes where an ant is sitting idle on the hill
        # myAnts = myInv.ants
        # for ant in myAnts:
        #     if myQueen.coords == self.anthillCoords:
        #         return -1.0
        #
        # #give positive weight to soldiers that are closer to the enemy queen
        # mySoldiers = getAntList(gs, me, (SOLDIER,))
        # enemyQueen = getAntList(gs, 1-me, (QUEEN,))[0]
        # soldierScore = 0.0
        # #starts at 120 so the AI wants 3 soldiers
        # maxSoldierScore = 120.0
        # for soldier in mySoldiers:
        #     #give priority to moves that make more soldiers
        #     soldierScore += 40
        #     #then give priority to moves that move soldiers close to the enemy queen
        #     soldierScore += 20 - approxDist(soldier.coords, enemyQueen.coords)
        #     maxSoldierScore += 19
        # #take ratio between soldierScore and its maximum
        # #the abs() is used to make sure the numerator is smaller than denominator
        # #soldierScore range is 0.0 to 1.0
        # soldierScore = (maxSoldierScore - abs(maxSoldierScore - soldierScore)) / maxSoldierScore
        #
        # #calculate ant score
        # myAntScore = 0
        # myAntHealthScore = 0
        # for ant in myAnts:
        #     myAntHealthScore += ant.health
        #     if ant.type == WORKER:
        #         myAntScore += 1
        #     elif ant.type == SOLDIER:
        #         myAntScore += 4
        #     elif ant.type == DRONE:
        #         myAntScore += 2
        #     elif ant.type == R_SOLDIER:
        #         myAntScore += 3
        # #theirAnts = getAntList(gs, 1-me, (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
        # theirAnts = theirInv.ants
        # theirAntScore = 0
        # theirAntHealthScore = 0
        # for ant in myAnts:
        #     theirAntHealthScore += ant.health
        #     if ant.type == WORKER:
        #         theirAntScore += 1
        #     elif ant.type == SOLDIER:
        #         theirAntScore += 4
        #     elif ant.type == DRONE:
        #         theirAntScore += 2
        #     elif ant.type == R_SOLDIER:
        #         theirAntScore += 3
        # antDiff = (myAntScore - theirAntScore) / max(myAntScore, theirAntScore)
        #
        # antHealthDiff = (myAntHealthScore - theirAntHealthScore) / (myAntScore + theirAntScore)
        #
        # #queen health
        # myQueen = getAntList(gs, me, (QUEEN,))
        # theirQueen = getAntList(gs, 1-me, (QUEEN,))
        # if len(theirQueen) != 0 and len(myQueen) != 0:
        #     queenDiff = (myQueen[0].health - theirQueen[0].health) / 10
        #
        # #calculating food and give positive weight to worker ant nearer the tunnel that are carrying food
        # theirWorkers = getAntList(gs, 1-me, (WORKER,))
        #
        # myCarryScore = 0
        # nearTunnelScore = 0
        # nearFoodScore = 0
        # numWorkersCarrying = 0
        # # for worker in myWorkers:
        # #     if worker.carrying:
        # #         numWorkersCarrying += 1
        # #         myCarryScore += 1
        # #         nearTunnelScore += approxDist(worker.coords, self.tunnelCoords) / self.maxTunnelDist
        # #     else:
        # #         nearFoodScore +=  approxDist(worker.coords, self.myFoodCoords) / self.maxTunnelDist
        # #
        # # if numWorkersCarrying != 0:
        # #     nearTunnelScore /= numWorkersCarrying
        # #     nearTunnelScore = 1 - nearTunnelScore
        # # if (len(myWorkers)-numWorkersCarrying) != 0:
        # #     nearFoodScore /= (len(myWorkers)-numWorkersCarrying)
        # #     nearFoodScore = 1 - nearFoodScore
        #
        # foodDistScore = 0
        # maxFoodDistScore = 1
        # for worker in myWorkers:
        #     if worker.carrying:
        #         myCarryScore += 1
        #         foodDistScore += self.maxTunnelDist - approxDist(worker.coords, self.tunnelCoords)
        #         maxFoodDistScore += self.maxTunnelDist
        #     else:
        #         foodDistScore += self.maxFood1Dist - approxDist(worker.coords, self.myFoodCoords)
        #         maxFoodDistScore += self.maxFood1Dist
        # foodDistScore = foodDistScore / maxFoodDistScore
        #
        #
        # # theirCarryScore = 0.0
        # # for worker in theirWorkers:
        # #     if worker.carrying:
        # #         theirCarryScore += 1
        #
        # foodScore = (myInv.foodCount + (myCarryScore / 4)) / 11
        # # theirPotentialFood = theirInv.foodCount + (theirCarryScore / 2)
        # #foodDiff = (myPotentialFood - theirPotentialFood) / 11
        #
        # output = ((4*foodScore) + foodDistScore + soldierScore) / 6
        # return output
        # #return (antDiff + queenDiff + nearTunnelScore + nearFoodScore + soldierScore) / 5

    def expandNode(self, node):
        moves = listAllLegalMoves(node["state"])
        if len(moves) != 1:
            for move in moves:
                if move.moveType == END:
                    moves.remove(move)
        moveList = []
        for move in moves:
            newNode = {"move": move}
            newNode["state"] = getNextState(node["state"], newNode["move"])
            getEnemyInv(self, newNode["state"])
            newNode["value"] = 0  # this is updated in bfs
            # newNode["value"] = self.evaluateState(newNode["state"])
            newNode["parent"] = node
            newNode["depth"] = node["depth"] + 1
            moveList.append(newNode)
        return moveList

    def evalListNodes(self, nodes):
        # max = -1
        # for node in nodes:
        #     if node["value"] > max:
        #         max = node["value"]
        # return max
        sum = 0
        for node in nodes:
            if node["depth"] == 1:
                # for debug
                sum += node["value"]
            else:
                sum += node["value"]
        return sum / len(nodes)

    def bfs(self, node, depth):
        newNodes = self.expandNode(node)
        # it is depth + 1 since we just expanded the node and are
        # now evaluating nodes at depth + 1
        if depth + 1 < self.depth_limit:
            # if the next set of nodes are inside the depth limit, do bfs()
            for n in newNodes:
                # print(str(newNodes.index(n)) + " , " + str(depth))
                n["value"] = self.evaluateState(n["state"])
                if n["value"] > 0:
                    n["value"] = (0.5 * self.evaluateState(n["state"])) + (0.5 * self.bfs(n, depth + 1))
        else:
            # else find the values of each node
            for n in newNodes:
                n["value"] = self.evaluateState(n["state"])
        evaluation = self.evalListNodes(newNodes)
        if depth > 0:
            return evaluation
        else:
            max = -10
            move = None
            for n in newNodes:
                if n["value"] > max:
                    max = n["value"]
                    move = n["move"]
            return move
