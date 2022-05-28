# Student agent: Add your own agent here
import random

from agents.agent import Agent
from store import register_agent
import sys


@register_agent("new_agent")
class NewAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(NewAgent, self).__init__()
        self.name = "newAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.autoplay = True

    # the 3 function is to find all valid position
    def can_move(self, chess_board, my_pos, dir):
        if not chess_board[my_pos[0], my_pos[1], dir]:
            return True
        else:
            return False

    def has_n_barrier(self, chess_board, cur_pos):
        return sum(chess_board[cur_pos[0], cur_pos[1]])

    def get_valid_pos(self, chess_board, my_pos, adv_pos, max_step, n):
        valid_pos_list = [my_pos]
        check_list = [my_pos]
        cur_step = 1
        while cur_step <= max_step:
            next_check = []
            for pos in check_list:
                for dir in range(4):
                    if self.can_move(chess_board, pos, dir):
                        next_pos = self.get_neighbours(pos, dir)[0]
                        if (next_pos != adv_pos and next_pos not in valid_pos_list and
                                self.has_n_barrier(chess_board, next_pos) < n):
                            valid_pos_list.append(next_pos)
                            next_check.append(next_pos)
            cur_step += 1
            check_list = next_check

        move_list = []
        for pos in valid_pos_list:
            for i in range(4):
                if not chess_board[pos[0], pos[1], i]:
                    move_list.append((pos, i))

        return move_list

    # use A* to arrange all possible next_pos
    def sort_valid_positions(self, move_list, adv_pos, chess_board, nd, nb):
        move_dic = {}
        for move in move_list:
            pos = move[0]
            diff_x = abs(pos[0] - adv_pos[0])
            diff_y = abs(pos[1] - adv_pos[1])
            dist = diff_x + diff_y
            move_dic[move] = nd * dist + nb * sum(chess_board[pos[0]][pos[1]])
        # sort value from low to high
        return dict(sorted(move_dic.items(), key=lambda item: item[1]))

    def get_neighbours(self, my_pos, dir):
        if dir == 0:
            return (my_pos[0]-1, my_pos[1]), 2
        if dir == 1:
            return (my_pos[0], my_pos[1]+1), 3
        if dir == 2:
            return (my_pos[0]+1, my_pos[1]), 0
        if dir == 3:
            return (my_pos[0], my_pos[1]-1), 1

    def check_not_reachable(self, chess_board, my_pos, adv_pos):
        size = len(chess_board) * len(chess_board)
        valid_pos_list = [my_pos]
        check_list = [my_pos]
        cur_step = 1
        while cur_step <= size:
            next_check = []
            for pos in check_list:
                for dir in range(4):
                    if self.can_move(chess_board, pos, dir):
                        next_pos = self.get_neighbours(pos, dir)[0]
                        if next_pos != adv_pos:
                            return False
                        if next_pos not in valid_pos_list:
                            valid_pos_list.append(next_pos)
                            next_check.append(next_pos)
            cur_step += 1
            check_list = next_check

        return True

    def check_score(self, chess_board, pos):
        size = len(chess_board)*len(chess_board)
        pos_list = [pos]
        check_list = [pos]
        cur_step = 1
        while cur_step < size:
            next_check = []
            for pos in check_list:
                for dir in range(4):
                    if self.can_move(chess_board, pos, dir):
                        next_pos = self.get_neighbours(pos, dir)[0]
                        if next_pos not in pos_list:
                            pos_list.append(next_pos)
                            next_check.append(next_pos)

            cur_score = len(pos_list)
            if cur_score == size:
                break

            cur_step += 1
            check_list = next_check

        return len(pos_list)

    def terminate(self, chess_board, my_pos, adv_pos):
        par = {}
        for row in range(chess_board.shape[0]):
            for col in range(chess_board.shape[0]):
                par[(row, col)] = (row, col)

        def find(pos):
            if par[pos] != pos:
                par[pos] = find(par[pos])
            return par[pos]

        for row in range(chess_board.shape[0]):
            for col in range(chess_board.shape[0]):
                moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
                for dir, move in enumerate(moves[1:3]):
                    if chess_board[row, col, dir + 1]:
                        continue
                    pos_a = find((row, col))
                    pos_b = find((row + move[0], col + move[1]))
                    if pos_a != pos_b:
                        par[pos_a] = pos_b

        for row in range(chess_board.shape[0]):
            for col in range(chess_board.shape[0]):
                find((row, col))
        p0_r = find(my_pos)
        p1_r = find(adv_pos)
        my_area = list(par.values()).count(p0_r)
        adv_area = list(par.values()).count(p1_r)
        if p0_r == p1_r:
            return False, my_area, adv_area
        return True, my_area, adv_area

    def step(self, chess_board, my_pos, adv_pos, max_step):
        size = len(chess_board)
        move_list = self.get_valid_pos(chess_board, my_pos, adv_pos, max_step, 3)
        sort_list = list(self.sort_valid_positions(move_list, adv_pos, chess_board, 1, 2).keys())
        random_move = move_list[random.randint(0,len(move_list)-1)]
        bad_move_list = []

        for move in move_list:
            next_my_pos = move[0]
            next_my_dir = move[1]
            next_my_neighbour = self.get_neighbours(next_my_pos, next_my_dir)
            next_my_neighbour_pos = next_my_neighbour[0]
            next_my_neighbour_dir = next_my_neighbour[1]
            chess_board[next_my_pos[0], next_my_pos[1], next_my_dir] = True
            chess_board[next_my_neighbour_pos[0], next_my_neighbour_pos[1], next_my_neighbour_dir] = True
            flag, s1, s2 = self.terminate(chess_board, next_my_pos, adv_pos)
            if flag:
                if s1 >= s2:
                    return move
                else:
                    bad_move_list.append(move)
            # else:
            #     if size < 11:
            #         adv_move_list = self.get_valid_pos(chess_board, adv_pos, my_pos, max_step, 3)
            #         for adv_move in adv_move_list:
            #             next_adv_pos = adv_move[0]
            #             next_adv_dir = adv_move[1]
            #             next_adv_neighbour = self.get_neighbours(next_adv_pos, next_adv_dir)
            #             next_adv_neighbour_pos = next_adv_neighbour[0]
            #             next_adv_neighbour_dir = next_adv_neighbour[1]
            #             chess_board[next_adv_pos[0], next_adv_pos[1], next_adv_dir] = True
            #             chess_board[next_adv_neighbour_pos[0], next_adv_neighbour_pos[1], next_adv_neighbour_dir] = True
            #             flag2, s21, s22 = self.terminate(chess_board, next_my_pos, next_adv_pos)
            #             if flag2 and s21 < s22:
            #                 bad_move_list.append(move)
            #
            #             chess_board[next_adv_pos[0], next_adv_pos[1], next_adv_dir] = False
            #             chess_board[next_adv_neighbour_pos[0], next_adv_neighbour_pos[1], next_adv_neighbour_dir] = False

            chess_board[next_my_pos[0], next_my_pos[1], next_my_dir] = False
            chess_board[next_my_neighbour_pos[0], next_my_neighbour_pos[1], next_my_neighbour_dir] = False

        for move in sort_list:
            if move not in bad_move_list:
                return move

        return random_move

