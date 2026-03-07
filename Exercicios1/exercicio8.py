def estatisticas(*args):
    media = sum(args) / len(args)
    maximo = max(args)
    minimo = min(args)

    return{
        "media" : media,
        "maximo" : maximo,
        "minimo" : minimo
    }

resultado = estatisticas(10, 3, 9 , 8)
print(resultado)