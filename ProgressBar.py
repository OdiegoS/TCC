import time
import tkinter

from tkinter.ttk import Progressbar

class ProgressBar(object):

    def __init__(self, tk_main, action = None):
        self.action = action
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

        self.start = time.time()

    def updatingBar(self, value = None):
        if(self.action == 'loading'):
            diff = time.time() - self.start
            if(diff > 0.1):
                self.count += 10
                self.progress['value']=self.count
                self.progress.update()
                if(self.count == 100):
                    self.count = 0
                self.start = time.time()
        else:
            self.count = self.count + value
            self.progress['value']=self.count
            self.progress.update()

    def close(self):
        self.tk.destroy()