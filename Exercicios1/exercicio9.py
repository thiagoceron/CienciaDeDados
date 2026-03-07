class Produto:
    def __init__(self, nome, preco, estoque):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    def vender (self, quantidade):
        if quantidade <= self.estoque:
            self.estoque -= quantidade
            print(f"Venda realizada: {quantidade} unidades(s) de {self.nome}")
        else:
            print("Estoque insuficiente")

    def repor (self, quantidade):
        self.estoque += quantidade
        print(f"{quantidade} unidades(s) adicionadas ao estoque")

    def exibir_informacoes(self):
        print(f"Produto: {self.nome}")
        print(f"Preço: {self.preco:.2f}")
        print(f"Estoque: {self.estoque}")  

produto1 = Produto("Iphone", 5000, 10)

produto1.exibir_informacoes()
produto1.vender(3)
produto1.repor(7)
produto1.exibir_informacoes()