from os import listdir
import tkinter as tk


class HeartsGUI:
    def __init__(self, client):
        self.client = client
        self.hand = [None]*13
        self.mode = 'pass'  # 'wait', 'play'
        self.msg = None
        self.selected = []
        self.setup_gui()

    def on_card_click(self, event):
        button = event.widget
        card_num = self.card_buttons.index(button)
        if self.mode == 'pass':
            if card_num in self.selected:
                self.selected.remove(card_num)
                event.widget.config(highlightbackground='#ffffff')
                self.submit_button.configure(state='disabled')
            elif len(self.selected) < 3:
                self.selected.append(card_num)
                event.widget.config(highlightbackground='#0088ff')
                if len(self.selected) == 3:
                    self.submit_button.configure(state='normal')
        elif self.mode == 'play':
            self.client.send(self.hand[card_num])

    def on_submit_click(self, event):
        if self.mode == 'pass':
            self.client.send(' '.join([self.hand[i] for i in self.selected]))

    def poll_loop(self, poll_delay=1000):
        if self.msg:
            msg_type = self.msg[:2]
            msg_data = self.msg[2:]
            if msg_type.startswith('h:'):
                self.set_hand(msg_data)
            elif msg_type.startswith('p:'):
                pass # show pass received
            elif msg_type.startswith('p?'):
                pass # request pass
            elif msg_type.startswith('c?'):
                pass # request card
            elif msg_type.startswith('s?'):
                pass # request add/subtract
            self.msg = None
        self.window.after(poll_delay, self.poll_loop)
    
    def set_hand(self, hand_str):
        self.hand = hand_str.split()
        for i in range(13):
            if i < len(self.hand):
                img = self.images[self.hand[i].upper()]
            else:
                img = self.images['blank']
            self.card_buttons[i].configure(image=img)

    def set_msg(self, msg):
        self.msg = msg

    def setup_gui(self):
        self.window = tk.Tk()
        self.images = {}
        for f in listdir('images'):
            self.images[f[:-4]] = tk.PhotoImage(file='images/'+f)
        tk.Label(self.window, text='top').grid(row=0, column=6)
        tk.Label(self.window, text='0').grid(row=1, column=6)
        tk.Label(self.window, image=self.images['blank']).grid(row=2, column=6)
        tk.Label(self.window, text='left').grid(row=3, column=3)
        tk.Label(self.window, text='0').grid(row=4, column=3)
        tk.Label(self.window, image=self.images['blank']).grid(row=3, column=4, rowspan=2)
        tk.Label(self.window, text='right').grid(row=3, column=9)
        tk.Label(self.window, text='0').grid(row=4, column=9)
        tk.Label(self.window, image=self.images['blank']).grid(row=3, column=8, rowspan=2)
        tk.Label(self.window, image=self.images['blank']).grid(row=6, column=6)
        tk.Label(self.window, text='bottom').grid(row=7, column=6)
        tk.Label(self.window, text='0').grid(row=8, column=6)
        self.card_buttons = []
        for i in range(13):
            self.card_buttons.append(tk.Button(self.window, image=self.images['blank']))
            self.card_buttons[i].grid(row=9, column=i)
            self.card_buttons[i].bind('<Button-1>', self.on_card_click)
        self.submit_button = tk.Button(self.window, text='Submit\nPass',
                                       state='disabled')
        self.submit_button.grid(row=9, column=13)
        self.submit_button.bind('<Button-1>', self.on_submit_click)

    def start(self, poll_freq=1000):
        self.poll_loop()
        self.window.mainloop()
