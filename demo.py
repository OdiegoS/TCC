# -*- coding: utf-8 -*

import tkinter
from tkinter import messagebox
from PIL import Image, ImageTk

 
class teste_tk(tkinter.Frame):

    def __init__(self,parent = None):
        tkinter.Frame.__init__(self,parent)
        
        self.parent = parent
        self.initialize()

    def initialize(self):

        #############################################
        #criando menu
        self.top = self.winfo_toplevel()
        self.menuBar = tkinter.Menu(self.top)
         
        mnuArquivo = tkinter.Menu(self.menuBar, tearoff=0)
        mnuArquivo.add_command(label="Novo", command=self.nada)
        mnuArquivo.add_command(label="Salvar", command=self.nada)
        mnuArquivo.add_separator()
        mnuArquivo.add_command(label="Sair", command=self.sair)
        self.menuBar.add_cascade(label="Arquivo", menu=mnuArquivo)
 
        mnuTeste = tkinter.Menu(self.menuBar, tearoff=0)
        mnuTeste.add_command(label="Blabla", command=self.nada)
        mnuTeste.add_command(label="Bla", command=self.nada)
        self.menuBar.add_cascade(label="Teste", menu=mnuTeste)
 
        mnuAjuda = tkinter.Menu(self.menuBar, tearoff=0)
        mnuAjuda.add_command(label="About", command=self.sobre)
        self.menuBar.add_cascade(label="Help", menu=mnuAjuda)

        self.top.config(menu=self.menuBar)
        ######################################
        
        self.fMain = tkinter.Frame(self.parent)
        #self.fMain.pack(side = 'top')
        self.fMain.grid(row=0, column = 0, stick='nswe')
        #self.fMain.rowconfigure(1, weight=1)
        #self.fMain.columnconfigure(1, weight=1)

        self.fLabel = tkinter.Frame(self.parent)
        #self.fLabel.pack(side = "right", fill = 'y')
        self.fLabel.grid(row = 0, column = 1, stick='nswe')
        #self.fLabel.rowconfigure(1, weight=1)
        #self.fLabel.columnconfigure(1, weight=1)

        self.fStatus = tkinter.Frame(self.parent)
        #self.fStatus.pack(side='bottom', fill='x')
        self.fStatus.grid(row = 1, column = 0, stick='nswe', columnspan=2)
        #self.fStatus.rowconfigure(1, weight=1)
        #self.fStatus.columnconfigure(1, weight=1)

        #imagem grande demais cobre o status (TODO: procurar como impedir)
        self.status = tkinter.Label(self.fStatus, text="Bla bla", bd=1,relief='sunken', anchor='w', bg='red')
        self.status.pack(side='bottom', fill='x')

        self.label = tkinter.Label(self.fLabel, text="Bla bla", bd=1,relief='sunken', anchor='w', bg='green')
        self.label.pack(side='right', fill = 'y')

        img = Image.open("demo_image.jpg")
        self.photo = ImageTk.PhotoImage(img)
        
        self.canvas = tkinter.Canvas(self.fMain, width=self.photo.width(), height=self.photo.height())
        self.canvas.config(bg="blue")
        self.canvas.image = self.photo

        #######
        #deveria ser: 998x665
        self.canvas.create_image(self.photo.width()/2, self.photo.height()/2, image=self.photo, tags="imgTag")
        self.canvas.pack()
        #self.canvas.pack(fill='both', expand=True)
        self.canvas.tag_bind("imgTag", "<Button-1>", self.onClick)
        self.canvas.tag_bind("imgTag", "<Motion>", self.motion)    
        

        #self.img = tkinter.Label(self.fMain, image=self.photo)
        #self.img.image = self.photo
        #self.img.pack()
        #self.img.bind("<Button-1>", self.onClick)
        #self.img.bind("<Motion>", self.motion)
        

    def nada(self):
        pass
     
    def sobre(self):
        pass
         
    def sair(self):
        ans = tkinter.messagebox.askquestion("Quit", "Você tem certeza?", icon='warning')

        if ans == 'yes':
            self.destroy()

    def onClick(self, event):
        print ("%d, %d" %(event.x, event.y) )

    def motion(self, event):
        self.status.configure(text=("X: %d \t Y: %d" %(event.x, event.y)))
        #self.status.pack()
        
 
if __name__ == "__main__":
    root = tkinter.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title('Teste')
    
    #root.geometry('1000x700') #ativado para testes
    #root.resizable(width=False, height=False)
    
    app = teste_tk(root)
    app.mainloop()
