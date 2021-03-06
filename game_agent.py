"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import math
import pickle

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

#    return increase_own_moves_score(game, player)
    return increase_opponent_move_penalty_near_endgame(game, player)
#    return square_move_diff(game, player)

def penalize_moves(moves, game):
    """This custom score will give 3 for each legal move but penalize edge
    moves by 1 and corner moves by 2 because of their limited moves on
    subsequent boards. To be used in penalize_edges_overlay_moves and
    penalize_edges

    For a 4x4 board, the value of a move to a square would look like:

    1221
    2332
    2332
    1221

    Parameters
    ----------
    moves : a list of two-tuples representing moves [(1, 2), (-1, 2)], etc.

    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    Returns
    ----------
    float
        The heuristic value for a set of moves
    """
    score = float(len(moves) \
                  - len([1 for (x,y) in moves if x == 0]) \
                  - len([1 for (x,y) in moves if y == 0]) \
                  - len([1 for (x,y) in moves if x == game.width - 1]) \
                  - len([1 for (x,y) in moves if y == game.height - 1]))
    return score

def penalize_edges(game, player):
    # This custom score computes the heuristic as explained in penalize_moves
    moves = game.get_legal_moves(player)
    return penalize_moves(moves, game)

def penalize_edges_overlay_moves(game, player):
    # This custom score computes the edge penaly for each
    # set of moves (player and opponent) and takes the
    # difference

    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    return penalize_moves(own_moves, game) - penalize_moves(opp_moves, game)

def square_move_diff(game, player):
    # This custom score is similar to the sample player "improved_score"
    # but scores with the square of the difference of moves reflecting the
    # increased likelihood of getting trapped

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return math.pow(own_moves,2) - math.pow(opp_moves, 2)

def increase_own_moves_score(game, player):
    # This custom score is similar to the improved score, but we double
    # the value of the player's moves

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return 1.3*own_moves - opp_moves

def increase_opponent_move_penalty_near_endgame(game, player):
    # This custom score is similar to increase_own_moves_score but
    # changes the coefficient near the endgame to emphasize reducing
    # the opponent's move

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    theta = 1.3
    if game.move_count > 25:
        theta = 0.75
    return theta*own_moves - opp_moves

class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        ----------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Return (-1, -1) when there are no available moves
        if not legal_moves or len(legal_moves) == 0:
            return (-1, -1)
        elif self.time_left() < self.TIMER_THRESHOLD:
            # If we just ran out of time, we want to take one of the
            # moves, so quickly return the first one
            return legal_moves[0]

        if self.method == 'minimax':
            method = self.minimax
        else:
            method = self.alphabeta

        move = legal_moves[0]
        try:
            # Iterative deepening or fixed depth below
            if self.iterative:
                for d in range(1, 99):
                    score, move_returned = method(game, d)
                    if move_returned != (-1, -1): move = move_returned
            else:
                score, move_returned = method(game, self.search_depth)
                if move_returned != (-1, -1): move = move_returned


        except Timeout:
            # Handle any actions required at timeout, if necessary
            return move

        # Return the best move from the last completed search iteration
        return move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        if depth == 0:
            raise ValueError("depth must be strictly greater than zero.")

        # If we are at a leaf that is a win for a player, return the score
        moves = [move for move in game.get_legal_moves()]
        if not moves or len(moves) == 0:
            return self.score(game, self), (-1, -1)

        # For a fixed depth of 1, we just return the score for each move.
        # For a deeper depth, we recurse by expanding each leaf
        move_score_pairs = None
        if depth == 1:
            move_score_pairs = [(self.score(game.forecast_move(move), self), move) \
                                for move in moves]
        else:
            move_score_pairs = [(self.minimax(game.forecast_move(move), depth-1, not maximizing_player)[0], \
                                 move) for move in moves]

        if maximizing_player:
            return max(move_score_pairs, key = lambda x: x[0])
        else:
            return min(move_score_pairs, key = lambda x: x[0])

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """


        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        if depth == 0:
            raise ValueError("depth must be strictly greater than zero.")

        moves = game.get_legal_moves()
        if not moves or len(moves) == 0:
            return self.score(game, self), (-1, -1)

        move_to_return = moves[0]
        if maximizing_player:
            val = float("-inf")

            for move in moves:
                if depth == 1:
                    newval = self.score(game.forecast_move(move), self)
                else:
                    newval = self.alphabeta(game.forecast_move(move), depth-1, alpha, beta, not maximizing_player)[0]
                # Check if the newval is more than the stored val
                # If so, update the move to return
                if val < newval:
                    val = newval
                    move_to_return = move
                # If we have a new max, update beta
                if val >= beta:
                    return val, move
                alpha = max(alpha, val)
        else:
            val = float("inf")
            for move in moves:
                if depth == 1:
                    newval = self.score(game.forecast_move(move), self)
                else:
                    newval = self.alphabeta(game.forecast_move(move), depth-1, alpha, beta, not maximizing_player)[0]
                # Check if the newval is less than the stored val
                # If so, update the move to return
                if val > newval:
                    val = newval
                    move_to_return = move
                # If we have a new min, update alpha
                if val <= alpha:
                    return val, move
                beta = min(beta, val)
        return val, move_to_return
