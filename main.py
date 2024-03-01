import os
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import parse_qs, urlparse
import hashlib
from database import conexao


class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            f = open(os.path.join(path, 'home.html'), 'r')
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read().encode('UTF-8'))
            f.close()
            return None

        except FileNotFoundError:
            pass

        return super().list_directory(path)

    def check_login(self, login, senha):
        # verifica se o login já existe no arquivo
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]

        return False

    def adicionar_usuario(self, login, senha, nome):
        cursor = conexao.cursor()

        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login (login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))

        conexao.commit()

        conexao.close()

    def remover_ultima_linha(self, arquivo):
        print('vou excluir ultima linha')
        with open(arquivo, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(arquivo, 'w', encoding='utf-8') as file:
            file.writelines(lines[:-1])

    def do_GET(self):
        """Serve a GET request."""
        if self.path == '/login':
            # tenta abrir o arquivo login.html
            try:
                with open(os.path.join(os.getcwd(), 'index.html'), 'r', encoding='UTF-8') as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode('UTF-8'))

            except FileNotFoundError:
                self.send_error(404, "File not found")

        elif self.path == '/login_failed':
            # responde ao cliente com a mensagem de login/senha incorreta
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            # le o conteudo da pagina login.html
            with open(os.path.join(os.getcwd(), 'register.html'), 'r', encoding='UTF-8') as login_file:
                content = login_file.read()

            # adiciona a mensagem de erro no conteudo da pagina
            self.wfile.write(content.encode('UTF-8'))

        elif self.path.startswith('/cadastro'):
            # extraindo os parametros da url
            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get('login', [''])[0]
            senha = query_params.get('senha', [''])[0]

            # mensagem de boas-vindas
            welcome_message = f"Olá {login}, seja bem-vindo! Percebemos que você é novo por aqui. Faça seu cadastro!"

            # responde ao cliente com a pagina de cadastro
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            # le o conteudo da pagina cadastro.html
            with open(os.path.join(os.getcwd(), 'register.html'), 'r', encoding='utf-8') as cadastro_file:
                content = cadastro_file.read()

            # substitui os marcadores de posição pelos valores correspondentes
            content = content.replace('{login}', login)
            content = content.replace('{senha}', senha)
            content = content.replace('{welcome_message}', welcome_message)

            # envia o conteudo modificado para o cliente
            self.wfile.write(content.encode('utf-8'))

            return  # adicionando um return para evitar a execução do restante do código

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/enviar_login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('UTF-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get("email", [''])[0]
            senha = form_data.get("senha", [''])[0]

            if self.check_login(login, senha):

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                mensagem = f"Usuário {login} logado com sucesso!"
                self.wfile.write(mensagem.encode('UTF-8'))
                self.wfile.flush()

            else:
                # verifica se o login ja existe no arquivo
                cursor = conexao.cursor()
                cursor.execute("SELECT login FROM dados_login WHERE login = %s", (login,))
                resultado = cursor.fetchone()

                if resultado:
                    self.send_response(302)
                    self.send_header('location', '/login_failed')
                    self.end_headers()
                    cursor.close()
                    return

                else:
                        self.send_response(302)
                        self.send_header('Location', f'cadastro?Login={login}&senha={senha}')
                        self.end_headers()
                        cursor.close()
                        return

        elif self.path.startswith('/confirmar_cadastro'):
            # obtém o comprimento do corpo da requisição
            content_length = int(self.headers['Content-Length'])
            # le o corpo da requisição
            body = self.rfile.read(content_length).decode('utf-8')
            # parseia os dados do formulário
            form_data = parse_qs(body, keep_blank_values=True)

            # query_params = parse_qs(urlparse(self.path).query)
            login = form_data.get('login', [''])[0]
            senha = form_data.get('senha', [''])[0]
            nome = form_data.get('nome', [''])[0]

            # hash a senha fornecida pelo usuario
            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

            self.adicionar_usuario(login, senha, nome)

            with open(os.path.join(os.getcwd(), 'msg_sucesso.html'), 'rb') as file:
                content = file.read().decode('utf-8')

            content = content.replace('{login}', login)
            content = content.replace('{nome}', nome)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

            if self.check_login(login, senha):
                # atualiza o arquivo com o nome, se a senha estiver correta

                with open('arquivos.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                with open('arquivos.txt', 'w', encoding='utf-8') as file:
                    for line in lines:
                        stored_login, stored_senha, stored_nome = line.strip().split(';')
                        if login == stored_login and senha_hash == stored_senha:
                            line = f'{login};{senha_hash};{nome}\n'
                        file.write(line)

                # redireciona o cliente para onde desejar após a condirmação
                with open(os.path.join(os.getcwd(), 'index.html'), 'r', encoding='UTF-8') as response_file:
                    content = response_file.read()

                self.send_response(302)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))

            else:
                # se o usuario nao existe ou a senha esta incorreta, redireciona para outra pagina
                self.remover_ultima_linha('dados_login.txt')
                self.send_response(302)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write('A senha não confere. Retome o procedimento!'.encode('utf-8'))

        else:
            super(MyHandler, self).do_POST()


# IP e Porta utilizada
porta = 8000
ip = "0.0.0.0"

with socketserver.TCPServer((ip, porta), MyHandler) as httpd:
    print(f"Servidor iniciado no IP {ip}: {porta}")
    httpd.serve_forever()
