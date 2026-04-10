import mysql.connector

cnx = mysql.connector.connect(
    user='thiagoceron',
    password='1234',
    host='localhost',  
    database='teste'
)

if cnx.is_connected():
    print("Conectado")

cnx.close()