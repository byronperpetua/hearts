from tkinter import *

window = Tk()

img = PhotoImage(file='images/blank.png')

Label(window, text='top').grid(row=0, column=6)
Label(window, text='0').grid(row=1, column=6)
Button(window, image=img).grid(row=2, column=6)
Label(window, text='left').grid(row=3, column=2)
Label(window, text='0').grid(row=4, column=2)
Button(window, image=img).grid(row=3, column=3, rowspan=2)
Label(window, text='right').grid(row=3, column=10)
Label(window, text='0').grid(row=4, column=10)
Button(window, image=img).grid(row=3, column=9, rowspan=2)
Button(window, image=img).grid(row=6, column=6)
Label(window, text='bottom').grid(row=7, column=6)
Label(window, text='0').grid(row=8, column=6)

for i in range(13):
    Button(window, image=img).grid(row=9, column=i)

window.mainloop()
