from math import ceil
import threading
from time import time

class Timer:
    def __init__(self, server):
        self.server = server
        self.times = [0]*4
        self.player_num = None
        self.last_checkpoint = None
        self.tick_timer = None

    def stop(self):
        self.update_time()
        self.player_num = None

    def reset_tick_timer(self):
        if self.tick_timer is not None:
            self.tick_timer.cancel()
        self.tick_timer = threading.Timer(1 - time() + self.last_checkpoint,
                                          self.tick)
        self.tick_timer.start()

    def set_player(self, new_player_num):
        self.update_time()
        self.player_num = new_player_num
        self.reset_tick_timer()

    def tick(self):
        if self.player_num is not None:
            self.update_time()
            self.server.broadcast('k:' + self.server.usernames[self.player_num]
                                  + ' ' + str(int(self.times[self.player_num])))
            self.reset_tick_timer()

    def update_time(self):
        new_checkpoint = time()
        if self.player_num is not None:
            self.times[self.player_num] += new_checkpoint - self.last_checkpoint
        self.last_checkpoint = new_checkpoint
