from functools import partial
from os import listdir
from os.path import dirname
from queue import Queue
from Server import Server
import sys
import tkinter as tk
from threading import Thread
from time import sleep

class GUI:
    def __init__(self, client):
        self.window = tk.Tk()
        self.client = client
        self.queue = Queue()
        self.selected = []
        self.round_scores = None
        self.current_trick = [None] * 4
        self.last_trick = [None] * 4
        self.lockout = False
        self.bg_color = '#104010'
        self.fg_color = '#e0e0e0'
        self.fg_color2 = '#608060'
        self.hl_color = '#5080c0'
        if getattr(sys, 'frozen', False):
            self.image_dir = sys._MEIPASS + '/images/'
        else:
            self.image_dir = dirname(__file__) + '/images/'
        self.setup_gui()
        self.set_mode('wait')
        self.poll_loop()
        self.window.mainloop()

    def add_to_queue(self, msg):
        self.queue.put(msg)

    def connect_popup(self):
        def enable_ip():
            ip_entry.configure(state='normal')
        def disable_ip():
            ip_entry.configure(state='disabled')
        def connect(event):
            name = username.get()
            if name and (' ' not in name) and (is_server.get() or ip.get()):
                self.window.title('Hearts - ' + name)
                if is_server.get():
                    server = Server()
                    Thread(target=server.start_game).start()
                    self.client.connect(name, '127.0.0.1')
                else:
                    self.client.connect(name, ip.get())
                Thread(target=self.client.loop, args=(self,)).start()
                Thread(target=self.client.chat_loop, args=(self,)).start()
                popup.destroy()
        popup = tk.Toplevel(self.window)
        popup.title('Connect')
        popup.protocol('WM_DELETE_WINDOW', lambda: None)
        popup.attributes('-topmost', True)
        popup.resizable(False, False)
        popup.grab_set()
        is_server = tk.IntVar()
        username = tk.StringVar()
        ip = tk.StringVar()
        tk.Radiobutton(popup, text='Client', variable=is_server, value=0,
                       command=enable_ip).grid(row=0, column=0)
        tk.Radiobutton(popup, text='Server', variable=is_server, value=1,
                       command=disable_ip).grid(row=0, column=1)
        tk.Label(popup, text='Name (no spaces):').grid(row=1, column=0)
        username_entry = tk.Entry(popup, textvariable=username)
        username_entry.grid(row=1, column=1)
        username_entry.bind('<Return>', connect)
        tk.Label(popup, text='Server IP:').grid(row=2, column=0)
        ip_entry = tk.Entry(popup, textvariable=ip)
        ip_entry.grid(row=2, column=1)
        ip_entry.bind('<Return>', connect)
        button = tk.Button(popup, text='Connect', command=lambda: connect(None))
        button.grid(row=3, column=1)

    def disable_button(self, button):
        button.configure(state='disabled')

    def enable_button(self, button):
        button.configure(state='normal')

    def end_trick(self, winner_username, delay_ms=1500):
        def clear_cards():
            for c in self.card_labels:
                c.configure(image=self.images['blank'])
            self.lockout = False
        self.lockout = True
        winner_num = self.usernames.index(winner_username)
        self.highlight_label(self.username_labels[winner_num])
        self.window.after(delay_ms, clear_cards)
        self.last_trick = self.current_trick.copy()

    def flash_cards(self, cards):
        for c in cards:
            button = self.card_buttons[self.hand.index(c)]
            self.flash(button, self.highlight_button, self.unhighlight_button)

    def flash(self, element, highlight_fn, unhighlight_fn, delay_ms=2000):
        highlight_fn(element)
        self.window.after(delay_ms, unhighlight_fn, element)

    def highlight_button(self, button):
        # First one only works on Mac, second one only works on Windows
        button.configure(highlightbackground=self.hl_color)
        button.configure(background=self.hl_color)

    def highlight_label(self, button):
        button.configure(background=self.hl_color)

    def highlight_username_labels(self):
        for l in self.username_labels:
            self.highlight_label(l)

    def last_trick_popup(self):
        popup = tk.Toplevel(self.window)
        popup.attributes('-topmost', True)
        popup.title('Last trick')
        popup.resizable(False, False)
        popup.grab_set()
        tk.Label(popup, image=self.images[self.last_trick[0]]).grid(row=2,
                                                                    column=1)
        tk.Label(popup, image=self.images[self.last_trick[1]]).grid(row=1,
                                                                    column=0)
        tk.Label(popup, image=self.images[self.last_trick[2]]).grid(row=0,
                                                                    column=1)
        tk.Label(popup, image=self.images[self.last_trick[3]]).grid(row=1,
                                                                    column=2)
        tk.Button(popup, text='Close', command=popup.destroy).grid(
            row=1, column=1, sticky='nsew')

    def moonshot_popup(self):
        popup = tk.Toplevel(self.window)
        popup.protocol('WM_DELETE_WINDOW', lambda: None)
        popup.attributes('-topmost', True)
        popup.resizable(False, False)
        popup.grab_set()
        tk.Label(popup, text='Add or subtract?').grid(row=0)
        def add():
            self.client.send('a')
            popup.destroy()
        def sub():
            self.client.send('s')
            popup.destroy()
        tk.Button(popup, text='Add', command=add).grid(row=1, column=0)
        tk.Button(popup, text='Subtract', command=sub).grid(row=1, column=1)

    def on_card_click(self, card_num):
        if self.mode == 'pass':
            if card_num in self.selected:
                self.selected.remove(card_num)
                self.unhighlight_button(self.card_buttons[card_num])
                self.submit_button.configure(state='disabled')
            elif len(self.selected) < 3:
                self.selected.append(card_num)
                self.highlight_button(self.card_buttons[card_num])
                if len(self.selected) == 3:
                    self.submit_button.configure(state='normal')
        elif self.mode == 'play' and not self.lockout:
            if card_num < len(self.hand):
                self.client.send(self.hand[card_num])
                self.set_mode('wait')

    def on_chat_enter(self, event):
        self.client.send_chat(self.chat_input.get())
        self.chat_input.delete(0, 'end')

    def on_last_trick_click(self):
        if self.last_trick[0] is not None:
            self.last_trick_popup()
            
    def on_round_scores_click(self):
        if self.round_scores is not None:
            self.round_scores_popup()

    def on_submit_click(self):
        if self.mode == 'pass' and len(self.selected) == 3:
            self.set_mode('wait')
            self.client.send(' '.join([self.hand[i] for i in self.selected]))
            self.selected = []

    def poll_loop(self, delay_ms=50):
        if not self.queue.empty():
            msg = self.queue.get()
            msg_type = msg[:2]
            msg_data = msg[2:].split()
            if msg_type.startswith('h:'): # hand to set 
                self.set_hand(msg_data)
            elif msg_type.startswith('p:'): # pass received
                self.flash_cards(msg_data)
            elif msg_type.startswith('c:'): # card played
                self.show_card(msg_data[0], msg_data[1])
            elif msg_type.startswith('s:'): # scores
                self.set_scores(msg_data)
            elif msg_type.startswith('t:'): # trick winner
                self.end_trick(msg_data[0])
            elif msg_type.startswith('u:'): # usernames
                self.set_usernames(msg_data)
            elif msg_type.startswith('k:'): # player and time elapsed
                self.show_time(msg_data[0], msg_data[1])
            elif msg_type.startswith('z:'): # sender and chat message
                self.show_chat(msg_data[0], ' '.join(msg_data[1:]))
            elif msg_type.startswith('i:'): # info for status bar
                self.status_bar.configure(text=' '.join(msg_data))
            elif msg_type.startswith('g:'): # player has submitted pass
                player_num = self.usernames.index(msg_data[0])
                self.unhighlight_label(self.username_labels[player_num])
            elif msg_type.startswith('p?'): # request pass
                self.set_mode('pass')
            elif msg_type.startswith('c?'): # request card to play
                self.set_mode('play')
            elif msg_type.startswith('a?'): # request add or subtract
                self.moonshot_popup()
        self.window.after(delay_ms, self.poll_loop)
        
    def round_scores_popup(self):
        popup = tk.Toplevel(self.window)
        popup.attributes('-topmost', True)
        popup.title('Round scores')
        popup.resizable(False, False)
        popup.grab_set()
        tk.Label(popup, text=self.round_scores, font=('Courier', 14)).grid(
            row=0, column=0)
        tk.Button(popup, text='Close', command=popup.destroy).grid(
            row=1, column=0, sticky='ew')
    
    def set_hand(self, cards):
        self.hand = cards
        for i in range(13):
            if i < len(self.hand):
                img = self.images[self.hand[i]]
            else:
                img = self.images['blank']
            self.card_buttons[i].configure(image=img)

    def set_mode(self, new_mode, short_delay_ms=1,
                 pass_highlight_delay_ms=1000):
        self.mode = new_mode
        if new_mode == 'wait':
            for b in self.card_buttons:
                # Ideally, disable all buttons, but the button just clicked
                # refuses to disable if we do.
                self.unhighlight_button(b)
            self.submit_button.configure(highlightbackground=self.bg_color,
                                         background=self.fg_color)
            self.window.after(short_delay_ms, self.disable_button,
                              self.submit_button)
        elif new_mode == 'pass':
            for b in self.card_buttons:
                self.enable_button(b)
                self.unhighlight_button(b)
            self.highlight_button(self.submit_button)
            self.window.after(pass_highlight_delay_ms,
                              self.highlight_username_labels)
            self.window.after(short_delay_ms, self.disable_button,
                              self.submit_button)
        elif new_mode == 'play':
            for b in self.card_buttons:
                self.enable_button(b)
            self.highlight_label(self.username_labels[0])
            self.window.after(short_delay_ms, self.disable_button,
                              self.submit_button)

    def set_scores(self, score_data, delay_ms=1500):
        score_strs = [None]*4
        for i in range(0, 8, 2):
            player_num = self.usernames.index(score_data[i])
            self.score_labels[player_num].configure(text=score_data[i+1])
            score_strs[player_num] = score_data[i+1]
        self.round_scores += '\n' + '  '.join([s + ' '*(8-len(s)) 
                                               for s in score_strs])
        self.window.after(delay_ms, self.unhighlight_last_trick_winner)           

    def set_usernames(self, usernames):
        self.usernames = usernames
        for i in range(len(self.usernames)):
            self.username_labels[i].configure(text=self.usernames[i])
        self.round_scores = '  '.join([u[:8] + ' '*(8-len(u))
                                       for u in self.usernames])

    def setup_chat_window(self):
        self.chat_window = tk.Toplevel(self.window)
        self.chat_window.title('Chat')
        self.chat_window.protocol('WM_DELETE_WINDOW', lambda: None)
        self.chat_display = tk.Text(self.chat_window, state='disabled',
                                    font=('Arial', 12), width=40,
                                    borderwidth=0, wrap=tk.WORD)
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        self.chat_display.tag_config('bold', font=('Arial', 12, 'bold'))
        self.chat_input = tk.Entry(self.chat_window, font=('Arial', 12),
                                   width=40)
        self.chat_input.grid(row=1, column=0, sticky='nsew')
        self.chat_input.bind('<Return>', self.on_chat_enter)
        self.chat_window.columnconfigure(0, weight=1)
        self.chat_window.rowconfigure(0, weight=1)

    def setup_gui(self):
        self.window.title('Hearts')
        self.window.configure(bg=self.bg_color)
        self.window.resizable(False, False)
        self.images = {}
        for f in listdir(self.image_dir):
            if f[-4:] == '.png':
                self.images[f[:-4]] = tk.PhotoImage(file=self.image_dir+f)
        self.username_labels = [None]*4
        self.time_labels = [None]*4
        self.score_labels = [None]*4
        self.card_labels = [None]*4
        self.card_buttons = []
        self.username_labels[0] = tk.Label(
            self.window, text='', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[0].grid(row=9, column=5, columnspan=3, sticky='s')
        self.score_labels[0] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[0].grid(row=10, column=6)
        self.time_labels[0] = tk.Label(
            self.window, text='0:00', bg=self.bg_color, fg=self.fg_color2)
        self.time_labels[0].grid(row=11, column=6, sticky='n')
        self.card_labels[0] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[0].grid(row=8, column=6)
        self.username_labels[1] = tk.Label(
            self.window, text='', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[1].grid(row=4, column=2, columnspan=2, sticky='se')
        self.score_labels[1] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[1].grid(row=5, column=3, sticky='e')
        self.time_labels[1] = tk.Label(
            self.window, text='0:00', bg=self.bg_color, fg=self.fg_color2)
        self.time_labels[1].grid(row=6, column=3, sticky='ne')
        self.card_labels[1] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[1].grid(row=4, column=4, rowspan=3)
        self.username_labels[2] = tk.Label(
            self.window, text='', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[2].grid(row=0, column=5, columnspan=3, sticky='s')
        self.score_labels[2] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[2].grid(row=1, column=6)
        self.time_labels[2] = tk.Label(
            self.window, text='0:00', bg=self.bg_color, fg=self.fg_color2)
        self.time_labels[2].grid(row=2, column=6, sticky='n')
        self.card_labels[2] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[2].grid(row=3, column=6)
        self.username_labels[3] = tk.Label(
            self.window, text='', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[3].grid(row=4, column=9, columnspan=2, sticky='sw')
        self.score_labels[3] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[3].grid(row=5, column=9, sticky='w')
        self.time_labels[3] = tk.Label(
            self.window, text='0:00', bg=self.bg_color, fg=self.fg_color2)
        self.time_labels[3].grid(row=6, column=9, sticky='nw')
        self.card_labels[3] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[3].grid(row=4, column=8, rowspan=3)
        for i in range(13):
            self.card_buttons.append(tk.Button(
                self.window, image=self.images['blank'],
                command=partial(self.on_card_click, i),
                highlightthickness=5, highlightbackground=self.bg_color))
            self.card_buttons[i].grid(row=12, column=i)
        self.submit_button = tk.Button(
            self.window, text='Submit\nPass', command=self.on_submit_click,
            state='disabled', highlightthickness=5)
        self.submit_button.grid(row=10, column=12, rowspan=2, sticky='ew')
        self.last_trick_button = tk.Button(
            self.window, command=self.on_last_trick_click, text='Last Trick',
            highlightbackground=self.bg_color)
        self.last_trick_button.grid(row=0, column=12, rowspan=1, sticky='ew')
        self.round_scores_button = tk.Button(
            self.window, command=self.on_round_scores_click, text='Scores',
            highlightbackground=self.bg_color)
        self.round_scores_button.grid(row=1, column=12, rowspan=1, sticky='ew')
        self.status_bar = tk.Label(self.window, text='', bg=self.bg_color,
                                   fg=self.fg_color)
        self.status_bar.grid(row=0, column=0, columnspan=6, sticky='w', padx=5)
        self.setup_chat_window()
        self.connect_popup()

    def show_card(self, username, card):
        player_num = self.usernames.index(username)
        # Save trick in order to show last trick later
        self.current_trick[player_num] = card
        self.card_labels[player_num].configure(image=self.images[card])
        self.unhighlight_username_labels()

    def show_chat(self, username, text):
        self.chat_display.config(state='normal')
        self.chat_display.insert('end', username + ': ', 'bold')
        self.chat_display.insert('end', text + '\n')
        self.chat_display.see('end')
        self.chat_display.config(state='disabled')

    def show_time(self, username, seconds_str):
        seconds = int(seconds_str)
        time_str = '{}:{:0>2d}'.format(seconds // 60, seconds % 60)
        self.time_labels[self.usernames.index(username)].configure(
            text=time_str)

    def unhighlight_button(self, button):
        button.configure(highlightbackground=self.bg_color)
        button.configure(background=self.bg_color)

    def unhighlight_label(self, label):
        label.configure(background=self.bg_color)

    def unhighlight_username_labels(self, exclude_self_on_turn=False):
        for l in self.username_labels:
            self.unhighlight_label(l)

    # Unhighlight last trick winner while preserving highlighting for next hand
    def unhighlight_last_trick_winner(self):
        if self.mode == 'play':
            for i in range(1, 4):
                self.unhighlight_label(self.username_labels[i])
        elif self.mode == 'wait':
            for i in range(0, 4):
                self.unhighlight_label(self.username_labels[i])
        # if mode is 'pass', labels are appropriately highlighted; do nothing