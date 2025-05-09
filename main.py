#este arquivo ESTÁ no ambiente vemv
# Consegui salvar no ambiente VENV
from enum import nonmember
from os import listdir


from kivy.app import App
from kivy.lang import Builder

from myfirebase import MyFireBase
from telas import  *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
from functools import partial
from myfirebase import MyFireBase
from bannervendedor import BannerVendedor
from datetime import date

GUI = Builder.load_file("main.kv")
class MainApp(App):
    cliente = None
    produto = None
    unidade = None


    def build(self):
        self.firebase = MyFireBase()
        return GUI

    def on_start(self): #--> assim que inicia o app, essa função é inicializada

        # carregar as fotos de perfil
        arquivo = os.listdir('icones/fotos_perfil')
        pagina_fotoperfil = self.root.ids['fotoperfilpage']
        lista_foto = pagina_fotoperfil.ids['lista_fotos_perfil']
        for foto in arquivo:
            imagem = ImageButton(source=f'icones/fotos_perfil/{foto}', on_release=partial(self.mudar_foto_perfil, foto))
            lista_foto.add_widget(imagem)

        # carregar as fotos dos clientes
        arquivo = os.listdir('icones/fotos_clientes')
        adicionar_vendaspage = self.root.ids['adicionarvendaspage']
        lista_clientes = adicionar_vendaspage.ids['lista_clientes']
        for foto_cliente in arquivo:
            imagem = ImageButton(source=f'icones/fotos_clientes/{foto_cliente}',
                                 on_release=partial (self.selecionar_cliente,foto_cliente ))
            label = LabelButton(text=foto_cliente.replace('.png', '').capitalize(),
                                on_release=partial (self.selecionar_cliente,foto_cliente ))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        # carregar as fotos dos produtos
        arquivo = os.listdir('icones/fotos_produtos')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_produto = pagina_adicionarvendas.ids['lista_produtos']
        for foto_produto in arquivo:
            imagem = ImageButton(source=f'icones/fotos_produtos/{foto_produto}',
                                 on_release=partial (self.selecionar_produto,foto_produto ))
            label = LabelButton(text=foto_produto.replace('.png', '').capitalize(),
                                on_release=partial (self.selecionar_produto,foto_produto ))
            lista_produto.add_widget(imagem)
            lista_produto.add_widget(label)

        # carregar a data
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        label_data = pagina_adicionarvendas.ids['label_data']
        label_data.text= f'Data: {date.today().strftime("%d/%m/%Y")}'

        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            # Abrir o arquivo de armazenamento do login do usuário
            with open('refreshToken.txt', 'r') as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token



            # Pegar informações do Usuário
            requisicao = requests.get(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{self.local_id}.json')
            requisicao_dic = requisicao.json()


            # Preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            # Preencher o ID único
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f'Seu ID único: {id_vendedor}'

            # Preencher o total de vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas[/color] [b]R$: {total_vendas}[/b]'

            # Preencher equipe
            self.equipe = requisicao_dic['equipe']

            # Preencher lista de vendas do Usuário
            try:
                print(requisicao_dic)
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], data=venda['data'], foto_cliente=venda['foto_cliente'],
                                         foto_produto=venda['foto_produto'], preco=venda['preco'], produto=venda['produto'],
                                         qtde=venda['quantidade'], unidade=venda['unidade'])

                    lista_vendas.add_widget(banner)

            except Exception as exceção:
                print(exceção)


            self.mudar_tela('homepage')


            # Preencher lista de equipe de vendedores
            equipe = requisicao_dic['equipe']
            lista_equipe = equipe.split(',')

            pagina_listavendedores = self.root.ids['listasvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)



        except:
            pass

    def mudar_tela(self,id_tela):
        gerenciador_tela = self.root.ids['screen_manager']
        gerenciador_tela.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{self.local_id}.json',
                                    data=info)

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link =  f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'

        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        pagina_adicionarvendedor = self.root.ids['adicionarvendedorpage']
        mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outrovendedor']

        if requisicao_dic == {}:
            mensagem_texto.text = 'Vendedor não encontrado'
        else:
            equipe = self.equipe.split(',')
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = 'Vendedor já faz parte da equipe'
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{self.local_id}.json',
                               data=info)
                mensagem_texto.text = 'Vendedor adicionado com sucesso'

    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace('.png', '')
        # pintar de azul o item que foi selecionado
        adicionar_vendaspage = self.root.ids['adicionarvendaspage']
        lista_clientes = adicionar_vendaspage.ids['lista_clientes']

        for item in list(lista_clientes.children):
            item.color = (1,1,1,1)
            # pintar de branco todos os outros item NÃO selecionados
            try:
                texto = item.text
                texto = texto.lower() + '.png'
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)

            except:
                pass

    def selecionar_produto(self, foto, *args):
        self.produto = foto.replace('.png', '')
        # pintar de azul o item que foi selecionado
        adicionar_vendaspage = self.root.ids['adicionarvendaspage']
        lista_produto = adicionar_vendaspage.ids['lista_produtos']

        for item in list(lista_produto.children):
            item.color = (1,1,1,1)
            # pintar de branco todos os outros item NÃO selecionados
            try:
                texto = item.text
                texto = texto.lower() + '.png'
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)

            except:
                pass


    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        self.unidade = id_label.replace('unidades_', '')
        pagina_adicionarvendas.ids['unidades_kg'].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids['unidades_unidades'].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids['unidades_litros'].color = (1, 1, 1, 1)

        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionarvendaspage = self.root.ids['adicionarvendaspage']
        data = pagina_adicionarvendaspage.ids['label_data'].text.replace('Data:', '')
        preco = pagina_adicionarvendaspage.ids['preco_total'].text
        quantidade = pagina_adicionarvendaspage.ids['qtde_total'].text

        if not cliente:
            pagina_adicionarvendaspage.ids['label_selecione_cliente'].color = (1,0,0,1)
        if not produto:
            pagina_adicionarvendaspage.ids['label_selecione_produto'].color = (1,0,0,0)
        if not  unidade:
            pagina_adicionarvendaspage.ids['unidades_kg'].color = (1,0,0,1)
            pagina_adicionarvendaspage.ids['unidades_unidades'].color = (1,0,0,1)
            pagina_adicionarvendaspage.ids['unidades_litros'].color = (1,0,0,1)
        if not preco:
            pagina_adicionarvendaspage.ids['label_preco'].color = (1,0,0,1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendaspage.ids['label_preco'].color = (1,0,0,1)
        if not quantidade:
            pagina_adicionarvendaspage.ids['label_qtde'].color = (1,0,0,1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendaspage.ids['label_qtde']

        # se a pessoa preencheu tudo certo, AGORA posso Adicionar a venda no Banco de Dados na Internet
        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_produto = produto + '.png'
            foto_cliente = cliente + '.png'

            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}", "quantidade": "{quantidade}"}}'
            requests.post(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{self.local_id}/vendas.json', data=info)

            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto,
                                 data=data, unidade=unidade,preco=preco,  qtde=quantidade)
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(banner)



            requisicao = requests.get(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json')
            total_vendas =float(requisicao.json())
            total_vendas += preco
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{self.local_id}.json',
                           data=info)

            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas[/color] [b]R$: {total_vendas}[/b]'

            self.mudar_tela('homepage')

        self.cliente = None
        self.produto = None
        self.unidade = None

MainApp().run()


