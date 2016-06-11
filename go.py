#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

In this script, we use the grid manager
to create a skeleton of a calculator.

Author: Jan Bodnar
Last modified: November 2015
Website: www.zetcode.com
"""

from Tkinter import Tk, W, E, Toplevel, END, HORIZONTAL, INSERT, Radiobutton, DISABLED, ACTIVE, NORMAL
from ttk import Frame, Button, Style
from ttk import Entry, Separator
from PIL import Image, ImageTk
from Tkinter import Tk, Label, BOTH, LabelFrame, Canvas
from ttk import Frame, Style
import glob
import os


IMGPATH = 'imgs/'

def on_leave(event):
    print "success"
    #event.widget.configure(font="normal_font")


class MyDialog:

    def __init__(self, parent):

        top = self.top = Toplevel(parent)

        Label(top, text="Value").pack()

        self.e = Entry(top)
        self.e.pack(padx=5)

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):

        print "value is", self.e.get()

        self.top.destroy()


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   

        self.entry3 = Entry(self)
        self.prev = None # previously select image / widget
        self.selected_image = None
        self.parent = parent
        self.ROWS = 5
        self.COLS = 6
        self.initUI()

    def do_image(self, event):
        print(event.widget)
        if self.prev:
            self.prev.configure(state=NORMAL)
        self.prev = event.widget
        event.widget.configure(state=ACTIVE)
        self.entry3.delete(0, END)
        self.entry3.insert(INSERT, str("success"))


    def get_files(self):

        img_names = []
        for img in glob.glob(os.path.join(IMGPATH, '*.jpg')):
            img_names.append(img)
        return img_names


    def initUI(self):
        img_names = self.get_files()
        print img_names
        self.parent.title("Calculator")
        
        Style().configure("TButton", padding=(0, 5, 0, 5), 
            font='serif 10')

        for col in xrange(self.COLS):
            self.columnconfigure(col, pad=3)

        for row in xrange(self.ROWS):
            self.rowconfigure(row, pad=3)

        while img_names:
            img_names.pop()

        entry = Entry(self)
        entry.grid(row=0, columnspan=6, sticky=W+E)
        entry.insert(END, "Default")

        test1 = Button(self, text="Sound 1", width=20)
        test1.grid(row=1, column=0)

        test2 = Button(self, text="Sound 2", width=20)
        test2.grid(row=1, column=1)


        bard = Image.open("imgs/DSC_0020.jpg")
        bard.thumbnail((150,150),Image.ANTIALIAS)
        bardejov = ImageTk.PhotoImage(bard)

        #Separator(self,orient=HORIZONTAL).grid(row=2, columnspan=5, sticky="ew")

        for x in xrange(2, self.ROWS):
            for y in xrange(0, self.COLS):

                lbl = Label(self, image=bardejov, borderwidth=5, activebackground="red")
                lbl.image = bardejov
                lbl.bind("<Button-1>", self.do_image)
                lbl.grid(row=x, column=y)

        self.entry3.grid(row=5, columnspan=2, sticky=W+E)
        self.entry3.insert(END, "Result")

        self.pack()


def main():
  
    root = Tk()
    root.configure(background='gray')
    root.resizable(0, 0)
    root.geometry("1000x600")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
