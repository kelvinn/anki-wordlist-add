#!/usr/bin/python
# -*- coding: utf-8 -*-

"""


"""

from Tkinter import Tk, W, E, Toplevel, END, HORIZONTAL, INSERT, Radiobutton, DISABLED, ACTIVE, NORMAL
from ttk import Frame, Button, Style
from ttk import Entry, Separator
from PIL import Image, ImageTk
from Tkinter import Tk, Label, BOTH, LabelFrame, Canvas
from ttk import Frame, Style
import glob
import os
import ConfigParser
from api import Word

IMGPATH = 'imgs/'

def on_leave(event):
    print "success"
    #event.widget.configure(font="normal_font")


def read_config():
    """Helper function to read a configuration file for api keys and etc

    :return: lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict
    """
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read('defaults.cfg')
    lang = config.get('settings', 'lang')
    output = config.get('settings', 'output')
    forvo_api_key = config.get('settings', 'forvo_api_key')
    pons_api_key = config.get('pons', 'api_key')
    pons_lang = config.get('pons', 'lang')
    pn_dict = config.get('pons', 'pn_dict')
    microsoft_api_key = config.get('microsoft', 'api_key')
    return lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict, microsoft_api_key

def showMyPreferencesDialog():
    PreferencesDialog()


class PreferencesDialog(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        window = Toplevel(self)
        b = Button(window, text="Open new window", command=self.ok)
        b.pack(side="top")

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

    def new_window(self):
        self.count += 1
        id = "New window #%s" % self.count
        window = Toplevel(self)
        label = Label(window, text=id)
        label.pack(side="top", fill="both", padx=10, pady=10)

    def do_image(self, event):
        #lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict, microsoft_api_key = read_config()
        #word = 'chient'
        #w = Word(word, lang, pn_dict, pons_api_key, forvo_api_key, output, microsoft_api_key)
        #w.get_images()

        if self.prev:
            self.prev.configure(state=NORMAL)
        self.prev = event.widget
        event.widget.configure(state=ACTIVE)
        self.selected_image = event.widget.cget("image")
        self.entry3.delete(0, END)
        self.entry3.insert(INSERT, str(self.selected_image))

    def do_sound(self, event):
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

    def new_window(self):
        self.newWindow = Toplevel(self.master)
        self.app = PreferencesDialog(self.newWindow)


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

        #while img_names:
        #    img_names.pop()

        entry = Entry(self)
        entry.grid(row=0, columnspan=6, sticky=W+E)
        entry.insert(END, "Default")

        test1 = Button(self, text="Sound 1", width=20)
        test1.grid(row=1, column=0)

        test2 = Button(self, text="Sound 2", width=20)
        test2.grid(row=1, column=1)


        #Separator(self,orient=HORIZONTAL).grid(row=2, columnspan=5, sticky="ew")

        for x in xrange(2, self.ROWS):
            for y in xrange(0, self.COLS):
                if img_names:
                    filename = img_names.pop()
                    img = Image.open(filename)
                    img.thumbnail((150,150),Image.ANTIALIAS)
                    tk_img = ImageTk.PhotoImage(img)
                    lbl = Label(self, image=tk_img, borderwidth=5, activebackground="red")
                    lbl.image = tk_img
                    lbl.bind("<Button-1>", self.do_image)
                    lbl.grid(row=x, column=y)


        self.entry3.grid(row=5, columnspan=2, sticky=W+E)
        self.entry3.insert(END, "Result")

        test2 = Button(self, text="Next", width=20)
        test2.grid(row=5, column=5)

        self.pack()


def main():


    root = Tk()
    root.configure(background='gray')
    root.resizable(0, 0)
    root.createcommand('tk::mac::ShowPreferences', showMyPreferencesDialog)
    root.geometry("1000x600")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
