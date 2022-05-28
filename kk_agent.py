# Student agent: Add your own agent here

from agents.agent import Agent
from store import register_agent
import sys
import numpy as np
import copy
# import time


@register_agent("kk_agent")
class KKAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(KKAgent, self).__init__()
        self.name = "kkAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.autoplay = True

    # the 3 function is to find all valid position
    def can_move(self, chess_board, my_pos, dir):
        if not chess_board[my_pos[0], my_pos[1], self.dir_map[dir]]:
            return True
        else:
            return False

    def has_n_barrier(self, chess_board, cur_pos):
        return sum(chess_board[cur_pos[0], cur_pos[1]])

    def get_valid_pos(self, chess_board, max_step, my_pos, adv_pos):
        valid_pos_list = [my_pos]
        check_list = [my_pos]
        cur_step = 1
        direction = ["u", "r", "d", "l"]
        while cur_step <= max_step:
            next_check = []
            for pos in check_list:
                if self.can_move(chess_board, pos, "u"):
                    next_pos = (pos[0] - 1, pos[1])
                    if next_pos != adv_pos and next_pos not in valid_pos_list and self.has_n_barrier(chess_board, next_pos) < 3:
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

                if self.can_move(chess_board, pos, "r"):
                    next_pos = (pos[0], pos[1] + 1)
                    if next_pos != adv_pos and next_pos not in valid_pos_list and self.has_n_barrier(chess_board, next_pos) < 3:
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

                if self.can_move(chess_board, pos, "d"):
                    next_pos = (pos[0] + 1, pos[1])
                    if next_pos != adv_pos and next_pos not in valid_pos_list and self.has_n_barrier(chess_board, next_pos) < 3:
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

                if self.can_move(chess_board, pos, "l"):
                    next_pos = (pos[0], pos[1] - 1)
                    if next_pos != adv_pos and next_pos not in valid_pos_list and self.has_n_barrier(chess_board, next_pos) < 3:
                        valid_pos_list.append(next_pos)
                        next_check.append(next_pos)

            cur_step += 1
            check_list = next_check

        return valid_pos_list

    # use A* to arrange all possible next_pos
    def sort_valid_positions(self, pos_list, adv_pos, chess_board):
        pos_dic = {}
        for pos in pos_list:
            diff_x = abs(pos[0]-adv_pos[0])
            diff_y = abs(pos[1]-adv_pos[1])
            dist = diff_x + diff_y
            pos_dic[pos] = dist + 2*sum(chess_board[pos[0], pos[1]])
            # pos_dic[pos] = sum(chess_board[pos[0]][pos[1]])
        # sort value from low to high
        return dict(sorted(pos_dic.items(), key=lambda item: item[1]))

    # def get_mean_expected(self, pos_list, chess_board):
    #     total = 0
    #     for pos in pos_list:
    #         total += sum(chess_board[pos[0]][pos[1]])
    #     return total/len(pos_list)

    # def deepcopy_chessboard(self, chess_board):
    #     copy_board = []
    #     for xs in chess_board:
    #         copy_ys = []
    #         for ys in xs:
    #             copy_barrier = []
    #             for barrier in ys:
    #                 copy_barrier.append(barrier)
    #             copy_ys.append(copy_barrier)
    #         copy_board.append(copy_ys)
    #     return np.array(copy_board)

    def safe_pos(self, pos_list, chess_board):
        min_barrier = 4
        opt_pos = ()
        for pos in pos_list:
            if self.has_n_barrier(chess_board, pos) < min_barrier:
                min_barrier = self.has_n_barrier(chess_board, pos)
                opt_pos = pos
        return opt_pos

    # def valid_pos(self, chess_board, max_step, my_pos, adv_pos):
    #     # BFS
    #     moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
    #     state_queue = [(my_pos, 0)]
    #     visited = {tuple(my_pos)}
    #     while state_queue:
    #         cur_pos, cur_step = state_queue.pop(0)
    #         r, c = cur_pos
    #         if cur_step == max_step:
    #             break
    #         for dir, move in enumerate(moves):
    #             if chess_board[r, c, dir]:
    #                 continue
    #             next_pos = tuple(map(lambda i, j: i + j, cur_pos, move))
    #             if np.array_equal(next_pos, adv_pos) or tuple(next_pos) in visited:
    #                 continue
    #             visited.add(tuple(next_pos))
    #             state_queue.append((next_pos, cur_step + 1))
    #     return visited

    def check_same(self, l1, l2):
        for i in l1:
            if i not in l2:
                return False
        return True

    def step(self, chess_board, my_pos, adv_pos, max_step):
        valid_pos_list = self.get_valid_pos(chess_board, max_step, my_pos, adv_pos)
        pos_dic = self.sort_valid_positions(valid_pos_list, adv_pos, chess_board)
        sorted_list = list(pos_dic.keys())

        adv_neighbor_u = (adv_pos[0] - 1, adv_pos[1])
        adv_neighbor_r = (adv_pos[0], adv_pos[1] + 1)
        adv_neighbor_d = (adv_pos[0] + 1, adv_pos[1])
        adv_neighbor_l = (adv_pos[0], adv_pos[1] - 1)

        # check if we could end the game with higher score
        bad_list = []
        # print(sorted_list)
        for pos in sorted_list:
            for dir in range(4):
                copy_board = copy.deepcopy(chess_board)
                copy_board[pos[0], pos[1], dir] = True
                flag, s1, s2 = self.terminate(copy_board, pos, adv_pos)
                if flag:
                    if s1 < s2:
                        bad_list.append((pos, dir))
                    else:
                        return pos, dir

        # keep track
        for pos in sorted_list:
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

        for pos in sorted_list:
            for i in range(4):
                if not chess_board[pos[0], pos[1], i]:
                    opt_move = (pos, i)
                    if opt_move not in bad_list:
                        return pos, i

        dir = 0
        safe_pos = self.safe_pos(valid_pos_list, chess_board)
        for i in range(4):
            if not chess_board[safe_pos[0], safe_pos[1], i]:
                dir = i
        return safe_pos, dir

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
