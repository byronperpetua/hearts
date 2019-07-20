from Logger import Logger
from Round import Round
from Timer import Timer

class Game:
    def __init__(self, server, max_score=100,
                 pass_dirs=('left', 'right', 'across', 'hold')):
        self.server = server
        self.logger = Logger()
        self.timer = Timer(server)
        self.num_players = len(server.usernames)
        self.scores = [0] * self.num_players
        self.max_score = max_score
        self.round_num = 1
        self.pass_dirs = pass_dirs
        self.pass_dir_num = 0

    def get_scores_str(self):
        s = 's:'
        for i in range(self.num_players):
            s += self.server.usernames[i] + ' ' + str(self.scores[i]) + ' '
        return s

    def play(self):
        while max(self.scores) < self.max_score:
            pass_dir = self.pass_dirs[self.pass_dir_num]
            self.curr_round = Round(self, pass_dir)
            self.curr_round.play()
            for i in range(self.num_players):
                self.scores[i] += self.curr_round.scores[i]
                self.logger.log_round(
                    round_num=self.round_num,
                    pass_dir=pass_dir,
                    player=self.server.usernames[i],
                    round_score=self.curr_round.scores[i],
                    cum_score=self.scores[i])
            self.server.broadcast(self.get_scores_str())
            self.round_num += 1
            self.pass_dir_num = (self.pass_dir_num + 1) % len(self.pass_dirs)

    def set_pass_dir(self, dir):
        self.pass_dir_num = self.pass_dirs.index(dir)
        self.curr_round.pass_dir = dir

    def set_score(self, player_num, score):
        self.scores[player_num] = score
        self.server.broadcast(self.get_scores_str())
