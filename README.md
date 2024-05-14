# Main changes

The V3 improved the following points:
- Reworking of the output: the output file is not an HTML file anymore, it is now a PDF made with all the pages in which the keyword has been found. Pages are added in the same order as in the document, and a page containing only the (cropped) name of the file from which the following pages are from separates one file from another, allowing clear transitions between different files' pages. A watermark has also been added at the top of each page.
- The search will now be performed in subdirectories (and so on) contained in the database.
- Changed the output file name from "output.pdf" to "BOT_QUERY_YEAR-MONTH-DAY_HOUR_MINUTE_SECONDS.pdf"
- You will not get a notification when the file has been created
- The version of the Searchbot is now indicated in the name of the window
- Small performances improvements

# Bug solving:

- The query will continue if the output folder has not been specified. It will be set to the database directory by default
- Fixed the blank separation page appearing instead of the page with the name of the file in some cases
- Fixed the watermark behaviour
