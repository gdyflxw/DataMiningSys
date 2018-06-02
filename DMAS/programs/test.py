import sqlite3
import pandas as pd

conn = sqlite3.connect('D:/CNPY.db')
c = conn.cursor()
cursor = c.execute("select CN,PY from CNPY")

d={}
for row in cursor:
    d[row[0]]=row[1]

def getpy(cn):
    p=''
    for i in cn:
        p+=d[i]
    return p

