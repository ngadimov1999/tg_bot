# -*- coding: utf-8 -*-
"""
Created on Mon May  4 10:46:06 2020

@author: QickKer
"""

import sqlite3
from threading import Lock

class DBHelper:
    
    lock = Lock()

    def __init__(self, dbname="db.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        
    def get_table_info(self, table_name):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(f'pragma table_info ({table_name})')
            data = cur.fetchall()
            return data
            
    def get_flexible_request(self, request_in_str):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(request_in_str)
            data = cur.fetchall()
            return data
        
    def commit(self):
        self.conn.commit()
    
    
    def drop_table(self, table_name):
        del_table = """drop TABLE if exists """+table_name
        with self.lock:
            self.conn.execute(del_table)
        self.conn.commit()

    def setup(self, table_name, column_list):
        columns = ''
        for column in column_list:
            columns+=column+""" text,"""    
        columns = columns[:-1]
        tblstmt = f"""CREATE TABLE IF NOT EXISTS {table_name} ("""
        tblstmt = tblstmt+columns+')'
#        print (tblstmt)
#        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)" 
#        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        with self.lock:
            self.conn.execute(tblstmt)
#        self.conn.execute(itemidx)
#        self.conn.execute(ownidx)
        self.conn.commit()

#        cursor = self.conn.cursor()
#        cursor.execute(f"""SELECT sql FROM sqlite_master
#                        WHERE tbl_name = '{table_name}' AND type = 'table'
#                        """)
#        print (cursor.fetchall())


    def add_item(self, table_name, values, primary_key = None, primary_value = None):
        strValues = ''
        for value in values:
            strValues+="'"+str(value)+"'"+','
        strValues = strValues[:-1]
        insert = f"INSERT into {table_name} VALUES ({strValues})"
        with self.lock:
            if primary_key!=None and primary_value!=None:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT {primary_key} FROM {table_name} WHERE {primary_key} = '{primary_value}'")
#                print (cursor.fetchone())
#                print (f"SELECT {primary_key} FROM {table_name}")
                if cursor.fetchone() is None:    
                    self.conn.execute(insert)
                else:
                    return "Запись уже существует"
            else:
#                print (insert)
                self.conn.execute(insert)
        self.conn.commit()

    def delete_item(self, table_name, column_of_condition, condition):
        stmt = f"DELETE FROM {table_name} WHERE {column_of_condition} = (?)"
        args = (condition, )
        with self.lock:
            self.conn.execute(stmt, args)
        self.conn.commit()

    def get_item(self, description, table_name, column_of_condition, condition):
        stmt = f"SELECT {description} FROM {table_name} WHERE {column_of_condition} = (?) order by {description}"  
        args = (condition, )
#        return (self.conn.execute(stmt,condition))
        with self.lock:
            return [x[0] for x in self.conn.execute(stmt, args)]
    
    def get_all_items(self, table_name, order_by = None):
        stmt = f"SELECT * FROM {table_name}"
        if order_by!=None:
            stmt+= f' order by {order_by}'
        with self.lock:
            return( [x for x in self.conn.execute(stmt)])
        self.conn.commit()

        
    def close_connect(self):
        self.conn.close()
        

    
#        "SELECT " + str(need_clmn) +  "FROM " + str(name_table)  + "WHERE " + str(prmtr2) + """like "%""" + str(need_text) + """%" """
    
    
###1. Инициализация таблицы
###2. Вставить одно объявление(Вставить несколько)
###3. Поиск объявления(ий) (по столбцу/строке/по значению)
###4. Редактирование объявления
###5. Удаление объявления

