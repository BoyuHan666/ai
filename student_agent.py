# Student agent: Add your own agent here
import random

from agents.agent import Agent
from store import register_agent
import sys
import time


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
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
            return (my_pos[0] - 1, my_pos[1]), 2
        if dir == 1:
            return (my_pos[0], my_pos[1] + 1), 3
        if dir == 2:
            return (my_pos[0] + 1, my_pos[1]), 0
        if dir == 3:
            return (my_pos[0], my_pos[1] - 1), 1

    def search(self, par, p):
        if par[p] != p:
            par[p] = self.search(par, par[p])
        return par[p]

    def check_not_reachable(self, chess_board, my_pos, adv_pos):
        size = 4 * len(chess_board)
        valid_pos_list = [my_pos]
        check_list = [my_pos]
        cur_step = 1
        while cur_step <= size:
            next_check = []
            for pos in check_list:
                for dir in range(4):
                    if self.can_move(chess_board, pos, dir):
                        next_pos = self.get_neighbours(pos, dir)[0]
                        if next_pos == adv_pos:
                            return False
                        if next_pos not in valid_pos_list:
                            valid_pos_list.append(next_pos)
                            next_check.append(next_pos)
            cur_step += 1
            check_list = next_check

        return True

    def check_score(self, chess_board, pos1, pos2):
        size = 4 * len(chess_board)
        pos_list = [pos1]
        check_list = [pos1]

        pos_list2 = [pos2]
        check_list2 = [pos2]
        cur_step = 1
        while cur_step < size:
            next_check = []
            next_check2 = []
            for p in check_list:
                for dir in range(4):
                    if self.can_move(chess_board, p, dir):
                        next_pos = self.get_neighbours(p, dir)[0]
                        if next_pos == pos2:
                            return False, 0, 0
                        if next_pos not in pos_list:
                            pos_list.append(next_pos)
                            next_check.append(next_pos)

            for p2 in check_list2:
                for dir2 in range(4):
                    if self.can_move(chess_board, p2, dir2):
                        next_pos2 = self.get_neighbours(p2, dir2)[0]
                        if next_pos2 == pos1:
                            return False, 0, 0
                        if next_pos2 not in pos_list2:
                            pos_list2.append(next_pos2)
                            next_check2.append(next_pos2)

            cur_score = len(pos_list)
            cur_score2 = len(pos_list2)
            if cur_score == size or cur_score2 == size:
                break

            cur_step += 1
            check_list = next_check
            check_list2 = next_check2

        return True, len(pos_list), len(pos_list2)

    def find_num_new_barriers(self, chess_board, max_step):
        size = len(chess_board)
        total = 0
        for i in range(size):
            for j in range(size):
                total += sum(chess_board[i, j])
        return (total - 4 * size - 4 * max_step) // 2

    def terminate(self, chess_board, my_pos, adv_pos):
        par = {}
        size = chess_board.shape[0]
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        for x in range(size):
            for y in range(size):
                par[(x, y)] = (x, y)

        for x in range(size):
            for y in range(size):
                for dir, move in enumerate(moves[1:3]):
                    if not chess_board[x, y, dir + 1] and (self.search(par, (x, y)) != self.search(par, (x + move[0], y + move[1]))):
                        par[self.search(par, (x, y))] = self.search(par, (x + move[0], y + move[1]))

        for x in range(size):
            for y in range(size):
                self.search(par, (x, y))

        my_area = list(par.values()).count(self.search(par, my_pos))
        adv_area = list(par.values()).count(self.search(par, adv_pos))
        if self.search(par, my_pos) == self.search(par, adv_pos):
            return False, my_area, adv_area

        return True, my_area, adv_area

    def step(self, chess_board, my_pos, adv_pos, max_step):
        size = len(chess_board)
        start = time.time()
        # print(size)
        cur_round_num = self.find_num_new_barriers(chess_board, max_step)
        move_list = self.get_valid_pos(chess_board, my_pos, adv_pos, max_step, 3)
        if cur_round_num < size:
            sort_list = list(self.sort_valid_positions(move_list, adv_pos, chess_board, 1, 3).keys())
        else:
            sort_list = list(self.sort_valid_positions(move_list, adv_pos, chess_board, 1, 2).keys())
        random_move = move_list[random.randint(0, len(move_list) - 1)]
        bad_move_list = []

        for move in sort_list:
            next_my_pos = move[0]
            next_my_dir = move[1]
            next_my_neighbour = self.get_neighbours(next_my_pos, next_my_dir)
            next_my_neighbour_pos = next_my_neighbour[0]
            next_my_neighbour_dir = next_my_neighbour[1]
            chess_board[next_my_pos[0], next_my_pos[1], next_my_dir] = True
            chess_board[next_my_neighbour_pos[0], next_my_neighbour_pos[1], next_my_neighbour_dir] = True
            not_reachable = self.check_not_reachable(chess_board, next_my_pos, adv_pos)
            if not_reachable:
                _, s1, s2 = self.terminate(chess_board, next_my_pos, adv_pos)
                if s1 >= s2:
                    return move
                else:
                    bad_move_list.append(move)
            else:
                if cur_round_num > max_step * 4 or (size < 11 and cur_round_num > max_step * 2) or (size < 9):
                    adv_move_list = self.get_valid_pos(chess_board, adv_pos, my_pos, max_step, 3)
                    if time.time() - start > 1.9:
                        continue
                    if time.time() - start > 1.8 and len(adv_move_list) > 40:
                        adv_move_list = adv_move_list[2:42]
                    if time.time() - start > 1.7 and len(adv_move_list) > 60:
                        adv_move_list = adv_move_list[2:62]
                    if time.time() - start > 1.6 and len(adv_move_list) > 80:
                        adv_move_list = adv_move_list[2:82]
                    if time.time() - start > 1.5 and len(adv_move_list) > 100:
                        adv_move_list = adv_move_list[2:102]

                    for adv_move in adv_move_list:
                        next_adv_pos = adv_move[0]
                        next_adv_dir = adv_move[1]
                        next_adv_neighbour = self.get_neighbours(next_adv_pos, next_adv_dir)
                        next_adv_neighbour_pos = next_adv_neighbour[0]
                        next_adv_neighbour_dir = next_adv_neighbour[1]
                        chess_board[next_adv_pos[0], next_adv_pos[1], next_adv_dir] = True
                        chess_board[next_adv_neighbour_pos[0], next_adv_neighbour_pos[1], next_adv_neighbour_dir] = True
                        not_reachable2 = self.check_not_reachable(chess_board, next_my_pos, next_adv_pos)
                        if not_reachable2:
                            flag2, s21, s22 = self.terminate(chess_board, next_my_pos, next_adv_pos)
                            if s21 < s22:
                                bad_move_list.append(move)

                        chess_board[next_adv_pos[0], next_adv_pos[1], next_adv_dir] = False
                        chess_board[
                            next_adv_neighbour_pos[0], next_adv_neighbour_pos[1], next_adv_neighbour_dir] = False

            chess_board[next_my_pos[0], next_my_pos[1], next_my_dir] = False
            chess_board[next_my_neighbour_pos[0], next_my_neighbour_pos[1], next_my_neighbour_dir] = False

        end = time.time()
        if end - start >= 2:
            print(cur_round_num)
            print(len(move_list))
            print("chess_board size is:" + str(size))
            print("overtime" + str(end - start))

        for move in sort_list:
            if move not in bad_move_list:
                return move
        return random_move
