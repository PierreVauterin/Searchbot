import os
import fitz
import re
import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import filedialog
import nltk
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
import datetime
import tkinter.messagebox
import time
from progressbar import createProgressBar,findKeyword


def colorText(canva,listKeywords:list[str],search:str) -> None:
    if(search=="root"):
        start_index = "1.0"
        while True:
            index = canva.search(listKeywords[0], start_index, stopindex="end", nocase=True)
            if not index:break
            word_end_index = canva.search(" ", f"{index}+1c", stopindex="end")
            if not word_end_index:word_end_index = "end"
            content = canva.get(index, word_end_index)
            uppercase_content = content.upper()
            canva.delete(index, word_end_index)
            canva.insert(index, uppercase_content)
            canva.tag_add("color", index, f"{index}+{len(listKeywords[0])}c")
            copyIndex = start_index
            start_index = f"{index}+{len(listKeywords[0])}c"
            if start_index == copyIndex:break
    else:
        for keyword in listKeywords:
            start_index = "1.0"
            while True:
                index = canva.search(keyword, start_index, stopindex="end")
                if not index:break
                canva.tag_add("color", index, f"{index}+{len(keyword)}c")
                start_index = f"{index}+{len(keyword)}c"
    canva.tag_config("color", foreground="red") # Maybe find a way to adapt this color to the current color scheme of the window*

def highlightText(bot,date,question) -> None:
    output=fitz.open(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
    for page in output:
        for keyword in question:
            matches=page.search_for(keyword)
            page.add_highlight_annot(matches)
    output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf",incremental=True,encryption=0)
    output.close()

def displayText(toDisplay,canva,bot):
    canva.insert(str(bot.yToPrint),text=toDisplay.strip()+"\n")
    bot.yToPrint += 1.0

def findSynonyms(keyword):
    setKeyword={keyword}
    for syn in wordnet.synsets(keyword): 
        for l in syn.lemmas():setKeyword.add(re.sub("_"," ",l.name().upper()))
    listKeyword=list(setKeyword)
    for val in listKeyword:
        if(val[-1]!="S"):listKeyword.append(val+"S")# So that plurals are detected too
    return listKeyword
        
def formatSentence(keyword:list[str],sentence,canva,bot) -> None:
    modified_sentence = sentence
    for val in keyword:modified_sentence = re.sub(r'\b{}\b'.format(re.escape(val)), f'{val}', modified_sentence, flags=re.IGNORECASE)
    displayText(modified_sentence + "\n",canva,bot)
    
def extract(bot,canva,search:str) -> int:
    displayText("Looking for {word} in the database, please wait...\n".format(word=bot.query),canva,bot)
    textList,fileList=[],[]
    date = str(datetime.datetime.today().replace(microsecond=0)).replace(" ","_").replace(":","_")
    if(search=="root"):
        question=[]
        question.append(PorterStemmer().stem(bot.query).upper())
    else:question=findSynonyms(bot.query)
    createProgressBar(bot,question,date,search,textList,fileList)
    print("Ca continue")
    if(os.path.isfile(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")):
        highlightText(bot,date,question)
        tkinter.messagebox.showinfo(title="File ready", message="Your file has been saved in "+bot.output+"/COWI_BOT_"+bot.query+"_"+date+".pdf")
    else:print("Mais ca plante")
    occurrences,usefulFiles=0,[]
    for i in range(len(textList)):
        sentence=findKeyword(question,textList[i],search)
        if(len(sentence)==0):continue
        else:
            usefulFiles.append(fileList[i])
            displayText("--------------------------------------------------"+fileList[i]+"--------------------------------------------------------------",canva,bot)
            occurrences+=len(sentence)
            for j in range(len(sentence)):
                formatSentence(question,sentence[j],canva,bot)
                displayText("\n\n",canva,bot)
    displayText("Total occurrences of the keyword found: {occurences}".format(occurences=occurrences),canva,bot)
    bot.yToPrint+=3.0
    if(occurrences!=0):
        colorText(canva,question,search)
        bot.yToPrint+=5.0
    return 1
