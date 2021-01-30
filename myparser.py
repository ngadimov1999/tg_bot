# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 16:18:20 2020

@author: QickKer
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:03:15 2020

@author: QickKer
"""
import request as Sqr
import re
#import dbhelper as db
import datetime
import json as js
import os
import urllib.request
from time import sleep
from tqdm.contrib.telegram import tqdm, trange
#from tqdm import trange

#os.chdir("C:\\Users\\QickKer\\Desktop\\Универ\\прога\\Кинопоиск\\Kinoporn")

class Parser:
   
    url = 'https://www.kinopoisk.ru/index.php?kp_query='
    host = 'https://www.kinopoisk.ru/'
    page_part = '&p='
    
    start_time = ''
    stop_time = ''
    
    queue = []
    
    
    def __init__(self, token, chat_id):
        self.start_time = datetime.datetime.now().strftime("%H:%M")
#        print (f'Время начала: {self.start_time}')
        
        self.queue.append(1)
        
        self.token = token
        self.chat_id = chat_id 
        
       
        

#        self.stop_time = datetime.datetime.now().strftime("%H:%M")
#        print (f'Время окончания: {self.stop_time}')
        
        
    def getMaxActorInfo(self,name):
        if len(self.queue) <= 5:
            self.make_search(name)
            actor_params = self.getActorParams()
            actor_id = actor_params[0]
            self.driver.get(self.host+'name/'+actor_id)
            tbody = self.driver.find_element_by_class_name("info")
            table = tbody.find_elements_by_tag_name('tr')
            dict_ = {}
            for row in table:
                td = row.find_elements_by_tag_name("td")
                dict_.update({td[0].text: td[1].text})
            
            image = self.driver.find_element_by_class_name('film-img-box')
            img = image.find_element_by_tag_name("img")
            url = img.get_attribute('src')
            img = urllib.request.urlopen(url).read()
            out = open("temp\\actor.jpg", "wb")
            out.write(img)
            out.close()
            self.queue.pop(0)
            self.driver.close()
            return dict_
        else:
            self.error()
        
       
    def error(self):
        self.queue.pop(0)
        return("К сожалению, сейчас сервер перегружен. Попробуйте через 30 минут.")
        
        
    def get_graph(self,name, deep = 1):
        if len(self.queue)<=3:
            self.make_search(name)
            self.actor = []
            actor_params = self.getActorParams()
            if type(actor_params)!= str:
                actor_id = actor_params[0] 
                name = actor_params[1]
                actor = self.createActor(actor_id, name)
                filename = actor_id+"_"+str(deep)   
                if filename+'.json' not in os.listdir('actors'):
        #            self.dfs(deep, actor,filename)
                    self.dfs(deep, actor, visited = [])
                    self.write_json(self.actor,filename)
                    self.queue.pop(0)
                    return ('Сейчас появится граф!'), filename
                    
                else:
                    self.driver.close()
                    return ("Актер имеется в базе. Сейчас нарисуем! Отрисовка может занять несколько минут"), filename
            else:
                return ("Вероятно, мы не смогли найти подходящий для тебя вариант. Попробуй всё заново!")                   
        else:
            self.error()
        self.driver.close()
            
    
    def dfs(self, deep, actor, visited = []): 
        
        
#        print (f"Проверим, парсили ли мы актера №{actor['actor_id']}")
        if actor['actor_id'] not in visited:
#            print ("Проверили, парсим")
            self.actor.append(actor)
            visited.append(actor['actor_id'])
            actor['relations'] = self.get_relations(actor)
            
            if deep > 1:
                deep -= 1
                for r in actor['relations']:
                    actor = r
                    self.dfs(deep = deep, actor = actor, visited = visited)
                    
#    def bfs(self, deep, actor, visited = [], queue = []):
#        
#        if actor['actor_id'] not in visited:
#            visited.append(actor['actor_id'])
#            actor['relations'] = self.get_relations(actor)
#            for element in actor['relations']:
#                if element['actor_id'] not in queue:
#                    queue.append(element['actor_id'])
#            
#            queue.pop(0)
#            
#            if queue:
#                self.bfs(deep, queue[0], visited, queue)
#        return visited
    
                              
    
    def write_json(self,obj,filename):
        with open(f"actors\\{filename}.json", 'w') as f:
            js.dump(obj,f, ensure_ascii=False)
    
    def make_search(self,name):
        self.driver = Sqr.Request(self.url).driver
        name = name.replace(' ','+')
        link = self.url+name
        self.driver.get(link)

    def getActorParams(self):
        try:
            most_wanted = self.driver.find_element_by_css_selector('.most_wanted')
            if re.search('актер', most_wanted.text) or re.search('актриса', most_wanted.text):
                data_id = most_wanted.find_element_by_xpath("//a[@data-id]").get_attribute("data-id")
                actor_name = most_wanted.find_element_by_class_name("name").text[:-5]
                return data_id, actor_name
            else:
                return "Это не актер. Введите еще раз"
        except:
            return 'По результатам поиска ничего не найдено. Введите еще раз'
    
    def getCorrectName(self, name):
        self.make_search(name)
        name = self.getActorParams()
        return name
        
    def get_relations(self, actor):
        relations = []
        link = self.host+'name/'+actor['actor_id']+'/relations/'
        self.driver.get(link) 

        tbody = self.driver.find_elements_by_tag_name("tr")
        
        category = None
#        try:
        for i in tqdm(range(8, len(tbody)-5), token = self.token, chat_id = self.chat_id, desc = actor['name']):
#            for i in trange(8, len(tbody)-5, desc = actor['name'], leave = False):
            if tbody[i].text:
#                    print (f"В таблице relations парсим {i} строку из {len(tbody)-5}")
                if re.search(r'\d',tbody[i].text):
                    splitline = tbody[i].text.split()
                    name = splitline[1]+" "+splitline[2]
                    filmCount = re.search(r'\d',splitline[-1]).group(0)
                    data_id = tbody[i].find_element_by_class_name("all").get_attribute('href').split('/')[-2]
                    actor = self.createActor(data_id,name,category,filmCount)
                    relations.append(actor)              
                else:
                    category = tbody[i].text
        return relations
#        except:
#            return None
        
    def createActor(self,actor_id,name,category= None,films = 0,relations=[]):
        if actor_id == None:
            print ("Актер не создан. Проверьте actorId")
            return None
        actor = {"actor_id":actor_id,
                 "name":name,
                 "films":films,
                 "category": category,
                 "relations":relations}
        return actor

    
#%%
#a = Parser(333,3).get_graph('Егор Крид',3)

#with tqdm(total=100) as pbar:
#    for i in range(10):
#        sleep(0.1)
#        pbar.update(1)
#        
#    for i in range(40):
#        sleep(0.1)
#        pbar.update(1)
    
        


    