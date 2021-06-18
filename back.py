import sqlite3

database = sqlite3.connect('dados_pizzaria.db')
cursor = database.cursor()
database.execute(
	'CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY, nome TEXT NOT NULL, endereco TEXT NOT NULL, bairro TEXT NOT NULL)')
database.execute('CREATE TABLE IF NOT EXISTS pizzas(sabor TEXT NOT NULL, ingredientes TEXT NOT NULL, preco REAL NOT NULL)')
database.execute('CREATE TABLE IF NOT EXISTS bebidas(bebida TEXT NOT NULL, tamanho TEXT NOT NULL, preco REAL NOT NULL)')
database.commit()

class Cliente:
	def cadastrar(nome, endereco, bairro):
		cursor.execute('INSERT INTO clientes VALUES(NULL, ?, ?, ?)', (nome, endereco, bairro))
		database.commit()

	def read(pedindo=False, pedidos_pendentes=[]):
		cursor.execute('SELECT nome, endereco, bairro FROM clientes')
		lista_clientes = cursor.fetchall()
		if pedidos_pendentes != [] and pedindo == True:
			for pedido in pedidos_pendentes:
				for indice, cliente in enumerate(lista_clientes):
					if pedido[0] in cliente[0]:
						del lista_clientes[indice]
		return lista_clientes

	def visualizar_cliente(nome, pedidos=False):
		if pedidos:
			nome = nome,
		cursor.execute('SELECT nome, endereco, bairro FROM clientes WHERE nome = ?', (nome))
		return cursor.fetchall()

	def atualizar(novo_nome, novo_endereco, novo_bairro, nome):
		cursor.execute('UPDATE clientes SET nome = ?, endereco = ?, bairro = ? WHERE nome = ?', (novo_nome, novo_endereco, novo_bairro, nome))
		database.commit()

	def excluir(a_excluir):
		cursor.execute('DELETE FROM clientes WHERE nome = ?', (a_excluir))
		database.commit()

class Pizza:
	def cadastrar(sabor, ingredientes, preco):
		float(preco)
		cursor.execute('INSERT INTO pizzas VALUES(?, ?, ?)', (sabor, ingredientes, preco))
		database.commit()

	def read(selecao=None, sabor=None):
		if selecao == None:
			cursor.execute('SELECT sabor FROM pizzas')
			return cursor.fetchall()
		if selecao == 'unica':
			cursor.execute('SELECT ingredientes, preco from pizzas WHERE sabor = ?', (sabor))
			return cursor.fetchall()[0]

	def excluir(a_excluir):
		cursor.execute('DELETE FROM pizzas WHERE sabor = ?', (a_excluir))
		database.commit()

class Bebida:
	def cadastrar(bebida, tamanho, preco):
		float(preco)
		cursor.execute('INSERT INTO bebidas VALUES(?, ?, ?)', (bebida, tamanho, preco))
		database.commit()

	def read(selecao=None, bebida=None):
		if selecao == None:
			cursor.execute('SELECT bebida FROM bebidas')
			return cursor.fetchall()
		if selecao == 'unica':
			cursor.execute('SELECT tamanho, preco from bebidas WHERE bebida = ?', (bebida))
			return cursor.fetchall()[0]

	def excluir(a_excluir):
		cursor.execute('DELETE FROM bebidas WHERE bebida = ?', (a_excluir))
		database.commit()