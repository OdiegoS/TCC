# -*- coding: utf-8 -*

import tkinter
import numpy as np
import ProgressBar as pb

from tkinter import filedialog
from tkinter import colorchooser
from tkinter import ttk
from projects import Projects

from tkinter.simpledialog import SimpleDialog
from watershed_flooding import Watershed


class win_main(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self,parent)
        
        self.parent = parent

        self.projects = Projects()
        
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
        self.openSettings()

        self.parent.focus_force()

################################################################################################
########                               Create Menu                                      ########
################################################################################################
    def createMenu(self):
        self.top = self.winfo_toplevel()
        self.menuBar = tkinter.Menu(self.top)
         
        self.mnuProject = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuProject.add_command(label="Create new project", command=self.createProj)
        self.mnuProject.add_command(label="Open project file", command=self.abrirProj)
        self.mnuProject.add_command(label="Save Project",  command=self.saveProject)
        self.mnuProject.add_command(label="Save Project As", command=self.saveProjectAs)
        self.mnuProject.add_separator()
        self.mnuProject.add_command(label="Quit", command=self.sair)
        self.menuBar.add_cascade(label="Project", menu=self.mnuProject)

        self.mnuImage = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuImage.add_command(label="Open Image", command=self.abrir)
        self.mnuImage.add_command(label="Open Stack", command=self.abrirBatch)
        
        self.menuBar.add_cascade(label="Image", menu=self.mnuImage)
 
        self.mnuAnnotation = tkinter.Menu(self.menuBar, tearoff=0)
        self.mnuAnnotation.add_command(label="Clear Annotation", command=self.reset)
        self.mnuAnnotation.add_command(label="Save Annotation", command=self.saveAnnotation)
        self.mnuAnnotation.add_command(label="Export Count", command=self.exportCount)
        self.menuBar.add_cascade(label="Annotation", menu=self.mnuAnnotation)

        self.menuBar.add_cascade(label="Configure", command=self.configure)
 
        mnuAjuda = tkinter.Menu(self.menuBar, tearoff=0)
        mnuAjuda.add_command(label="About", command=self.sobre)
        self.menuBar.add_cascade(label="Help", menu=mnuAjuda)

        self.top.config(menu=self.menuBar)

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

        newWin_btnOK = tkinter.Button(createWin, text="Confirm", padx=3)
        newWin_btnOK['command'] = lambda btn = [newWin_entProj, newWin_entUser, createWin]: self.newWinConfirm(btn)
        newWin_btnOK.grid(row = 3, column = 0)
        
        newWin_btnCancel = tkinter.Button(createWin, text="Cancel", padx=3, command = createWin.destroy)
        newWin_btnCancel.grid(row = 3, column = 1)
        
    def newWinConfirm(self, info):
        if( (len(info[0].get().replace(" ", "") ) == 0) or (len(info[1].get().replace(" ", "") ) == 0) ):
            tkinter.messagebox.showwarning("Warning", "A field name has been left blank.\nEnter a name in the field before proceeding.")
            return

        self.projects.newProject(info[0].get(), info[1].get())

        info[2].destroy()

        self.loadSettings(True)


    def abrirProj(self):
        filedir = filedialog.askopenfilename(initialdir= self.projects.getAppPath() + "/Projects/",filetypes = [("NeuroNote Project", "*.neuronote")] )

        if(len(filedir) > 0):
            self.projects.setProjectPath(filedir)
            
            self.loadSettings()
        return

    def saveProject(self):
        self.projects.saveProject()
        tkinter.messagebox.showwarning("Warning", "Project saved.")
    
    
    def saveProjectAs(self):

        res = filedialog.asksaveasfilename(defaultextension=".neuronote", filetypes = ( ("Neuronote Files","*.neuronote"),
                                                         ("All Files", "*.*") ) )
        self.projects.saveProject(res)
        tkinter.messagebox.showwarning("Warning", "Project saved.")

    def sair(self):
        ans = tkinter.messagebox.askquestion("Quit", "Are you sure?", icon='warning')

        if ans == 'yes':
            self.parent.destroy()
    
    def abrir(self, menu = True):

        #testa se foi chamado pelo menu
        if(menu):
            filedir = filedialog.askopenfilename(initialdir= self.projects.getLastImagePath() ,filetypes = ( ("Jpeg Images", "*.jpg"),
                                                            ("Gif Images","*.gif"),
                                                            ("Png Images","*.png"),
                                                            ("Tiff Images",".*tiff") ) )
                                                            #("All Files", "*.*") ) )
            #testa se o diretório do arquivo está vazio
            if(not filedir):
                return
            
            self.projects.updateImagePaths(filedir)
            self.projects.openImage(self.parent, filedir)
            tkinter.messagebox.showwarning("Warning", "Image loaded.")
        else:
            self.projects.updateImagePaths()
            self.projects.openImage(self.parent)

        self.projects.loadAnnotation()
        self.refresh()
        
    def abrirBatch(self, menu = True):

        if(menu):
            dirname = filedialog.askdirectory(initialdir= self.projects.getLastImagePath())

            if(not dirname):
                return

            limpar = self.projects.openBatch(self.parent, dirname)
            tkinter.messagebox.showwarning("Warning", "All images loaded.")
        else:
            limpar = self.projects.openBatch(self.parent)

        if ( self.projects.getQtdImage() > 0) and (limpar == 0):
            self.projects.loadAnnotation()
            self.refresh()

    def reset(self):
        self.projects.clearImage()
        tkinter.messagebox.showwarning("Warning", "Image(s) cleaned.")
        self.refresh()

    def saveAnnotation(self):
        self.projects.saveAnnotation()
        tkinter.messagebox.showwarning("Warning", "Annotation saved.")

    def exportCount(self):
        path = self.projects.getExportPath()

        res = filedialog.asksaveasfilename(title="Export as ", initialfile="count_"+self.projects.getCurrUserName(), initialdir=path, defaultextension=".txt", filetypes = ( ("Text Files","*.txt"), ("All Files", "*.*") ) )
        if(isinstance(res, str) and res != ""):
            self.projects.exportCount(self.parent, res)
            tkinter.messagebox.showwarning("Warning", "Count exported.")

    def sobre(self):
        pass

    def configure(self):
        createWin= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        createWin.title("Insert new Values")
        centralized = [ (self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55 ]
        createWin.geometry('+%d+%d' %(centralized[0], centralized[1]) )
        createWin.minsize(width=270, height=150)
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.grab_set()

        value_padx = (15,0)
        value_pady = (15,0)

        createWin.newWin_lbX = tkinter.Label(createWin, text="X: ")
        createWin.newWin_lbX.grid(row = 0, column = 0, padx=value_padx)
        createWin.newWin_lbY = tkinter.Label(createWin, text="Y: ")
        createWin.newWin_lbY.grid(row = 1, column = 0, padx=value_padx)
        createWin.newWin_lbZ = tkinter.Label(createWin, text="Z: ")
        createWin.newWin_lbZ.grid(row = 2, column = 0, padx=value_padx)
        createWin.newWin_lbZ = tkinter.Label(createWin, text="Color: ")
        createWin.newWin_lbZ.grid(row = 3, column = 0, padx=value_padx)
        
        createWin.newWin_entX = tkinter.Entry(createWin)
        createWin.newWin_entX.insert(0, self.projects.getWradius()[0])
        createWin.newWin_entX.grid(row = 0, column = 1, padx=value_padx)
        createWin.newWin_entY = tkinter.Entry(createWin)
        createWin.newWin_entY.insert(0, self.projects.getWradius()[1])
        createWin.newWin_entY.grid(row = 1, column = 1, padx=value_padx)
        createWin.newWin_entZ = tkinter.Entry(createWin)
        createWin.newWin_entZ.insert(0, self.projects.getWradius()[2])
        createWin.newWin_entZ.grid(row = 2, column = 1, padx=value_padx)

        createWin.newWin_btnColor = tkinter.Button(createWin, width = 5, bg=self.projects.getWradius()[3])
        createWin.newWin_btnColor['command'] = lambda : self.changeColor(createWin.newWin_btnColor)
        createWin.newWin_btnColor.grid(row = 3, column = 1, padx=value_padx)

        createWin.newWin_lbX = tkinter.Label(createWin, text="Gradient: ")
        createWin.newWin_lbX.grid(row = 4, column = 0, padx=value_padx, pady=value_pady)

        options = ["Morphological", "Sobel", "Sobel 3D"]
        createWin.newWin_op = ttk.Combobox(createWin, values=options, state='readonly')
        createWin.newWin_op.current(options.index(self.projects.grad))
        createWin.newWin_op.grid(row = 4, column = 1, padx=value_padx, pady=value_pady)

        createWin.newWin_op.bind("<<ComboboxSelected>>", lambda event: self.comboEvent(createWin))
        self.comboEvent(createWin)

        createWin.newWin_btnOK = tkinter.Button(createWin, text="Confirm", padx=3)
        createWin.newWin_btnOK['command'] = lambda btn = createWin: self.confirmConfigure(btn)
        createWin.newWin_btnOK.grid(row = 6, column = 0, padx=value_padx, pady=value_pady)
        
        createWin.newWin_btnCancel = tkinter.Button(createWin, text="Cancel", padx=3, command = createWin.destroy)
        createWin.newWin_btnCancel.grid(row = 6, column = 1, padx=value_padx, pady=value_pady)

    def confirmConfigure(self, createWin):
        newWin_entX, newWin_entY, newWin_entZ, newWin_btnColor, newWin_op = [createWin.newWin_entX, createWin.newWin_entY, createWin.newWin_entZ, createWin.newWin_btnColor, createWin.newWin_op]
        if( (len(newWin_entX.get().replace(" ", "") ) == 0) or (len(newWin_entY.get().replace(" ", "") ) == 0) or (len(newWin_entZ.get().replace(" ", "") ) == 0) or (len(newWin_op.get().replace(" ", "") ) == 0)):
            tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="A field name has been left blank.\nEnter a number in the field before proceeding.")
            return

        if( (not newWin_entX.get().isdigit()) or (not newWin_entY.get().isdigit()) or (not newWin_entZ.get().isdigit()) ):
            tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="Please, enter a valid number.")
            return

        if(hasattr(createWin, 'newWin_entPeso')):
            newWin_entPeso = createWin.newWin_entPeso
            if(len(newWin_entPeso.get().replace(" ", "") ) == 0):
                tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="A field name has been left blank.\nEnter a number in the field before proceeding.")
                return
            else:
                campoPeso = newWin_entPeso.get().replace(",", ".")
                try:
                    float(campoPeso)
                except ValueError:
                    tkinter.messagebox.showwarning(parent=createWin,title="Warning", message="Please, enter a valid number.")
                    return
            resp = self.projects.configure(int(newWin_entX.get()), int(newWin_entY.get()), int(newWin_entZ.get()), newWin_btnColor.cget('bg'), newWin_op.get(), campoPeso)
        else:
            resp = self.projects.configure(int(newWin_entX.get()), int(newWin_entY.get()), int(newWin_entZ.get()), newWin_btnColor.cget('bg'), newWin_op.get())

        if(resp):
            if(self.projects.changeGradient(self.parent)):
                self.refresh()

        createWin.destroy()

    def comboEvent(self, createWin):
        if(createWin.newWin_op.get() == "Sobel 3D"):
            createWin.newWin_lbPeso = tkinter.Label(createWin, text="Peso Sobel 3D: ")
            createWin.newWin_lbPeso.grid(row = 5, column = 0, padx=(15,0))
            createWin.newWin_entPeso = tkinter.Entry(createWin)
            createWin.newWin_entPeso.insert(0, self.projects.getSobel3Peso())
            createWin.newWin_entPeso.grid(row = 5, column = 1, padx=(15,0))
        elif(hasattr(createWin, 'newWin_lbPeso')):
            createWin.newWin_lbPeso.destroy()
            del(createWin.newWin_lbPeso)
            createWin.newWin_entPeso.destroy()
            del(createWin.newWin_entPeso)

################################################################################################
########                               Frame Main                                       ########
################################################################################################


    def frameMain(self):
        self.fMain = tkinter.Frame(self.parent)
        self.fMain.grid(row=0, column = 0)


        self.parent.columnconfigure(0, weight=1, minsize=450)

        self.imgScrollVertical = tkinter.Scrollbar(self.fMain, orient="vertical")
        self.imgScrollHorizontal = tkinter.Scrollbar(self.fMain, orient="horizontal")
        self.canvas = tkinter.Canvas(self.fMain, highlightthickness=10, scrollregion=(0,0,100,100), xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)

        self.imgScrollVertical.config(command=self.canvas.yview)
        self.imgScrollHorizontal.config(command=self.canvas.xview)
        

        self.imgScrollVertical.pack(side="right", fill="y")
        self.imgScrollHorizontal.pack(side="bottom", fill="x")
        self.canvas.pack(fill='both', expand=True)

################################################################################################
########                               Frame Status                                     ########
################################################################################################

    def frameStatus(self):
        self.fStatus = tkinter.Frame(self.parent)
        self.fStatus.grid(row = 1, column = 0, stick='nswe', columnspan=2)

        self.status = tkinter.Label(self.fStatus, text="", bd=1,relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')

        self.status.x = -1
        self.status.y = -1

################################################################################################
########                               Frame Label                                      ########
################################################################################################

    def frameLabel(self):
        self.frameRight = tkinter.Frame(self.parent)
        self.frameRight.grid(row = 0, column = 1, stick='nswe', ipadx=5)


        self.parent.columnconfigure(1, weight=1, minsize=300)
        self.frameRight.rowconfigure(0, weight=1, minsize=170)
        self.frameRight.columnconfigure(0, weight=1)
        self.frameRight.rowconfigure(1, weight=1, minsize=130)
                
        self.frameLb = tkinter.Frame(self.frameRight)
        self.frameLb.grid(row = 0, stick='nswe', ipadx=5)

        self.lbScrollVertical = tkinter.Scrollbar(self.frameLb, orient="vertical")
        self.lbScrollHorizontal = tkinter.Scrollbar(self.frameLb, orient="horizontal")
        self.lbCanvas = tkinter.Canvas(self.frameLb, xscrollcommand=self.lbScrollHorizontal.set, yscrollcommand=self.lbScrollVertical.set, height=self.parent.winfo_screenheight()/2)#, width= 250)
        self.lbScrollVertical.config(command=self.lbCanvas.yview)
        self.lbScrollHorizontal.config(command=self.lbCanvas.xview)

        self.fLabel = tkinter.Frame(self.lbCanvas)
        self.fLabel.pack(fill="both", expand=False)

        self.lbCanvas.create_window( 0,0, window=self.fLabel, anchor="nw")
        
        self.lbScrollVertical.pack(side="right", fill="y")
        self.lbScrollHorizontal.pack(side="bottom", fill="x")
        self.lbCanvas.pack(side="left", fill="both", expand=True)

        self.lb_comment = []
        self.label = []
        self.labelTitle = []

        self.labelTitle.append(tkinter.Label(self.fLabel, text="Label", relief='raised', padx=3, border=0))
        self.labelTitle[0].grid(row=0, column = 0, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Comments", relief='raised', padx=3, border=0))
        self.labelTitle[1].grid(row=0, column = 1, ipady=10)
        self.labelTitle.append(tkinter.Label(self.fLabel, text="Mark Color", relief='raised', padx=3,border=0))
        self.labelTitle[2].grid(row=0, column = 2, ipady=10)

        self.btn_addLb = tkinter.Button(self.fLabel, text="Insert Label", padx=3, command= self.addLb)
        self.btn_rmLb = tkinter.Button(self.fLabel, text="Remove Last Label", padx=3, state = "disabled", command= self.rmLb)

        self.addLb()
        self.addLb()
        
        self.frameUser = tkinter.Frame(self.frameRight)
        self.frameUser.grid(row = 1, stick='nswe', ipadx=5)

        self.userScrollVertical = tkinter.Scrollbar(self.frameUser, orient="vertical")
        self.userScrollHorizontal = tkinter.Scrollbar(self.frameUser, orient="horizontal")
        self.userCanvas = tkinter.Canvas(self.frameUser, xscrollcommand=self.userScrollHorizontal.set, yscrollcommand=self.userScrollVertical.set)#, width= 250)
        self.userScrollVertical.config(command=self.userCanvas.yview)
        self.userScrollHorizontal.config(command=self.userCanvas.xview)

        self.fUser = tkinter.Frame(self.userCanvas)
        self.fUser.pack(fill="both", expand=False)

        self.userCanvas.create_window( 0, 0, window=self.fUser, anchor="nw")
        
        self.userScrollVertical.pack(side="right", fill="y")
        self.userScrollHorizontal.pack(side="bottom", fill="x")
        self.userCanvas.pack(side="left", fill="both", expand=True)

        self.User_radio = []
        self.User_btnRm = []

        self.userTitle = tkinter.Label(self.fUser, text="Users:", padx=3)
        self.userTitle.grid(row=0, ipady = 10)

        self.User_btnAdd = tkinter.Button(self.fUser, text="Insert specialist", padx=3, command = self.addUser)

    def addLb(self, load = None):

        i = len(self.label)
        self.label.append( [ [],[],[] ] )

        if(i == 1):
            self.btn_rmLb.configure(state="normal")

        if(load == None):
            self.lb_comment.append(tkinter.StringVar())
            self.lb_comment[i].set("Comment_%d" %(i+1) )

            color = self.projects.getNextColor(i)

            if(self.projects.getQtdLabel() > 0):
                self.projects.addLabel(self.lb_comment[i].get(), color)
        else:
            self.lb_comment.append(tkinter.StringVar())
            self.lb_comment[i].set(load[0])

            color = load[1]

        self.label[i][0] = tkinter.Button(self.fLabel, text="%d" %(i+1), padx=3)
        self.label[i][0]['command'] = lambda : self.selectLb(None, i)
        self.label[i][0].grid(row=i+1, column = 0, ipady=5)

        self.label[i][1] = tkinter.Button(self.fLabel, textvariable=self.lb_comment[i], padx=3, command=lambda:self.commentLb(i))
        self.label[i][1].grid(row=i+1, column = 1, ipady=5)

        self.label[i][2] = tkinter.Button(self.fLabel, text="Color", padx=3, bg=color)
        self.label[i][2]['command'] = lambda : self.changeColor(self.label[i][2], i)
        self.label[i][2].grid(row=i+1, column = 2, ipady=5)
        
        self.btn_addLb.grid(row=i+2, column = 0, ipady=5)
        self.btn_rmLb.grid(row=i+2, column = 2, ipady=5)

    def commentLb(self, i):

        comment = tkinter.simpledialog.askstring("Editing Comment", "Comment:", initialvalue = self.lb_comment[i].get(), parent=self.parent)

        if(comment == None):
            return

        if (len(comment.replace(" ", "")) == 0):
            tkinter.messagebox.showwarning("Warning", "Comments can't be empty.\n")
            return

        self.lb_comment[i].set(comment)
        self.projects.setLabelComment(i, comment)

    def rmLb(self, flag = None):

        if( len(self.label) == 2) and (flag == None):
            self.btn_rmLb.configure(state="disabled")

        for i in range(3):
            self.label[-1][i].destroy()

        del self.lb_comment[-1]
        del self.label[-1]

        if(flag == None):
            self.projects.removeLabel()

    def changeColor(self, btn, i = None):
        color = colorchooser.askcolor()

        if(color[1] == None):
            return
            
        btn.configure(bg=color[1])
        if(i == None): return
        self.projects.setLabelColor(i, color[1])

    def addUser(self):
        new = tkinter.simpledialog.askstring("New user", "Insert new user name:", parent = self.parent)

        if(new == None):
            return

        if (len(new.replace(" ", "")) == 0):
            tkinter.messagebox.showwarning("Warning", "The user name can't be empty.\n")
            return
        
        for i in range(0, self.projects.getQtdUser() ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        self.projects.addUser(new)

        var = tkinter.IntVar()

        self.User_btnAdd.grid_remove()
        
        self.User_radio = []
        self.User_btnRm = []
        for i in range(0, self.projects.getQtdUser() ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(i), variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3, command = self.rmUser) )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

        self.User_radio[ self.projects.getCurrUserID() ].select()
                
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)

    def userSelected(self, var):

        if( self.projects.isCurrUser(var.get()) ):
            return
        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about changing user?", icon = "warning")
        if(ans == "yes"):
            self.projects.setCurrUser(var.get())
            self.loadUser()
            
        self.User_radio[ self.projects.getCurrUserID() ].select()

    def loadUser(self):

        self.projects.updateImagePaths()
        self.projects.updateCurrImg("load")
        

        if( self.projects.existImagePaths() ):
            
            if( self.projects.isBatchImg() ):
                self.abrirBatch(False)
            else:
                self.abrir(False)
        else:
            self.parent.title("Teste")
            self.status.configure(text=(""))
            self.canvas.delete("imgTag")
            self.canvas.delete("maskTag")

        for i in range(0, len(self.User_radio) ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        self.User_radio = []
        self.User_btnRm = []

        var = tkinter.IntVar()
        
        for i in range(0, self.projects.getQtdUser() ):
            
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(i), variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3) )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

        self.User_radio[ self.projects.getCurrUserID() ].select()

        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0, ipady=5)

    def rmUser(self,user):
        
        if( self.projects.isCurrUser(user) ):
            tkinter.messagebox.showwarning("Warning", "You can't remove an active user.\nPlease, change the user and try again.")
            return

        ans = tkinter.messagebox.askquestion("Warning", "Are you sure about deleting this specialist?", icon = "warning")
        if(ans == "no"):
            return

        for i in range(0, self.projects.getQtdUser() ):
            self.User_radio[i].destroy()
            self.User_btnRm[i].destroy()

        self.projects.removeUser(user)

        var = tkinter.IntVar()

        self.User_btnAdd.grid_remove()
        
        self.User_radio = []
        self.User_btnRm = []
        for i in range(0, self.projects.getQtdUser() ):
            self.User_radio.append(tkinter.Radiobutton(self.fUser, text=self.projects.getUserName(i), variable = var, value=i) )
            self.User_radio[i]['command'] = lambda radio = var : self.userSelected(radio)
            self.User_radio[i].grid(row = i+1, column = 0)

            self.User_btnRm.append(tkinter.Button(self.fUser, text="Remove", padx=3) )
            self.User_btnRm[i]['command'] = lambda btn = i: self.rmUser(btn)
            self.User_btnRm[i].grid(row = i+1, column = 1)

        self.User_radio[ self.projects.getCurrUserID() ].select()
                
        self.User_btnAdd.grid(row = len(self.User_radio)+2, column = 0)

        tkinter.messagebox.showwarning("Warning", "Specialist " + self.projects.getUserName(user) + " has been deleted.")


################################################################################################
########                               Add Bind                                         ########
################################################################################################

    def addBind(self):
        self.canvas.shiftPress = False
        ##########
        #Image Bind
        self.canvas.tag_bind("maskTag", "<Button-1>", self.onClick)
        self.canvas.tag_bind("maskTag", "<Motion>", self.motion)

        self.parent.bind("<Next>", self.moveImg)
        self.parent.bind("<Prior>", self.moveImg)

        self.parent.bind("<MouseWheel>", self.moveImg) #Windows
        self.parent.bind("<Button-4>", self.moveImg) #Linux
        self.parent.bind("<Button-5>", self.moveImg) #Linux

        self.parent.bind("<F2>", self.showHideMask)
        self.parent.bind("<F3>", self.showHideGrad)
        ##########

        #Label Bind
        
        for i in range(10):
            self.parent.bind(str(i), self.selectLb)
            self.parent.bind("<KP_" + str(i) + ">", self.selectLb) #Linux - Numpad

        
        self.fMain.bind("<Configure>", self.OnFrameConfigureImg)
        self.fLabel.bind("<Configure>", self.OnFrameConfigureLabel)
        self.fUser.bind("<Configure>", self.OnFrameConfigureUser)

        self.parent.bind("<plus>", self.zoom)
        self.parent.bind("<minus>", self.zoom)
        self.parent.bind("<KP_Add>", self.zoom) #Linux - Numpad
        self.parent.bind("<KP_Subtract>", self.zoom) #Linux - Numpad

        self.canvas.tag_bind("maskTag", "<Shift-ButtonPress-3>", self.buttonPress)
        self.canvas.tag_bind("maskTag", "<Shift-B3-Motion>", self.buttonMove)

        self.canvas.tag_bind("maskTag", "<ButtonRelease-3>", self.buttonRelease)

    def onClick(self, event):

        if( (event.x < 10) or (event.y < 10)):
            return

        if( (event.x > (self.canvas.winfo_width() - 10)) or (event.y > (self.canvas.winfo_height() - 10)) ):
            return

        x = int(self.canvas.canvasx(event.x) / self.projects.getImgScale())
        y = int(self.canvas.canvasy(event.y) / self.projects.getImgScale())

        if( (x < 0) or (y < 0) ):
            return

        limite = [(self.canvas.bbox("imgTag")[2] / self.projects.getImgScale()) - 1, (self.canvas.bbox("imgTag")[3] / self.projects.getImgScale()) - 1]
        if( (x > limite[0]) or (y > limite[1]) ):
            return

        if ( self.projects.getSelectedLb() < 0 ):
            print("não está selecionado")
            return

        colorHex = self.projects.getLabels(self.projects.getSelectedLb())[1]

        colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

        print ("%d, %d" %(x, y) )

        mask = self.projects.getMask(self.projects.getCurrImgID())
        annotation = self.projects.getAnnotation(self.projects.getCurrImgID())

        tam = self.projects.getWradius()

        progressBar = pb.Loading(self.parent)

        coord = self.projects.applyWatershed([x,y], progressBar)

        limite_x = max(0, x-tam[0])
        limite_y = max(0, y-tam[1])

        z_start = max(0, self.projects.getCurrImgID() - tam[2])
        z_end = min(self.projects.getQtdImage()-1, self.projects.getCurrImgID() + tam[2]) + 1

        for i in range(z_start,z_end):
            if(len(coord[0]) > 0):
                for c in coord[0]:
                    m = self.projects.getMask(i)
                    a = self.projects.getAnnotation(i)
                    m.putpixel( (limite_x + c[0], limite_y + c[1]), colorRGB )
                    a.putpixel( (limite_x + c[0], limite_y + c[1]), self.projects.getSelectedLb() + 1)
                self.projects.setMask(i, m)
                self.projects.setAnnotation(i, a)
            del(coord[0])
                
        progressBar.close()
        self.paint()

    def motion(self, event):

        if( (event.x < 10) or (event.y < 10)):
            return

        if( (event.x > (self.canvas.winfo_width() - 10)) or (event.y > (self.canvas.winfo_height() - 10)) ):
            return

        self.eventX = event.x
        self.eventY = event.y

        x = self.canvas.canvasx(event.x) / self.projects.getImgScale()
        y = self.canvas.canvasy(event.y) / self.projects.getImgScale()

        if( (x < 0) or (y < 0) ):
            return

        limite = [ (self.canvas.bbox("imgTag")[2] / self.projects.getImgScale()) - 1, (self.canvas.bbox("imgTag")[3] / self.projects.getImgScale()) - 1]

        if( (x > limite[0]) or (y > limite[1]) ):
            return

        self.status.x = x
        self.status.y = y

        tam = [ self.projects.getWradius()[0] * self.projects.getImgScale(), self.projects.getWradius()[1] * self.projects.getImgScale() ]
        self.canvas.coords(self.canvas.rect, self.canvas.canvasx(event.x)-tam[0], self.canvas.canvasy(event.y)-tam[1], self.canvas.canvasx(event.x)+tam[0], self.canvas.canvasy(event.y)+tam[1])
        self.canvas.itemconfigure(self.canvas.rect, outline = self.projects.getWradius()[3])
        
        self.updateStatus()

    def moveImg(self, event):
        change = 0
        if (event.keysym == "Next") or (event.delta < 0) or (event.num == 5):
            if( self.projects.getCurrImgID()  > 0):
                self.projects.updateCurrImg("sub")
                change = 1
        if (event.keysym == "Prior") or (event.delta > 0) or (event.num == 4):
            if self.projects.getCurrImgID() < self.projects.getQtdImage()-1:
                self.projects.updateCurrImg("add")
                change = 1
        if change == 1:
            self.refresh()

    def showHideMask(self, event):
        self.projects.changeMaskClean()
        self.paint()

    def showHideGrad(self, event):
        self.projects.changeGradImg()
        self.paint()

    def selectLb(self, event, click = None):
        if(click == None):
            if(event.keysym[0] == 'K'):
                key = int(event.keysym.split('_')[1]) - 1
            else:
                key = int(event.keysym) - 1
        else:
            key = click

        if(key == -1):
            key = 9

        if(key >= self.projects.getQtdLabel()):
            return
        
        if( (self.projects.getSelectedLb() > -1) and (self.projects.getSelectedLb() != key) ):
            self.label[self.projects.getSelectedLb()][0].configure(relief='flat')
            self.label[self.projects.getSelectedLb()][1].configure(relief='flat')
            self.label[self.projects.getSelectedLb()][2].configure(relief='flat')
            
            
        self.label[key][0].configure(relief='solid')
        self.label[key][1].configure(relief='solid')
        self.label[key][2].configure(relief='solid')

        self.projects.setSelectedLb(key)

    def OnFrameConfigureImg(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def OnFrameConfigureLabel(self, event):
        self.lbCanvas.configure(scrollregion=self.lbCanvas.bbox("all"))

    def OnFrameConfigureUser(self, event):
        self.userCanvas.configure(scrollregion=self.userCanvas.bbox("all"))

    def zoom(self,event):
        if( (event.keysym == "plus") or (event.keysym == "KP_Add") ):
            res = self.projects.increaseImgScale()
        else:
            res = self.projects.decreaseImgScale()

        if(res):
            self.redraw(True)

    def buttonPress(self, event):
        self.canvas.scan_mark(event.x, event.y)

        self.canvas.shiftPress = True

    def buttonMove(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def buttonRelease(self, event):
        if(self.canvas.shiftPress):
            self.canvas.shiftPress = False
            return
        tam = self.projects.getWradius()
        coord_x = [max(0, int(self.canvas.canvasx(event.x) / self.projects.getImgScale()) - tam[0]), min(self.projects.getDimensionCurrImg()[0], int(self.canvas.canvasx(event.x) / self.projects.getImgScale()) + tam[0]) ]
        coord_y = [max(0, int(self.canvas.canvasy(event.y) / self.projects.getImgScale()) - tam[1]), min(self.projects.getDimensionCurrImg()[1], int(self.canvas.canvasy(event.y) / self.projects.getImgScale()) + tam[1]) ]
        coord_z = [max(0, self.projects.getCurrImgID() - tam[2]), min(self.projects.getQtdImage(), self.projects.getCurrImgID() + tam[2] + 1) ]

        colorHex = self.projects.getLabels(self.projects.getSelectedLb())[1]
        colorRGB = tuple(int(colorHex.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

        for z in range(coord_z[0], coord_z[1]):
            for i in range(coord_x[0], coord_x[1]):
                for j in range (coord_y[0], coord_y[1]):
                    m = self.projects.getMask(z)
                    a = self.projects.getAnnotation(z)
                    if(m.getpixel((i, j))[:-1] == colorRGB):
                        m.putpixel( (i, j), (0,0,0,0) )
                        a.putpixel( (i, j), 0 )
            self.projects.setMask(z, m)
            self.projects.setAnnotation(z, a)

        self.paint()

################################################################################################
########                               Open Settings                                    ########
################################################################################################

    def openSettings(self):
        self.projects.openSettings()
        
        if( not self.projects.isProjectExist() ):
            tkinter.messagebox.showwarning("Warning", "There is no project yet.\nPlease, click in OK and create a new project.")
            self.createProj()
            return
        self.loadSettings()

    def loadSettings(self, new = False):

        if (not self.projects.isRecentProjectExist()):
            tkinter.messagebox.showwarning("Warning", "Recent project not found.\nPlease, click in OK and create a new project or open an existing project.")
            self.chooseAction()
            return

        self.projects.loadSettings()

        if( self.projects.getQtdUser()  > 1):
            self.createWin_choose()
        else:
            self.loadUser()
            self.loadComments()
            self.selectLb(None, 0)
            if( new ):
                msg = "Welcome "
            else:
                msg = "Welcome back "
            tkinter.messagebox.showinfo(message=msg + self.projects.getCurrUserName() )

    def chooseAction(self):
        createWin = tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge')
        createWin.title("")
        centralized = [(self.parent.winfo_screenwidth() // 2) - 175, (self.parent.winfo_screenheight() // 2) - 55]
        createWin.geometry('+%d+%d' % (centralized[0], centralized[1]))
        createWin.minsize(100,100)
        createWin.resizable(width=False, height=False)
        createWin.focus_force()
        createWin.grab_set()

        createWin.grid_columnconfigure(0, minsize=50)
        createWin.grid_columnconfigure(3, minsize=50)

        btnNewProject = tkinter.Button(createWin, text="Create a new project")
        btnNewProject.grid(row=2, column=1)
        createWin.grid_rowconfigure(btnNewProject, minsize=50)

        btnOpenProject = tkinter.Button(createWin, text="Open a project")
        btnOpenProject.grid(row=4, column=1)
        createWin.grid_rowconfigure(btnOpenProject, minsize=50)

        btnNewProject['command'] = lambda btn=[createWin, True]: self.choooseActionEvent(btn)
        btnOpenProject['command'] = lambda btn=[createWin, False]: self.choooseActionEvent(btn)

    def choooseActionEvent(self, param):

        if(param[1]):
            self.createProj()
        else:
            self.abrirProj()

        param[0].destroy()
    
    def createWin_choose(self):

        tkinter.messagebox.showinfo(message="Opening Project")

        topChooseWindow= tkinter.Toplevel(self.parent, borderwidth=4, relief='ridge' )
        topChooseWindow.title("Who are you?")
        topChooseWindow.resizable(width=False, height=False)
        topChooseWindow.focus_force()
        topChooseWindow.grab_set()

        self.canvasWin = tkinter.Canvas(topChooseWindow)
        chooseWindow = tkinter.Frame(self.canvasWin)
        vsb = tkinter.Scrollbar(topChooseWindow, orient="vertical", command=self.canvasWin.yview)
        hsb = tkinter.Scrollbar(topChooseWindow, orient="horizontal", command=self.canvasWin.xview)
        self.canvasWin.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.canvasWin.pack(side="left", fill="both", expand=True)
        self.canvasWin.create_window((0, 0), window=chooseWindow, anchor="nw", tags="chooseWindow")

        chooseWindow.bind("<Configure>", self.onChooseWindowConfigure)

        chWin_lb = tkinter.Label(chooseWindow, text="What's your name?", anchor="center")
        chWin_lb.grid(row = 0, column = 0, padx = 52)

        chWin_radio = []
        var = tkinter.IntVar()
        for i in range(self.projects.getQtdUser()):
                
            chWin_radio.append(tkinter.Radiobutton(chooseWindow, text=self.projects.getUserName(i), variable = var, value=i) )
            chWin_radio[i]['command'] = lambda radio = var: self.radioSelected(radio)
            chWin_radio[i].grid(row = i+1, column = 0, padx = 52)

        chWin_radio[ self.projects.getCurrUserID() ].select()
        
        chWin_btnConfirm = tkinter.Button(chooseWindow, text="Confirm", padx=10)
        chWin_btnConfirm['command'] = lambda btn = topChooseWindow: self.confirmUser(btn)
        chWin_btnConfirm.grid(row = len(chWin_radio)+2, column = 0, padx = 52, pady = 10)

        screen_width = self.parent.winfo_screenwidth() / 2
        screen_height = self.parent.winfo_screenheight() / 2

        size = [topChooseWindow.winfo_reqwidth(), topChooseWindow.winfo_reqheight()]
        x = screen_width - (size[0] / 2)
        y = screen_height - (size[1] / 2)

        if( (size[0] + x) < 824):
            size[0] = size[0] + 824 - (size[0] + x)

        if( i < 4):
            size[1] = size[1] - (50 - ((i-1) * 22))
        topChooseWindow.geometry("%dx%d+%d+%d" % (size[0], size[1], x, y))

    def onChooseWindowConfigure(self, event):
        self.canvasWin.configure(scrollregion=self.canvasWin.bbox("all"))

    def radioSelected(self, param):    
        self.projects.setCurrUser(param.get())

    def confirmUser(self, window):
        self.canvasWin = None
        del(self.canvasWin)
        window.destroy()
        tkinter.messagebox.showinfo(message="Welcome back %s" %(self.projects.getCurrUserName()) )
        self.loadUser()
        self.loadComments()
    
    def loadComments(self):
        
        self.btn_rmLb.configure(state="disabled")


        for i in range(len(self.label) ):
            self.rmLb(1)

        del self.lb_comment[:]
        self.lb_label = []

        for i in range( self.projects.getQtdLabel() ):
            self.addLb( self.projects.getLabels(i) )

################################################################################################
########                                                                                ########
################################################################################################

    def refresh(self):
        self.canvas.delete("all")

        if(self.projects.getImgScale() != 1):
            self.redraw()
            return

        dimensionImg = self.projects.getDimensionCurrImg()

        self.canvas.config(width=dimensionImg[0], height=dimensionImg[1] )
        self.canvas.image = self.projects.getCurrImg()
        self.canvas.mask = self.projects.getCurrMask()

        tam = [ int(dimensionImg[0] / 2), int(dimensionImg[1] / 2) ]

        self.canvas.imgID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.image, tags="imgTag")
        self.canvas.maskID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.mask, tags="maskTag")
        self.canvas.pack(fill='both', expand=True)

        self.dX = 0
        self.dY = 0
        
        if( self.projects.isBatchImg() ):
            self.projects.updateUserImg()

        self.updateStatus()
        self.parent.title("Teste (%s)" %self.projects.getPathCurrImg() )
        tam = [ self.projects.getWradius()[0] * self.projects.getImgScale(), self.projects.getWradius()[1] * self.projects.getImgScale() ]
        self.canvas.rect = self.canvas.create_rectangle(self.status.x-tam[0], self.status.y-tam[1], self.status.x+tam[0], self.status.y+tam[1], outline = self.projects.getWradius()[3])

    def redraw(self, zoom = False):
        self.canvas.delete("all")

        dimensionImg = self.projects.getDimensionCurrImg()

        size = int(self.projects.getImgScale() * dimensionImg[0]), int(self.projects.getImgScale() * dimensionImg[1])
        
        self.canvas.image = self.projects.getCurrImgResize(size)
        self.canvas.mask = self.projects.getCurrMaskResize(size)

        tam = [ int(size[0] / 2), int(size[1] / 2)]

        self.canvas.config(width=size[0], height=size[1])

        self.canvas.imgID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.image, tags="imgTag")
        self.canvas.maskID = self.canvas.create_image(tam[0], tam[1], image=self.canvas.mask, tags="maskTag")

        self.dX = 0
        self.dY = 0

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.config(xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)

        self.canvas.pack(fill='both', expand=True)

        if(zoom):
            coord = [(self.status.x * self.projects.getImgScale() + 1) / size[0], (self.status.y * self.projects.getImgScale() + 1) / size[1]]

            self.canvas.xview_moveto(coord[0])
            self.canvas.yview_moveto(coord[1])

            self.imgScrollHorizontal.update()
            self.imgScrollVertical.update()

            tamScroll = [self.imgScrollHorizontal.get()[1] - self.imgScrollHorizontal.get()[0], self.imgScrollVertical.get()[1] - self.imgScrollVertical.get()[0] ]
            valor = [10,10]

            if ((tamScroll[0] + coord[0]) > 1.0):
                valor[0] = int((tamScroll[0] + coord[0] - 1.0) * size[0])
                valor[0] = int(valor[0])

            if( (tamScroll[1] + coord[1]) > 1.0):
                valor[1] = int((tamScroll[1] + coord[1] - 1.0) * size[1])
                valor[1] = int(valor[1])

            self.canvas.scan_mark(valor[0], valor[1])
            self.canvas.scan_dragto(self.eventX, self.eventY, 1)

        self.updateStatus()
        tam = [ self.projects.getWradius()[0] * self.projects.getImgScale(), self.projects.getWradius()[1] * self.projects.getImgScale() ]
        rec_x = self.status.x * self.projects.getImgScale()
        rec_y = self.status.y * self.projects.getImgScale()
        self.canvas.rect = self.canvas.create_rectangle(rec_x-tam[0],  rec_y-tam[1], rec_x+tam[0],  rec_y+tam[1], outline = self.projects.getWradius()[3])

    def paint(self):

        dimensionImg = self.projects.getDimensionCurrImg()

        size = int(self.projects.getImgScale() * dimensionImg[0]), int(self.projects.getImgScale() * dimensionImg[1])
        self.canvas.image = self.projects.getCurrImgResize(size)
        self.canvas.mask = self.projects.getCurrMaskResize(size)

        self.canvas.itemconfigure(self.canvas.imgID, image=self.canvas.image)
        self.canvas.itemconfigure(self.canvas.maskID, image=self.canvas.mask)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.config(xscrollcommand=self.imgScrollHorizontal.set, yscrollcommand=self.imgScrollVertical.set)

        self.canvas.pack(fill='both', expand=True)

    def updateStatus(self):
        if (self.projects.isBatchImg()):
            self.status.configure(text=("X: %d \t Y: %d \t Z: %d / %d \t\t Scale: %d%%" % (self.status.x, self.status.y, self.projects.getCurrImgID() + 1, self.projects.getQtdImage(), self.projects.getImgScale() * 100)))
        else:
            self.status.configure(text=("X: %d \t Y: %d \t\t Scale: %d%%" % (self.status.x, self.status.y, self.projects.getImgScale() * 100)))

#########################################################################
#########################################################################
if __name__ == "__main__":
    root = tkinter.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title('Teste')

    root.minsize(750,340)
    
    app = win_main(root)
    app.mainloop()
