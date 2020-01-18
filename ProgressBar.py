import time
import tkinter

from tkinter.ttk import Progressbar

class ProgressBar(object):

    def __init__(self, tk_main):
        self.count = 0
        self.tk=tkinter.Toplevel(tk_main)
        self.tk.overrideredirect(1)
        centralized = [ (tk_main.winfo_screenwidth() // 2) - 175, (tk_main.winfo_screenheight() // 2) - 55 ]
        self.tk.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        self.tk.minsize(width=100, height=20)
        self.tk.resizable(width=False, height=False)
        self.tk.grab_set()
        self.tk.focus_force()
        self.tk.attributes("-topmost", True)

        self.progress=Progressbar(self.tk,orient=tkinter.HORIZONTAL,length=100,mode='determinate')
        self.progress.pack()

    def updatingBar(self, value):
        self.count = self.count + value
        print(self.count)
        self.progress['value']=self.count
        self.progress.update()

    def close(self):
        self.tk.destroy()

class Loading(object):

    def __init__(self, tk_main):
        self.count = 0
        self.count_2 = 0
        self.tk=tkinter.Toplevel(tk_main)
        self.tk.overrideredirect(1)
        centralized = [ (tk_main.winfo_screenwidth() // 2) - 175, (tk_main.winfo_screenheight() // 2) - 55 ]
        self.tk.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        self.tk.minsize(width=100, height=20)
        self.tk.resizable(width=False, height=False)
        self.tk.grab_set()
        self.tk.focus_force()
        self.tk.attributes("-topmost", True)

        self.progress=Progressbar(self.tk,orient=tkinter.HORIZONTAL,length=100,mode='indeterminate')
        self.progress.pack()

        self.start = time.time()

    def updatingBar(self):
        diff = time.time() - self.start

        if(diff > 0.1):
            self.count += 10
            self.progress['value']=self.count
            self.progress.update()
            if(self.count == 100):
                self.count = 0
            self.start = time.time()

    def close(self):
        self.tk.destroy()