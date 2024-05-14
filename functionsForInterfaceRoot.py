import os
import fitz
import re
import nltk
from nltk.stem import PorterStemmer
import datetime
import tkinter.messagebox

def colorText(canva, keyword):
    start_index = "1.0"
    while True:
        index = canva.search(keyword, start_index, stopindex="end", nocase=True)
        if not index:break
        word_end_index = canva.search(" ", f"{index}+1c", stopindex="end")
        if not word_end_index:
            word_end_index = "end"
        content = canva.get(index, word_end_index)
        uppercase_content = content.upper()
        canva.delete(index, word_end_index)
        canva.insert(index, uppercase_content)
        canva.tag_add("color", index, word_end_index)
        copyIndex = start_index
        start_index = word_end_index
        if start_index == copyIndex:break
    canva.tag_config("color", foreground="red")

def displayText(toDisplay,canva,bot,keyword):
    canva.insert(str(bot.yToPrint),text=toDisplay.strip()+"\n")
    bot.yToPrint += 1.0
  
def findKeyword(keyword, text):
    found_sentences = []
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\n)(?=\s|[A-Z])', text)
    for sentence in sentences:
        if(keyword in PorterStemmer().stem(sentence).upper()):found_sentences.append(sentence)
    if len(found_sentences) == 0:found_sentences = 0
    return found_sentences

def extract_text_from_pdf(pdf_file_path,keyword,filename,bot,date):
    doc = fitz.open(pdf_file_path)
    fontsize=30
    res,outputCreated,outputModified,firstModification,pagesKeyword= "",False,False,True,[]
    outputExists=os.path.isfile(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
    if(outputExists):output=fitz.open(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
    for page in doc:
        page_text = page.get_text()
        lines = page_text.split('\n')
        sanitized_lines = [line for line in lines if not line.strip().isdigit()]
        sanitized_text = '\n'.join(sanitized_lines)
        res += sanitized_text
        if(findKeyword(keyword,sanitized_text)!=0):
            if(not outputExists):
                output=fitz.open()
                outputCreated=True
                outputExists=True
            if(firstModification):
                newPage=output.new_page(len(output))
                textLength = fitz.get_text_length(filename[:30], fontname="helv", fontsize=fontsize)
                newPage.insert_text(fitz.Point((newPage.mediabox.width-textLength)/2,(newPage.mediabox.height-textLength)/2),filename[:30],fontsize=fontsize)
                firstModification=False
            if(page.number not in pagesKeyword):
                pagesKeyword.append(page.number)
                page.clean_contents()
                output.insert_pdf(doc, from_page=page.number, to_page=page.number)
                watermark="{filename}-page {pageNumber}".format(filename=filename[:30],pageNumber=page.number+1)
                output[len(output)-1].insert_text((fitz.get_text_length(watermark, fontname="helv", fontsize=5)/2, 10), watermark)
                outputModified=True
    if(outputCreated):
        output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
        output.close()
    elif(outputModified):
        output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf",incremental=True,encryption=0)
        output.close()
    doc.close()
    return re.sub(r"\n(?![A-Z])", "", res)

def keywordInColor(keyword, sentence,canva,bot):
    modified_sentence = sentence
    modified_sentence = re.sub(r'\b{}\b'.format(re.escape(keyword)), f'{keyword}', modified_sentence, flags=re.IGNORECASE)
    displayText(modified_sentence + "\n",canva,bot,keyword)
    
def extractRoot(bot,canva):
    displayText("Looking for {word} in the database, please wait...\n".format(word=bot.query),canva,bot,[])
    date = str(datetime.datetime.today().replace(microsecond=0)).replace(" ","_").replace(":","_")
    textList,fileList=[],[]
    question=PorterStemmer().stem(bot.query).upper()
    for pathSearch,subdirs,files in os.walk(bot.directory):
        for filename in files:
            if(filename[-4:]!=".pdf"):continue # We only read PDFs, then we do not take into account other formats
            path = os.path.join(pathSearch, filename)
            path=os.path.normpath(path)
            textList.append(extract_text_from_pdf(path,question,filename,bot,date))
            fileList.append(filename)
    if(os.path.isfile(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")):
        output=fitz.open(bot.output+"/BOT_"+bot.query+"_"+date+".pdf")
        for page in output:
            matches=page.search_for(question)
            page.add_highlight_annot(matches)
        output.save(bot.output+"/BOT_"+bot.query+"_"+date+".pdf",incremental=True,encryption=0)
        output.close()
        tkinter.messagebox.showinfo(title="File ready", message="Your file has been saved in "+bot.output+"/COWI_BOT_"+bot.query+"_"+date+".pdf")
    occurrences,usefulFiles=0,[]
    for i in range(len(textList)):
        sentence=findKeyword(question,textList[i])
        if(sentence==0):continue
        else:
            usefulFiles.append(fileList[i])
            displayText("--------------------------------------------------"+fileList[i]+"--------------------------------------------------------------\n",canva,bot,question)
            occurrences+=len(sentence)
            for j in range(len(sentence)):
                keywordInColor(question,sentence[j],canva,bot)
                displayText("\n\n",canva,bot,question)
    displayText("Total occurrences of the keyword found: {occurences}".format(occurences=occurrences),canva,bot,question)
    bot.yToPrint+=3.0
    if(occurrences!=0):
        colorText(canva,question)
        bot.yToPrint+=5.0
    return 1
