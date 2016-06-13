#!/usr/bin/python
# -*- coding: utf-8 -*-

"""


"""

from tkinter import Tk, W, E, Toplevel, END, HORIZONTAL, INSERT, Radiobutton, DISABLED, ACTIVE, NORMAL, PhotoImage
from tkinter.ttk import Frame, Button, Style
from tkinter.ttk import Entry, Separator
from PIL import Image, ImageTk
from tkinter import Tk, Label, BOTH, LabelFrame, Canvas
from tkinter.ttk import Frame, Style
import glob
import os
import requests
import urllib
from configparser import ConfigParser
from api import Word
from io import BytesIO
import threading
import multiprocessing as mp


IMGPATH = 'imgs/'

def on_leave(event):
    print("success")
    #event.widget.configure(font="normal_font")


def read_config():
    """Helper function to read a configuration file for api keys and etc

    :return: lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict
    """
    config = ConfigParser(allow_no_value=True)
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
        self.columnconfigure(2, pad=3)
        self.rowconfigure(3, pad=3)


        fvo_label = Label(window, text="Forvo API Key:", font=("Helvetica", 16), height=2)
        fvo_label.grid(row=0, column=0, padx=3, sticky=W)

        fvo_entry = Entry(window, width=50, font=("Helvetica", 16))
        fvo_entry.grid(row=0, column=1, padx=3, sticky=W+E)

        ms_label = Label(window, text="Microsoft Bing API Key:", font=("Helvetica", 16), height=2)
        ms_label.grid(row=1, column=0, padx=3, sticky=W)

        ms_entry = Entry(window, width=50, font=("Helvetica", 16))
        ms_entry.grid(row=1, column=1, padx=3, sticky=W+E)

        fvo_label = Label(window, text="SAVE", font=("Helvetica", 16), height=2)
        fvo_label.grid(row=2, column=1, padx=3, sticky=W+E)


    def ok(self):

        print("value is")

        self.destroy()


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   

        self.word = 'chien'
        self.entry3 = Entry(self)
        self.prev_image = None # previously select image / widget
        self.prev_audio = None # previously selected audio / widget
        self.selected_image = None
        self.selected_audio = None
        self.parent = parent
        self.ROWS = 5
        self.COLS = 6

        self.image_dict = {}


        lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict, microsoft_api_key = read_config()
        self.w = Word(self.word, lang, pn_dict, pons_api_key, forvo_api_key, output, microsoft_api_key)
        self.audio_links = self.w.get_audio_links()
        self.ipa = self.w.get_ipa()
        self.images = self.w.get_images()
        self.initUI()

    def do_image(self, event):
        #lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict, microsoft_api_key = read_config()
        #word = 'chient'
        #w = Word(word, lang, pn_dict, pons_api_key, forvo_api_key, output, microsoft_api_key)
        #w.get_images()

        if self.prev_image:
            self.prev_image.configure(state=NORMAL)
        self.prev_image = event.widget
        event.widget.configure(state=ACTIVE)
        self.selected_image = event.widget.cget('image')
        #self.entry3.delete(0, END)
        #self.entry3.insert(INSERT, str(self.selected_image))

    def do_sound(self, event):
        if self.prev_audio:
            self.prev_audio.configure(state=NORMAL)
        self.prev_audio = event.widget
        event.widget.configure(state=ACTIVE)
        self.selected_audio = event.widget.cget("text")

        file_path, file_name = self.w.download(self.audio_links[self.selected_audio])

        self.after(1, self.w.play(file_path))

    def do_save(self, event):
        #img.save(filename, quality=90, optimize=True)
        print(self.image_dict[self.selected_image])
        i = self.image_dict[self.selected_image]
        i.save('output.jpg')
        print(self.selected_audio)

    def get_files(self):
        img_names = []
        for img in glob.glob(os.path.join(IMGPATH, '*.jpg')):
            img_names.append(img)
        return img_names

    def new_window(self):
        self.newWindow = Toplevel(self.master)
        self.app = PreferencesDialog(self.newWindow)

    def demo_cmd(self):
        print("success")

    def initUI(self):
        self.parent.title("Calculator")


        for col in range(self.COLS):
            self.columnconfigure(col, pad=3)

        for row in range(self.ROWS):
            self.rowconfigure(row, pad=3)


        word = Label(self, text=self.word, font=("Helvetica", 25), height=2)
        word.grid(row=0, columnspan=6, sticky=W+E)

        for num in range(0, self.COLS):
            if num < len(self.audio_links):
                audio_links = list(self.audio_links.items())
                snd = Label(self, text=str(audio_links[num][0]), font=("Helvetica", 16), height=2)
                snd.bind("<Button-1>", self.do_sound)
                snd.grid(row=1, column=num, padx=3, pady=3, sticky=W+E)

        #Separator(self,orient=HORIZONTAL).grid(row=2, columnspan=5, sticky="ew")


        for x in range(2, self.ROWS):
            for y in range(0, self.COLS):
                if self.images:
                    bing_image_obj = self.images.pop()

                    try:
                        r = requests.get(bing_image_obj.media_url)
                        data = BytesIO(r.content)
                        img = Image.open(data)

                    except (UnicodeError, OSError):
                        pass

                    try:
                        img.thumbnail((150, 150),Image.ANTIALIAS)
                        tk_img = ImageTk.PhotoImage(img)

                        lbl = Label(self, image=tk_img, borderwidth=5, activebackground="red")
                        lbl.image = tk_img
                        lbl.bind("<Button-1>", self.do_image)
                        lbl.grid(row=x, column=y, padx=3, pady=3)
                        self.image_dict.update({lbl.cget('image'): img})
                    except IOError:
                        pass




        skip_lbl = Label(self, text="SKIP", font=("Helvetica", 16), height=2)
        skip_lbl.grid(row=5, column=4, padx=3, sticky=W+E)

        next_lbl = Label(self, text="SAVE", font=("Helvetica", 16), height=2)
        next_lbl.bind("<Button-1>", self.do_save)
        next_lbl.grid(row=5, column=5, padx=3, pady=3, sticky=W+E)

        self.pack()


def main():
    root = Tk()
    root.configure(background='gray')
    #root.resizable(0, 0)
    root.minsize(width=1024, height=700)
    root.createcommand('tk::mac::ShowPreferences', showMyPreferencesDialog)
    root.geometry("1000x700")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
