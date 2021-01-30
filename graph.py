import networkx as nx
import matplotlib.pyplot as plt
import json
import asyncio

#%%
# ПРОВЕРИТЬ ПРАВИЛЬНОСТЬ ДИРЕКТОРИЙ!

class Graph():
    def __init__(self, filename, films_count):
        #Тут вставить путь до папки с json файлами, проверьте двойные палочки \\  
        with open (f'actors\\{filename}') as f:
            self.jsonka = json.load(f)
             
            self.G = nx.Graph()  
            
            self.profess_list = {}
            self.colors = ['black','red','green','cyan','magenta','yellow','blue','orange','brown','pink','black','purple','springgreen','plum','teal','aqua','indigo','slategray','peru', 'linen','tomato','darkred','coral','khaki','gold','lime']
            self.list_categories = []
            self.labels_edges = {}
            
            self.get_categories()
            self.add_colors()
#            self.print_colors()
            self.create_nodes(films_count)
            self.create_graph(filename)


#извлекаем категории
    def get_categories(self):
        for el in self.jsonka:
            for i in range(len(el['relations'])):
                category = el['relations'][i]['category']
                if category not in self.list_categories:
                    self.list_categories.append(el['relations'][i]['category'])
            
            
#добавляем цвета к категориям   
    def add_colors(self):
        for i in range(len(self.list_categories)):
            my_color = self.colors[i]
            self.profess_list.update({self.list_categories[i]:my_color})
            
#            my_color = random.choice(self.colors)
#            self.colors.remove(my_color)
#            self.profess_list.update({i:my_color})
    


#Принтим пользователю обозначение цветов
    def print_colors(self): 
        profess_info = 'Профессия: Цвет на графе' + '\n'
#        print('Профессия',':','Цвет на графе')
        for i in range(len(self.profess_list)):       
            values = list(self.profess_list.values())[i]
            keys = list(self.profess_list.keys())[i]
            profess_info += f'{keys}: {values}' + '\n'
        print('Тут должно быть что-то')
        print(profess_info)
        return profess_info
        
#            print(values,':',keys)

#        print(self.profess_list)

#строим граф   
    def create_nodes(self, films_count):  
        for el in (self.jsonka):
            name = el['name']
            for i in range(len(el['relations'])):
                connection = el['relations'][i]['name']
                
                category = el['relations'][i]['category']
                films = el['relations'][i]['films']
                if films >= str(films_count):
                    self.labels_edges.update({(name,connection):films})
                    
                list_edges = []
                
                
                self.list_categories.append(category)
        
                if category in self.profess_list and films >= str(films_count):
                    category_color = self.profess_list[category]
                    list_edges.append((name,connection,{'color': category_color}))
                    self.G.add_edges_from(list_edges)
#        print(list_edges)        
#        print(self.labels_edges)
    

    def create_graph(self,filename):
        pos = nx.spring_layout(self.G)
        
        fig=plt.figure(figsize=(100,100))
        
        colors = nx.get_edge_attributes(self.G,'color').values()
        
        nx.draw_networkx(self.G, pos, label = 'NetworkX', width=1, linewidths=1,
        node_size=80, node_color='orange',alpha=0.6, arrows = False, with_labels = True, edge_color = colors)
        
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels = self.labels_edges, font_color='black', edge_color=colors, label_pos = 0.5, font_size = 8)
        
        plt.axis('off')
        save_file = filename.split('.')[0]
        
        #Тут вставить путь до папки куда будет складываться Граф!
        plt.savefig(f'graphs\\{save_file}.png')
 


        #plt.show()



#%%
    
#a = Graph('4183472_1.json','1')
        

        

        