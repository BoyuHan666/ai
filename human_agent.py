# Human Input agent
from agents.agent import Agent
from store import register_agent
import sys


@register_agent("human_agent")
class HumanAgent(Agent):
    def __init__(self):
        super(HumanAgent, self).__init__()
        self.name = "HumanAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    # def can_move(self, chess_board, my_pos, dir):
    #     if not chess_board[my_pos[0]][my_pos[1]][self.dir_map[dir]]:
    #         return True
    #     else:
    #         return False
    #
    # def get_valid_pos(self, chess_board, max_step, my_pos, adv_pos):
    #     valid_pos_list = [my_pos]
    #     check_list = [my_pos]
    #     cur_step = 1
    #     while cur_step <= max_step:
    #         next_check = []
    #         for pos in check_list:
    #             if self.can_move(chess_board, pos, "u"):
    #                 next_pos = (pos[0]-1, pos[1])
    #                 if next_pos != adv_pos and next_pos not in valid_pos_list:
    #                     valid_pos_list.append(next_pos)
    #                     next_check.append(next_pos)
    #
    #             if self.can_move(chess_board, pos, "r"):
    #                 next_pos = (pos[0], pos[1]+1)
    #                 if next_pos != adv_pos and next_pos not in valid_pos_list:
    #                     valid_pos_list.append(next_pos)
    #                     next_check.append(next_pos)
    #
    #             if self.can_move(chess_board, pos, "d"):
    #                 next_pos = (pos[0]+1, pos[1])
    #                 if next_pos != adv_pos and next_pos not in valid_pos_list:
    #                     valid_pos_list.append(next_pos)
    #                     next_check.append(next_pos)
    #
    #             if self.can_move(chess_board, pos, "l"):
    #                 next_pos = (pos[0], pos[1]-1)
    #                 if next_pos != adv_pos and next_pos not in valid_pos_list:
    #                     valid_pos_list.append(next_pos)
    #                     next_check.append(next_pos)
    #
    #         cur_step += 1
    #         check_list = next_check
    #
    #     return valid_pos_list

    def step(self, chess_board, my_pos, adv_pos, max_step):
        # valid_pos_list = self.get_valid_pos(chess_board, max_step, my_pos, adv_pos)
        # print(len(valid_pos_list))
        # print("valid_pos_list is shown as follow:")
        # print(valid_pos_list)

        text = input("Your move (x,y,dir) or input q to quit: ")
        while len(text.split(",")) != 3 and "q" not in text.lower():
            print("Wrong Input Format!")
            text = input("Your move (x,y,dir) or input q to quit: ")
        if "q" in text.lower():
            print("Game ended by user!")
            sys.exit(0)
        x, y, dir = text.split(",")
        x, y, dir = x.strip(), y.strip(), dir.strip()
        x, y = int(x), int(y)
        while not self.check_valid_input(
            x, y, dir, chess_board.shape[0], chess_board.shape[1]
        ):
            print(
                "Invalid Move! (x, y) should be within the board and dir should be one of u,r,d,l."
            )
            text = input("Your move (x,y,dir) or input q to quit: ")
            while len(text.split(",")) != 3 and "q" not in text.lower():
                print("Wrong Input Format!")
                text = input("Your move (x,y,dir) or input q to quit: ")
            if "q" in text.lower():
                print("Game ended by user!")
                sys.exit(0)
            x, y, dir = text.split(",")
            x, y, dir = x.strip(), y.strip(), dir.strip()
            x, y = int(x), int(y)
        my_pos = (x, y)

        return my_pos, self.dir_map[dir]

    def check_valid_input(self, x, y, dir, x_max, y_max):
        return 0 <= x < x_max and 0 <= y < y_max and dir in self.dir_map
