import PySimpleGUI as sg
from back import database, cursor, Cliente, Pizza, Bebida
import sqlite3
import string
from datetime import date

def dados_pagina_visualizar(retornar_nome=False):
	def montar_checkbox(item):
		total = 0
		x = 0
		for item in pedidos_pendentes:
			if item[0] == nome_cliente:
				for i, v in enumerate(item):
					chave = str(i)
					if i > 0:
						total += v[2]
						linha = f'{v[0]} {v[1]} R$ {v[2]:.2f}'
						elemento = [sg.Checkbox(linha, key=chave)]
						pedido.append(elemento)
						if event != '-EXCLUIR_ITEM-':
							pedido_atual.append(v)
						if len(linha) > x:
							x = len(linha)
		return total, x

	dados = Cliente.visualizar_cliente(nome_cliente, True)
	nome, endereco, bairro = dados[0][0], dados[0][1], dados[0][2]
	pedido = []
	if retornar_nome:
		return nome
	if nome not in pedido_atual:
		pedido_atual.append(nome)
	total, x = montar_checkbox(pedido_atual)
	return pedido, total, x, nome, endereco, bairro

def tela_inicial():
	tema = 'Gerenciador de pedidos da Pizza Boa'
	layout = [
		[sg.Text(tema, size=(len(tema), 2))],
		[sg.Button('Fazer pedido', key='-MENU-')],
		[sg.Button('Pedidos', key='-PEDIDOS-')],
		[sg.Button('Clientes', key='-CLIENTES-')]
	]
	return sg.Window('inicio', layout, finalize=True)

def voltar():
	global janela

	memoria_janelas.pop()
	janela.close()
	janela = memoria_janelas[-1]()

def menu():
	val1, val2 = True, False

	if cliente_selecionado:
		val1, val2 = False, True
	if alterando_pedido and pedido_alterado == False:
		val1 = val2

	layout = [
		[sg.Button('Pizzas', key='-PIZZAS-')],
		[sg.Button('Bebidas', key='-BEBIDAS-')],
		[sg.Text()],
		[sg.Button('Sacola', visible=val2, key='-SACOLA-')],
		[sg.Button('Cancelar pedido', button_color='darkgoldenrod', key='-CANCELAR_PEDIDO-', visible=val2), sg.Button(
			'Finalizar pedido', button_color='green', visible=val2, key='-FINALIZAR-')],
		[sg.Button('Voltar', key='-VOLTAR-', visible=val1)],
	]
	return sg.Window('menu', layout, finalize=True)

def pedidos():
	global pedidos_pendentes
	pedidos = []
	tamanho = 0
	y = ''
	visivel = True
	if pedidos_pendentes == []:
		pedidos = ['Nenhum pedido pendente']
		visivel = False
	else:
		for c in pedidos_pendentes:
			individual_pedido = ''
			linha = []
			for i, k in enumerate(c):
				if i == 0:
					linha.append([k])
				else:
					y = str(k[0]) + ' ' + str(k[1])
					individual_pedido += '; ' + y if individual_pedido != '' else y
					linha.append(individual_pedido)
			pedidos.append(linha)
			soma_campos = len(linha[0]) + len(linha[1])
			if soma_campos > tamanho:
				tamanho = soma_campos
	layout = [
		[sg.Table(pedidos, headings=['Cliente', 'Pedido'], justification='left', key='-BOX-', size=(tamanho, 10)), sg.Button(
			'Visualizar', visible=visivel, key='-VISUALIZAR-')],
		[sg.Button('Voltar', key='-VOLTAR-')]
	]
	return sg.Window('Pedidos', layout, finalize=True)

def visualizar_pedido(retornar_nome=False):
	if retornar_nome:
		return dados_pagina_visualizar(True)
	pedido, total, x, nome, endereco, bairro = dados_pagina_visualizar()
	if x < 35:
		x = 35

	layout = [
		[sg.Text('Dados do Cliente', justification='center')],
		[sg.Text(f'Nome: {nome}')],
		[sg.Text(f'Endereço: {endereco}')],
		[sg.Text(f'Bairro: {bairro}')],
		[sg.Text()],
		[sg.Text('Pedido', justification='center')],
		[sg.Column(pedido, key='-CHECK-')],
		[sg.Text(f'Valor total: R$ {total:,.2f}', size=(x, 1), justification='right', font=('Ariel', 12))],
		[sg.Button('Excluir', button_color='firebrick', key='-EXCLUIR_ITEM-'), sg.Button('Adicionar', key='-ADICIONAR_ITEM2-')],
		[sg.Button('Voltar', key='-VOLTAR-'), sg.Text(size=(x-15, 1)), sg.Button('Pedido entregue', button_color='green', key='-ENTREGUE-')]
	]
	return sg.Window('Janela de Visualização', layout, finalize=True)

def clientes(pedindo=False):
	global tabela
	clientes = Cliente.read(pedindo, pedidos_pendentes)
	tabela = []
	val1, val2 = True, False
	chave_botao = '-VOLTAR-'

	for item in clientes:
		linha = list(item)
		tabela.append(linha)
		tabela = sorted(tabela)
	tabela = sg.Table(tabela, headings=['Nome', 'Endereço', 'Bairro'], justification='left', key='-TABELA-')
	if clientes == []:
		tabela = sg.Listbox(['Nenhum cliente cadastrado'], size=(30, 10), key='-TABELA-')
	if pedindo:
		val1, val2 = False, True
		chave_botao = '-VOLTAR2-'

	layout = [
		[sg.Text('Clientes cadastrados:')],
		[tabela, sg.Column([
				[sg.Button('Novo cliente', key='-NOVO_CLIENTE-')],
				[sg.Button('Editar', key='-EDITAR-')],
				[sg.Button('excluir', key='-EXCLUIR-', visible=val1, button_color='firebrick')],
				[sg.Text()],
				[sg.Text()],
				[sg.Text()],
				[sg.Button('Selecionar', button_color='green', visible=val2, key='-SELECIONAR-')]
			])
		],
		[sg.Text()],
		[sg.Button('Voltar', size=(6, 2), key=chave_botao)]
	]
	return sg.Window('Clientes', layout, finalize=True)

def novo_cliente():
	tamanho = (9, 1)
	layout = [
		[sg.Text('Nome', size = tamanho), sg.Input(key='nome')],
		[sg.Text('Endereço', size = tamanho), sg.Input(key='endereco')],
		[sg.Text('Bairro', size = tamanho), sg.Input(key='bairro')],
		[sg.Text()],
		[sg.Button('Cancelar', size=(6, 2), key='-CANCELAR-'), sg.Button('Cadastrar', size=(6, 2), key='-CADASTRAR-')]
	]
	return sg.Window('Cadastrar novo cliente', layout, finalize=True)

def produtos(produto):
	elementos_coluna = []

	if produto == 'pizza':
		x = sorted(Pizza.read())#sabores
		y = chaves_pizzas
		texto = 'Nenhuma pizza cadastrada'
		titulo = 'Pizzas'
		botao_adicionar = '-JANELA_ADICIONAR_PIZZA-'
		botao_excluir = '-EXCLUIR_PIZZA-'
	if produto == 'bebida':
		x = sorted(Bebida.read())#bebidas
		y = chaves_bebidas
		text = 'Nenhuma bebida cadastrada'
		titulo = 'Bebidas'
		botao_adicionar = '-JANELA_ADICIONAR_BEBIDA-'
		botao_excluir = '-EXCLUIR_BEBIDA-'
	for item in x:
		texto_botao = item[0].title()
		chave = '-'+texto_botao.upper()+'-'
		if chave not in y:
			y.append(chave)
		botao = [sg.Button(texto_botao, key=chave)]
		elementos_coluna.append(botao)

	elemento = sg.Text('Nenhuma pizza cadastrada') if len(elementos_coluna) == 0 else sg.HorizontalSeparator()
	ordem = ([sg.Text()], [elemento]) if len(elementos_coluna) != 0 else ([elemento], [sg.Text()])

	layout = [
		[sg.Column(elementos_coluna, key='-COLUNA-')],
		ordem[0:],
		[sg.Button('Adicionar', key=botao_adicionar), sg.Button('Excluir', key=botao_excluir)],
		[sg.Button('Voltar', key='-VOLTAR-')]
	]
	return sg.Window(titulo, layout, finalize=True)

def sacola():
	elementos_coluna = []
	total = 0
	x = 30

	for i, v in enumerate(pedido_atual):
		if i > 0:
			preco = v[-1]
			texto = f'{v[0]} {v[1]} R$ {preco:.2f}'
			chave = str(i)
			check = [sg.Checkbox(texto, key=chave)]
			elementos_coluna.append(check)
			total += preco
			if len(texto) > x:
				x = len(texto)

	layout = [
		[sg.Text('Itens atuais do pedido:')],
		[sg.Column(elementos_coluna, key='-ITENS_SACOLA-')],
		[sg.Text(f'Valor total: R$ {total:,.2f}', size=(x, 1), justification='right', font=('Ariel', 12))],
		[sg.Button('Voltar', key='-VOLTAR-'), sg.Button('Excluir', button_color='firebrick', key='-EXCLUIR_ITEM-')]
	]
	return sg.Window('Sacola', layout, finalize=True)

def janela_adicionar_pizza():
	layout = [
		[sg.Text('Sabor', size=(10, 1)), sg.Input(key='-SABOR-')],
		[sg.Text('Ingredientes'), sg.Input(key='-INGREDIENTES-')],
		[sg.Text('preço', size=(10, 1)), sg.Input(key='-PRECO-')],
		[sg.Button('Adicionar', key='-ADICIONAR_PIZZA-'), sg.Button('Cancelar', key='-CANCELAR-')],
	]
	return sg.Window('Nova pizza', layout, finalize=True)

def janela_adicionar_bebida():
	layout = [
		[sg.Text('Bebida', size=(8, 1)), sg.Input(key='-BEBIDA-')],
		[sg.Text('Tamanho', size=(8, 1)), sg.Input(key='-TAMANHO-')],
		[sg.Text('preço', size=(8, 1)), sg.Input(key='-PRECO-')],
		[sg.Button('Adicionar', key='-ADICIONAR_BEBIDA-'), sg.Button('Cancelar', key='-CANCELAR-')],
	]
	return sg.Window('Nova pizza', layout, finalize=True)
	
def fechar_programa():
	layout = [
		[sg.Text('Tem certeza que deseja fechar o programa?')],
		[sg.Button('Sim', key='-SIM-'), sg.Button('Não', key='-NAO-')]
	]
	return sg.Window('Encerrar programa', layout, finalize=True, keep_on_top=True)

def janela_confirmar_exclusao():
	layout = [
		[sg.Text(f'Tem certeza que deseja excluir o registro de {a_excluir[0]}?')],
		[sg.Button('Sim', key='-SIM-'), sg.Button('Não', key='-NAO-')]
	]
	return sg.Window('Confirmar Exclusão', layout, finalize=True)

def janela_editar():
	tamanho = (9, 1)
	layout = [
		[sg.Text('Nome', size = tamanho), sg.Input(nome, key='nome')],
		[sg.Text('Endereço', size = tamanho), sg.Input(endereco, key='endereco')],
		[sg.Text('Bairro', size = tamanho), sg.Input(bairro, key='bairro')],
		[sg.Text()],
		[sg.Button('Cancelar', size=(6, 2), key='-CANCELAR-'), sg.Button('atualizar', size=(6, 2), key='-ATUALIZAR-')]
	]
	return sg.Window('Editar Registro', layout, finalize=True)

def pedir():
	if produto == 'pizza':
		visivel = True
		texto1 = f'Pizza de {item[0]}'
		texto2 = f'Ingredientes: {ingredientes}'
	if produto == 'bebida':
		x = item[0].title()
		visivel = False
		texto1 = f'{x} {tamanho}'
		texto2 = ''

	layout = [
		[sg.Text(texto1)],
		[sg.Text(texto2, visible=visivel)],
		[sg.Text(f'Preço: R$ {preco:,.2f}')],
		[sg.Text('Quantidade'), sg.Combo(values=list(range(1, 100)), default_value=1, key='-QUANTIDADE-')],
		[sg.Text('Observações:', visible=visivel), sg.Input(key='-OBS-', visible=visivel)],
		[sg.Text('Selecione as opções desejadas abaixo.', visible=visivel)],
		[sg.Checkbox('Borda recheada', key='-BORDA-', visible=visivel)],
		[sg.Text('Massa:', visible=visivel)],
		[sg.Radio('Comum', group_id='massa', key='-COMUM-', visible=visivel), sg.Radio(
			'Pan', group_id='massa', default=True,key='-PAN-', visible=visivel)],
		[sg.Button('Cancelar', key='-VOLTAR-'), sg.Button('Adicionar ao pedido', key='-ADICIONAR_AO_PEDIDO-')]
	]
	return sg.Window('Customizando pizza', layout, finalize=True)

def excluir_produto(produto):
	if produto == 'pizza':
		x = Pizza.read()
		y = sorted(Pizza.read())
		z = chaves_pizzas
		texto = 'Selecione os sabores de pizza que deseja excluir.'
	if produto == 'bebida':
		x = Bebida.read()
		y = sorted(Bebida.read())
		z = chaves_bebidas
		texto = 'Selecione as bebidas que deseja excluir.'
	elementos_coluna = []

	for item in y:
		texto_box = item[0].capitalize()
		chave = '-'+texto_box.upper()+'-'
		if chave not in z:
			z.append(chave)
		check = [sg.Checkbox(texto_box, key=chave)]
		elementos_coluna.append(check)

	layout = [
		[sg.Text(texto)],
		[sg.Column(elementos_coluna)],
		[sg.Button('Cancelar', key='-CANCELAR-'), sg.Button('Deletar', button_color='firebrick', key='-DELETAR-')]
	]
	return sg.Window('Confirmar exclusão', layout, finalize=True)

def cancelar_pedido():
	layout = [
		[sg.Text(f'Tem certeza que quer cancelar o pedido de {pedido_atual[0]}?')],
		[sg.Button('Sim', key='-SIM-'), sg.Button('Não', key='-CANCELAR-')]
	]
	return sg.Window('Cancelar Pedido', layout, finalize=True, keep_on_top=True)

def fechar_pedido():
	layout = [
		[sg.Text(f'Tem certeza que deseja fechar o pedido de {nome}')],
		[sg.Button('Sim', key='-SIM-'), sg.Button('Não', key='-NAO-')]
	]
	return sg.Window('Fechar Pedido', layout, finalize=True, keep_on_top=True)

sg.theme('DefaultNoMoreNagging')
memoria_janelas = [tela_inicial]
memoria_janelas2 = []

lista_janelas = {'-VOLTAR-':tela_inicial, '-MENU-':menu, '-CLIENTES-':clientes}
lista_chaves_janelas = list(lista_janelas.keys())
lista_valores_janelas = list(lista_janelas.values())

cliente_selecionado = alterando_pedido = pedido_alterado = sacola_aberta = False

chaves_pizzas = []
chaves_bebidas = []
pedido_atual = []
pedidos_pendentes = []

janela_fechar_aberta = janela_excluir_aberta = cancelar_pedido_aberto = fechar_pedido_aberto = False

tabela = None

janela = tela_inicial()

while True:
	window, event, values = sg.read_all_windows()

	if event in lista_chaves_janelas:
		for i, v in enumerate(lista_chaves_janelas):
			if event == v:
				if event == '-VOLTAR-':
					if memoria_janelas2 != []:
						pedido_atual.pop()
					if type(memoria_janelas[-1]) == dict:
						pedido_atual = []
						alterando_pedido = cliente_selecionado = False
					memoria_janelas.pop()
				else:
					memoria_janelas.append(lista_valores_janelas[i])
				janela.close()
				if event == '-VOLTAR-' and type(memoria_janelas[-1]) == str:
					janela = produtos(memoria_janelas[-1])
				elif event == '-VOLTAR-' and type(memoria_janelas[-1]) == dict:
					janela = list(memoria_janelas[-1].values())[0]()
				else:
					janela = memoria_janelas[-1]()
	elif event in chaves_pizzas or event in chaves_bebidas:
		item = (event[1:-1].lower(),)
		if produto == 'pizza':
			ingredientes, preco = Pizza.read('unica', item)
		if produto == 'bebida':
			tamanho, preco = Bebida.read('unica', item)
		janela.close()
		janela = pedir()
		memoria_janelas.append(pedir)
	elif event == '-PIZZAS-' or event == '-BEBIDAS-':
		janela.close()
		produto = 'pizza' if event == '-PIZZAS-' else 'bebida'
		janela = produtos(produto)
		memoria_janelas.append(produto)
	elif event == '-ADICIONAR_AO_PEDIDO-':
		quantidade = values['-QUANTIDADE-']
		preco *= quantidade
		if alterando_pedido:
			pedido_alterado = True
		if produto == 'pizza':
			obs = values['-OBS-']
			massa = 'PAN' if values['-PAN-'] else 'comum'
			x = 'pizzas' if quantidade > 1 else 'pizza'
			if values['-BORDA-']:
				item = f'{x} {massa} de {item[0]} com borda recheada'
			else:
				item = f'{x} {massa} de {item[0]}'
			if obs != '':
				item += f', {obs}'
		if produto == 'bebida':
			item = item[0]
		pedido_atual.append([quantidade, item, preco])
		if cliente_selecionado:
			sg.Popup('item adicionado ao pedido', keep_on_top=True)
			janela.close()
			if alterando_pedido:
				del(memoria_janelas[-2:])
				janela = memoria_janelas[-1]()
			else:
				del(memoria_janelas[2:])
				janela = menu()
		else:	
			janela.hide() #Não posso fechar, pois preciso de parâmetros para a função pedir_pizza
			janela3 = clientes(True)
			memoria_janelas2.append(clientes)
	elif event == '-SACOLA-':
		janela.close()
		janela = sacola()
		sacola_aberta = True
		memoria_janelas.append(sacola)
	elif event == '-EXCLUIR_ITEM-':
		valores = list(values.values())
		selecionado = False
		contador = 0
		if alterando_pedido:
			pedido_alterado = True
		if True in valores:
			selecionado = True
			contador = valores.count(True)
		if selecionado is False:
			sg.Popup('ERRO: nenhum item selecionado', text_color='firebrick')
		elif contador == len(valores):
			janela2 = cancelar_pedido()
			cancelar_pedido_aberto = True
		else:
			c = 1
			for i, v in enumerate(values):
				if values[v] == True:
					del(pedido_atual[i+c])
					if sacola_aberta is False:
						del(pedidos_pendentes[0][i+c])
					c -= 1
			janela.close()
			if sacola_aberta:
				janela = sacola()
			else:
				janela = visualizar_pedido()
	elif event == '-ADICIONAR_ITEM2-':
		janela.close()
		cliente_selecionado = True
		janela = menu()
		memoria_janelas.append(menu)
	elif event == '-CANCELAR_PEDIDO-':
		janela2 = cancelar_pedido()
		cancelar_pedido_aberto = True
	elif event == '-FINALIZAR-':
		if alterando_pedido:
			for i, v in enumerate(pedidos_pendentes):
				if v[0] == pedido_atual[0]:
					pedidos_pendentes[i] = pedido_atual
		else:
			pedidos_pendentes.append(pedido_atual)	
		pedido_atual = []
		cliente_selecionado = alterando_pedido = pedido_alterado = sacola_aberta = False		 
		sg.Popup('Pedido Finalizado', keep_on_top=True)
		janela.close()
		memoria_janelas = [tela_inicial]
		janela = tela_inicial()
	elif event == '-PEDIDOS-':
		janela.close()
		janela = pedidos()
		memoria_janelas.append(pedidos)
	elif event == '-VISUALIZAR-':
		try:
			nome_cliente = pedidos_pendentes[values['-BOX-'][0]][0]
			janela.close()
			janela = visualizar_pedido()
			memoria_janelas.append({'-VISUALIZAR-':visualizar_pedido})
			alterando_pedido = True
		except IndexError:
			sg.Popup('Selecione um pedido')
	elif event == '-ENTREGUE-':
		nome = visualizar_pedido(True)
		janela2 = fechar_pedido()
		fechar_pedido_aberto = True
	elif event == '-VOLTAR2-':
		pedido_atual.pop()
		janela3.close()
		del(memoria_janelas2[0:])
		janela.un_hide()
	elif event == '-SELECIONAR-':
		if values['-TABELA-'] == []:
			sg.Popup('Por favor, selecione um cliente', keep_on_top=True)
		else:
			pedido_atual.insert(0, tabela.Values[values['-TABELA-'][0]][0])
			cliente_selecionado = True
			sg.Popup('Item adicionado ao pedido', keep_on_top=True)
			janela3.close()
			janela.close()
			janela = menu()
			memoria_janelas2 = []
			del(memoria_janelas[2:])
	elif event == '-JANELA_ADICIONAR_PIZZA-':
		janela2 = janela_adicionar_pizza()
	elif event == '-JANELA_ADICIONAR_BEBIDA-':
		janela2 = janela_adicionar_bebida()
	elif event == '-ADICIONAR_PIZZA-':
		try:
			novo_sabor = values['-SABOR-'].strip().lower()
			ingredientes = values['-INGREDIENTES-']
			preco = values['-PRECO-']			
			Pizza.cadastrar(novo_sabor, ingredientes, preco)
			janela2.close()
			janela.close()
			janela = produtos('pizza')
			sg.Popup(f'Pizza de {novo_sabor} adicionada ao menu', keep_on_top=True)
		except ValueError:
			sg.Popup('ERRO: Por favor, no campo preço, digite apenas números e use ponto no lugar da vírgula.')
	elif event == '-ADICIONAR_BEBIDA-':
		try:
			nova_bebida = values['-BEBIDA-'].strip().lower()
			tamanho = values['-TAMANHO-']
			preco = values['-PRECO-']			
			Bebida.cadastrar(nova_bebida, tamanho, preco)
			janela2.close()
			janela.close()
			janela = produtos('bebida')
			sg.Popup(f'{nova_bebida} cadastrado ao menu', keep_on_top=True)
		except ValueError:
			sg.Popup('ERRO: Por favor, no campo preço, digite apenas números e use ponto no lugar da vírgula.')		
	elif event == '-DELETAR-':
		if True in values.values():
			for k in values:
				if values[k] == True:
					a_excluir = (k[1:-1].lower(),)
					if produto == 'pizza':
						Pizza.excluir(a_excluir)
					if produto == 'bebida':
						Bebida.excluir(a_excluir)
			janela2.close()
			janela.close()
			if memoria_janelas2[-1] == 'pizza':
				janela = produtos('pizza')
			if memoria_janelas2[-1] == 'bebida':
				janela = produtos('bebida')
			memoria_janelas2.pop()
		else:
			sg.Popup('Selecione um sabor de pizza a ser deletado.')
	elif event == '-NOVO_CLIENTE-':
		janela2 = novo_cliente()
	elif event == '-CADASTRAR-' or event == '-ATUALIZAR-':
		novo_nome = values['nome'].strip().title()
		novo_endereco = values['endereco'].strip().title()
		novo_bairro = values['bairro'].strip().title()
		if novo_nome == '' or novo_endereco == '' or novo_bairro == '':
			sg.Popup('Por favor, preencha todos os campos', keep_on_top=True)
		elif event == '-CADASTRAR-':
			Cliente.cadastrar(novo_nome, novo_endereco, novo_bairro)
		else:
			Cliente.atualizar(novo_nome, novo_endereco, novo_bairro, nome)
			sg.Popup('Dados atualizados com sucesso', keep_on_top=True)
		if event == '-CADASTRAR-' or event == '-ATUALIZAR-':
			janela2.close()
			if pedido_atual == []:
				janela.close()
				janela = clientes()
			else:
				pedido_atual.insert(0, values['nome'])
				cliente_selecionado = True
				sg.Popup('Item adicionado ao pedido', keep_on_top=True)
				janela3.close()
				janela.close()
				janela = menu()
				memoria_janelas2 = []
	elif event == '-CANCELAR-':
		if cancelar_pedido_aberto == True:
			cancelar_pedido_aberto = False
			janela3.close()
		janela2.close()
	elif event == '-EXCLUIR-' or event == '-EDITAR-':
		if Cliente.read() == []:
			sg.Popup('Não há nenhum cliente cadastrado no sistema.', keep_on_top=True)
		elif values['-TABELA-'] == []:
			sg.Popup('Por favor, selecione um cliente', keep_on_top=True)
		elif event == '-EXCLUIR-':
			a_excluir = (tabela.Values[values['-TABELA-'][0]][0],)
			janela_excluir = janela_confirmar_exclusao()
			janela_excluir_aberta = True
		elif event == '-EDITAR-':
			nome = (tabela.Values[values['-TABELA-'][0]][0],)
			nome, endereco, bairro = Cliente.visualizar_cliente(nome)[0]
			janela2 = janela_editar()
	elif event == '-EXCLUIR_PIZZA-':
		janela2 = excluir_produto('pizza')
		memoria_janelas2.append('pizza')
	elif event == '-EXCLUIR_BEBIDA-':
		janela2 = excluir_produto('bebida')
		memoria_janelas2.append('bebida')
	else:
		if event == '-SIM-':
			if janela_fechar_aberta:
				break
			elif cancelar_pedido_aberto:
				if sacola_aberta is False:
					for i, v in enumerate(pedidos_pendentes):
						if v[0] == pedido_atual[0]:
							del(pedidos_pendentes[i])
				pedido_atual = []
				cliente_selecionado = False
				janela.close()
				janela2.close()
				cancelar_pedido_aberto = False
				alterando_pedido = False
				janela = tela_inicial()
				sg.Popup('Pedido cancelado', keep_on_top=True)
				del(memoria_janelas[1:])
			elif fechar_pedido_aberto:
				for i, v in enumerate(pedidos_pendentes):
					if v[0] == nome:
						del(pedidos_pendentes[i])
				pedido_atual = []
				janela2.close()
				sg.Popup('Pedido fechado com sucesso.', keep_on_top=True)
				janela.close()
				fechar_pedido_aberto = False
				memoria_janelas.pop()
				janela = pedidos()
			else:
				Cliente.excluir(a_excluir)
				janela_excluir.close()
				janela_excluir_aberta = False
				janela['-TABELA-'].Update(Cliente.read())
		elif janela_excluir_aberta:
			janela_excluir.close()
			janela_excluir_aberta = False
		elif janela_fechar_aberta:
			janela_fechar.close()
			janela_fechar_aberta = False
		elif fechar_pedido_aberto:
			janela2.close()
			fechar_pedido_aberto = False
		else:
			janela_fechar = fechar_programa()
			janela_fechar_aberta = True