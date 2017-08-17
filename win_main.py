# -*- coding: utf-8 -*

import tkinter
from tkinter import messagebox
from tkinter import filedialog
from tkinter.colorchooser import *
from PIL import Image
from PIL import ImageTk
import os
import glob
from tkinter.simpledialog import SimpleDialog
 
class win_main(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self,parent)
        
        self.parent = parent
        self.image = []
        self.currImg = 0
        self.loadComment = None

        self.dirImage = "/"
        self.dirStack = "/"
        self.dirLoadComments = "/"
        self.dirSaveComments = "/"
        self.dirLoadAnnotations = "/"
        self.dirSaveAnnotations = "/"

        if (not os.path.isfile("settings") ):
            file = open("settings","w")
            file.close
            self.saveSettings()
        
        self.initialize()

    def initialize(self):

        #carregando settings
        self.loadSettings()

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

    def loadSettings(self):
        file = open("settings","r")

        lines = file.read().splitlines()

        self.dirImage = lines[0]
        self.dirStack = lines[1]
        self.dirLoadComments = lines[2]
        self.dirSaveComments = lines[3]
        self.dirLoadAnnotations = lines[4]
        self.dirSaveAnnotations = lines[5]

    def saveSettings(self):
        file = open("settings","w")

        file.write(self.dirImage + "\n")
        file.write(self.dirStack + "\n")
        file.write(self.dirLoadComments + "\n")
        file.write(self.dirSaveComments + "\n")
        file.write(self.dirLoadAnnotations + "\n")
        file.write(self.dirSaveAnnotations + "\n")

    def createMenu(self):
        self.top = self.winfo_toplevel()
        self.menuBar = tkinter.Menu(self.top)
         
        self.mnuArquivo = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuArquivo.add_command(label="Open Image", command=self.abrir)
        self.mnuArquivo.add_command(label="Open Directory", command=self.abrirBatch)
        self.mnuArquivo.add_command(label="Save Annotation ", command=self.nada)
        self.mnuArquivo.add_command(label="Save Comments", state = "disabled", command=self.saveComments)
        self.mnuArquivo.add_command(label="Save Comments As", command=self.saveCommentsAs)
        self.mnuArquivo.add_command(label="Load Comments", command=self.loadComments)
        self.mnuArquivo.add_separator()
        self.mnuArquivo.add_command(label="Quit", command=self.sair)
        self.menuBar.add_cascade(label="File", menu=self.mnuArquivo)
 
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
        self.frameLb = tkinter.Frame(self.parent, bg="pink")
        #self.fLabel = tkinter.Frame(self.lbCanvas, bg="green")
        self.frameLb.grid(row = 0, column = 1, stick='nswe', ipadx=5)
        
        self.lbScroll = tkinter.Scrollbar(self.frameLb, orient="vertical")
        self.lbCanvas = tkinter.Canvas(self.frameLb, bg ="green", yscrollcommand=self.lbScroll.set)#, width= 250)
        self.lbScroll.config(command=self.lbCanvas.yview)

        self.fLabel = tkinter.Frame(self.lbCanvas, bg="blue")
        self.fLabel.pack(fill="both", expand=False)

        self.lbCanvas.create_window( 0,0, window=self.fLabel, anchor="nw")
        
        self.lbScroll.pack(side="right", fill="y")
        self.lbCanvas.pack(side="left", fill="both", expand=True)
                

        #self.lbCanvas.config(scrollregion=self.lbCanvas.bbox("all"))
        #self.lbCanvas.yview_moveto(0)

        self.lb_comment = []
        self.label = []
        self.lbSelect = -1
        self.labelTitle = []

        self.labelTitle.append(tkinter.Label(self.fLabel, text="Label", relief='raised', padx=3))
        self.labelTitle[0].grid(row=0, column = 0, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Comments", relief='raised', padx=3))
        self.labelTitle[1].grid(row=0, column = 1, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Mark Color", relief='raised', padx=3))
        self.labelTitle[2].grid(row=0, column = 2, ipady=10)

        self.btn_addLb = tkinter.Button(self.fLabel, text="Add New Label", padx=3, command= self.addLb)
        self.btn_rmLb = tkinter.Button(self.fLabel, text="Delete Last Label", padx=3, command= self.rmLb)
        
        if(self.dirLoadComments == "/"):
            self.addLb()
        else:
            self.loadComments(1)

    def colorDefault(self):

        i = len(self.label)

        if(i<9):
        
            switcher = {
                1: "#ff0000",
                2: "#00ff00",
                3: "#0000ff",
                4: "#ffff00",
                5: "#ff00ff",
                6: "#00ffff",
                7: "#ffa500",
                8: "#a020f0"
            }
            return switcher.get(i)

        return '#%02x%02x%02x' %( (i*35)%255, (i*55)%255, (i*15)%255)

    def commentLb(self, i):

        comment = tkinter.simpledialog.askstring("Editing Comment", "Comment:", initialvalue = self.lb_comment[i].get(), parent=self.parent)

        if(comment == None):
            return
        
        self.lb_comment[i].set(comment)

    def addLb(self, load = None):

        i = len(self.label)
        self.label.append( [ [],[],[] ] )

        if(load == None):
            self.lb_comment.append(tkinter.StringVar())
            self.lb_comment[i].set("Comment_%d" %(i+1) )

            color = self.colorDefault()
        else:
            self.lb_comment.append(tkinter.StringVar())
            self.lb_comment[i].set(load[0])

            color = load[1]


        self.label[i][0] = tkinter.Label(self.fLabel, text="%d" %(i+1), padx=3)
        self.label[i][0].grid(row=i+1, column = 0, ipady=5)

        self.label[i][1] = tkinter.Button(self.fLabel, textvariable=self.lb_comment[i], padx=3, command=lambda:self.commentLb(i))
        #self.label[i][1].bind("<Return>", self.lostFocus)
        #self.label[i][1].bind("<Enter>", self.lostFocus)

        #self.label[i][1] = tkinter.Label(self.fLabel, text=est_label[i][0], padx=3)
        self.label[i][1].grid(row=i+1, column = 1, ipady=5)

        self.label[i][2] = tkinter.Button(self.fLabel, text="Cor", padx=3, bg=color)
        self.label[i][2]['command'] = lambda btn = self.label[i][2]: self.changeColor(btn)
        self.label[i][2].grid(row=i+1, column = 2, ipady=5)
        
        self.btn_addLb.grid(row=i+2, column = 0, ipady=5)
        self.btn_rmLb.grid(row=i+2, column = 2, ipady=5)
            

    def rmLb(self, flag = None):

        if( len(self.label) == 1) and (flag == None):
            tkinter.messagebox.showwarning("Warning", "You can't delete all the labels. You need at least one to work!")
            return

        for i in range(3):
            self.label[-1][i].destroy()

        del self.label[-1]

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

        self.fLabel.bind("<Configure>", self.OnFrameConfigure)


    def changeColor(self, btn):
        color = askcolor()

        print(color)

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
        ini_dir = self.dirImage.split("/")
        del ini_dir[-1]
            
        filedir = filedialog.askopenfilename(initialdir= "/".join(ini_dir) + "/" ,filetypes = ( ("Jpeg Images", "*.jpg"),
                                                           ("Gif Images","*.gif"),
                                                           ("Png Images","*.png"),
                                                           ("Tiff Images",".*tiff") ) )
                                                            #("All Files", "*.*") ) )
        #print(filedir)
        self.files = [filedir]
        self.image = [(ImageTk.PhotoImage(Image.open(filedir)))]
        self.currImg = 0

        self.refresh()

        self.dirImage = filedir
        self.saveSettings()
        
        
    def abrirBatch(self):
        dirname = filedialog.askdirectory(initialdir= self.dirStack)
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

        self.dirStack = dirname
        self.saveSettings()

    def saveComments(self):

        file = open(self.loadComment,"w")

        for i in range(len(self.lb_comment)):
            file.write("%d %s %s\n" %( i+1, self.label[i][2].cget("bg"), self.lb_comment[i].get() ) )

        file.close()
        

    def saveCommentsAs(self):
        ini_dir = self.dirSaveComments.split("/")
        del ini_dir[-1]
        
        res = filedialog.asksaveasfilename(initialdir= "/".join(ini_dir) + "/", defaultextension=".txt", filetypes = ( ("Text Files","*.txt"),
                                                         ("All Files", "*.*") ) )

        file = open(res,"w")
        print(res)

        for i in range(len(self.lb_comment)):
            file.write("%d %s %s\n" %( i+1, self.label[i][2].cget("bg"), self.lb_comment[i].get() ) )

        file.close()

        self.dirSaveComments = res
        self.saveSettings()

    def loadComments(self, flag = None):

        if(flag == None):
            ini_dir = self.dirLoadComments.split("/")
            del ini_dir[-1]
            
            res = filedialog.askopenfilename(initialdir= "/".join(ini_dir) + "/" ,filetypes = [ ("Text Files","*.txt") ] )
        else:
            res = self.dirLoadComments

        file = open(res,"r")

        lines = file.read().splitlines()

        lb_est = [ [ [],[] ] for i in range(1) ]

        for label in lines:
            sep = label.split(" ")
            color = sep[1]
            
            del sep[1]
            del sep[0]

            lb_est.append( [" ".join(sep), color ] )
        del lb_est[0]

        for i in range(len(self.label) ):
            self.rmLb(1)

        del self.lb_comment[:]
        self.lb_label = []

        for i in range(len(lb_est)):
            self.addLb(lb_est[i])

        self.dirLoadComments = res

        self.saveSettings()
        file.close()

        self.mnuArquivo.entryconfig("Save Comments", state="normal")

    def nada(self):
        pass
     
    def sobre(self):
        pass
         
    def sair(self):
        ans = tkinter.messagebox.askquestion("Quit", "Are you sure?", icon='warning')

        if ans == 'yes':
            #self.destroy()
            self.parent.destroy()

        
#########################################################################
#            Binds Functions
#########################################################################

    def OnFrameConfigure(self, event):
        self.lbCanvas.configure(scrollregion=self.lbCanvas.bbox("all"))


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
