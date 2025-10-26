```
python3.13 -m venv taxcode
```

```
source taxcode/bin/activate
```

```
pip install -r requirements.txt
```

## Backend

You can run the backend server using uvicorn. 
For development use the following:   
```
uvicorn backend.main:app --reload
```

For deployment use the following:
```
uvicorn backend.main:app
```

## Frontend
Run the Gladio frontend as follows:
````
python frontend/app.py
```

## Preprocessing

The PDFs preprocessing happens offline. Enter the `offline` folder and you have to run the pipeline, with the order:

1. PDF extractor;  
2. MD processing;   
3. Section Chunking;   
4. Page Chunking;    

Pay attention that the PDF extractor does not recognize the headers, so you have to manuallly add `##' to the desired sections and remove any other `#` or `###` or `####`. Sections are splitted based on the indexes.

The chunking is multi-level. First macro level is the pdf (there are three different pdfs), second is section based (based on the index). Inside of the sections happen the real chunking (2000 chars, 200 overlaps). Another check on the pages is performed, such that in the metadata it is possible to add the page reference as well, together with Fascicolo and Section name.