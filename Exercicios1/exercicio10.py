class Veiculo:
    def __init__(self, nome):
        self.nome = nome

    def tipo_habilitacao(self):
        print("Tipo de habilitação nao tem")

class Carro(Veiculo):
    def  tipo_habilitacao(self):
        print("Habilitação é o tipo B")           

class Moto(Veiculo):
    def tipo_habilitacao(self):
        print("Habilitação é o tipo A")

veiculo1 = Carro("Astrão")
veiculo2 = Moto("GSX-R1000") 

print(veiculo1.nome)
veiculo1.tipo_habilitacao()

print(veiculo2.nome)
veiculo2.tipo_habilitacao()