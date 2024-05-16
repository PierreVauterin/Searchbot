import customtkinter
import os
from fileHandling import extract_text_from_pdf

def clicker():
    testProgress.step()
    theLabel.configure(text=testProgress.get())

def onClosing(window,e=None):window.quit()

def createProgressBar(bot,keywords,date,search,textList,fileList):
    customtkinter.set_appearance_mode(bot.colorTheme[0])
    customtkinter.set_default_color_theme(bot.colorTheme[1])
    root=customtkinter.CTk()
    root.title("Test progress bar")
    root.geometry("400x200")
    testProgress=customtkinter.CTkProgressBar(root,orientation="horizontal",
                                              width=300,height=20,corner_radius=100,mode="determinate",determinate_speed=.1,indeterminate_speed=.5,
                                              border_width=.5,border_color="grey",fg_color=("black","white"),progress_color="blue")
    testProgress.pack(pady=40)
    testProgress.set(0)
    theLabel=customtkinter.CTkLabel(root,text="",font=("Helvetica",18))
    theLabel.pack(pady=10)
    root.after(100,lambda:processFiles(testProgress, root, theLabel,bot,keywords,date,search,textList,fileList)) # Maybe time this
    root.protocol("WM_DELETE_WINDOW", lambda: onClosing(root))
    root.mainloop()
    root.destroy()

def processFiles(testProgress,root,label,bot,keywords,date,search,textList,fileList): # Consider it is not 0 since we checked with the database
    iterStep=1/bot.numberFiles
    progressStep=iterStep
    testProgress.start()
    i=0
    for pathSearch,subdirs,files in os.walk(bot.directory):
        for filename in files:
            if(filename[-4:]!=".pdf"):continue # We only read PDFs, then we do not take into account other formats
            i+=1
            path = os.path.join(pathSearch, filename)
            path=os.path.normpath(path)
            textList.append(extract_text_from_pdf(path,keywords,filename,bot,date,search))
            fileList.append(filename)
            testProgress.set(progressStep)
            progressStep+=iterStep
            root.update_idletasks()
            label.configure(text="Files processed: "+str(i)+"/"+str(bot.numberFiles))
    testProgress.stop()
    onClosing(root)
