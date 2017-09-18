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

        self.dir = [None, None]

        self.dirProject = "/"
        self.dirImage = "/"
        self.dirStack = "/"
        self.dirLoadComments = "/"
        self.dirSaveComments = "/"
        self.dirLoadAnnotations = "/"
        self.dirSaveAnnotations = "/"

        if (not os.path.isfile("settings") ):
            file = open("settings","w")
            file.close
            #self.saveSettings()

        if (not os.path.isdir("Projects") ):
            os.makedirs("Projects")
        
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

        #carregando settings (se houver)
        self.loadSettings()

    def loadSettings(self, project_dir = None):

        
        if(project_dir == None):
            file = open("settings","r")

            project_dir = file.read().splitlines()
            
            file.close()

            if len(project_dir) == 0:
                tkinter.messagebox.showwarning("Warning", "There is no project yet.\nPlease, click in OK and create a new project.")
                self.createProj()
                #self.firstProj()
                return
            
            self.dir[0] = project_dir[0]
            self.dir[1] = project_dir[1]
         
        self.users = []
        self.userID = 0

        
        #listUsers = os.listdir(recentProj[0])
        file = open("/".join(self.dir),"r")
        #file = open("C:\\Users\\diego\\Downloads\\TCC\\Projects\\teste\\teste.neuronote","r")
        project = file.read().splitlines()
        #listUsers = file.read
        file.close()

        for i in range(2, 2*int(project[1])+int(project[1])+1, 3) :
            
            if project[0] == project[i]:
                self.userID = len(self.users)
                
            self.users.append( [project[i], project[i+1], project[i+2] ] )

        self.user = self.users[self.userID]
        
        lb = project[2*int(project[1])+int(project[1])+2 : ]
        self.loadComments(lb)

        #listUsers = project[0:-1]
        #listUsers.sort()
        
        '''
        for expert in listUsers:
            #self.users.append(expert.split("gt_")[1])
            self.users.append(expert)

            #if(recentProj[1] == self.users[-1]):
            if(project[0] == self.users[-1]):
                userSelection = len(self.users)-1
        '''
        
        if(len(self.users) > 1):
            self.createWin_choose()
        else:
            if(project_dir == "new" ):
                tkinter.messagebox.showinfo(message="Welcome %s" %(self.user[0]) )
            else:
                tkinter.messagebox.showinfo(message="Welcome back %s" %(self.user[0]) )
            
            self.loadUser()
        
        
        

    def createWin_choose(self):

        tkinter.messagebox.showinfo(message="Opening Project: %s" %(self.dir[1].split(".neuronote")[0] ) )

        chooseWindow= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        chooseWindow.title("Who are you?")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        chooseWindow.geometry('250x110+%d+%d' %(centralized[0], centralized[1]) )
        chooseWindow.resizable(width=False, height=False)
        chooseWindow.focus_force()
        chooseWindow.grab_set()

        chWin_lb = tkinter.Label(chooseWindow, text="What's your name?", anchor="center")
        chWin_lb.grid(row = 0, column = 0, padx = 70)

        chWin_radio = []
        var = tkinter.IntVar()
        for i in range(len(self.users) ):
                
            chWin_radio.append(tkinter.Radiobutton(chooseWindow, text=self.users[i][0], variable = var, value=i) )
            chWin_radio[i]['command'] = lambda radio = var: self.radioSelected(radio)
            chWin_radio[i].grid(row = i+1, column = 0, padx = 70)

        chWin_radio[self.userID].select()
        #self.user = var.get()

        chWin_btnConfirm = tkinter.Button(chooseWindow, text="Confirm", padx=3, bg = "green")
        chWin_btnConfirm['command'] = lambda btn = chooseWindow: self.confirmUser(btn)
        chWin_btnConfirm.grid(row = len(chWin_radio)+2, column = 0, padx = 70)

    def radioSelected(self, param):    
        #self.user = param[0].get
        #self.userID = param[1]
        self.userID = param.get()
        self.user = self.users[self.userID]


    def confirmUser(self, window):
        window.destroy()
        tkinter.messagebox.showinfo(message="Welcome back %s" %(self.user[0]) )
        self.loadUser()
        

    def loadUser(self):
        #lines = project.read().splitlines()
        #direct = "C:/Users/diego/Downloads/TCC/teste_demo/"
        #lines = open(direct + self.user + ".info", "r").read().splitlines()

        #self.dirImage = lines[0]
        #self.lastImage = lines[1]
        self.dirImage = self.user[1]
        self.lastImage = self.user[2]

        if( not (self.dirImage == "/") ):
            self.abrirBatch(self.dirImage)

        #self.loadComments(project)

        #self.dirStack = lines[1]
        #self.dirLoadComments = lines[2]
        #self.dirSaveComments = lines[3]
        #self.dirLoadAnnotations = lines[4]
        #self.dirSaveAnnotations = lines[5]

        self.userTitle = tkinter.Label(self.fUser, text="Users:", padx=3)
        self.userTitle.grid(row=0)

        self.User_radio = []
        self.User_btnRm = []
        var = tkinter.IntVar()
        
        for i in range(0, len(self.users) ):
            
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.users[i][0], variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, bg = "red") )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

            #if(self.user == self.users[i]):
                #self.User_radio[i].select()
        self.User_radio[self.userID].select()

        self.User_btnAdd = tkinter.Button(self.fUser, text="Insert specialist", padx=3, bg = "green", command = self.addUser)
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)


    def rmUser(self,user):
        
        if(self.userID == user ):
            tkinter.messagebox.showwarning("Warning", "You can't remove an active user.\nPlease, change the user and try again.")
            return

        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about deleting this specialist?", icon = "warning")
        if(ans == "no"):
            return

        for i in range(0, len(self.users) ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        name = self.users[user][0]
        del self.users[user]

        var = tkinter.IntVar()

        self.User_btnAdd.grid_remove()
        
        self.User_radio = []
        self.User_btnRm = []
        for i in range(0, len(self.users) ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.users[i][0], variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, bg = "red") )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

            if(self.user[0] == self.users[i][0]):
                #self.User_radio[i].select()
                self.userID = i

        self.User_radio[self.userID].select()
                
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)

        tkinter.messagebox.showwarning("Warning", "Specialist " + name + " has been deleted.")
        
    def addUser(self):
        new = tkinter.simpledialog.askstring("New user", "Insert new user name:", parent = self.parent)

        if(new == None):
            return
        
        for i in range(0, len(self.users) ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        self.users.append([new, "/", "/"])

        #print(self.users)
        #self.users.sort(key=lambda name: name[0][0])
        self.users.sort()
        #print("\n##########\n")
        #print(self.users)
        
        var = tkinter.IntVar()

        self.User_btnAdd.grid_remove()
        
        self.User_radio = []
        self.User_btnRm = []
        for i in range(0, len(self.users) ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.users[i][0], variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, bg = "red", command = self.rmUser) )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

            if(self.user[0] == self.users[i][0]):
                #self.User_radio[i].select()
                self.userID = i

        self.User_radio[self.userID].select()
                
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)

    def userSelected(self, var):

        if(self.userID == var.get() ):
            return
        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about changing user?", icon = "warning")
        if(ans == "yes"):
            self.userID = var.get()
        '''
        for i in range(0, len(self.users) ):
            if(self.user == self.users[i]):
                self.User_radio[i].select()
        '''
        self.User_radio[self.userID].select()

        self.user = self.users[self.userID]

    def saveSettings(self):
        return
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
         
        self.mnuProject = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuProject.add_command(label="Create new project", command=self.createProj)
        self.mnuProject.add_command(label="Open project file", command=self.abrirProj)
        self.mnuProject.add_command(label="Save Project",  command=self.saveProject)
        self.mnuProject.add_command(label="Save Project As", command=self.saveProjectAs)
        self.menuBar.add_cascade(label="Project", menu=self.mnuProject)

        self.mnuArquivo = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuArquivo.add_command(label="Open Image", state = "disabled", command=self.abrir)
        self.mnuArquivo.add_command(label="Open Directory", command=self.abrirBatch)
        #self.mnuArquivo.add_command(label="Save Annotation ", command=self.nada)
        #self.mnuArquivo.add_command(label="Save Comments", state = "disabled", command=self.saveComments)
        #self.mnuArquivo.add_command(label="Save Comments As", command=self.saveCommentsAs)
        #self.mnuArquivo.add_command(label="Load Comments", command=self.loadComments)
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
        self.frameRight = tkinter.Frame(self.parent, bg= "orange")
        self.frameRight.grid(row = 0, column = 1, stick='nswe', ipadx=5)

                
        self.frameLb = tkinter.Frame(self.frameRight, bg="pink")
        #self.fLabel = tkinter.Frame(self.lbCanvas, bg="green")
        self.frameLb.grid(row = 0, stick='nswe', ipadx=5)
        
        self.lbScroll = tkinter.Scrollbar(self.frameLb, orient="vertical")
        self.lbCanvas = tkinter.Canvas(self.frameLb, bg ="green", yscrollcommand=self.lbScroll.set, height=self.parent.winfo_screenheight()/2)#, width= 250)
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

        self.btn_addLb = tkinter.Button(self.fLabel, text="Insert Label", padx=3, command= self.addLb)
        self.btn_rmLb = tkinter.Button(self.fLabel, text="Remove Last Label", padx=3, state = "disabled", command= self.rmLb)
        #self.btn_rmLb = tkinter.Button(self.fLabel, text="Remove Last Label", padx=3, command= self.rmLb)
        
        if(self.dirLoadComments == "/"):
            self.addLb()
            self.addLb()
        else:
            self.loadComments(1)

        
        self.frameUser = tkinter.Frame(self.frameRight, bg="purple")
        self.frameUser.grid(row = 1, stick='nswe', ipadx=5)

        self.userScroll = tkinter.Scrollbar(self.frameUser, orient="vertical")
        self.userCanvas = tkinter.Canvas(self.frameUser, bg ="pink", yscrollcommand=self.userScroll.set)#, width= 250)
        self.userScroll.config(command=self.userCanvas.yview)

        self.fUser = tkinter.Frame(self.userCanvas, bg="gray")
        self.fUser.pack(fill="both", expand=False)

        #120
        self.userCanvas.create_window( 0, 0, window=self.fUser, anchor="nw")
        
        self.userScroll.pack(side="right", fill="y")
        self.userCanvas.pack(side="left", fill="both", expand=True)
        
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

        if(i == 1):
            self.btn_rmLb.configure(state="normal")
            #self.btn_rmLb.grid()

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

        if( len(self.label) == 2) and (flag == None):
            #tkinter.messagebox.showwarning("Warning", "You can't delete all the labels. You need at least one to work!")
            #return
            self.btn_rmLb.configure(state="disabled")
            #self.btn_rmLb.grid_remove()

        for i in range(3):
            self.label[-1][i].destroy()

        del self.lb_comment[-1]
        del self.label[-1]

    def addBind(self):
        ##########
        #Image Bind
        self.canvas.tag_bind("imgTag", "<Button-1>", self.onClick)
        self.canvas.tag_bind("imgTag", "<Motion>", self.motion)

        self.parent.bind("<Next>", self.moveImg)
        self.parent.bind("<Prior>", self.moveImg)

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

    def createProj(self):
        createWin= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        createWin.title("New Project")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        createWin.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.grab_set()

        newWin_lbProj = tkinter.Label(createWin, text="Project Name: ")
        newWin_lbProj.grid(row = 0, column = 0)
        newWin_lbUser = tkinter.Label(createWin, text="Your Username: ")
        newWin_lbUser.grid(row = 1, column = 0)

        newWin_entProj = tkinter.Entry(createWin)
        newWin_entProj.grid(row = 0, column = 1)
        newWin_entUser = tkinter.Entry(createWin)
        newWin_entUser.grid(row = 1, column = 1)

        newUsers = []
        newWin_addUser = tkinter.Button(createWin, text="Insert other specialist", bg="yellow")
        newWin_addUser.grid(row=2, column = 1)

        newWin_btnOK = tkinter.Button(createWin, text="Confirm", padx=3, bg = "green")
        newWin_btnOK['command'] = lambda btn = [newWin_entProj, newWin_entUser, createWin]: self.newWinConfirm(btn)
        newWin_btnOK.grid(row = 3, column = 0)
        
        newWin_btnCancel = tkinter.Button(createWin, text="Cancel", padx=3, bg = "red", command = createWin.destroy)
        newWin_btnCancel.grid(row = 3, column = 1)
        
    def newWinConfirm(self, info):
        if( (len(info[0].get().replace(" ", "") ) == 0) or (len(info[1].get().replace(" ", "") ) == 0) ):
            tkinter.messagebox.showwarning("Warning", "A field name has been left blank.\nEnter a name in the field before proceeding.")
            return

        os.makedirs("Projects/" + info[0].get() )
        file = open("Projects/" + info[0].get() + "/" + info[0].get() + ".neuronote","w")
        file.write(info[1].get() + "\n1\n" + info[1].get() + "\n/\n/\n")
        file.write("1 #ff0000 Comment_1\n2 #00ff00 Comment_2")
        file.flush()
        file.close

        self.dir[0] = "Projects/" + info[0].get()
        self.dir[1] = info[0].get() + ".neuronote"

        info[2].destroy()

        file = open("settings","w")
        file.write(self.dir[0] + "\n" + self.dir[1])
        file.flush()
        file.close
        
        self.loadSettings("new")


    def abrirProj(self):
        filedir = filedialog.askopenfilename(initialdir= os.path.dirname(os.path.realpath(__file__)) + "/Projects/",filetypes = [("NeuroNote Project", "*.neuronote")] )
        #filedir = filedialog.askopenfilename(initialdir = "/Projects",filetypes = [("NeuroNote Project", "*.neuronote")] )

        if(len(filedir) > 0):
            self.dir = os.path.split(filedir)
            
            self.loadSettings(filedir)
        return
    
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
        
        
    def abrirBatch(self, dirname = None):

        if(dirname == None):
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

    def saveProject(self):

        file = open(self.dir[0] + "/" + self.dir[1],"w")

        file.write(self.user[0] + "\n%d\n" %(len(self.users)) )

        for i in range(len(self.users)):
            file.write("%s\n%s\n%s\n" %( self.users[i][0], self.users[i][1], self.users[i][2] ) )

        for i in range(len(self.lb_comment)):
            file.write("%d %s %s\n" %( i+1, self.label[i][2].cget("bg"), self.lb_comment[i].get() ) )

        file.flush()
        file.close()
        

    def saveProjectAs(self):

        res = filedialog.asksaveasfilename(defaultextension=".neuronote", filetypes = ( ("Neuronote Files","*.neuronote"),
                                                         ("All Files", "*.*") ) )

        file = open(res,"w")
        #print(res)

        file.write(self.user[0] + "\n%d\n" %(len(self.users)) )

        for i in range(len(self.users)):
            file.write("%s\n%s\n%s\n" %( self.users[i][0], self.users[i][1], self.users[i][2] ) )

        for i in range(len(self.lb_comment)):
            file.write("%d %s %s\n" %( i+1, self.label[i][2].cget("bg"), self.lb_comment[i].get() ) )

        file.flush()        
        file.close()

        #self.dirSaveComments = res
        #self.saveSettings()

    def loadComments(self, lines):

        """
        if(flag == None):
            ini_dir = self.dirLoadComments.split("/")
            del ini_dir[-1]
            
            res = filedialog.askopenfilename(initialdir= "/".join(ini_dir) + "/" ,filetypes = [ ("Text Files","*.txt") ] )
        else:
            res = self.dirLoadComments

        file = open(res,"r")

        lines = file.read().splitlines()
        """

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

        #self.dirLoadComments = res

        #self.saveSettings()
        #file.close()

        #self.mnuArquivo.entryconfig("Save Comments", state="normal")

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
        if (event.keysym == "Next") or (event.delta < 0) or (event.num == 5):
            if(self.currImg > 0):
                self.currImg = self.currImg - 1
                change = 1
        if (event.keysym == "Prior") or (event.delta > 0) or (event.num == 4):
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
