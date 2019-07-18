import csv
import datetime

class Logger:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
        with open(self.timestamp + '-round.csv', 'w', newline='') as f:
            csv.writer(f).writerow(['round_num', 'pass_dir', 'player',
                                    'round_score', 'cum_score'])
        with open(self.timestamp + '-pass.csv', 'a', newline='') as f:
            csv.writer(f).writerow(['round_num', 'pass_dir', 'from_player',
                                    'to_player', 'card'])
        with open(self.timestamp + '-play.csv', 'a', newline='') as f:
            csv.writer(f).writerow(['round_num', 'trick_num',
                                    'card_num_in_trick', 'player', 'card'])

    def log_round(self, round_num, pass_dir, player, round_score, cum_score):
        with open(self.timestamp + '-round.csv', 'a', newline='') as f:
            csv.writer(f).writerow([round_num, pass_dir, player, round_score,
                                    cum_score])

    def log_pass(self, round_num, pass_dir, from_player, to_player, card):
        with open(self.timestamp + '-pass.csv', 'a', newline='') as f:
            csv.writer(f).writerow([round_num, pass_dir, from_player,
                                    to_player, card])

    def log_play(self, round_num, trick_num, card_num_in_trick, player, card):
        with open(self.timestamp + '-play.csv', 'a', newline='') as f:
            csv.writer(f).writerow([round_num, trick_num, card_num_in_trick,
                                    player, card])
