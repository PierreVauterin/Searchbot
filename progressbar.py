import customtkinter
import sys
import tkinter.messagebox
import time
        
def clicker():
    testProgress.step()
    theLabel.configure(text=testProgress.get())

def update(testProgress,root,label,numberOfFiles): # Consider it is not 0 since we checked with the database
    iterStep=1/numberOfFiles
    progressStep=iterStep
    testProgress.start()
    for i in range(numberOfFiles):
        print("Iteration: ",i)
        testProgress.set(progressStep)
        progressStep+=iterStep
        root.update_idletasks()
        label.configure(text="Files processed: "+str(i+2)+"/"+str(numberOfFiles))
    label.configure(text="Processing finished!")
    onClosing(root,testProgress)

def onClosing(window,testProgress,e=None):
    testProgress.stop()
    window.destroy()
    sys.exit(0)

def createProgressBar():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")
    root=customtkinter.CTk()
    root.title("Test progress bar")
    root.geometry("400x200")
    testProgress=customtkinter.CTkProgressBar(root,orientation="horizontal",
                                              width=300,height=20,corner_radius=100,mode="determinate",determinate_speed=.1,indeterminate_speed=.5,
                                              border_width=.5,border_color="grey",fg_color="white",progress_color="black")
    testProgress.pack(pady=40)
    testProgress.set(0)

    theLabel=customtkinter.CTkLabel(root,text="",font=("Helvetica",18))
    theLabel.pack(pady=10)

    toClickButton=customtkinter.CTkButton(root,text="Click",command=lambda:update(testProgress,root,theLabel,100))
    toClickButton.pack(pady=10)

    root.bind("<Escape>", lambda e: onClosing(root,testProgress))
    root.protocol("WM_DELETE_WINDOW", lambda: onClosing(root,testProgress))
    root.mainloop()

createProgressBar()
