import tkinter.messagebox
import customtkinter
from tkinter import filedialog
from search import extract
import os
import sys

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Bot:
    def __init__(self, directory, query,yToPrint,output,numberFiles,colorTheme):
        self.directory=directory
        self.query=query
        self.yToPrint=yToPrint
        self.output=output
        self.numberFiles=numberFiles
        self.colorTheme=colorTheme
        
def searchDir(bot,botDirectoryLabel):
    tkinter.Tk().withdraw()
    bot.directory=filedialog.askdirectory(title="Indicate database directory")
    try:
        fileCount=0
        for root,directories,files in os.walk(bot.directory):
            for file in files:
                if file.endswith(".pdf"):fileCount+=1
        if(fileCount==0):
            tkinter.messagebox.showerror("No PDFs", "There are no PDF files in this directory, please choose another directory")
            bot.directory=""
        else:
            bot.numberFiles=fileCount
            bot.output=filedialog.askdirectory(title="Indicate folder to save output in")
    except FileNotFoundError:bot.directory=""
    if(bot.output==""):bot.output=bot.directory
    botDirectoryLabel.configure(text="Directory chosen: "+bot.directory)

def getQuery(entryField,bot,displayField,button):
    bot.query=entryField.get().upper()
    if(bot.query!="" and bot.directory!=""):
        displayField.configure(state="normal") # We unlock the text field so that the function can write inside
        displayField.delete("1.0","end") #We remove everything that was written, so that we do not have to scroll to see the new results
        if(button.get()=="Synonyms"):extract(bot,displayField,"synonyms")
        else:extract(bot,displayField,"root")
        displayField.configure(state="disabled") # We lock it after so that the text will not be modified accidentally
    elif(bot.query!="" and bot.directory==""):tkinter.messagebox.showerror("No database selected", "Please choose a database directory before sending a query")
    elif(bot.query=="" and bot.directory!=""):tkinter.messagebox.showerror("No keyword given", "Please write a query before sending it")
    else:tkinter.messagebox.showerror("No keyword and no database", "Please write a query and choose a database directory before sending a query")
    
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        bot = Bot("", "", 1.0,"",0,["Light","blue"])
        # configure window
        self.title("Search bot V4.0")
        self.geometry(f"{1200}x{600}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Options", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=lambda mode: self.change_appearance_mode_event(mode,bot))
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.search_label = customtkinter.CTkLabel(self.sidebar_frame, text="Type of search:", anchor="w")
        self.search_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.search_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Synonyms", "Root search"])
        self.search_optionemenu.grid(row=2, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        botDirectoryLabel = customtkinter.CTkLabel(master=self,text="No database directory selected for now",fg_color="transparent")
        botDirectoryLabel.grid(row=2, column=1, columnspan=2, padx=(20, 0), pady=(10, 10), sticky="nsew")
        
        selectDirectory = customtkinter.CTkButton(master=self,text="Select database & output folder",fg_color="#3A7EBF", border_width=2, text_color="white", command=lambda: searchDir(bot, botDirectoryLabel))
        selectDirectory.grid(row=2, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Please enter the keyword here",fg_color=("grey90","black"))
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        
        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="#3A7EBF", border_width=2, text_color="white",text="Send query",command=lambda: getQuery(self.entry, bot,self.textbox,self.search_optionemenu))
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.textbox = customtkinter.CTkTextbox(self, width=250,height=450,state="disabled",border_color="grey",border_width=2,fg_color=("white","black"))
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # set default values
        self.appearance_mode_optionemenu.set("Light")
        self.search_optionemenu.set("Synonyms")

        # Set shortcuts
        self.bind("<Escape>", lambda e: self.onClosing(self))
        self.protocol("WM_DELETE_WINDOW", lambda: self.onClosing(self))
        self.bind("<Return>", lambda e: getQuery(self.entry,bot,self.textbox,self.search_optionemenu))

    def change_appearance_mode_event(self, new_appearance_mode: str, bot):
        bot.colorTheme[0]=new_appearance_mode
        customtkinter.set_appearance_mode(new_appearance_mode)
        
    def onClosing(self,e=None):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            sys.exit(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
