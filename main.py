import os
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import parse_qs

class MeuManipulador(SimpleHTTPRequestHandler):
    def listar_diretorio(self, path):
        try:
            # Tenta abrir o arquivo bsvc.html no diretório especificado
            f = open(os.path.join(path, 'index.html'), 'rb')
            # Se o arquivo for encontrado, envia uma resposta de sucesso (código 200)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Copia o conteúdo do arquivo para o cliente
            self.copyfile(f, self.wfile)
            f.close()
            return None
        except FileNotFoundError:
            pass
        # Se o arquivo não for encontrado, continua com o comportamento padrão
        return super().listar_diretorio(path)

    def do_GET(self):
        if self.path == "/login":
            try:
                with open(os.path.join(os.getcwd(), "index.html"), "r") as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write((""))
            except FileNotFoundError:
                self.send_error(404, "File not found")

        elif self.path == '/login_failed':
            self.send_response(200)
            self.send_header
            self.end_headers

            # with open(os.path.join(os.getcwd(), 'login.html'), 'r' enconding='utf-8') as file:
            #     content = login_file.read

            # mensagem = 'dfkjgfndkjngf'
            # content = content.replace("lionjdsbjfn")

            # self.wfile.write(content.encode())

        else:
            super().do_GET()

    
    def usuario_existente(self, login):
        with open('arquivos.txt', 'r') as dados_file:
            for line in dados_file:
                stored_login, _ = line.strip().split(';')
                print(stored_login)
                if login == stored_login:
                    return True
        return False

    def do_POST(self):

        if self.path == '/enviar_login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body)       

            with open(os.path.join(os.getcwd(), "response.html"), "r") as response_file:
                content = response_file.read()

            print("Dados do formulário: ")
            print("Email: ", form_data.get('email',[''])[0])
            print("Senha: ", form_data.get('senha',[''])[0])

            login = form_data.get('email', [''])[0]

            if self.usuario_existente(login):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                mensagem = f'Usuario {login} já consta em nossos registros'
                self.wfile.write(mensagem.encode('utf-8'))
            else:
                email=form_data.get('email',[''])[0]
                password = form_data.get('senha',[''])[0]

                with open('arquivos.txt', 'a') as dados_file_write:
                    dados_file_write.write(f"{email}; {password}\n")
                    print(dados_file_write)

            
        else:
            super(MeuManipulador.self).do_POST()



# Define o IP a ser utilizado
endereco_ip = '0.0.0.0'
porta = 8000

manipulador = MeuManipulador

# Inicia o servidor na porta especificada
with socketserver.TCPServer(("", porta), manipulador) as http:
    print(f"Servidor gerado na porta {porta}")

    # Mantém o servidor em execução indefinidamente
    http.serve_forever()