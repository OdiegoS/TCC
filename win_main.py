# -*- coding: utf-8 -*

import tkinter
from tkinter import messagebox
from tkinter import filedialog
from tkinter.colorchooser import *
from PIL import Image
from PIL import ImageTk
import os
import glob
 
class win_main(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self,parent)
        
        self.parent = parent
        self.image = []
        self.currImg = 0
        
        self.initialize()

    def initialize(self):

        #criando menu
        self.createMenu()

        #Frame principal (onde aparece a imagem)
        self.frameMain()

        #Frame de status
        self.frameStatus()

        #Frame Label
        self.frameLabel()

        #Apenas Key Binds
        self.addBind()

    def createMenu(self):
        self.top = self.winfo_toplevel()
        self.menuBar = tkinter.Menu(self.top)
         
        mnuArquivo = tkinter.Menu(self.menuBar, tearoff=0)
        mnuArquivo.add_command(label="Abrir Imagem", command=self.abrir)
        mnuArquivo.add_command(label="Abrir Diretorio", command=self.abrirBatch)
        mnuArquivo.add_command(label="Save Annotation ", command=self.nada)
        mnuArquivo.add_command(label="Save Comments", command=self.nada)
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

    def frameMain(self):
        self.fMain = tkinter.Frame(self.parent)
        #self.fMain.grid(row=0, column = 0, stick='nw')
        self.fMain.grid(row=0, column = 0)

        self.canvas = tkinter.Canvas(self.fMain, width=998, height=665, highlightthickness=0)
        self.canvas.config(bg="yellow")

        #998x665
        #Somar 2 se qt pixel for par e somar 1 se qt de pixel for impar?
        #self.canvas.create_image(self.photo.width()/2+2, self.photo.height()/2+1, image=self.photo, tags="imgTag")
        self.canvas.pack(fill='both', expand=True)
        
    def frameStatus(self):
        self.fStatus = tkinter.Frame(self.parent)
        self.fStatus.grid(row = 1, column = 0, stick='nswe', columnspan=2)
        
        self.status = tkinter.Label(self.fStatus, text="X: -- \t Y: -- \t Z: -- / --", bd=1,relief='sunken', anchor='w', bg='red')
        self.status.pack(side='bottom', fill='x')
        
    def frameLabel(self):
        self.fLabel = tkinter.Frame(self.parent, bg="green")
        self.fLabel.grid(row = 0, column = 1, stick='nswe', ipadx=5, )

        #################################
        color_code = '#%02x%02x%02x'
        est_color = [ [color_code  %(139, 137, 137) ],
                      [color_code  %(255, 239, 213) ],
                      [color_code  %(240, 255, 240) ],
                      [color_code  %(112, 138, 144) ],
                      [color_code  %(123, 104, 238) ],
                      [color_code  %(000, 191, 255) ],
                      [color_code  %(000, 255, 255) ],
                      [color_code  %(255, 20, 147)  ],
                      [color_code  %(173, 255, 47)  ],
                      [color_code  %(255, 165, 000) ] ]
        lb_comment = []
        for i in range(10):
            lb_comment.append(tkinter.StringVar())
            lb_comment[i].set("Comment_%d" %(i+1) )

        
        self.label = [ [ [],[],[] ] for i in range(10)]
        self.lbSelect = -1
        self.labelTitle = []

        self.labelTitle.append(tkinter.Label(self.fLabel, text="Rotulo", relief='raised', padx=3))
        self.labelTitle[0].grid(row=0, column = 0, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Comment", relief='raised', padx=3))
        self.labelTitle[1].grid(row=0, column = 1, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Cor", relief='raised', padx=3))
        self.labelTitle[2].grid(row=0, column = 2, ipady=10)

        for i in range(10):
 
            self.label[i][0] = tkinter.Label(self.fLabel, text="%d" %(i+1), padx=3)
            self.label[i][0].grid(row=i+1, column = 0, ipady=5)

            self.label[i][1] = tkinter.Entry(self.fLabel, textvariable=lb_comment[i])
            self.label[i][1].bind("<Return>", self.lostFocus)
            #self.label[i][1].bind("<Enter>", self.lostFocus)

            #self.label[i][1] = tkinter.Label(self.fLabel, text=est_label[i][0], padx=3)
            self.label[i][1].grid(row=i+1, column = 1, ipady=5)

            self.label[i][2] = tkinter.Button(self.fLabel, text="Cor", padx=3, bg=est_color[i])
            self.label[i][2]['command'] = lambda btn = self.label[i][2]: self.changeColor(btn)
            self.label[i][2].grid(row=i+1, column = 2, ipady=5)

    def addBind(self):
        ##########
        #Image Bind
        self.canvas.tag_bind("imgTag", "<Button-1>", self.onClick)
        self.canvas.tag_bind("imgTag", "<Motion>", self.motion)

        self.parent.bind("<Left>", self.moveImg)
        self.parent.bind("<Right>", self.moveImg)

        self.parent.bind("<MouseWheel>", self.moveImg) #Windows
        self.parent.bind("<Button-4>", self.moveImg) #Linux
        self.parent.bind("<Button-5>", self.moveImg) #Linux
        #print(self.canvas.bbox("imgTag"))
        ##########

        #Label Bind
        for i in range(10):
            self.parent.bind(str(i), self.selectLb)
            self.parent.bind("<KP_" + str(i) + ">", self.selectLb) #Linux - Numpad


    def changeColor(self, btn):
        color = askcolor() 

        if(color[1] == None):
            return
            
        btn.configure(bg=color[1])

    def refresh(self):
        self.canvas.config(width=self.image[ self.currImg ].width(), height=self.image[ self.currImg ].height())
        self.canvas.image = self.image[ self.currImg ]

        self.canvas.create_image(self.image[ self.currImg ].width()/2+2, self.image[ self.currImg ].height()/2+1, image=self.image[ self.currImg ], tags="imgTag")
        self.canvas.pack(fill='both', expand=True)

        self.status.configure(text=("X: -- \t Y: -- \t Z: %d / %d" %(self.currImg+1, len(self.image) )))

        self.parent.title("Teste (%s)" %self.files[self.currImg])
        
#########################################################################
#            Menu Bar Functions
#########################################################################

    def abrir(self):
        filedir = filedialog.askopenfilename(filetypes = ( ("Jpeg Images", "*.jpg"),
                                                           ("Gif Images","*.gif"),
                                                           ("Png Images","*.png"),
                                                           ("Tiff Images",".*tiff") ) )
                                                            #("All Files", "*.*") ) )
        #print(filedir)
        self.files = [filedir]
        self.image = [(ImageTk.PhotoImage(Image.open(filedir)))]
        self.currImg = 0

        self.refresh()
        
        
    def abrirBatch(self):
        dirname = filedialog.askdirectory()
        #print(dirname)

        limpar = 1

        images_ext = [".jpg",".gif",".png",".tiff"]

        listFiles = os.listdir(dirname)
        listFiles.sort()
        #print(listFiles)
        for filename in listFiles:
            
            ext = os.path.splitext(filename)[1]
            if ext.lower() not in images_ext:
                continue
            
            if(limpar == 1):
                self.files = []
                self.image = []
                self.currImg = 0
                limpar = 0
            self.image.append(ImageTk.PhotoImage(Image.open(dirname + "/" + filename)))
            self.files.append(dirname + "/" + filename)
            #print(filename)

            if ( (len(self.image) > 0) and (limpar == 0) ):
                #print(len(self.image))
                self.refresh()

    def nada(self):
        pass
     
    def sobre(self):
        pass
         
    def sair(self):
        ans = tkinter.messagebox.askquestion("Quit", "Você tem certeza?", icon='warning')

        if ans == 'yes':
            #self.destroy()
            self.parent.destroy()

        
#########################################################################
#            Binds Functions
#########################################################################
    def lostFocus(self, event):
        self.fLabel.focus()

    def selectLb(self, event):
        if(event.keysym[0] == 'K'):
            key = int(event.keysym.split('_')[1]) - 1
        else:
            key = int(event.keysym) - 1

        if(key == -1):
            key = 9
        #print("Selecionado Label #%d" %(key) )
    
        if( (self.lbSelect > -1) and (self.lbSelect != key) ):
            self.label[self.lbSelect][0].configure(relief='flat')
            self.label[self.lbSelect][1].configure(relief='flat')
            self.label[self.lbSelect][2].configure(relief='flat')
            
            
        self.label[key][0].configure(relief='solid')
        self.label[key][1].configure(relief='solid')
        self.label[key][2].configure(relief='solid')

        self.lbSelect = key
        
    def onClick(self, event):
        print ("%d, %d" %(event.x, event.y) )

    def motion(self, event):
        self.status.configure(text=("X: %d \t Y: %d \t Z: %d / %d" %(event.x, event.y, self.currImg+1, len(self.image) )))
        #self.status.pack()

    def moveImg(self, event):
        #print(self.currImg)
        #print(event)
        change = 0
        if (event.keysym == "Left") or (event.delta < 0) or (event.num == 5):
            if(self.currImg > 0):
                self.currImg = self.currImg - 1
                change = 1
        if (event.keysym == "Right") or (event.delta > 0) or (event.num == 4):
            if self.currImg < len(self.image)-1:
                self.currImg = self.currImg + 1
                change = 1
        #print(self.currImg)
        if change == 1:
            self.refresh()

#########################################################################
#########################################################################
if __name__ == "__main__":
    root = tkinter.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title('Teste')
    
    #root.geometry('1000x700') #ativado para testes
    #root.resizable(width=False, height=False)
    
    app = win_main(root)
    app.mainloop()
