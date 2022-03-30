
### Installing

There are two modules that need to be aquired separately:

`UDpipe` (http://ufal.mff.cuni.cz/udpipe), where the executable should be available in swegram_main/handle_texts/pipeline/nlp/udpipe/udpipe. It makes use of an English model, the default path is nlp/udpipe/en/english-ud-2.0-170801.udpipe.

`efselab` (https://github.com/robertostling/efselab), along with the Swedish annotation pipeline, for which instructions can be found in the readme for efselab. The swedish pipeline should be available in swegram_main/handle_texts/pipeline/nlp/efselab/swe_pipeline.py

`unoconv` (https://github.com/unoconv/unoconv), which is used to convert `*.doc`, `*.docx` and many other formats into pure text file.

`LibreOffice` (https://downloadarchive.documentfoundation.org/libreoffice/old/), which is required by `unoconv` to do the convertion. **NOTE If you are debugging on a MacOS computer, using versions from 3.6.0.1 to 4.3.x only.**

### Configuring

swegram/base.py contains settings that are typically shared between production and development environments. It then imports the appropriate configuration, either local.py or production.py. This is based on the system it's running on, if it's Linux, production.py will be imported, otherwise local.py, change this as needed. production.py is not included in the repository; just make a copy of local.py and change the appropriate settings (`DEBUG`, `PRODUCTION`, `SECRET_KEY` etc.). The paths in `swegram_main/config.py` also need to be changed. Also remember to add ALLOWED_HOSTS to production.py.

The templates, `swegram_main/templates/`, and `swegram_main/views.py` contain a few hardcoded URLs, the easiest way would be to search all of them for "swegram" and replace them.

When running with PROTUCTION = True, unoconv (https://github.com/dagwieers/unoconv) is used to automatically convert some formats such as doc to txt (see the annotate_uploaded_file() function in upload_file.py, it's called using subprocess).

A database is required, local.py is configured to use postgres.

By default, LocMemCache is used for caching (for development purposes), but this should be changed to something like Redis or Memcached, or a database cache like postgres.

Remember to check requirements.txt and install anything that's missing.



### Swegram package


#### Import swegram as a module

1. Supported file format
   1. Plain text
2. Supported languages: Swedish and English
3. The main components in Swegram
   1. parse
   2. extract_features
4. Create Dockerfile
   