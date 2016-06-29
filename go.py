#!/usr/bin/python
# -*- coding: utf-8 -*-

"""


"""

from tkinter import filedialog, Tk, W, E, Toplevel, END, TOP, HORIZONTAL, INSERT, Radiobutton, DISABLED, ACTIVE, NORMAL, Menu, PhotoImage
from tkinter.ttk import Frame
from tkinter.ttk import Entry
from PIL import Image, ImageTk
from tkinter import Label
import requests
from configparser import ConfigParser
from api import Word
from io import BytesIO
import threading
import queue
import csv


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


class ThreadedTask(threading.Thread):
    def __init__(self, tk_obj, queue, bing_image_obj, row, col):
        threading.Thread.__init__(self)
        self.tk_obj = tk_obj
        self.bing_image_obj = bing_image_obj
        self.row = row
        self.col = col
        self.queue = queue

    def run(self):
        img = None
        try:
            r = requests.get(self.bing_image_obj['thumbnailUrl'])
            if r:
                data = BytesIO(r.content)
                img = Image.open(data)

        except (UnicodeError, OSError, AttributeError):
            pass

        try:
            if img:
                img.thumbnail((150, 150), Image.ANTIALIAS)
                tk_img = ImageTk.PhotoImage(img)

                lbl = Label(self.tk_obj, image=tk_img, borderwidth=5, activebackground="red")
                lbl.image = tk_img
                lbl.bind("<Button-1>", self.tk_obj.do_image)
                lbl.grid(row=self.row, column=self.col, padx=3, pady=3)
                self.tk_obj.image_dict.update({lbl.cget('image'): img})
        except IOError:
            pass
        self.queue.put("Task finished")


def rewrite_word_list(words):
    with open('output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for word in words:
            row = [word] + list(words[word].values())
            writer.writerow(row)


class WordGui(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   

        #self.words = ['chien', 'chat', 'lapin', 'couloir', "l'oeuf"]
        self.word_dict = {}
        self.word_dict_out = {}
        self.prev_image = None # previously select image / widget
        self.prev_audio = None # previously selected audio / widget
        self.selected_image = None
        self.selected_audio = None
        self.parent = parent
        self.ROWS = 5
        self.COLS = 6
        self.title = None
        self.save_lbl = Label()
        self.image_dict = {}
        self.queue = queue.Queue()
        self.file_opt = options = {}


        self.initUI()

    def process_queue(self):
        try:
            msg = self.queue.get(0)
            # Show result of the task if needed
        except queue.Empty:
            self.after(100, self.process_queue)

    def do_image(self, event):
        if self.prev_image:
            self.prev_image.configure(state=NORMAL)
        self.prev_image = event.widget
        event.widget.configure(state=ACTIVE)
        self.selected_image = event.widget.cget('image')

    def askopenfilename(self):
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        """
        # get filename
        filename = filedialog.askopenfilename(**self.file_opt)
         # open file on your own
        if filename:
            with open(str(filename), 'r') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in list(reader):
                    self.word_dict[row['word']] = {}
                    self.word_dict_out[row['word']] = {}

                    for i in row:
                        if str(i) is not 'word':
                            self.word_dict[row['word']].update({i: row[i]})
                            self.word_dict_out[row['word']].update({i: row[i]})

        self.next_word()

    def do_sound(self, event):
        if self.prev_audio:
            self.prev_audio.configure(state=NORMAL)
        self.prev_audio = event.widget
        event.widget.configure(state=ACTIVE)
        self.selected_audio = event.widget.cget("text")

        file_path, file_name = self.w.download(self.audio_links[self.selected_audio])

        self.downloaded_audio = file_name
        self.after(1, self.w.play(file_path))

    def do_skip(self, event):
        if len(self.word_dict) > 0:
            self.selected_audio = None
            self.selected_image = None
            self.next_word()
        else:
            rewrite_word_list(self.word_dict_out)
            print("Should close")

    def do_save(self, event):
        self.save_lbl.config(text="WAIT...")
        if self.selected_image:
            i = self.image_dict[self.selected_image]
            f_name = str(self.current_word) + '.jpg'
            img_filename = "imgs/" + f_name
            i.save(img_filename)
            self.word_dict_out[self.current_word].update({'picture': '<img src="%s" />' % f_name})

        if self.selected_audio:
            self.word_dict_out[self.current_word].update({'pronunciation': "[sound:%s]" % self.downloaded_audio})
        else:
            self.word_dict_out[self.current_word].update({'pronunciation': " "})

        if self.ipa:
            if 'ipa' in self.ipa.keys():
                self.word_dict_out[self.current_word].update({'ipa': str(self.ipa['ipa'])})
            else:
                self.word_dict_out[self.current_word].update({'ipa': " "})
            if 'wordclass' in self.ipa.keys():
                self.word_dict_out[self.current_word].update({'wordclass': str(self.ipa['wordclass'])})
            else:
                self.word_dict_out[self.current_word].update({'wordclass': ' '})
        else:
            self.word_dict_out[self.current_word].update({'pronunciation': "[sound:%s]" % self.downloaded_audio})

        if len(self.word_dict) > 0:
            self.next_word()
        else:
            rewrite_word_list(self.word_dict_out)
            print("Should close")

    def new_window(self):
        self.newWindow = Toplevel(self.master)
        self.app = PreferencesDialog(self.newWindow)

    def next_word(self):

        self.current_word = self.word_dict.popitem()[0]

        for label in self.grid_slaves():
            label.grid_forget()

        lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict, microsoft_api_key = read_config()
        self.w = Word(self.current_word, lang, pn_dict, pons_api_key, forvo_api_key, output, microsoft_api_key)
        self.audio_links = self.w.get_audio_links()
        self.ipa = self.w.get_ipa()
        self.images = self.w.get_images()

        self.title = Label(self, text=self.current_word, font=("Helvetica", 25), height=2)
        self.title.grid(row=0, columnspan=4, sticky=W+E)

        # We put the SKIP and SAVE buttons up here in case the audio/images fails
        self.skip_lbl = Label(self, text="SKIP", font=("Helvetica", 25), height=2)
        self.skip_lbl.bind("<Button-1>", self.do_skip)
        self.skip_lbl.grid(row=0, column=4, padx=3, sticky=W+E)

        self.save_lbl = Label(self, text="SAVE", font=("Helvetica", 25), height=2)
        self.save_lbl.bind("<Button-1>", self.do_save)
        self.save_lbl.grid(row=0, column=5, padx=3, pady=3, sticky=W+E)


        for num in range(0, self.COLS):
            if self.audio_links:
                if num < len(self.audio_links):

                    audio_links = list(self.audio_links.items())
                    snd = Label(self, text=str(audio_links[num][0]), font=("Helvetica", 16), height=2)
                    snd.bind("<Button-1>", self.do_sound)
                    snd.grid(row=1, column=num, padx=3, pady=3, sticky=W+E)

        for x in range(2, self.ROWS):
            for y in range(0, self.COLS):
                if self.images:
                    bing_image_obj = self.images.pop()
                    ThreadedTask(self, self.queue, bing_image_obj, x, y).start()
                    #self.after(100, self.process_queue)




        self.pack()

    def initUI(self):
        self.parent.title("Calculator")

        for col in range(self.COLS):
            self.columnconfigure(col, pad=3, minsize=170)

        for row in range(self.ROWS):
            self.rowconfigure(row, pad=3)

        if len(self.word_dict) > 0:
            self.next_word()


def main():

    root = Tk()
    root.configure(background='gray')
    #root.resizable(0, 0)
    root.minsize(width=1024, height=700)
    root.createcommand('tk::mac::ShowPreferences', showMyPreferencesDialog)
    root.geometry("1000x750")

    app = WordGui(root)

   # Menu
    menubar = Menu(root)
    root['menu'] = menubar
    menu_file = Menu(menubar)
    menu_edit = Menu(menubar)
    menubar.add_cascade(menu=menu_file, label='File')
    menubar.add_cascade(menu=menu_edit, label='Edit')
    menu_file.add_command(label='New')
    menu_file.add_command(label='Open...', command=app.askopenfilename)
    menu_file.add_command(label='Close')


    root.mainloop()

if __name__ == '__main__':
    main()