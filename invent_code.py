import telebot, time
import qrcode
import cv2
import uuid
import sqlite3
import datetime as DT
#import pymysql
# pip install pyTelegramBotApi
#from config import host, user, password, db_name
from telebot import types # для указание типов

BOT_TOKEN = '5670724810:AAGKKtFVjSOGt6CNJQaxBG_XZVVcwXZQz4U'

bot = telebot.TeleBot(BOT_TOKEN)

#----------------------------------------------------------------------------------------------------------
#								Подключение к БД	
#----------------------------------------------------------------------------------------------------------	

conn = sqlite3.connect('inventory.db', check_same_thread=False)
cursor = conn.cursor()

#----------------------------------------------------------------------------------------------------------
#								Дефы	
#----------------------------------------------------------------------------------------------------------	

def registration_user(user_id: int, user_name: str, last_name: str, login: str):
	cursor.execute('INSERT INTO reg_user (reg_user_id, reg_user_name, reg_last_name, reg_nickname) VALUES (?, ?, ?, ?)', (user_id, user_name, last_name, login))
	conn.commit()

def add_reg_sr(rez_qr: int, reg_ser_num: str, fk_type_name_tech: int, reg_date: str):
	cursor.execute('INSERT INTO reg_sr (rez_qr, reg_ser_num, fk_type_name_tech, reg_date) VALUES (?, ?, ?, ?)', (data, message_sr, type_tech, date_reg_sr))
	conn.commit()

def add_status_reg_sr(desc: str, data: int):
	cursor.execute('UPDATE reg_sr SET reg_desc = (?) WHERE rez_qr = (?)', (desc, data))
	conn.commit()

def add_fk_status(desc: str, data: int):
	cursor.execute('UPDATE reg_sr SET fk_status = (?) WHERE rez_qr = (?)', (st_id, data))
	conn.commit()
	
def add_location(fk_num_build, fk_num_floor, loc_cab, fk_reg_user, loc_date, fk_reg_sr):
	cursor.execute('INSERT INTO location (fk_num_build, fk_num_floor, loc_cab, fk_reg_user, loc_date, fk_reg_sr) VALUES (?, ?, ?, ?, ?, ?)', (user_message_building, get_floor, number_cb, get_user_id, add_loc_data, get_reg_sr))
	conn.commit()

def edit_location(fk_num_build, fk_num_floor, loc_cab, fk_reg_user, loc_date, fk_reg_sr):
	cursor.execute('UPDATE location SET fk_num_build = (?), fk_num_floor = (?), loc_cab = (?), fk_reg_user = (?), loc_date = (?), fk_reg_sr = (?) WHERE fk_reg_sr = (?)', (user_message_building, get_floor, number_cb, get_user_id, add_loc_data, get_reg_sr, get_reg_sr))
	conn.commit()


#----------------------------------------------------------------------------------------------------------
#								Старт
#----------------------------------------------------------------------------------------------------------	

@bot.message_handler(commands=['start'])
def start(message):
	global user_id
	bot.send_message(message.chat.id, text="Привет, {0.first_name}!".format(message.from_user))
	us_id = message.from_user.id 
	cursor.execute("SELECT reg_user_id  FROM reg_user WHERE reg_user_id = '%s'" % us_id)
	user_id = cursor.fetchall()
	if str(us_id) not in  str(user_id):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		btn1 = types.KeyboardButton("Зарегистрироваться")
		markup.add(btn1)
		bot.send_message(message.chat.id, 'Предлагаю Вам зарегистрироваться!', reply_markup=markup)
	else:
		bot.send_message(message.chat.id, 'Для того, чтобы продолжить работу Бота, отправьте фотографию QR-кода на компьютерной техники.')

#----------------------------------------------------------------------------------------------------------
#								Добавить ID и Имя пользователя в БД	
#----------------------------------------------------------------------------------------------------------	

@bot.message_handler(content_types=['text']) #Для того, чтобы if реагировал на кнопки, необходимо тут указать имеено content_types
def get_text_messages(message):
	
	if message.text == 'Зарегистрироваться':	
		us_id = message.from_user.id
		us_name = message.from_user.first_name
		la_name = message.from_user.last_name
		nick = message.from_user.username
		cursor.execute("SELECT reg_user_id  FROM reg_user") 
		user_id = cursor.fetchall()

		if str(us_id) not in  str(user_id):
			registration_user(user_id=us_id, user_name=us_name, last_name=la_name, login=nick) # Передаёт переменные для добавления в БД
			a = telebot.types.ReplyKeyboardRemove()
			bot.send_message(message.chat.id, 'Ваше имя добавлено в базу данных!\nОтправьте фотографию QR-кода в чат =)', reply_markup=a)
		else:
			a = telebot.types.ReplyKeyboardRemove()
			bot.send_message(message.chat.id, 'Отправьте фотографию QR-кода в чат =)', reply_markup=a)

#----------------------------------------------------------------------------------------------------------
#								Добавить серийный номер
#----------------------------------------------------------------------------------------------------------	

	elif message.text == 'Добавить':
		a = telebot.types.ReplyKeyboardRemove()
		add = bot.send_message(message.chat.id, 'Напишите серийный номер', reply_markup=a)
		bot.register_next_step_handler(add,add_type_tech)

	elif message.text == 'Изменить местоположение':
		bot.send_message(message.chat.id, 'Выберите новое местоположение')
		bot.register_next_step_handler(trigger ,choice_btn)
	elif message.text == 'Отмена':
		a = telebot.types.ReplyKeyboardRemove()
		back = bot.send_message(message.chat.id, 'Отправьте фотографию QR-кода в чат =)', reply_markup=a)
		bot.register_next_step_handler(back,message_post)
	else:
		bot.send_message(message.chat.id,'Error 637')

#----------------------------------------------------------------------------------------------------------
#								Добавить тип техники
#----------------------------------------------------------------------------------------------------------	

def add_type_tech(message):
	global message_sr
	message_sr1 = [message.text]
	message_sr = (' '.join(map(str, message_sr1))).replace("'", '').replace("[", '').replace("]", '') # убираем лишние символы

	markup_type = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	btn_type1 = types.KeyboardButton("Стац.компьютер")
	btn_type2 = types.KeyboardButton("Монитор")
	btn_type3 = types.KeyboardButton("Моноблок")
	btn_type4 = types.KeyboardButton("МФУ")
	btn_type5 = types.KeyboardButton("Сканер")
	btn_type6 = types.KeyboardButton("Принтер")
	btn_type7 = types.KeyboardButton("Ноутбук")
	markup_type.add(btn_type1, btn_type2, btn_type3, btn_type4, btn_type5, btn_type6, btn_type7) 
	number_type = bot.send_message(message.chat.id, 'Далее, необходимо указать тип техники:', reply_markup=markup_type) # Выдаёт много хлама
	bot.register_next_step_handler(number_type,add_tech)

#----------------------------------------------------------------------------------------------------------
#								Добавить технику
#----------------------------------------------------------------------------------------------------------	

def add_tech(message):
	add_type = [message.text]																						# list ['Тип, который пользователь выбрал из меню']
	add_type2 = (' '.join(map(str, add_type))).replace("'", '').replace("[", '').replace("]", '') 							# убираем лишние символы
	cursor.execute("SELECT ty_name FROM type_tech") 
	ty_te = cursor.fetchall()																									# list со всеми названиями здани
	if str(add_type2) in str(ty_te): 																				# Проверяем, есть ли название здания, который выбрал пользователь, в списке всех зданий
		cursor.execute("SELECT id FROM type_tech WHERE ty_name == (?)", [add_type2] )
		type_id = cursor.fetchall() 																				# Достаём ID здания, который указал пользователь. Получаем [(цифра,)]
		add_type = (' '.join(map(str, type_id))).replace('(', '').replace(')', '').replace(',', '').replace("'", '') 		# убираем лишние символы

	markup_name_te = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

	if add_type == str("1"):
		btn_name1 = types.KeyboardButton("Compaq Pro 6305 Microtower")
		btn_name2 = types.KeyboardButton("EliteDesk 800 G5 TWR")
		btn_name3 = types.KeyboardButton("ThinkCentre M73e")
		markup_name_te.add(btn_name1, btn_name2, btn_name3) 
		number_name = bot.send_message(message.chat.id, 'Далее, необходимо указать название техники:', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_name_tech)
	elif add_type == str("2"):
		btn_name1 = types.KeyboardButton("S20B300B")
		btn_name2 = types.KeyboardButton("VA2448-LED")
		btn_name3 = types.KeyboardButton("V246HL")
		btn_name4 = types.KeyboardButton("BL2420-T")
		btn_name5 = types.KeyboardButton("EliteDisplay E273q")
		markup_name_te.add(btn_name1, btn_name2, btn_name3, btn_name4, btn_name5) 
		number_name = bot.send_message(message.chat.id, 'Далее, необходимо указать название техники:', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_name_tech)
	elif add_type == str("3"):
		btn_name1 = types.KeyboardButton("Veriton Z4860G")
		btn_name2 = types.KeyboardButton("ProOne 440 G5 NT")
		markup_name_te.add(btn_name1, btn_name2) 
		number_name = bot.send_message(message.chat.id, 'Далее, необходимо указать название техники:', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_name_tech)
	elif add_type == str("4"):
		btn_name1 = types.KeyboardButton("Xpress M2070FW")
		btn_name2 = types.KeyboardButton("LaserJet Pro MFP M428fdn")
		btn_name3 = types.KeyboardButton("SCX 5637FR")
		btn_name4 = types.KeyboardButton("ECOSYS M6230cidn")
		btn_name5 = types.KeyboardButton("LaserJet MFP M438n")
		markup_name_te.add(btn_name1, btn_name2, btn_name3, btn_name4, btn_name5) 
		number_name = bot.send_message(message.chat.id, 'Далее, необходимо указать название техники:', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_name_tech)
	elif add_type == str("5"):
		btn_name1 = types.KeyboardButton("i2600 Scanner")
		btn_name2 = types.KeyboardButton("ScanJet 5590")
		markup_name_te.add(btn_name1, btn_name2) 
		number_name = bot.send_message(message.chat.id, 'Далее, необходимо указать название техники:', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_name_tech)
	elif add_type == str("6"):
		btn_name1 = types.KeyboardButton("ML-3750ND")
		btn_name2 = types.KeyboardButton("LaserJet Pro M15w")
		btn_name3 = types.KeyboardButton("LaserJet P1006")
		btn_name4 = types.KeyboardButton("LaserJet 1022")
		btn_name5 = types.KeyboardButton("LaserJet Pro P1102")
		btn_name6 = types.KeyboardButton("Color LaserJet Pro M452nw")
		markup_name_te.add(btn_name1, btn_name2, btn_name3, btn_name4, btn_name5, btn_name6) 
		number_name = bot.send_message(message.chat.id, 'Далее, необходимо указать название техники:', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_name_tech)
	elif add_type == str("7"):
		btn_name1 = types.KeyboardButton("Выбрать другую технику")
		markup_name_te.add(btn_name1) 
		number_name = bot.send_message(message.chat.id, 'Ноутбуки отсутствуют!', reply_markup=markup_name_te) # Выдаёт много хлама
		bot.register_next_step_handler(number_name,add_tech)
	else:
		bot.send_message(message.chat.id, 'Ошибка 143')

#----------------------------------------------------------------------------------------------------------
#								Находим внешний ключ от type_name_tech + находим дату и время	
#----------------------------------------------------------------------------------------------------------	

def add_name_tech(message):
	global type_tech # Это нужно...
	global date_reg_sr
	global markup_sd
	add_name = message.text # Тип List (Выводит название техники с ковычками, запятыми и скобками)

	cursor.execute("SELECT id FROM name_tech WHERE te_name == (?)", [add_name]) # Тип List 
	na_te = cursor.fetchall() # Тип List

	id_name = (' '.join(map(str, na_te))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '') # Тип Str 	ID таблицы name_tech 	Чистое число

	cursor.execute("SELECT id FROM type_name_tech WHERE fk_name_tech == (?)", [id_name]) 
	ty_na = cursor.fetchall() # Тип List

	type_tech = (' '.join(map(str, ty_na))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '') # Тип str 	ID таблицы type_nema_tach 	Чистое число

	tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x)) #Конвертация даты в читабельный вид Необходимо импорт телебот, дата
	date_reg_sr = str(tconv(message.date)) # Вносим дату в переменную

	add_reg_sr(data, message_sr, type_tech, date_reg_sr) # Добавляем данные в таблицу reg_sr

#----------------------------------------------------------------------------------------------------------
#								Выбор пользователя, после сохранения серийного номера	
#----------------------------------------------------------------------------------------------------------	

	markup_sd = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	btn_sd1 = types.KeyboardButton("Добавить описание")
	btn_sd2 = types.KeyboardButton("Добавить статус")
	btn_sd3 = types.KeyboardButton("Добавить локацию")
	markup_sd.add(btn_sd1, btn_sd2, btn_sd3) 
	user_choice = bot.send_message(message.chat.id, 'Вы внесли технику в базу данных!\nВыберите дальшейшее действие или отправьте следующую фотографию QR-кода', reply_markup=markup_sd)
	bot.register_next_step_handler(user_choice,choice_btn)

def choice_btn(message):
	global desc
	
	user_choice = [message.text] # ['Добавить описание']

	a = telebot.types.ReplyKeyboardRemove() # Убираем предыдущие кнопки
	if user_choice == ['Добавить описание']:
		desc = bot.send_message(message.chat.id, 'Напишите описание техники: ', reply_markup=a)
		bot.register_next_step_handler(desc,add_desc)

	elif user_choice == ['Добавить статус']:

		markup_stat = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		btn_stat1 = types.KeyboardButton("Отметка о инвентаризации")
		btn_stat2 = types.KeyboardButton("Находится на ремонте")
		btn_stat3 = types.KeyboardButton("Новая техника")
		btn_stat4 = types.KeyboardButton("Списан")
		btn_stat5 = types.KeyboardButton("Выдан сотруднику")
		btn_stat6 = types.KeyboardButton("Сломан")
		btn_stat7 = types.KeyboardButton("Ожидание выдачи сотруднику")
		markup_stat.add(btn_stat1, btn_stat2, btn_stat3, btn_stat4, btn_stat5, btn_stat6, btn_stat7) 
		user_desc = bot.send_message(message.chat.id, 'Выберите статус:', reply_markup=markup_stat)
		bot.register_next_step_handler(user_desc,add_status)

	elif user_choice == ['Добавить локацию'] or user_choice == ['Изменить местоположение']:
		global markup_build

		markup_build = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		btn_add1 = types.KeyboardButton("Главное здание")
		btn_add2 = types.KeyboardButton("Травмпункт 1")
		btn_add3 = types.KeyboardButton("Чистая хирургия")
		btn_add4 = types.KeyboardButton("ОВЛ")
		btn_add5 = types.KeyboardButton("Административный корпус")
		btn_add6 = types.KeyboardButton("Лаборатория")
		btn_add7 = types.KeyboardButton("НМП")
		btn_add8 = types.KeyboardButton("Санаторий")
		btn_add9 = types.KeyboardButton("Травмпункт 2")
		btn_add10 = types.KeyboardButton("Пищеблок")
		btn_add11 = types.KeyboardButton("Склад")
		markup_build.add(btn_add1, btn_add2, btn_add3, btn_add4, btn_add5, btn_add6, btn_add7, btn_add8, btn_add9, btn_add10, btn_add11)

		add_build = bot.send_message(message.chat.id, 'Укажите здание, где находится данная техника.', reply_markup=markup_build)
		bot.register_next_step_handler(add_build,add_id_building)

	elif user_choice == ['Отмена']:
		bot.send_message(message.chat.id, 'Отправьте фотографию QR-кода в чат =)')
	else:
		bot.send_message(message.chat.id, 'Ошибка 712')

#----------------------------------------------------------------------------------------------------------
			# Проверяем, какую кнопку нажал пользователь, затем получаем ID здания и выбираем этаж
#----------------------------------------------------------------------------------------------------------	

def add_id_building(message):
	global user_message_building # ID здания, который выбрал пользователь. 2 столбец
	user_message_building = [message.text]	 # list ['Название здания, который пользователь выбрал из меню']
	cursor.execute("SELECT num_bu_name_build FROM num_build") 
	na_bi = cursor.fetchall()				 # list со всеми названиями зданий	
	if str(user_message_building) not in str(na_bi): # Проверяем, есть ли название здания, который выбрал пользователь, в списке всех зданий
		cursor.execute("SELECT id FROM num_build WHERE num_bu_name_build == (?)", user_message_building)
		user_message_building = cursor.fetchall() # Достаём ID здания, который указал пользователь. Получаем [(цифра,)]
		user_message_building = (' '.join(map(str, user_message_building))).replace('(', '').replace(')', '').replace(',', '').replace("'", '') # убираем лишние символы
		markup_floor = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		if user_message_building == str('1'):
			btn_floor1 = types.KeyboardButton("7")
			btn_floor2 = types.KeyboardButton("6")
			btn_floor3 = types.KeyboardButton("5")
			btn_floor4 = types.KeyboardButton("4")
			btn_floor5 = types.KeyboardButton("3")
			btn_floor6 = types.KeyboardButton("2")
			btn_floor7 = types.KeyboardButton("1")
			btn_floor8 = types.KeyboardButton("-1")
			btn_floor9 = types.KeyboardButton("-2")
			btn_floor10 = types.KeyboardButton("-3")
			btn_floor11 = types.KeyboardButton("-4")
			markup_floor.add(btn_floor1, btn_floor2, btn_floor3, btn_floor4, btn_floor5, btn_floor6, btn_floor7, btn_floor8, btn_floor9, btn_floor10, btn_floor11) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('2'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			markup_floor.add(btn_floor1, btn_floor2) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('3'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			btn_floor3 = types.KeyboardButton("3")
			markup_floor.add(btn_floor1, btn_floor2, btn_floor3) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('4'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			markup_floor.add(btn_floor1, btn_floor2) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('5'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			btn_floor3 = types.KeyboardButton("3")
			markup_floor.add(btn_floor1, btn_floor2, btn_floor3) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('6'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			btn_floor3 = types.KeyboardButton("3")
			markup_floor.add(btn_floor1, btn_floor2, btn_floor3) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('7'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			markup_floor.add(btn_floor1, btn_floor2) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('8'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("2")
			btn_floor3 = types.KeyboardButton("3")
			markup_floor.add(btn_floor1, btn_floor2, btn_floor3) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('9'):
			btn_floor1 = types.KeyboardButton("1")
			markup_floor.add(btn_floor1) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('10'):
			btn_floor1 = types.KeyboardButton("1")
			btn_floor2 = types.KeyboardButton("-1")
			markup_floor.add(btn_floor1, btn_floor2) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		elif user_message_building == str('11'):
			btn_floor1 = types.KeyboardButton("-3")
			markup_floor.add(btn_floor1) 
			number_floor = bot.send_message(message.chat.id, 'Укажите этаж:', reply_markup=markup_floor) # Выдаёт много хлама
			bot.register_next_step_handler(number_floor,add_floor)
		else:
			bot.send_message(message.chat.id,'Error 565')
		
	else:
		bot.send_message(message.chat.id,'Error 345')

#----------------------------------------------------------------------------------------------------------
#								Адаптируем значение пользователя для поиска этажа в БД	
#----------------------------------------------------------------------------------------------------------	

def add_floor(message):
	global floor
	global get_floor # ID этажа
	floor = [message.text]
	floor = (' '.join(map(str, floor))).replace(',', '').replace("'", '').replace("[", '').replace("]", '') # убираем лишние символы
	a = str('этаж')
	x = str(' ')
	b = message.text # list Название этажа, который ввёл пользователь
	floor_list = [b + x + a]
	cursor.execute("SELECT id FROM num_floor WHERE fl_name == (?)", floor_list, )
	get_floor = cursor.fetchall() # Получаем ID этажа
	get_floor = (' '.join(map(str, get_floor))).replace('(', '').replace(')', '').replace(',', '').replace("'", '').replace("[", '').replace("]", '') # убираем лишние символы
	a = telebot.types.ReplyKeyboardRemove() # Убирает кнопку, когда будет вывод следующей строки
	add_cb = bot.send_message(message.chat.id, 'Теперь напишите номер кабинета:', reply_markup=a)
	bot.register_next_step_handler(add_cb,add_cabinet)

#----------------------------------------------------------------------------------------------------------
#								Добавляем номер кабинета и точное время	
#----------------------------------------------------------------------------------------------------------

def add_cabinet(message):
	global number_cb # Номер кабинета
	global add_loc_data # Дата и время
	global get_user_id # ID пользователя
	global get_reg_sr # ID серийного номера
	num_cb = [message.text]
	number_cb = (' '.join(map(str, num_cb))).replace("'", '').replace("[", '').replace("]", '') # убираем лишние символы

	tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x)) #Конвертация даты в читабельный вид Необходимо импорт телебот, дата
	add_loc_data = str(tconv(message.date)) # Вносим дату в переменную

	id_us = message.from_user.id

	cursor.execute("SELECT id FROM reg_user WHERE reg_user_id == '%s'" % id_us) 
	num_us_id = cursor.fetchall()
	get_user_id = (' '.join(map(str, num_us_id))).replace('(', '').replace(')', '').replace(',', '').replace("'", '').replace("[", '').replace("]", '') # убираем лишние символы

	cursor.execute("SELECT id FROM reg_sr WHERE rez_qr == '%s'" % data)
	num_reg_sr = cursor.fetchall() 
	get_reg_sr = (' '.join(map(str, num_reg_sr))).replace('(', '').replace(')', '').replace(',', '').replace("[", '').replace("]", '') # убираем лишние символы

	if trigger == 'tr_add':
		add_location(user_message_building, get_floor, get_user_id, add_loc_data, number_cb, get_reg_sr)
	elif trigger == 'tr_edit':
		edit_location(user_message_building, get_floor, get_user_id, add_loc_data, number_cb, get_reg_sr)
	else:
		bot.send_message(message.chat.id, 'Ошибка 944')

	markup_sd = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	btn_sd1 = types.KeyboardButton("Добавить описание")
	btn_sd2 = types.KeyboardButton("Добавить статус")
	markup_sd.add(btn_sd1, btn_sd2) 
	a = telebot.types.ReplyKeyboardRemove() # Убирает кнопку, когда будет вывод следующей строки
	bot.send_message(message.chat.id, 'Вы успешно добавили местоположение техники!\nОтправьте следующую фотографию QR-кода', reply_markup=a)

#----------------------------------------------------------------------------------------------------------
#								Добавление описания, после нажатия кнопки	
#----------------------------------------------------------------------------------------------------------	

def add_desc(message):
	desc = message.text
	close = bot.send_message(message.chat.id, 'Вы добавили описание!\nВыберите дальшейшее действие или отправьте следующую фотографию QR-кода', reply_markup=markup_sd)
	add_status_reg_sr(desc, data)		# ДОБАВЛЕНИЕ В БД ОПИСАНИЯ!!!	ДОБАВЛЕНИЕ В БД ОПИСАНИЯ!!!	ДОБАВЛЕНИЕ В БД ОПИСАНИЯ!!!
	bot.register_next_step_handler(close,choice_btn)

#----------------------------------------------------------------------------------------------------------
#								Добавление статуса, после нажатия кнопки	
#----------------------------------------------------------------------------------------------------------	

def add_status(message):
	global st_id
	user_choice_stat = [message.text]

	cursor.execute("SELECT id FROM status WHERE st_name_status == (?)", user_choice_stat, )
	choice_st_id = cursor.fetchall() # Достаём ID статуса, который указал пользователь. Получаем [(цифра,)]
	st_id = (' '.join(map(str, choice_st_id))).replace('(', '').replace(')', '').replace(',', '').replace("'", '') # убираем лишние символы
	add_fk_status(st_id, data)
	close = bot.send_message(message.chat.id, 'Вы добавили статус!', reply_markup=markup_sd)
	bot.register_next_step_handler(close,choice_btn)
#----------------------------------------------------------------------------------------------------------
#								Проверка результата QR-кода	
#----------------------------------------------------------------------------------------------------------						

@bot.message_handler(content_types = ['photo'])
def message_post(message):
	global data
	f_id = message.photo[-1].file_id
	file_info= bot.get_file(f_id) #Собирает информациюо файле
	down_file = bot.download_file(file_info.file_path) #Скачивает файл
	name = str(uuid.uuid4()) #Даёт рандомное название
	with open(name + '.jpg', 'wb') as file: #Открывает файл. (wb) ключ только для просмотра
		file.write(down_file) 				#Записывает в файл
	img_qrcode = cv2.imread(name + '.jpg') #Находим фотографию по названию и читаем
	detector = cv2.QRCodeDetector()

	data, clear_qrcode, points = detector.detectAndDecode(img_qrcode) #данные, декодированные из QR-кода, выходной массив вершин найденного четырехугольника QR-кода и выходное изображение, содержащее исправленный и преобразованный в двоичную форму QR-код.
	if points is not None:
		try:
			if int(data) >= int(10001) and int(data) <= int(99999):
				cursor.execute("SELECT reg_ser_num FROM reg_sr WHERE rez_qr = '%s'" % data)
				res_qr = cursor.fetchall() # Результат qr-кода грязный
				res_qr_code = (' '.join(map(str, res_qr))).replace('(', '').replace(')', '').replace(',', '').replace("'", '') # Результат qr-кода чистый
				if not res_qr_code:
					bot.send_message(message.chat.id, 'Результат QR-кода: %s\nСерийный номер: Отсутствует' % int(data))
				else:
					# cursor.execute("SELECT fk_type_name_tech FROM reg_sr WHERE rez_qr = '%s'" % data)
					# te_rez = cursor.fetchall() # Внешний ключ от таблицы type_name_tech
					# tech_rez = (' '.join(map(str, te_rez))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')

					cursor.execute("""SELECT te_firm, te_name FROM name_tech JOIN type_name_tech ON name_tech.id = type_name_tech.fk_name_tech
					JOIN reg_sr ON type_name_tech.id = reg_sr.fk_type_name_tech WHERE reg_sr.rez_qr = '%s'""" % data )
					tech_rez2 = cursor.fetchall()
					tech = (' '.join(map(str, tech_rez2))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')

					cursor.execute("""SELECT reg_desc FROM reg_sr WHERE rez_qr = '%s'""" % int(data) )
					desc_te = cursor.fetchall()
					desc_tech = (' '.join(map(str, desc_te))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')
	#----------------------------------------------------------------------------------------------------------
	#								Поиск данных для вывода местоположения	
	#----------------------------------------------------------------------------------------------------------
					cursor.execute("""SELECT id FROM reg_sr WHERE rez_qr == '%s'""" % data )
					search_id = cursor.fetchall()
					search_id_reg_sr = (' '.join(map(str, search_id))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')
					
					cursor.execute("""SELECT num_bu_name_build FROM location JOIN num_build ON location.fk_num_build = num_build.id WHERE location.fk_reg_sr == '%s'""" % search_id_reg_sr )
					search_build_unfinish = cursor.fetchall()
					search_build = (' '.join(map(str, search_build_unfinish))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')

					cursor.execute("""SELECT fl_name FROM location JOIN num_floor ON location.fk_num_floor = num_floor.id WHERE location.fk_reg_sr == '%s'""" % search_id_reg_sr )
					search_floor_unfinish = cursor.fetchall()
					search_floor = (' '.join(map(str, search_floor_unfinish))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')

					cursor.execute("""SELECT loc_cab FROM location WHERE location.fk_reg_sr == '%s'""" % search_id_reg_sr )
					search_cab_unfinish = cursor.fetchall()
					search_cab = (' '.join(map(str, search_cab_unfinish))).replace("'", '').replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(",", '')
			
	#----------------------------------------------------------------------------------------------------------					
					bot.send_message(message.chat.id, """Результат QR-кода: %s\nСерийный номер: %s\nНаименование: %s\nЛокация: %s, %s, %s кабинет\nОписание: %s""" % (int(data), res_qr_code, tech, search_build, search_floor, search_cab, desc_tech))

				global trigger
				if not res_qr:
					trigger = 'tr_add'
					markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
					btn_add1 = types.KeyboardButton("Добавить")
					btn_add2 = types.KeyboardButton("Отмена")
					markup.add(btn_add1, btn_add2)
					add = bot.send_message(message.chat.id, 'Хотите добавить данные?', reply_markup=markup)
				else:
					trigger = 'tr_edit'
					markup_f = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
					btn_edit1 = types.KeyboardButton("Изменить местоположение")
					btn_edit2 = types.KeyboardButton("Отмена")
					markup_f.add(btn_edit1, btn_edit2)
					edit_loc_tech = bot.send_message(message.chat.id, 'Хотите изменить местоположение техники?', reply_markup=markup_f)
					bot.register_next_step_handler(edit_loc_tech,choice_btn)

			else:
				bot.send_message(message.chat.id, 'QR-код не найден в таблице инвентаризации!')
		except:
			bot.send_message(message.chat.id, 'Нельзя сканировать QR-коды, которые не относятся к инвентаризации!')
			return
	else:
		bot.send_message(message.chat.id, 'QR-код не найден!\nОтправьте фотографию ещё раз)')
		cv2.waitKey(0)
		cv2.destroyAllWindows()

#----------------------------------------------------------------------------------------------------------
#								Конец	
#----------------------------------------------------------------------------------------------------------	

bot.polling()

