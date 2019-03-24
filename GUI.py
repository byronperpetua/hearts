from os import listdir
import tkinter as tk
from threading import Thread
from time import sleep
from Server import Server

class GUI:
    def __init__(self, client):
        self.client = client
        self.msg = None
        self.selected = []
        self.lockout = False
        self.bg_color = 'dark green'
        self.fg_color = 'white'
        self.hl_color = 'dodger blue'
        self.setup_gui()
        self.set_mode('wait')

    def connect_popup(self):
        def enable_ip():
            ip_entry.configure(state='normal')
        def disable_ip():
            ip_entry.configure(state='disabled')
        def submit(event):
            if username.get() and (is_server.get() or ip.get()):
                self.window.title('Hearts - ' + username.get())
                if is_server.get():
                    server = Server()
                    Thread(target=server.start_game).start()
                self.client.connect(username.get(), ip.get())
                Thread(target=self.client.loop, args=(self,)).start()
                popup.destroy()
        popup = tk.Toplevel(self.window)
        popup.title('Connect')
        popup.protocol('WM_DELETE_WINDOW', lambda: None)
        popup.attributes('-topmost', True)
        is_server = tk.IntVar()
        username = tk.StringVar()
        ip = tk.StringVar()
        tk.Radiobutton(popup, text='Client', variable=is_server, value=0,
                       command=enable_ip).grid(row=0, column=0)
        tk.Radiobutton(popup, text='Server', variable=is_server, value=1,
                       command=disable_ip).grid(row=0, column=1)
        tk.Label(popup, text='Name:').grid(row=1, column=0)
        tk.Entry(popup, textvariable=username).grid(row=1, column=1)
        tk.Label(popup, text='Server IP:').grid(row=2, column=0)
        ip_entry = tk.Entry(popup, textvariable=ip)
        ip_entry.grid(row=2, column=1)
        button = tk.Button(popup, text='Submit')
        button.grid(row=3, column=1)
        button.bind('<ButtonRelease>', submit)

    def disable_button(self, button):
        button.configure(state='disabled')

    def end_trick(self, winner_username, delay_ms=2000):
        def clear_cards():
            for c in self.card_labels:
                c.configure(image=self.images['blank'])
            self.lockout = False
        self.lockout = True
        winner_num = self.usernames.index(winner_username)
        self.highlight_label(self.username_labels[winner_num])
        self.window.after(delay_ms, clear_cards)

    def flash_cards(self, cards):
        for c in cards:
            button = self.card_buttons[self.hand.index(c)]
            self.flash(button, self.highlight_button, self.unhighlight_button)

    def flash(self, element, highlight_fn, unhighlight_fn, delay_ms=2000):
        highlight_fn(element)
        element.after(delay_ms, unhighlight_fn, element)

    def highlight_button(self, button):
        button.configure(highlightbackground=self.hl_color)

    def highlight_label(self, button):
        button.configure(background=self.hl_color)

    def moonshot_popup(self):
        popup = tk.Toplevel(self.window)
        popup.protocol('WM_DELETE_WINDOW', lambda: None)
        popup.attributes('-topmost', True)
        tk.Label(popup, text='Add or subtract?').grid(row=0)
        def add(event):
            self.client.send('a')
            popup.destroy()
        def sub(event):
            self.client.send('s')
            popup.destroy()
        add_button = tk.Button(popup, text='Add')
        add_button.grid(row=1, column=0)
        add_button.bind('<ButtonRelease>', add)
        sub_button = tk.Button(popup, text='Subtract')
        sub_button.grid(row=1, column=1)
        sub_button.bind('<ButtonRelease>', sub)

    def on_card_click(self, event):
        button = event.widget
        card_num = self.card_buttons.index(button)
        if self.mode == 'pass':
            if card_num in self.selected:
                self.selected.remove(card_num)
                self.unhighlight_button(event.widget)
                self.submit_button.configure(state='disabled')
            elif len(self.selected) < 3:
                self.selected.append(card_num)
                self.highlight_button(event.widget)
                if len(self.selected) == 3:
                    self.submit_button.configure(state='normal')
        elif self.mode == 'play' and not self.lockout:
            self.set_mode('wait')
            self.client.send(self.hand[card_num])

    def on_submit_click(self, event):
        if self.mode == 'pass' and len(self.selected) == 3:
            self.set_mode('wait')
            self.client.send(' '.join([self.hand[i] for i in self.selected]))
            self.selected = []

    def poll_loop(self, delay_ms=50):
        if self.msg:
            msg_type = self.msg[:2]
            msg_data = self.msg[2:].split()
            if msg_type.startswith('h:'):
                self.set_hand(msg_data)
            elif msg_type.startswith('p:'):
                self.flash_cards(msg_data)
            elif msg_type.startswith('c:'): 
                self.show_card(msg_data[0], msg_data[1])
            elif msg_type.startswith('s:'):
                self.set_scores(msg_data)
            elif msg_type.startswith('t:'):
                self.end_trick(msg_data[0])
            elif msg_type.startswith('u:'):
                self.set_usernames(msg_data)
            elif msg_type.startswith('p?'):
                self.set_mode('pass')
            elif msg_type.startswith('c?'):
                self.set_mode('play')
            elif msg_type.startswith('a?'):
                self.moonshot_popup()
            self.msg = None
        self.window.after(delay_ms, self.poll_loop)
    
    def set_hand(self, cards):
        self.hand = cards
        for i in range(13):
            if i < len(self.hand):
                img = self.images[self.hand[i]]
            else:
                img = self.images['blank']
            self.card_buttons[i].configure(image=img)

    def set_mode(self, new_mode):
        self.mode = new_mode
        if new_mode == 'wait':
            for b in self.card_buttons:
                self.unhighlight_button(b)
            self.submit_button.configure(highlightbackground=self.bg_color)
            self.window.after(100, self.disable_button, self.submit_button)
        elif new_mode == 'pass':
            for b in self.card_buttons:
                self.unhighlight_button(b)
            self.submit_button.configure(highlightbackground=self.hl_color)
            self.window.after(100, self.disable_button, self.submit_button)
        elif new_mode == 'play':
            for b in self.card_buttons:
                self.unhighlight_button(b)
            self.window.after(100, self.disable_button, self.submit_button)

    def set_msg(self, msg):
        self.msg = msg

    def set_scores(self, score_data):
        for i in range(0, 8, 2):
            player_num = self.usernames.index(score_data[i])
            self.score_labels[player_num].configure(text=score_data[i+1])
        for l in self.username_labels:
            self.unhighlight_label(l)

    def set_usernames(self, usernames):
        self.usernames = usernames
        for i in range(len(self.usernames)):
            self.username_labels[i].configure(text=self.usernames[i])

    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title('Hearts')
        self.images = {}
        for f in listdir('images'):
            self.images[f[:-4]] = tk.PhotoImage(file='images/'+f)
        self.username_labels = [None]*4
        self.score_labels = [None]*4
        self.card_labels = [None]*4
        self.card_buttons = []
        self.username_labels[0] = tk.Label(
            self.window, text='bottom',bg=self.bg_color, fg=self.fg_color)
        self.username_labels[0].grid(row=7, column=6)
        self.score_labels[0] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[0].grid(row=8, column=6)
        self.card_labels[0] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[0].grid(row=6, column=6)
        self.username_labels[1] = tk.Label(
            self.window, text='left', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[1].grid(row=3, column=3)
        self.score_labels[1] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[1].grid(row=4, column=3)
        self.card_labels[1] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[1].grid(row=3, column=4, rowspan=2)
        self.username_labels[2] = tk.Label(
            self.window, text='top', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[2].grid(row=0, column=6)
        self.score_labels[2] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[2].grid(row=1, column=6)
        self.card_labels[2] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[2].grid(row=2, column=6)
        self.username_labels[3] = tk.Label(
            self.window, text='right', bg=self.bg_color, fg=self.fg_color)
        self.username_labels[3].grid(row=3, column=9)
        self.score_labels[3] = tk.Label(
            self.window, text='0', bg=self.bg_color, fg=self.fg_color)
        self.score_labels[3].grid(row=4, column=9)
        self.card_labels[3] = tk.Label(
            self.window, image=self.images['blank'], bg=self.bg_color,
            fg=self.fg_color)
        self.card_labels[3].grid(row=3, column=8, rowspan=2)
        for i in range(13):
            self.card_buttons.append(tk.Button(
                self.window, image=self.images['blank'],
                highlightthickness=5, highlightbackground=self.bg_color))
            self.card_buttons[i].grid(row=9, column=i)
            self.card_buttons[i].bind('<ButtonRelease>', self.on_card_click)
        self.submit_button = tk.Button(self.window, text='Submit\nPass',
                                       state='disabled', highlightthickness=5)
        self.submit_button.grid(row=9, column=13)
        self.submit_button.bind('<ButtonRelease>', self.on_submit_click)
        self.window.configure(bg=self.bg_color)

    def show_card(self, username, card):
        player_num = self.usernames.index(username)
        self.card_labels[player_num].configure(image=self.images[card])
        for l in self.username_labels:
            self.unhighlight_label(l)

    def start(self):
        self.connect_popup()
        self.poll_loop()
        self.window.mainloop()

    def unhighlight_button(self, button):
        button.configure(highlightbackground=self.bg_color)

    def unhighlight_label(self, label):
        label.configure(background=self.bg_color)
