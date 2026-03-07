import json
from datetime import datetime, timedelta

class Livro:
    def __init__(self, titulo, autor, isbn, disponivel=True):
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.disponivel = disponivel

    def to_dict(self):
        return self.__dict__


class Usuario:
    def __init__(self, nome, cpf):
        self.nome = nome
        self.cpf = cpf
        self.livros_emprestados = {}

    def to_dict(self):
        return {
            "nome": self.nome,
            "cpf": self.cpf,
            "livros_emprestados": self.livros_emprestados
        }


class Biblioteca:

    def __init__(self):
        self.livros = []
        self.usuarios = []

    def adicionar_livro(self, livro):
        self.livros.append(livro)

    def cadastrar_usuario(self, usuario):
        self.usuarios.append(usuario)

    def buscar_livro(self, titulo):
        for livro in self.livros:
            if livro.titulo.lower() == titulo.lower():
                return livro
        return None

    def emprestar_livro(self, titulo, cpf):

        livro = self.buscar_livro(titulo)

        usuario = next((u for u in self.usuarios if u.cpf == cpf), None)

        if not livro:
            print("Livro não encontrado")
            return

        if not usuario:
            print("Usuário não encontrado")
            return

        if not livro.disponivel:
            print("Livro indisponível")
            return

        prazo = datetime.now() + timedelta(days=7)

        usuario.livros_emprestados[livro.isbn] = prazo.strftime("%d/%m/%Y")
        livro.disponivel = False

        print("Livro emprestado com sucesso")

    def devolver_livro(self, isbn, cpf):

        usuario = next((u for u in self.usuarios if u.cpf == cpf), None)

        if not usuario:
            print("Usuário não encontrado")
            return

        if isbn not in usuario.livros_emprestados:
            print("Esse usuário não pegou esse livro")
            return

        del usuario.livros_emprestados[isbn]

        for livro in self.livros:
            if livro.isbn == isbn:
                livro.disponivel = True

        print("Livro devolvido")

    def salvar(self):

        dados = {
            "livros": [l.to_dict() for l in self.livros],
            "usuarios": [u.to_dict() for u in self.usuarios]
        }

        with open("biblioteca.json", "w") as f:
            json.dump(dados, f, indent=4)

    def carregar(self):

        try:
            with open("biblioteca.json") as f:
                dados = json.load(f)

            for l in dados["livros"]:
                self.livros.append(Livro(**l))

            for u in dados["usuarios"]:
                usuario = Usuario(u["nome"], u["cpf"])
                usuario.livros_emprestados = u["livros_emprestados"]
                self.usuarios.append(usuario)

        except FileNotFoundError:
            pass

def menu():

    biblioteca = Biblioteca()
    biblioteca.carregar()

    while True:

        print("\n--- Biblioteca ---")
        print("1 - Adicionar livro")
        print("2 - Cadastrar usuário")
        print("3 - Emprestar livro")
        print("4 - Devolver livro")
        print("5 - Sair")

        op = input("Escolha: ")

        try:

            if op == "1":

                titulo = input("Título: ")
                autor = input("Autor: ")
                isbn = input("ISBN: ")

                biblioteca.adicionar_livro(Livro(titulo, autor, isbn))

            elif op == "2":

                nome = input("Nome: ")
                cpf = input("CPF: ")

                biblioteca.cadastrar_usuario(Usuario(nome, cpf))

            elif op == "3":

                titulo = input("Título do livro: ")
                cpf = input("CPF usuário: ")

                biblioteca.emprestar_livro(titulo, cpf)

            elif op == "4":

                isbn = input("ISBN do livro: ")
                cpf = input("CPF usuário: ")

                biblioteca.devolver_livro(isbn, cpf)

            elif op == "5":

                biblioteca.salvar()
                print("Sistema encerrado")
                break

            else:
                print("Opção inválida")

        except Exception as e:
            print("Erro:", e)


menu()