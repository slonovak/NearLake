from tkinter import *

import socket

import select

import random

import time





actions = [

	'производит с загрязнением',

	'производит с очисткой',

	'сменил производство',

	'инспектирует',

	'примирует'

]



lake_money = [

	[5, -20],

	[19, -8],

	[26, -3],

	[33, 3],

	[41, 7],

	[51, 14],

	[64, 21],

	[80, 28],

	[100, 35],

	[110, 40],

	[121, 63],

	[133, 79],

	[146, 92],

	[161, 111],

	[177, 127],

]



game = {

	'lake': 0,

	'clients': {},

	'state': -1,

	'port': 0,

	'step': 1

}





server = socket.socket()
sockets = []





def portnum(event):

	port = int(message_entry.get())

	message_entry.delete(0, END)

	if not game['port']:

		server.bind(('localhost', port))

		server.listen(5)
		sockets.append(server)
		root.after(100, handle)

		print(port)

		text.insert(END, 'Server run on port:{}\n'.format(port))

		text.see(END)

		game['port'] = port



def start(event):

	if game['port']:

		game['state'] = 0

		text.insert(END, 'Game started\n')

		text.see(END)



def round_processing():

	inpectors = list(filter(lambda x: x['choice']==4, game['clients'].values()))

	if len(inpectors):

		inpector_lost = 8//len(inpectors)

	presentors = list(filter(lambda x: x['choice']==5, game['clients'].values()))

	if len(presentors):

		presentor_lost = 8//len(presentors)

	if game['step'] == 12:

		game['lake'] = random.randint(1, 12)

		if game['lake'] > 6:

			game['lake'] = 6

	for i in sockets:

		if i is server:

			text.insert(END, 'Ход {}:\n'.format(game['step']))

			text.see(END)


		else:

			text.insert(END, '{} {}\n'.format(game['clients'][i]['addr'], actions[game['clients'][i]['choice'] - 1]))

			text.see(END)

			if game['clients'][i]['choice'] == 1:

				if not len(inpectors):

					game['clients'][i]['money'] += lake_money[game['lake'] + 8][0]

					if game['lake'] > -8:

						game['lake'] -= 1

					text.insert(END, '\t{} Получил:{}$ ({}), озеро:{}\n'.format(str(game['clients'][i]['addr']), lake_money[game['lake'] + 8][0], game['clients'][i]['money'], game['lake']))

					text.see(END)

				else:

					game['clients'][i]['money'] -= 20

					text.insert(END, '\t{} Оштрафован на 20$ ({})\n'.format(str(game['clients'][i]['addr']) ,game['clients'][i]['money']))

					text.see(END)

			elif game['clients'][i]['choice'] == 2:

				game['clients'][i]['money'] += lake_money[game['lake'] + 8][1]

				if game['lake'] < 6:

					game['lake'] += 1

				text.insert(END, '\t{} Получил:{}$ ({}), озеро:{}\n'.format(str(game['clients'][i]['addr']), lake_money[game['lake'] + 8][1], game['clients'][i]['money'], game['lake']))

				if len(presentors):
					game['clients'][i]['money'] += 10
					text.insert(END, '\t{} примирован на 10$ ({})\n'.format(str(game['clients'][i]['addr']), game['clients'][i]['money']))

				text.see(END)

			elif game['clients'][i]['choice'] == 3:

				game['clients'][i]['money'] += 8

				text.insert(END, '\t{} Получил:8$ ({})\n'.format(str(game['clients'][i]['addr']), game['clients'][i]['money']))

				text.see(END)

			elif game['clients'][i]['choice'] == 4:

				game['clients'][i]['money'] -= inpector_lost

				text.insert(END, '\tБорется с нарушителями\n')

				text.see(END)

			elif game['clients'][i]['choice'] == 5:

				game['clients'][i]['money'] -= presentor_lost

				text.insert(END, '\tНаграждает хороших людей\n')

				text.see(END)

			game['clients'][i]['done'] = False

	for i in sockets[1:]:

		i.send(bytes(str(game['step']).encode()))
		time.sleep(0.05)
		i.send(bytes(str(game['lake']).encode()))
		time.sleep(0.05)
		i.send(bytes(str(game['clients'][i]['money']).encode()))

	game['state'] = 0
	game['step'] += 1







def handle():
	ins, _, _ = select.select(sockets, [], [], 0)

	for i in ins:

		if i is server:

			conn, addr = server.accept()

			sockets.append(conn)

			#data = conn.recv(50).decode('utf-8') #// Feature

			game['clients'][conn] = {

				'money': 0,

				'done': False,

				'choice': 0,

				'addr': addr,

				#'name': data #// Feature

			}

			print('Подключился {}'.format(addr)) #//Feature

		else:

				# game['clients'][i]

			data = i.recv(4)

			data = data.decode('utf-8')

			if not data:

				sockets.remove(i)

				print('Отключился {}'.format(game['clients'][i]['addr']))

				game['clients'].pop(i)

				i.close()



				#root.deletefilehandler(i.fileno())

			else:

				if game['state'] != -1:

					if game['clients'][i]['done']:

						i.send(bytes('already done'.encode()))

					elif game['state'] != 0:

						i.send(bytes('wait, round processing'.encode()))

					else:

						game['clients'][i]['choice'] = int(data)

						game['clients'][i]['done'] = True

						i.send(bytes('ok'.encode()))

			if all(map(lambda x: x['done'], game['clients'].values())) and game['state'] == 0:

				game['state'] = 1

				round_processing()

	root.after(100, handle)







# all(map(lambda x: x['done'], game['clients'].values()))



root = Tk()

root.title("Near Lake")

root.geometry("600x400")

message_entry = Entry(width=90)

text = Text(root, height=15, width=90)

text.pack()

message_entry.pack()

root.bind("<Return>", portnum)

run_game = Button(text="run game")

run_game.bind('<Button-1>', start)

run_game.pack()



root.mainloop()