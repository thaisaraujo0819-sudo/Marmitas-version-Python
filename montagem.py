import json
import os
import validacao

# --- CONFIGURAÇÃO DE CAMINHO ---
caminho_json = r"C:\Users\thais\Documents\Dieta\Marmitas\alimentos\base_alimentos.json"

try:
    with open(caminho_json, 'r', encoding='utf-8') as f:
        database = json.load(f)
    print("✅ Sucesso: Banco de dados carregado!")
except Exception as e:
    print(f"❌ Erro ao carregar banco de dados: {e}")
    database = {}

def revisar_marmita(lista_marmita, mapa_cat, mapa_sub, mapa_ali, dieta_num):
    while True:
        print("\n--- 📋 REVISÃO DA SUA MARMITA ---")
        for i, item in enumerate(lista_marmita, 1):
            print(f"{i}. Alterar: {item}")
        
        # Nova opção dinâmica
        num_adicionar = len(lista_marmita) + 1
        print(f"{num_adicionar}. [+] ADICIONAR NOVO ITEM")
        print("0. Finalizar e Salvar")

        opcoes_validas = [str(i) for i in range(len(lista_marmita) + 2)]
        escolha = validacao.validacao_texto(f"\nEscolha uma opção (0-{num_adicionar}): ", opcoes_validas)

        if escolha == "0":
            break 
        
        # Lógica para ADICIONAR
        if escolha == str(num_adicionar):
            print("\n--- ➕ ADICIONANDO NOVO ITEM ---")
            nova_cat = pedir_escolha(mapa_cat, "CATEGORIA DO NOVO ITEM", permite_voltar=False, dieta_num=dieta_num)
            nova_sub = pedir_escolha(mapa_sub[nova_cat], f"TIPOS DE {nova_cat}", dieta_num=dieta_num)
            novo_item = pedir_escolha(mapa_ali[nova_sub], f"ALIMENTOS EM {nova_sub}", dieta_num=dieta_num)
            
            lista_marmita.append(novo_item.replace('_', ' '))
            print(f"✅ {novo_item.replace('_', ' ')} adicionado com sucesso!")
            continue # Volta para o topo da revisão

        # Lógica para ALTERAR (o que você já tinha)
        indice = int(escolha) - 1
        print(f"\n🔄 Alterando: {lista_marmita[indice]}")
        nova_cat = pedir_escolha(mapa_cat, "NOVA CATEGORIA", permite_voltar=False, dieta_num=dieta_num)
        nova_sub = pedir_escolha(mapa_sub[nova_cat], f"TIPOS DE {nova_cat}", dieta_num=dieta_num)
        novo_item = pedir_escolha(mapa_ali[nova_sub], f"ALIMENTOS EM {nova_sub}", dieta_num=dieta_num)
        
        lista_marmita[indice] = novo_item.replace('_', ' ')
        print("✅ Item alterado com sucesso!")

    return lista_marmita
# --- FUNÇÕES DE APOIO ---
def filtrar_por_dieta(opcao_dieta, mapa_categorias):
    mapa_novo = {}
    contador = 1
    for nome_real in mapa_categorias.values():
        if opcao_dieta == 2 and nome_real == "Proteina_animal":
            continue
        mapa_novo[contador] = nome_real
        contador += 1
    return mapa_novo

def pedir_escolha(opcoes_dict, mensagem, permite_voltar=True, dieta_num=1):
    while True:
        print(f"\n--- {mensagem} ---")
        
        # 1. Criamos um mapeamento visual que IGNORE a 'prioridade'
        menu_visual = {}
        contador = 1
        
        for num_original, nome in opcoes_dict.items():
            # Se o nome for 'prioridade', o sistema ignora para o MENU, 
            # mas ele continua existindo no dicionário original para os cálculos.
            if str(nome).lower() == "prioridade":
                continue
                
            menu_visual[str(contador)] = nome
            contador += 1

        # 2. Definimos as opções que o usuário pode digitar
        opcoes_validas = list(menu_visual.keys())
        
        if permite_voltar:
            opcoes_validas.append("0")
            print("0. [Voltar ao menu anterior]")
            
        # 3. Exibimos o menu limpo para o usuário
        for num, nome in menu_visual.items():
            exibicao = nome.replace('_', ' ')
            # Sua lógica específica de tradução de nomes
            if dieta_num == 1 and nome == "Proteina_vegetal":
                exibicao = "Leguminosas, Graos e Ovos"
            
            print(f"{num}. {exibicao}")
        
        # 4. Validação da entrada
        entrada = validacao.validacao_texto("\nDigite o número desejado: ", opcoes_validas)
        
        if entrada == "0":
            return "VOLTAR"
        
        # Retorna o nome do alimento/categoria original para manter a compatibilidade
        return menu_visual[entrada]
    
def lista_de_categoria_subcategoria(link):
    mapa_cat, mapa_sub, mapa_ali = {}, {}, {}
    for i, categoria in enumerate(link, 1):
        mapa_cat[i] = categoria
        mapa_sub[categoria] = {}
        for j, subcategoria in enumerate(link[categoria], 1):
            mapa_sub[categoria][j] = subcategoria
            mapa_ali[subcategoria] = {}
            for k, alimento in enumerate(link[categoria][subcategoria], 1):
                mapa_ali[subcategoria][k] = alimento
    return mapa_cat, mapa_sub, mapa_ali

