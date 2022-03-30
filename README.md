# swegram
SWEGRAM: Annotation and Analysis of English and Swedish Texts!


# Swegram as a module

```
import swegram as sg

# parse texts in a folder
texts = sg.parse(FILE_PATH, LANGUAGE='en')

# parse a text 
text_obj = sg.parse(FILE_PATH, FILE_NAME, LANGUAGE)

# output the annotated file in a separate file. 
text_obj.to_txt()

# get the paragraphs and sentences
paragraphs = text_obj.paragraphs
sentences = text_obj.sentences

# output the statistics
text_obj.stats2csv(level='')
text_obj.stats2txt(level='')
text_obj.stats2json(level='')

```
