import random
import pprint
import sys
from operator import itemgetter

class TicTacToe:
    def __init__(self, playerX, playerO):
        self.board = [' ']*9
        self.playerX, self.playerO = playerX, playerO
        self.playerX_turn = random.choice([True, False])

    def play_game(self):

        moneyX = 50
        moneyO = 50
        self.playerX.start_game('X', moneyX)
        self.playerO.start_game('O', moneyO)

        betX = 0
        betO = 0

        while True: #yolo

            if self.playerX.breed == "human":
                print("Both Players Make bets:")

            betX = 0
            betO = 0

            while betX == betO and (moneyX != 0 or moneyO != 0):
                betX = self.playerX.place_bet(self.board,self.playerO.money)
                betO = self.playerO.place_bet(self.board,self.playerX.money)
                print("X: ",betX, "\tO: ",betO)
                if self.playerX.breed == "human":
                    print("Both bets equal! Try again...")
                if moneyX == moneyO == 1:
                    break;

            if moneyX == moneyO == 1:
                player.reward(0, self.board, "bet")
                other_player.reward(0, self.board, "bet")
                self.playerX.money = moneyX
                self.playerO.money = moneyO
                break

            if betX - betO == betX - moneyX == betO - moneyO == 0: #both players out of money; draw
                player.reward(0, self.board, "bet")
                other_player.reward(0, self.board, "bet")
                self.playerX.money = moneyX
                self.playerO.money = moneyO
                break

            moneyX = moneyX - betX
            moneyO = moneyO - betO

            if self.playerX.breed == "human":
                print("You bet: $",betX, ", Opponent bet: $", betO)

            self.playerX_turn = True if betX > betO else False

            if self.playerX_turn:
                player, char, other_player, player_money, other_money, money_after_bet, money_after_bet_other = self.playerX, 'X', self.playerO, self.playerX.money, self.playerO.money, moneyX, moneyO
            else:
                player, char, other_player, player_money, other_money, money_after_bet, money_after_bet_other = self.playerO, 'O', self.playerX, self.playerO.money, self.playerX.money, moneyO, moneyX

            if player.breed == "human":
                self.display_board()

            space = player.move(self.board)
            if self.board[space-1] != ' ': # illegal move
                player.reward(-99, self.board, "move") # score of shame
                self.playerX.money = moneyX
                self.playerO.money = moneyO
                break

            self.board[space-1] = char

            if (betX > 20):
                self.playerX.reward(-0.5, self.board, "bet")
            if (betO > 20):
                self.playerO.reward(-0.5, self.board, "bet")

            if self.player_wins(char):
                player.reward(1, self.board, "move")
                player.reward(1, self.board, "bet")
                other_player.reward(-1, self.board, "move")
                other_player.reward(-1, self.board, "bet")
                self.playerX.money = moneyX
                self.playerO.money = moneyO
                if player.breed == "human" or other_player.breed == "human":
                    self.display_board()
                break
            if self.board_full(): # tie game
                player.reward(0.5, self.board, "both")
                other_player.reward(0.5, self.board, "both")
                self.playerX.money = moneyX
                self.playerO.money = moneyO
                if player.breed == "human" or other_player.breed == "human":
                    self.display_board()
                break

            player.reward(0,self.board, "move")
            other_player.reward(0, self.board, "move")
            if (money_after_bet == 0):
                player.reward(-2, self.board, "bet")
            else:
                player.reward(0, self.board, "bet")
            if (money_after_bet_other == 0):
                other_player.reward(-2, self.board, "bet")
            else:
                other_player.reward(0, self.board, "bet")

            self.playerX.money = moneyX
            self.playerO.money = moneyO
            self.playerX_turn = False
            betX = 0
            betO = 0
            if player.breed == "human" or other_player.breed == "human":
                self.display_board()

    def player_wins(self, char):
        for a,b,c in [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]:
            if char == self.board[a] == self.board[b] == self.board[c]:
                return True
        return False

    def board_full(self):
        return not any([space == ' ' for space in self.board])

    def display_board(self):
        row = " {} | {} | {}"
        hr = "\n-----------\n"
        print ((row + hr + row + hr + row).format(*self.board))


class Player(object):
    def __init__(self):
        self.breed = "human"
        self.money = 0

    def start_game(self, char, money):
        self.money = money
        print ("\nNew game!")

    def place_bet(self, board, opp_money):
        bet = 0
        while True:
            bet = int(input(("Opponent has $", opp_money, ". You have $", self.money, "...Your bet: ")))
            if bet <= self.money and bet >= 0:
                break
        return bet

    def move(self, board):
        return int(input("Your move? "))

    def reward(self, value, board, reward_for):
        print ("{} rewarded: {}".format(self.breed, value))

    def available_moves(self, board):
        return [i+1 for i in range(0,9) if board[i] == ' ']


class QLearningPlayer(Player):
    def __init__(self, epsilon=0.2, alpha=0.3, gamma=0.8):
        self.breed = "Qlearner"
        self.harm_humans = False
        self.q_move = {}    # (state, action) keys: Q_move values
        self.q_bet = {} # (state, money, opp_money, bet_amount) keys: Q_bet values
        self.epsilon = epsilon # e-greedy chance of random exploration
        self.alpha = alpha # learning rate
        self.gamma = gamma # discount factor for future rewards
        self.money = 0

    def start_game(self, char, money):
        self.last_board = (' ',)*9
        self.last_move = None
        self.last_bet = None
        self.money = money
        self.last_opp_wealth = None

    def getQ_bet(self, state, money, opp_wealth, bet):
        # encourage exploration; "optimistic" 1.0 initial values
        if self.q_bet.get((state, money, opp_wealth, bet)) is None:
            self.q_bet[(state, money, opp_wealth, bet)] = 1.0
        return self.q_bet.get((state, money, opp_wealth, bet))

    def getQ_move(self, state, action):
        # encourage exploration; "optimistic" 1.0 initial values
        if self.q_move.get((state, action)) is None:
            self.q_move[(state, action)] = 1.0
        return self.q_move.get((state, action))

    def place_bet(self, board, opp_money):
        self.last_board = tuple(board)
        opp_wealth = opp_money
        '''opp_wealth = 0;
        if opp_money == 50:
            opp_wealth = 8
        elif opp_money > 42:
            opp_wealth = 7
        elif opp_money >= 35:
            opp_wealth = 6
        elif opp_money >= 25:
            opp_wealth = 5
        elif opp_money >= 15:
            opp_wealth = 4
        elif opp_money >= 8:
            opp_wealth = 3
        elif opp_money >= 3:
            opp_wealth = 2
        elif opp_money >=1:
            opp_wealth = 1'''
        self.last_opp_wealth = opp_money
        if self.money == 0:
            return 0
        actions = [i for i in range(1,min(opp_money+2, self.money+1))]
        #print("I have: $",self.money,"last_bet:",self.last_bet)
        if random.random() < self.epsilon: # explore!
            self.last_bet = random.choice(actions)
            return self.last_bet
        qbet = [self.getQ_bet(self.last_board,self.money,opp_wealth,a) for a in actions]
        maxQ_bet = max(qbet)

        if qbet.count(maxQ_bet) > 1:
            best_options = [i for i in range(len(actions)) if qbet[i] == maxQ_bet]
            i = random.choice(best_options)
        else:
            i = qbet.index(maxQ_bet)

        self.last_bet = actions[i]
        return actions[i]

    def move(self, board):
        self.last_board = tuple(board)
        actions = self.available_moves(board)

        if random.random() < self.epsilon: # explore!
            self.last_move = random.choice(actions)
            return self.last_move

        qs = [self.getQ_move(self.last_board, a) for a in actions]
        maxQ_move = max(qs)

        if qs.count(maxQ_move) > 1:
            #more than 1 best option; choose among them randomly
            best_options = [i for i in range(len(actions)) if qs[i] == maxQ_move]
            i = random.choice(best_options)
        else:
            i = qs.index(maxQ_move)

        self.last_move = actions[i]
        return actions[i]

    def reward(self, value, board, reward_for):
        if reward_for == "move":
            self.reward_move(value, board)
        elif reward_for == "bet":
            self.reward_bet(value, board)
        else:
            self.reward_move(value, board)
            self.reward_bet(value, board)

    def reward_bet(self, value, board):
        if self.last_bet:
            self.learn_bet(self.last_board, self.last_bet, self.money, self.last_opp_wealth, value, tuple(board))

    def learn_bet(self, state, bet_made, money_before_bet, opp_money_before_bet, reward, result_state):
        prev_q = self.getQ_bet(state, money_before_bet, opp_money_before_bet, bet_made)
        maxNext = []
        for i in range(0,opp_money_before_bet):
            for j in range(0,money_before_bet-bet_made+1):
                maxNext.append(self.getQ_bet(result_state,money_before_bet-bet_made,i,j))
        maxqnew = reward if maxNext == [] else max(maxNext)
        self.q_bet[(state, money_before_bet, opp_money_before_bet, bet_made)] = prev_q + self.alpha*((reward + self.gamma*maxqnew) - prev_q)

    def reward_move(self, value, board):
        if self.last_move:
            self.learn_move(self.last_board, self.last_move, value, tuple(board))

    def learn_move(self, state, action, reward, result_state):
        prev_move = self.getQ_move(state, action)
        maxNext = [self.getQ_move(result_state, a) for a in self.available_moves(result_state)];
        maxqnew = reward if maxNext == [] else max(maxNext)
        self.q_move[(state, action)] = prev_move + self.alpha * ((reward + self.gamma*maxqnew) - prev_move)


class RandomPlayer(Player):
    def __init__(self):
        self.breed = "random"
        self.money = 0

    def place_bet(self, board, opp_money):
        return random.randint(0,min(self.money,opp_money+1))

    def reward(self, value, board, reward_for):
        pass

    def start_game(self, char, money):
        self.money = money

    def move(self, board):
        return random.choice(self.available_moves(board))


class MinimaxPlayer(Player):
    def __init__(self):
        self.breed = "minimax"
        self.best_moves = {}
        self.money = 0

    def start_game(self, char, money):
        self.me = char
        self.enemy = self.other(char)
        self.money = money

    def place_bet(self, board, opp_money):
        return random.randint(0,min(self.money,opp_money+1))

    def other(self, char):
        return 'O' if char == 'X' else 'X'

    def move(self, board):
        if tuple(board) in self.best_moves:
            return random.choice(self.best_moves[tuple(board)])
        if len(self.available_moves(board)) == 9:
            return random.choice([1,3,7,9])
        best_yet = -2
        choices = []
        for move in self.available_moves(board):
            board[move-1] = self.me
            optimal = self.minimax(board, self.enemy, -2, 2)
            board[move-1] = ' '
            if optimal > best_yet:
                choices = [move]
                best_yet = optimal
            elif optimal == best_yet:
                choices.append(move)
        self.best_moves[tuple(board)] = choices
        return random.choice(choices)

    def minimax(self, board, char, alpha, beta):
        if self.player_wins(self.me, board):
            return 1
        if self.player_wins(self.enemy, board):
            return -1
        if self.board_full(board):
            return 0
        for move in self.available_moves(board):
            board[move-1] = char
            val = self.minimax(board, self.other(char), alpha, beta)
            board[move-1] = ' '
            if char == self.me:
                if val > alpha:
                    alpha = val
                if alpha >= beta:
                    return beta
            else:
                if val < beta:
                    beta = val
                if beta <= alpha:
                    return alpha
        if char == self.me:
            return alpha
        else:
            return beta

    def player_wins(self, char, board):
        for a,b,c in [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]:
            if char == board[a] == board[b] == board[c]:
                return True
        return False

    def board_full(self, board):
        return not any([space == ' ' for space in board])

    def reward(self, value, board, reward_for):
        pass


class MinimuddledPlayer(MinimaxPlayer):
    def __init__(self, confusion=0.1):
        super(MinimuddledPlayer, self).__init__()
        self.breed = "muddled"
        self.confusion = confusion
        self.money = 0
        self.ideal_player = MinimaxPlayer()

    def start_game(self, char, money):
        self.ideal_player.me = char
        self.ideal_player.enemy = self.other(char)
        self.money = money

    def place_bet(self, board, opp_money):
        return random.randint(0,min(self.money,opp_money+1))

    def move(self, board):
        if random.random() > self.confusion:
            return self.ideal_player.move(board)
        else:
            return random.choice(self.available_moves(board))


# p1 = RandomPlayer()
# p1 = MinimaxPlayer()
# p1 = MinimuddledPlayer()
p1 = RandomPlayer()
p2 = QLearningPlayer()
for i in range(0,40000):
    t = TicTacToe(p1, p2)
    print("training random...episode ", i)
    t.play_game()

p1 = MinimaxPlayer()
for i in range(0,40000):
    t = TicTacToe(p1, p2)
    print("training minimax...episode ", i)
    t.play_game()

'''p1 = MinimuddledPlayer()
for i in range(0,40000):
    t = TicTacToe(p1, p2)
    print("training minimax...episode ", i)
    t.play_game()'''

'''p1 = QLearningPlayer()
p2.epsilon = 0.5
for i in range(0,5000):
    t = TicTacToe(p1, p2)
    print("training with self-play instance...episode ", i)
    t.play_game()'''

p1 = Player()
p2.epsilon = 0.05
p2.alpha = 0.5
#pprint.pprint(sorted(p2.q_bet.items(), key=itemgetter(1)))

while True:
    t = TicTacToe(p1, p2)
    t.play_game()
