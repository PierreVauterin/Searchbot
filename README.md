# Presentation

This is the Searchbot, a small tool which makes researches in large databases faster. You can ask it to search keyword occurrences in a database composed of any number of files and folders you want, and it will output the search on its screen and in a PDF file composed of all the pages of the documents in which the keyword appears in.
This tool is still in active development, if you encounter issues, or if you have requests, feal free to create an issue on this repository, and I will do my best to tackle it.

# Installation

To download the code, you can either clone the repository, which allows you to easily get the updates, or download the ZIP archive (click on the green "Code" button and then "Download ZIP"). Then, you can run the requirements.txt file to install all the libraries. To run it, go in the command prompt, and then type: pip install -r requirements.txt
You can now run main.py, and the Searchbot will work correctly!

# How to use it

Sending a query to the bot is made in 3 steps:
- Choose the type of search you want (Synonym or Root search)
- Enter the keyword you are looking for in the query field
- Choose both database directory and output directory

# Current limitations

Here is a list of the limitations of the tool, which will be tackled by the following updates:
- Only PDFs files are being scanned by the tool
- Password-protected PDF will simply be skipped by the software
