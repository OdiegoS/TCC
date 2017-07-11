# -*- coding: utf-8 -*

import tkinter
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk

 
class teste_tk(tkinter.Tk):

    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
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

        #imagem grande demais cobre o status (TODO: procurar como impedir)
        self.status = tkinter.Label(text="Bla bla", bd=1,relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')


        img = Image.open("demo_image.jpg")
        self.photo = ImageTk.PhotoImage(img)

        
        #imagem não preenchendo a janela (TODO: procurar uma forma)
        #canvas = tkinter.Canvas(self)
        #canvas.grid(row = 0, column = 0)
        #canvas.create_image(0,0,image=self.photo)

        self.label = tkinter.Label(image=self.photo)
        self.label.image = self.photo
        self.label.pack()

        self.label.bind("<Button-1>", self.onClick)
        self.label.bind("<Motion>", self.motion)
        

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
    app = teste_tk(None)
    app.title('Teste')
    app.geometry('1000x700') #ativado para testes
    #app.resizable(width=False, height=False)
    app.mainloop()
