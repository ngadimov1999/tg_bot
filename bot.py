import telebot
import config
import random
import myparser
import sqlite3
import dbhelper
from telebot import types
import datetime
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import graph
import time
listOfFav = []  #нужен только для кнопки "добавить в избранное" из функции drawgraph
bot = telebot.TeleBot(config.TOKEN)  #нужен токен бота
count = 0
admins = [275645967, 720669823, 341859359]  #список админов
superAdmin = [341859359]  #суперадмин

@bot.message_handler(commands=['start'])
def Welcome(message):
    # отправка стикера
    sti = open('стикеры/hello.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)

    #создание юзера и баз данынх
    db=dbhelper.DBHelper('server.db')
#    db.drop_table('favorites')
#    db.drop_table('users')
#    db.setup('favorites',['id','actorName'])
#    db.setup('users',['id','name','lastActive', 'inviteDate','category'])
  
    check_user = db.get_item('id','users','id',message.chat.id)
    if check_user == []:
        user_id = message.chat.id
        name = message.chat.first_name
        date = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M")
#        lastActive 
#        print (name,date)
#        db.add_item('users',f'{user_id},{name},{date},{date},user')
        values = [user_id,name,date,date,'user']
        db.add_item('users',values, primary_key = 'id', primary_value = user_id)
#        db.get_table_info('users')
#    print (db.get_all_items('users'))
    
#    db.add_item('users','')

    #кнопки под полем ввода
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item_graph = types.KeyboardButton("Построить граф 📊")
    item_favor = types.KeyboardButton("Избранное 🌟")
    a = message.chat.id
#    print (message.chat.id)
#_____________________________________ADMIN_________________________________________
    request = f"SELECT category FROM users WHERE id = {a}"
    bd = dbhelper.DBHelper(dbname="server.db")
    bdRequest = bd.get_flexible_request(request)
    bd.commit()
    if bdRequest[0][0] == "admin":
        item_admin = types.KeyboardButton("Статистика ‍📊")
        markup.add(item_admin)
    if bdRequest[0][0] == "superadmin":
        item_admin = types.KeyboardButton("Статистика ‍📊")
        item_superAdmin = types.KeyboardButton("Редактировать админов ‍👾")
        markup.add(item_admin, item_superAdmin)
#___________________________________________________________________________________
    #добавление кнопок
    markup.add(item_graph, item_favor)
# ______________________________Приветствие__________________________________
    bot.send_message(message.chat.id, "Привет, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный чтобы помочь тебе построить социальный граф актера!".format(message.from_user, bot.get_me()),
        parse_mode='html', reply_markup=markup)

#_________________________________
@bot.message_handler(commands=["setadmin"])
def answer(message):
    try:
        command = message.text.split(" ")[1]
        if command == "123456":
            user_id = message.chat.id
            request = f"UPDATE users SET category = 'admin' WHERE id = {user_id}"
            bd = dbhelper.DBHelper(dbname="server.db")
            bdRequest = bd.get_flexible_request(request)
            bd.commit()
    except:
        return

@bot.message_handler(commands=["setsuperadmin"])
def answer(message):
    try:
        command = message.text.split(" ")[1]
        if command == "123456":
            user_id = message.chat.id
            request = f"UPDATE users SET category = 'superadmin' WHERE id = {user_id}"
            bd = dbhelper.DBHelper(dbname="server.db")
            bdRequest = bd.get_flexible_request(request)
            bd.commit()
    except:
        return

cf = []




def DrawGraph2(message):
    cf.append(message.text)
    print('da ', message.text)
    return message.text




# def getStat

def drawGraph(message):  #функция где строится граф


    isFormat = message.text.split(',')
    if len(isFormat)!= 2:
        msg = bot.send_message(message.chat.id, 'Попробуй еще раз. Формат: Имя Фамилия, глубина')
        bot.register_next_step_handler(msg, drawGraph)  #askSource
        return
    if type(isFormat[0])!= str:
        msg = bot.send_message(message.chat.id,'Актер должен быть актером! ;)')
        bot.register_next_step_handler(msg, drawGraph) #askSource
        return
    try:
        isFormat[1] = int(isFormat[1])
    except:
        msg = bot.send_message(message.chat.id,'Глубина задается числом, попробуй еще раз')
        bot.register_next_step_handler(msg, drawGraph) #askSource
        return
    if len(isFormat[0].split()) < 2:
        msg = bot.send_message(message.chat.id,'Проверь фио актера и попробуй еще раз!')
        bot.register_next_step_handler(msg, drawGraph) #askSource
        return

    msg = bot.send_message(message.chat.id,
                           f'Актер, которого парсим: <b>{isFormat[0].title()}</b>.\nПарсим до колена №{str(isFormat[1])}',
                           parse_mode='html')

    msg = bot.send_message(message.chat.id, 'Введите количество фильмов, по которым хотите отфильтровать граф')
    bot.register_next_step_handler(msg, DrawGraph2)
    mistake = myparser.Parser(token=config.TOKEN, chat_id=message.chat.id).get_graph(isFormat[0], isFormat[1])




    if re.search(r'\d', mistake[1]):


        file_json = mistake[1] + ".json"
        done_graph = graph.Graph(file_json, cf[0])  # сюда надо передать количество фильмов
        cf.clear()
        prof_colors = done_graph.print_colors()
        colors_msg = bot.send_message(message.chat.id, prof_colors)

        filename = mistake[1]

        file_png = filename + '.png'
        img = open(f'graphs\\{file_png}', 'rb')

        msg = bot.send_message(message.chat.id, mistake[0])
        bot.send_document(message.chat.id, img)





    # здесь типа выводится граф
    listOfFav.append(message.text.split(",")[0])

    # print(listOfFav)
    markup = types.InlineKeyboardMarkup()
    item_addFav = types.InlineKeyboardButton("Добавить", callback_data="weKnowName")
    item_no = types.InlineKeyboardButton("Нет", callback_data="No")
    markup.add(item_addFav, item_no)
    bot.send_message(message.chat.id, "Добавить в избранное?", reply_markup=markup)



    

def addAdmin(message):
    user_id = message.chat.id
    request = f"UPDATE users SET category = 'admin' WHERE id = {user_id}"
    bd = dbhelper.DBHelper(dbname="server.db")
    bdRequest = bd.get_flexible_request(request)
    bd.commit()
    bot.send_message(message.chat.id, "Ок!")

def delAdmin(message):
    user_id = message.chat.id
    ser_id = message.chat.id
    request = f"UPDATE users SET category = 'user' WHERE id = {user_id}"
    bd = dbhelper.DBHelper(dbname="server.db")
    bdRequest = bd.get_flexible_request(request)
    bd.commit()
    bot.send_message(message.chat.id, "Ок!")

@bot.message_handler(content_types = ['text'])
def Basic(message):
    
    if message.chat.type == 'private':
        request1 = f"SELECT category FROM users WHERE id = {message.chat.id}"
        bd = dbhelper.DBHelper(dbname="server.db")
        bdRequest = bd.get_flexible_request(request1)
        bd.commit()

        db=dbhelper.DBHelper('server.db')
        date = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M")
        db.get_flexible_request(f"UPDATE users SET lastActive = '{date}' where id = '{message.chat.id}'")
#        print (db.get_all_items('users'))
        
        #_________________________________Прстроить граф___________________________________
        if message.text == "Построить граф 📊":
            msg = bot.send_message(message.chat.id, "Введите имя актера и глубину в формате: Имя Фамилия, глубина")
            reply = bot.register_next_step_handler(msg, drawGraph)

        # ________________________________Вывод избранных__________________________________
        elif message.text == "Избранное 🌟":
            userID = message.chat.id

            markup = types.InlineKeyboardMarkup()

            request = f"SELECT actorName FROM favorites WHERE id = {userID}"

            bd = dbhelper.DBHelper(dbname="server.db")
            bdRequest = bd.get_flexible_request(request)
            bd.commit()
            #отправка стикера
            sti = open('стикеры/favorites.tgs', 'rb')
            bot.send_sticker(message.chat.id, sti)
            #кнопки под сообщением с избранным
            item_addFav = types.InlineKeyboardButton("Добавить", callback_data="addFav")
            item_delFav = types.InlineKeyboardButton("Удалить", callback_data="delFav")
            item_more = types.InlineKeyboardButton("Подробнее", callback_data="more")
            if bdRequest == []:
                listToSend = "Ваш список избранных пуст!"
                markup.add(item_addFav)
            else:
                listToSend=""
                for i in range(len(bdRequest)):
                    listToSend +=f"{i+1}. " + bdRequest[i][0] + "\n"
                markup.add(item_addFav, item_delFav, item_more)

            #список избранных
            bot.send_message(message.chat.id, listToSend, parse_mode="html", reply_markup=markup)
            
        elif message.text == "Статистика ‍📊":
            for admin in admins:
                if admin == message.chat.id:
                    markup = types.InlineKeyboardMarkup()
                    item_newUsers = types.InlineKeyboardButton("Новые пользователи", callback_data="new_users")
                    item_active = types.InlineKeyboardButton("Активности", callback_data="active")
                    item_baza = types.InlineKeyboardButton("База данных", callback_data="baza")
                    markup.add(item_newUsers,item_active,item_baza)
                    bot.send_message(message.chat.id, 'Выбери тип статистики',reply_markup = markup)

        elif message.text == "Редактировать админов ‍👾" and bdRequest[0][0] == "superadmin":
            # супер-админ
            markup = types.InlineKeyboardMarkup()
            item_addAdm = types.InlineKeyboardButton("Добавить", callback_data="addAdmin")
            item_delAdm = types.InlineKeyboardButton("Удалить", callback_data="delAdmin")
            markup.add(item_addAdm, item_delAdm)
            bot.send_message(message.chat.id, "Удалить или добавить админа?", reply_markup=markup)

        #____________________________ответ на неотхваченные слова__________________________
        else:
            a = random.randint(0, 10)
            if a == 0:
                bot.send_message(message.chat.id, "Я не знаю что даже и ответить...")
            elif a == 1:
                bot.send_message(message.chat.id, "Не могу печатать, у меня клешни")
            elif a == 2:
                bot.send_message(message.chat.id, "Окей))")
            elif a == 3:
                bot.send_message(message.chat.id, "Понятно")
            elif a == 4:
                bot.send_message(message.chat.id, "Прикольно)")
            elif a == 5:
                bot.send_message(message.chat.id, "Давай как-нибудь потом")
            elif a == 6:
                bot.send_message(message.chat.id, "Извини, я не расслышал")
            elif a == 7:
                bot.send_message(message.chat.id, "🤔")
            elif a == 8:
                bot.send_sticker(message.chat.id, open('стикеры/hmmm.tgs', 'rb'))
            elif a == 9:
                bot.send_photo(message.chat.id, open('фоточки/catfish.jpg', 'rb'))
            elif a == 10:
                bot.send_message(message.chat.id, "Извини, немного занят")
                bot.send_photo(message.chat.id, open('фоточки/sorry.jpg', 'rb'))
        #_________________________________________________________________________________

def addFav(message):  #функция добавления в избранное
    user_id = message.chat.id
    listOfFav.append(message.text)
    actorName = " ".join(listOfFav)
    bot.send_message(message.chat.id, "Секунду!")
    actorName = myparser.Parser(token=config.TOKEN, chat_id=message.chat.id).getCorrectName(actorName)
    listOfFav.clear()
    db = dbhelper.DBHelper("server.db")
    res = db.add_item("favorites", [user_id, actorName[1]], primary_key="actorName", primary_value=actorName[1])
    if res:
        bot.send_message(message.chat.id, res)
    if not res:
        bot.send_message(message.chat.id, "Ок!")

def addFavIfWeKnow(message, actor):
    # sql.execute("""CREATE TABLE IF NOT EXISTS favorites (
    #         id TEXT,
    #         actorName TEXT
    #     )""")
    # bd.setup(table_name="favorites", column_list=["id", "actorName"])

    user_id = message.chat.id

    actorName = " ".join(listOfFav)
    listOfFav.clear()
    db = dbhelper.DBHelper("server.db")
    # sql.execute("INSERT INTO favorites VALUES (?, ?)", (user_id, actor))

    res = db.add_item("favorites", [user_id, actorName], primary_key="actorName", primary_value=actorName)
    if res:
        bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, "Ок!")

def delFav(message):  #функция удаления из избранного
    bd = dbhelper.DBHelper("server.db")
    listOfFavorites = bd.get_flexible_request(f"SELECT * FROM favorites WHERE id = '{message.chat.id}'")
    if re.search(r"\D", message.text):
        msg = bot.send_message(message.chat.id, "Вы ввели не цифру. Введите ещё раз")
        bot.register_next_step_handler(msg, delFav)
    else:
        if len(listOfFavorites) < int(message.text):
            msg = bot.send_message(message.chat.id, "Вы ввели неправильное число. Введите ещё раз")
            bot.register_next_step_handler(msg, delFav)
            return
        actorForDelete = listOfFavorites[int(message.text) - 1][1]
        bd.delete_item("favorites", "actorName", actorForDelete)
        bot.send_message(message.chat.id, "Ок!")

    # listOfFav.append(message.text)
    # actorName = " ".join(listOfFav)
    # actorName = myparser.Parser(token=config.TOKEN, chat_id=message.chat.id).getCorrectName(actorName)
    # listOfFav.clear()
    # здесь происходит удаление(троллинг)
    # user_id = message.chat.id
    # db = dbhelper.DBHelper("server.db")
    # res = db.delete_item("favorites", "actorName", actorName[1])
    # if res:
    #     bot.send_message(message.chat.id, res)
    # else:
    #     bot.send_message(message.chat.id, "Ок!")

def more(message):
    bd = dbhelper.DBHelper("server.db")
    if re.search(r"\D", message.text):
        msg = bot.send_message(message.chat.id, "Вы ввели не цифру. Введите ещё раз")
        bot.register_next_step_handler(msg, more)
    else:
        listOfFavorites = bd.get_flexible_request(f"SELECT * FROM favorites WHERE id = '{message.chat.id}'")
        bd.commit()
        actorForMore = listOfFavorites[int(message.text) - 1][1]
        bot.send_message(message.chat.id, "Секунду!")
        pars = myparser.Parser(token=config.TOKEN, chat_id=message.chat.id).getMaxActorInfo(actorForMore)
        listOfKeys = [*pars]
        listOfValues = list(pars.values())
        listOfResult = []
        for i in range(len(listOfKeys)):
            listOfResult.append(listOfKeys[i]+":"+" "+listOfValues[i]+"\n")
        itogStr = " \n".join(listOfResult).title()
        openPhoto = open('temp\\actor.jpg', "rb")
        bot.send_photo(message.chat.id, openPhoto)
        openPhoto.close()
        os.remove('temp\\actor.jpg')
        bot.send_message(message.chat.id, itogStr)
    
def new_users(message):
    search = re.search('\d{2}-\d{2}-\d{4}', message.text)
    if len(message.text) == 21 and search:
        from_ = message.text[:10]
        to = message.text[11:]
        
    else:
        msg = bot.send_message(message.chat.id,'Неверный формат даты. Введите еще раз')
        bot.register_next_step_handler(msg, new_users) #askSource
        return
    
    db=dbhelper.DBHelper('server.db')
    
    to_send = f'<b>Список новых пользователей:</b>\n'
    
    from_ = get_date(from_)
    to = get_date(to)
    
    result = db.get_all_items('users', order_by = 'inviteDate ')
#    print (result)
    
    x = []
    y = []
    
    for each in result:
        sumdate = get_date(each[3][:10])
        if each[3][:10] not in x:
            x.append(each[3][:10])
            y.append(1)
        else:
            for i in range(len(x)):
                if x[i] == each[3][:10]:
                    y[i]+=1
        if sumdate >= from_ and sumdate <=to:
            to_send+=f'{each[0]} {each[1]}\n'
     
    if len(to_send) > 35:
        bot.send_message(message.chat.id, to_send, parse_mode = 'html')
        fig, ax = plt.subplots()

        ax.plot(x, y, color = 'r', linewidth = 3)

        #  Тоже самое проделываем с делениями на оси "y":
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        time = str(datetime.datetime.now())[11:].replace(".",':').replace(":",'')

        plt.savefig(f'temp\\{time}.png')

        ing = open(f'temp\\{time}.png', 'rb')
        bot.send_photo(message.chat.id, ing)
        ing.close()

        os.remove(f'temp\\{time}.png')
    else:
        bot.send_message(message.chat.id, 'Новых пользователей за период не найдено')

def get_date(line):
    year = int(line[6:10])*12*30
#    print (year)
    month = int(line[3:5])*30
#    print (month)
    day = int(line[0:2])
#    print (day)
    return year+month+day  
    
def more(message):
    bd = dbhelper.DBHelper("server.db")
    listOfFavorites = bd.get_flexible_request(f"SELECT * FROM favorites WHERE id = '{message.chat.id}'")
    if re.search(r"\D", message.text):
        msg = bot.send_message(message.chat.id, "Вы ввели не цифру. Введите ещё раз")
        bot.register_next_step_handler(msg, more)
    else:
        if len(listOfFavorites) < int(message.text):
            msg = bot.send_message(message.chat.id, "Вы ввели неправильное число. Введите ещё раз")
            bot.register_next_step_handler(msg, more)
            return
        actorForMore = listOfFavorites[int(message.text) - 1][1]
        bot.send_message(message.chat.id, "Секунду!")
        pars = myparser.Parser(token=config.TOKEN, chat_id=message.chat.id).getMaxActorInfo(actorForMore)
        listOfKeys = [*pars]
        listOfValues = list(pars.values())
        listOfResult = []
        for i in range(len(listOfKeys)):
            listOfResult.append(listOfKeys[i] + ":" + " " + listOfValues[i] + "\n")
        itogStr = " \n".join(listOfResult).title()
        openPhoto = open('temp\\actor.jpg', "rb")
        bot.send_photo(message.chat.id, openPhoto)
        openPhoto.close()
        os.remove('temp\\actor.jpg')
        bot.send_message(message.chat.id, itogStr)


def active(message):
    user_str = '<b>Выберите № юзера</b>\n'
    db = dbhelper.DBHelper('server.db')
    user_list = db.get_all_items('users')
    for i in range(len(user_list)):
        user_str += f'{str(i + 1)}. {user_list[i][0]}, {user_list[i][1]}\n'

    msg = bot.send_message(message.chat.id, user_str, parse_mode='html')
    bot.register_next_step_handler(msg, get_user_stat)


def get_user_stat(message):
    db = dbhelper.DBHelper('server.db')
    #    if rownum < int(message.text)
    try:
        user = db.get_flexible_request(f"select * from users where rowid = {message.text}")
        text = f"<b>ID</b>: {user[0][0]}\n<b>Name</b>: {user[0][1]}\n<b>Last active</b>: {user[0][2]}\n<b>Ivite date</b>: {user[0][3]}\n"
        bot.send_message(message.chat.id, text, parse_mode='html')
    except:
        msg = bot.send_message(message.chat.id, "Повторите попытку")
        bot.register_next_step_handler(msg, active)


def all_users(message):
    try:
        db = dbhelper.DBHelper('server.db')
        count_of_users = db.get_flexible_request("select count(*) from users")[0][0]
        bot.send_message(message.chat.id, f"Всего пользователей: <b>{count_of_users}</b>", parse_mode="html")
    except:
        msg = bot.send_message(message.chat.id, "Повторите попытку")
        bot.register_next_step_handler(msg, all_users)


def get_count_of_actors(message):
    try:
        list_dir = os.listdir(path="actors")
        if list_dir != []:
            count = len(list_dir)
            deep = []
            for el in list_dir:
                for i in range(len(el)):
                    if el[i] == "_":
                        temp = i
                    if el[i] == ".":
                        point = i
                deep.append(int(el[temp + 1:point]))
            bot.send_message(message.chat.id,
                             f"Всего актеров в базе: <b>{count}</b>\nМаксимальное плечо в базе: <b>{max(deep)}</b>",
                             parse_mode="html")
        else:
            msg = bot.send_message(message.chat.id, "В базе нет актеров")
    except:
        msg = bot.send_message(message.chat.id, "Повторите попытку")
        bot.register_next_step_handler(msg, get_count_of_actors)
#функция по ответу на нажание кнопки InlineKeyboardButton
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'addFav':
                #добавление в избранное
                msg = bot.send_message(call.message.chat.id, "Введите имя актера")
                bot.register_next_step_handler(msg, addFav)

            if call.data == "weKnowName":
                actor = "".join(listOfFav)
                addFavIfWeKnow(call.message, actor)

            if call.data == "No":
                bot.send_message(call.message.chat.id, "Ок!")

            if call.data == "delFav":
                #удаление из избранных
                msg = bot.send_message(call.message.chat.id, "Введите цифру")
                bot.register_next_step_handler(msg, delFav)

            if call.data == "more":
                msg = bot.send_message(call.message.chat.id, "Введите цифру")
                bot.register_next_step_handler(msg, more)
                
            if call.data == "new_users":
                '''новые пользователи'''
                msg = bot.send_message(call.message.chat.id, "Введите период в формате: ДД-ММ-ГГГГ ДД-ММ-ГГГГ")
                bot.register_next_step_handler(msg, new_users)

            if call.data == "active":
                '''новые пользователи'''
                markup = types.InlineKeyboardMarkup()
                konkuser = types.InlineKeyboardButton("Конкретный юзер", callback_data="konkuser")

                povsem = types.InlineKeyboardButton("По всем", callback_data="povsem")
                markup.add(konkuser, povsem)
                bot.send_message(call.message.chat.id, 'Выбери тип статистики', reply_markup=markup)
            #                msg = bot.send_message(call.message.chat.id, markup)
            #                bot.register_next_step_handler(msg, active)

            if call.data == "konkuser":
                '''конкретный пользователь'''
                active(call.message)

            if call.data == "povsem":
                '''все юзеры'''
                all_users(call.message)

            if call.data == "baza":
                '''новые пользователи'''
                get_count_of_actors(call.message)

            if call.data == "addAdmin":
                msg = bot.send_message(call.message.chat.id, "Введите ID пользователя")
                bot.register_next_step_handler(msg, addAdmin)
            


    except Exception as e:
        print(repr(e))
#%%
#непрерывная работа бота(бот работает тогда, когда запущен код)
if __name__ == '__main__':
    bot.polling(none_stop=True)