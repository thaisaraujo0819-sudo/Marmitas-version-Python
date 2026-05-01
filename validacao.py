from utilitarios import REGRAS_CADASTRO

#Funcao de validar numeros em input
def validacao_numero(item):
    # Verifique se "quantidade" está aqui para o Python saber que é INT e não FLOAT
    campos_inteiros = ["idade", "altura", "quantidade"]
    tipo_num = int if item in campos_inteiros else float

    # Descobre em qual bloco está essa chave
    pergunta = f"Informe {item}: "
    for bloco, campos in REGRAS_CADASTRO.items():
        if item in campos:
            pergunta = campos[item]["pergunta"]
            break

    while True:
        try:
            valor = tipo_num(input(pergunta + " "))
            if valor <= 0:
                print(f"[!] {item.capitalize()} deve ser maior que zero.")
                continue
            return valor
        except ValueError:
            exemplo = "25" if tipo_num is int else "75.5"
            print(f"[!] Entrada inválida para {item}. Digite um número (Ex: {exemplo}).")


#Funcao de validar texto em input
def validacao_texto(palavra,opcoes_validas):
    while True:   
        print(palavra)
        termo = input( ).lower().strip()
        if termo in opcoes_validas:
            return termo
        else:
            print("Digite uma das letras relacionadas a sua opcao!")

def validacao_nome(pedido):
    while True:
        termo = input(pedido).strip()
        if termo:
            return termo.lower()
        print("Esse campo não pode ficar vazio. Digite novamente.")