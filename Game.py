from Round import Round


class Game:
    def __init__(self, server, max_score=100,
                 pass_dirs=('left', 'right', 'across', 'hold')):
        self.server = server
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
            rnd = Round(self.server, self.pass_dirs[self.pass_dir_num])
            rnd.play()
            for i in range(self.num_players):
                self.scores[i] += rnd.scores[i]
            self.server.broadcast(self.get_scores_str())
            self.round_num += 1
            self.pass_dir_num = (self.pass_dir_num + 1) % len(self.pass_dirs)