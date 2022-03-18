+++
title = "list_tcc"
chapter = false
weight = 100
hidden = false
+++

## Summary

This uses the Python `sqlite` library to query TCC databases and return the contents.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

## Usage

```
list_tcc
```

## Detailed Summary
With the relevant access, Medusa uses the `sqlite` library to query the contents of either the Root or user-specific TCC databases. This is then formatted by a browser script in the UI.

```Python
    def list_tcc(self,task_id,tcc=True, db="/Library/Application Support/com.apple.TCC/TCC.db"):
        import sqlite3

        with sqlite3.connect(db) as con:
            columns = []
            for row in con.execute('PRAGMA table_info("access")'):
                columns.append(row)

            tcc = []
            for row in con.execute('SELECT * FROM "access"'):
                tcc.append(row)
            results = []
            for entry in tcc:
                line={}
                count = 0 
                for ent in entry:
                    if columns[count][2] == "BLOB" and ent != None:
                        line[columns[count][1]] = base64.b64encode(ent).decode()
                    else: line[columns[count][1]] = str(ent)
                    count+=1
                results.append(line)

            tcc_results = {}
            tcc_results["entries"] = results
            return { "tcc": results }

```