```
python -m venv taxcode
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

