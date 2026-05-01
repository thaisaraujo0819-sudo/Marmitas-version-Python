import validacao
import os
import json
import utilitarios
from utilitarios import REGRAS_CADASTRO

"""
ESTA FUNÇÃO É O "MOTOR" DO CADASTRO:
Ela serve para Biometria, Rotina e Alimentação. 
Ela lê o REGRAS_CADASTRO e decide se usa validação de texto ou número.
"""
"""def processar_bloco(perfil, bloco, caminho):
    print(f"\n" + "="*15 + f" CONFIGURANDO: {bloco.upper()} " + "="*15)
    
    campos = REGRAS_CADASTRO[bloco]
    
    for chave, config in campos.items():
        valor_atual = perfil[bloco].get(chave)
        
        if valor_atual in [None, "", 0, "0", "null"]:
            pergunta = config["pergunta"]
            opcoes = config["opcoes"]
            
            # --- INÍCIO DA MUDANÇA ---
            
            # 1. Verifica se é uma das chaves que aceitam "Enter" para padrão 100
            if chave in ["preferencia_vegetais", "preferencia_legumes"]:
                print(pergunta)
                resp = input(">> ").strip()
                # Se for número usa o valor, se for "nao"/vazio/letras usa 100
                valor = int(resp) if resp.isdigit() else 100
            
            # 2. Se não for preferência, segue a lógica normal de OPÇÕES (Texto)
            elif opcoes:
                valor = validacao.validacao_texto(pergunta, opcoes)
            
            # 3. Se não tem opções e não é preferência, é número RÍGIDO (Biometria)
            else:
                valor = validacao.validacao_numero(chave)
                
            # --- FIM DA MUDANÇA ---
            
            perfil[bloco][chave] = valor
            utilitarios.salvar_arquivo(caminho, perfil)
            print(f"[✓] {chave.capitalize()} salvo!")

    return perfil"""

def processar_bloco(perfil, bloco, caminho):
    print(f"\n" + "="*15 + f" CONFIGURANDO: {bloco.upper()} " + "="*15)

    campos = REGRAS_CADASTRO[bloco]

    for chave, config in campos.items():
        valor_atual = perfil[bloco].get(chave)
        if valor_atual in [None, "", 0, "0", "null"]:
            pergunta = config["pergunta"]
            opcoes = config["opcoes"]

            if chave in ["preferencia_vegetais", "preferencia_legumes"]:
                print(pergunta)
                resp = input(">> ").strip()
                valor = int(resp) if resp.isdigit() else 100

            elif opcoes:
                valor = validacao.validacao_texto(pergunta, opcoes)

            else:
                valor = validacao.validacao_numero(chave)

            perfil[bloco][chave] = valor
            utilitarios.salvar_arquivo(caminho, perfil)
            print(f"[✓] {chave.capitalize()} salvo!")

    return perfil


"""--------------------------- FLUXO DE CONTINUAÇÃO / CRIAÇÃO ---------------------------"""

def continuar_cadastro(perfil, caminho):
    # O loop percorre as chaves principais: 'biometria', 'rotina', 'alimentacao_original'
    for bloco in REGRAS_CADASTRO.keys():
        if bloco not in perfil:
            perfil[bloco] = {}
        
        # Verifica se falta algum campo obrigatório dentro deste bloco
        campos_nas_regras = REGRAS_CADASTRO[bloco].keys()
        campos_vazios = [
            c for c in campos_nas_regras 
            if perfil[bloco].get(c) in [None, "", 0, "0", "null"]
        ]
        
        # Se houver campos vazios, chama o processador para esse bloco
        if len(campos_vazios) > 0:
            processar_bloco(perfil, bloco, caminho)
            
    return perfil

def fluxo_cadastro(nome, sobrenome, caminho):
    print(f"\n--- Criando perfil para {nome} {sobrenome} ---")

    perfil = {
        "biometria": {"nome": nome, "sobrenome": sobrenome},
        "rotina": {},
        "alimentacao_original": {}
    }

    # garante que todas as gavetas existem
    for bloco in REGRAS_CADASTRO.keys():
        if bloco not in perfil:
            perfil[bloco] = {}

    # processa cada bloco com base no REGRAS_CADASTRO
    perfil = processar_bloco(perfil, "biometria", caminho)
    perfil = processar_bloco(perfil, "rotina", caminho)
    perfil = processar_bloco(perfil, "alimentacao_original", caminho)

    utilitarios.salvar_arquivo(caminho, perfil)
    return perfil
"""------------------------------- MENU DE ALTERAÇÃO ------------------------------"""

def menu_alteracao(perfil, caminho):
    while True:
        print("\n" + "="*20 + " MENU DE ALTERAÇÃO " + "="*20)
        print("1 - Biometria\n2 - Rotina\n3 - Alimentação\n0 - Voltar ao Menu Principal")
        
        escolha = validacao.validacao_texto("O que deseja alterar? ", ["1", "2", "3", "0"])
        
        if escolha == "0":
            break
            
        # Mapeia a escolha do menu para o nome do bloco no REGRAS_CADASTRO
        blocos_map = {"1": "biometria", "2": "rotina", "3": "alimentacao_original"}
        bloco_alvo = blocos_map[escolha]
        
        # Gera a lista de campos dinamicamente para o usuário escolher qual mudar
        campos = list(REGRAS_CADASTRO[bloco_alvo].keys())
        
        print(f"\n--- ALTERAR {bloco_alvo.replace('_', ' ').upper()} ---")
        for i, campo in enumerate(campos, 1):
            print(f"{i} - {campo.capitalize()}")
        print(f"{len(campos) + 1} - Voltar")
        
        # Validação para garantir que o usuário escolha um número válido na lista
        opcoes_numericas = [str(i) for i in range(1, len(campos) + 2)]
        sub_escolha = int(validacao.validacao_texto("Escolha o número do campo: ", opcoes_numericas))
        
        # Se não escolheu "Voltar"
        if sub_escolha <= len(campos):
            chave_escolhida = campos[sub_escolha - 1]
            config = REGRAS_CADASTRO[bloco_alvo][chave_escolhida]
            
            # Aplica a mesma lógica de decisão entre texto e número
            if config["opcoes"]:
                novo_valor = validacao.validacao_texto(config["pergunta"], config["opcoes"])
            else:
                novo_valor = validacao.validacao_numero(chave_escolhida)
                
            perfil[bloco_alvo][chave_escolhida] = novo_valor
            utilitarios.salvar_arquivo(caminho, perfil)
            print(f"\n[✓] {chave_escolhida.capitalize()} atualizado com sucesso!")
            
    return perfil