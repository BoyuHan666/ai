# Student agent: Add your own agent here

from agents.agent import Agent
from store import register_agent
import sys
import numpy as np
import copy


# import time


@register_agent("advanced_agent")
class AdvancedAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(AdvancedAgent, self).__init__()
        self.name = "advancedAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.autoplay = True
        # the 3 function is to find all valid position

    def can_move(self, chess_board, my_pos, dir):
        if not chess_board[my_pos[0]][my_pos[1]][self.dir_map[dir]]:
            return True
        else:
            return False

    def has_n_barrier(self, chess_board, cur_pos):
        return sum(chess_board[cur_pos[0]][cur_pos[1]])

    def get_valid_pos(self, chess_board, max_step, my_pos, adv_pos, n):
        valid_pos_list = [my_pos]
        check_list = [my_pos]
        cur_step = 1
        direction = ["u", "r", "d", "l"]
        while cur_step <= max_step:
            next_check = []
            for pos in check_list:
                if self.can_move(chess_board, pos, "u"):
                    next_pos = (pos[0] - 1, pos[1])
                    if (next_pos != adv_pos) and (next_pos not in valid_pos_list) and (
                            self.has_n_barrier(chess_board, next_pos) < n):
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

                if self.can_move(chess_board, pos, "r"):
                    next_pos = (pos[0], pos[1] + 1)
                    if (next_pos != adv_pos) and (next_pos not in valid_pos_list) and (
                            self.has_n_barrier(chess_board, next_pos) < n):
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

                if self.can_move(chess_board, pos, "d"):
                    next_pos = (pos[0] + 1, pos[1])
                    if (next_pos != adv_pos) and (next_pos not in valid_pos_list) and (
                            self.has_n_barrier(chess_board, next_pos) < n):
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

                if self.can_move(chess_board, pos, "l"):
                    next_pos = (pos[0], pos[1] - 1)
                    if (next_pos != adv_pos) and (next_pos not in valid_pos_list) and (
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

        return valid_pos_list, move_list

        # use A* to arrange all possible next_pos

    def sort_valid_positions(self, move_list, adv_pos, chess_board):
        move_dic = {}
        for move in move_list:
            pos = move[0]
            diff_x = abs(pos[0] - adv_pos[0])
            diff_y = abs(pos[1] - adv_pos[1])
            dist = diff_x + diff_y
            move_dic[move] = dist + 2 * sum(chess_board[pos[0]][pos[1]])
        # sort value from low to high
        return dict(sorted(move_dic.items(), key=lambda item: item[1]))

    def safe_pos(self, move_list, chess_board):
        min_barrier = 4
        opt_move = ()
        for move in move_list:
            pos = move[0]
            if self.has_n_barrier(chess_board, pos) < min_barrier:
                min_barrier = self.has_n_barrier(chess_board, pos)
                opt_move = move
        return opt_move

    def valid_pos(self, chess_board, max_step, my_pos, adv_pos):
        # BFS
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        state_queue = [(my_pos, 0)]
        valid_pos_list = {tuple(my_pos)}
        while state_queue:
            cur_pos, cur_step = state_queue.pop(0)
            r, c = cur_pos
            if cur_step == max_step:
                break
            for dir, move in enumerate(moves):
                if chess_board[r, c, dir]:
                    continue
                next_pos = tuple(map(lambda i, j: i + j, cur_pos, move))
                if np.array_equal(next_pos, adv_pos) or tuple(next_pos) in valid_pos_list:
                    continue
                valid_pos_list.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        move_list = []
        for pos in valid_pos_list:
            for i in range(4):
                if not chess_board[pos[0], pos[1], i]:
                    move_list.append((pos, i))

        return valid_pos_list, move_list

    def add_neigbour_barrier(self, chess_board, my_pos, dir):
        adv_pos = (0,0)
        adv_dir = 0
        if dir == 0:
            adv_pos = (my_pos[0]-1, my_pos[1])
            adv_dir = 2
        if dir == 1:
            adv_pos = (my_pos[0], my_pos[1]+1)
            adv_dir = 3
        if dir == 2:
            adv_pos = (my_pos[0]+1, my_pos[1])
            adv_dir = 0
        if dir == 3:
            adv_pos = (my_pos[0], my_pos[1]+1)
            adv_dir = 1
        chess_board[adv_pos[0], adv_pos[1], adv_dir] = True
        return chess_board

    def step(self, chess_board, my_pos, adv_pos, max_step):
        valid_pos_list, move_list = self.get_valid_pos(chess_board, max_step, my_pos, adv_pos, 5)
        # valid_pos_list, move_list = self.valid_pos(chess_board, max_step, my_pos, adv_pos)
        # print(self.check_same(valid_pos_list, vl2))
        move_dic = self.sort_valid_positions(move_list, adv_pos, chess_board)

        sorted_list = list(move_dic.keys())
        adv_neighbor_u = (adv_pos[0] - 1, adv_pos[1])
        adv_neighbor_r = (adv_pos[0], adv_pos[1] + 1)
        adv_neighbor_d = (adv_pos[0] + 1, adv_pos[1])
        adv_neighbor_l = (adv_pos[0], adv_pos[1] - 1)

        bad_list = []
        for move in sorted_list:
            pos = move[0]
            dir = move[1]
            copy_board = copy.deepcopy(chess_board)
            copy_board[pos[0], pos[1], dir] = True
            copy_board = self.add_neigbour_barrier(copy_board, pos, dir)
            flag, s1, s2 = self.terminate(copy_board, pos, adv_pos)
            if flag and s1 > s2:
                print("good good")
                return move
            if flag and s1 < s2:
                print("bad bad")
                bad_list.append(move)

        for move in sorted_list:
            pos = move[0]
            if pos == adv_neighbor_u and not chess_board[pos[0], pos[1], 2]:
                if (pos, self.dir_map["d"]) not in bad_list:
                    return pos, self.dir_map["d"]
            if pos == adv_neighbor_r and not chess_board[pos[0], pos[1], 3]:
                if (pos, self.dir_map["l"]) not in bad_list:
                    return pos, self.dir_map["l"]
            if pos == adv_neighbor_d and not chess_board[pos[0], pos[1], 0]:
                if (pos, self.dir_map["u"]) not in bad_list:
                    return pos, self.dir_map["u"]
            if pos == adv_neighbor_l and not chess_board[pos[0], pos[1], 1]:
                if (pos, self.dir_map["r"]) not in bad_list:
                    return pos, self.dir_map["r"]

        for move in sorted_list:
            if move not in bad_list:
                return move

        safe_move = self.safe_pos(move_list, chess_board)[0]
        return safe_move

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
        return not (p0_r == p1_r), my_area, adv_area
