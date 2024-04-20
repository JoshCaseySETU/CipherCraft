import mysql.connector

 
def databaseConnect(query, data=None, fetchone=False):
    dbPara = {
        'host': 'localhost',        
        'port': 3333,               
        'database': 'CipherCraft',      
        'user': 'root',        
        'password': 'root'
    }
    
    connection = None
    result = None
    
    try: 
        connection = mysql.connector.connect(**dbPara)

        if connection.is_connected():
            print("Connected to the database successfully!")
            
            
            cursor = connection.cursor()
            cursor.execute(query, data) 
            
            if fetchone:
                result = cursor.fetchone() 
            else:
                result = cursor.fetchall()  
                          
            connection.commit()    
            cursor.close()

    except mysql.connector.Error as e:
        print(f"Error: Unable to connect to the database.\n{e}")
 
    finally:
        if connection.is_connected():
            print("Closing the database connection.")
            connection.close()
    
    return result
