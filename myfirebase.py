import requests
from kivy.app import App

class MyFireBase():
    API_KEY = 'AIzaSyBI-3X1qGOuk411c9jT4BTkn5SCvINa7zA'


    def criar_conta (self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'
        info = {'email':email,
                'password': senha,
                'returnSecureToken': True}

        requisicao = requests.post(link, data=info)

        requisicao_dic = requisicao.json()


        if requisicao.ok:
            print('Cadastro realizado com sucesso')
            # requisicao_dic['idToken']  --> é a sua autenticação
            # requisicao_dic['refreshToken']  --> mantêm o usuário logado no banco de Dados
            # requisicao_dic['localId'] --> é o 'ID' do usuário no bando de Dados que criamos no google
            refresh_token = requisicao_dic['refreshToken']
            local_id = requisicao_dic['localId']
            id_token = requisicao_dic['idToken']

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            with open('refreshToken.txt', 'w') as arquivo:   # cria um arquivo.txt e ao mesmo tempo cria uma variável
                arquivo.write(refresh_token)                  # que eu posso manipular !!!!

            req_id = requests.get(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}')
            id_vendedor = req_id.json()


            link = f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}'
            info_usuario = f'{{"avatar": "hash.png" , "equipe": "" , "total_vendas": "0", "vendas": "", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usurario = requests.patch(link, data=info_usuario)

            # Atualizar o proximo_id_vendedor
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f'https://aplicativokivyojeda-default-rtdb.firebaseio.com/.json?auth={id_token}', data=info_id_vendedor)


            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('homepage')

        else:
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['loginpage']
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1,0,0,1)


    def fazer_login(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
        info = {'email': email,
                'password': senha,
                'returnSecureToken': True}

        requisicao = requests.post(link, data=info)

        requisicao_dic = requisicao.json()

        if requisicao.ok:
            print('Login realizado com sucesso')
            # requisicao_dic['idToken']  --> é a sua autenticação
            # requisicao_dic['refreshToken']  --> mantêm o usuário logado no banco de Dados
            # requisicao_dic['localId'] --> é o 'ID' do usuário no bando de Dados que criamos no google
            refresh_token = requisicao_dic['refreshToken']
            local_id = requisicao_dic['localId']
            id_token = requisicao_dic['idToken']

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            with open('refreshToken.txt', 'w') as arquivo:   # cria um arquivo.txt e ao mesmo tempo cria uma variável
                arquivo.write(refresh_token)                  # que eu posso manipular !!!!


            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('homepage')

        else:
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['loginpage']
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1,0,0,1)

    def trocar_token(self, refresh_token):
        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
        info = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        requisicao = requests.post(link, data=info)

        requisicao_dic = requisicao.json()
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']

        return (local_id, id_token)