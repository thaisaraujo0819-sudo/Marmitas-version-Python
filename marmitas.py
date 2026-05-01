import os
import json
import sys
import calculo
import Criar_alterar
import validacao
import utilitarios
from utilitarios import REGRAS_CADASTRO
import imprimir
from montagem import (
    lista_de_categoria_subcategoria, 
    pedir_escolha, 
    filtrar_por_dieta, 
    revisar_marmita,
    database 
)
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
    
# --- CONFIGURAÇÕES ---
TABELA_ALIMENTOS = utilitarios.carregar_base_alimentos()
Pasta_usuarios = "dados_usuarios"

def gerar_lista_compras(plano_da_semana, tabela_alimentos,base_preparacoes ):
    lista_compras = {}

    for marmita in plano_da_semana:
        qtd_marmitas = marmita.get('quantidade', 1)
        pesos = marmita.get('pesos', {}) 
        
        for alimento, gramas_pronto in pesos.items():
            # 1. NORMALIZAR O NOME QUE VEM DO PLANO (ex: "Lasanha acem" -> "lasanha_acem")
            alimento_normalizado = alimento.strip().lower().replace(" ", "_")
            
            proporcoes = None
            preparacoes = base_preparacoes.get("Preparacoes_compostas", {})
            
            # 2. BUSCAR DENTRO DAS CATEGORIAS
            for categoria_nome, itens_categoria in preparacoes.items():
                # Normalizamos as chaves do JSON para garantir a comparação
                # Criamos um dicionário onde as chaves são todas minúsculas
                itens_normalizados = {k.lower(): v for k, v in itens_categoria.items() if isinstance(v, dict)}
                
                if alimento_normalizado in itens_normalizados:
                    proporcoes = itens_normalizados[alimento_normalizado].get("proporcao", {})
                    break
            
            # 3. EXPLODIR OU MANTER ITEM ÚNICO
            if proporcoes:
                # Se achou, multiplica o peso pronto pela proporção de cada ingrediente
                itens_para_processar = {ing: gramas_pronto * prop for ing, prop in proporcoes.items()}
            else:
                # Se não achou, mantém o original (ex: Arroz)
                itens_para_processar = {alimento: gramas_pronto}

            # 4. PROCESSAR CADA INGREDIENTE RESULTANTE
            for nome_item, peso_calculado in itens_para_processar.items():
                # Aqui usamos o nome do ingrediente para buscar na tabela de fator de mercado
                nome_busca = nome_item.replace("_", " ").lower().strip()
                dados = tabela_alimentos.get(nome_busca, {})
                
                fator = dados.get('fator_mercado', 1.0)
                total_cru = (peso_calculado * qtd_marmitas) * fator
                
                # Soma no dicionário final (usando o nome original do ingrediente como chave)
                lista_compras[nome_item] = lista_compras.get(nome_item, 0) + total_cru

    #resumo_mercado_final = []
    lista_compras_dicionario = {}
    print("\n" + "="*15 + " 🛒 LISTA DE MERCADO (PESO CRU) " + "="*15)
    if not lista_compras:
        print("Nenhum item encontrado para a lista.")
    
    for item, peso in lista_compras.items():
        nome_limpo = item.replace("_", " ").lower().strip()
        dados = tabela_alimentos.get(nome_limpo, {})

        unidade_base = str(dados.get("unidade_medida", "g")).lower().strip()
        peso_un = dados.get("peso_por_unidade", 0)

        if unidade_base == "ml":
            unidade = "L" if peso >= 1000 else "ml"
            valor = peso / 1000 if peso >= 1000 else peso
            texto = f" - {item.replace('_', ' ').capitalize()}: {valor:.2f}{unidade}"

        elif unidade_base != "g" and peso_un > 0:
            qtd_un = round(peso / peso_un)
            if qtd_un == 0 and peso > 0:
                qtd_un = 1
            texto = f" - {item.replace('_', ' ').capitalize()}: {qtd_un} {unidade_base} (~{round(peso)}g)"
        else:
            unidade = "kg" if peso >= 1000 else "g"
            valor = peso / 1000 if peso >= 1000 else peso
            texto  = f" - {item.replace('_', ' ').capitalize()}: {valor:.2f}{unidade}"

        print(texto)
        #resumo_mercado_final.append(texto)
        lista_compras_dicionario[item] = {
            "peso_bruto": peso,
            "texto_formatado": texto.replace(" - ", ""), # Remove o tracinho
            "unidade": unidade_base
        }

    return lista_compras, lista_compras_dicionario


def exibir_resumo_compacto(perfil, dados_marmita, saldo_anterior=0):
    b, r = perfil["biometria"], perfil["rotina"]

    p = float(b["peso"])
    a = float(b["altura"])
    i = int(b["idade"])
    s = b["sexo"].lower()

    ne = r["nivel de exercicio"].lower()
    ob = r["objetivo"].lower()
    doce = r["gosta de doce"].lower()
    refe_pref = r.get("refeicao preferida")
    velocidade = r.get("velocidade", "a")
    suplemento = str(r.get("suplemento", "n")).lower().strip()

    bloco_alimentacao = perfil.get("alimentacao_original") or perfil.get("alimentacaooriginal") or {}
    refeicoes_ativas = [
        ref for ref, valor in bloco_alimentacao.items()
        if str(valor).isdigit() and int(valor) > 0
        and ref not in ["contagem refeicao", "doce", "refeicao favorita"]
    ]

    resultado = calculo.calculo_principal(
        p, a, i, s, ne, ob, refe_pref, refeicoes_ativas, doce, velocidade
    )

    resultado = calculo.ajustar_metas_por_viabilidade(
        resultado, perfil, refeicoes_ativas, suplemento
    )

    nome_ref_atual = dados_marmita.get("refeicao_alvo", "").lower().strip()

    mapa_nomes = {
        "café": "cafe da manha",
        "cafe": "cafe da manha",
        "lanche da manhã": "lanche da manha",
        "lanche da manha": "lanche da manha",
        "lanche manhã": "lanche da manha",
        "lanche manha": "lanche da manha",
        "lanche da tarde": "lanche da tarde",
        "lanche tarde": "lanche da tarde",
        "almoço": "almoco",
        "almoco": "almoco",
        "janta": "janta"
    }

    chave_busca = mapa_nomes.get(nome_ref_atual, nome_ref_atual)

    meta_macros = resultado["Macros por Refeicao"].get(chave_busca)
    if not meta_macros:
        meta_macros = list(resultado["Macros por Refeicao"].values())[0]

    meta_kcal_com_saldo = meta_macros["calorias"] + saldo_anterior
    meta_proteina = meta_macros["proteina"]

    pref_v = r.get("preferencia_vegetais", 100)
    pref_l = r.get("preferencia_legumes", 100)

    resumo_mercado = {}
    qtd_marmitas = dados_marmita.get("quantidade", 1)

    pesos = calculo.calcular_pesos_refeicao(
        meta_macros,
        dados_marmita["itens"],
        TABELA_ALIMENTOS,
        pref_l,
        pref_v
    )

    print(f"\n🍴 {dados_marmita['refeicao_alvo'].upper()} ({dados_marmita['quantidade']} unidades)")
    print(f"🎯 Meta Calorias: {round(meta_kcal_com_saldo)} kcal (Original: {meta_macros['calorias']} | Saldo: {round(saldo_anterior)})")
    print(f"🥩 Meta Proteína: {round(meta_proteina)}g")

    total_kcal = 0
    total_prot = 0
    calorias_por_alimento = {}

    for item, gramas in pesos.items():
        peso_total_compra = gramas * qtd_marmitas
        if item in resumo_mercado:
            resumo_mercado[item] += peso_total_compra
        else:
            resumo_mercado[item] = peso_total_compra

        item_limpo = item.replace("_", " ").lower().strip()
        dados_ali = TABELA_ALIMENTOS.get(item_limpo, {})

        kcal_100g = dados_ali.get("calorias", 0)
        prot_100g = dados_ali.get("proteina", 0)

        unidade = str(dados_ali.get("unidade_medida", "g")).lower().strip()
        peso_un = dados_ali.get("peso_por_unidade", 1)

        if unidade == "ml":
            texto_quantidade = f"{round(gramas)}ml"
            quantidade_calculo = gramas

        elif unidade != "g" and peso_un > 0:
            quantidade_un = gramas / peso_un

            if abs(quantidade_un - round(quantidade_un)) < 0.01:
                quantidade_txt = str(int(round(quantidade_un)))
            else:
                quantidade_txt = f"{quantidade_un:.1f}".rstrip("0").rstrip(".")

            texto_quantidade = f"{quantidade_txt} {unidade}"
            quantidade_calculo = gramas

        else:
            texto_quantidade = f"{round(gramas)}g"
            quantidade_calculo = gramas

        kcal_item = (kcal_100g * quantidade_calculo) / 100
        prot_item = (prot_100g * quantidade_calculo) / 100

        nome_base = item.replace("_", " ").lower().strip()
        calorias_por_alimento[nome_base] = calorias_por_alimento.get(nome_base, 0) + kcal_item
        
        total_kcal += kcal_item
        total_prot += prot_item


        print(f"   └─ {item.replace('_', ' ').capitalize()}: {texto_quantidade} ({round(kcal_item)} kcal)")

    print(f"🔥 Total Realizado: {round(total_kcal)} kcal | 🥩 Prot Realizada: {round(total_prot)}g")

    if total_prot < meta_proteina * 0.8:
        print(f"💡 Dica: Adicione uma fonte extra de proteína ou reduza o carbo para atingir os {round(meta_proteina)}g.")

    diferenca = meta_kcal_com_saldo - total_kcal
    novo_saldo = 0

    if abs(diferenca) > 35:
        print(f"\n[!] Diferença de {round(diferenca)} kcal detectada.")
        print("1. Ignorar | 2. Transferir para a próxima refeição")
        escolha = validacao.validacao_texto("Escolha: ", ["1", "2"])

        if escolha == "2":
            novo_saldo = diferenca
            print(f"✅ Saldo de {round(novo_saldo)} kcal enviado.")

    return pesos, novo_saldo, total_kcal, total_prot,resumo_mercado

def exibir_resumo(perfil):
    print("\n" + "="*20 + " RESUMO DO PERFIL " + "="*20)
    
    # 1. Biometria
    bio = perfil.get("biometria", {})
    print(f"👤 USUÁRIO: {str(bio.get('nome','')).upper()} {str(bio.get('sobrenome','')).upper()}")
    print(f"⚖️  PESO: {bio.get('peso')}kg | 📏 ALTURA: {bio.get('altura')}cm | 🎂 IDADE: {bio.get('idade')}")
    print(f"📏 CINTURA: {bio.get('circuferencia cintura')}cm")
    
    # 2. Rotina e Velocidade da Meta
    rot = perfil.get("rotina", {})
    
    # Mapeamento para exibir o valor real da velocidade
    mapa_velocidade = {
        "a": "0.3kg/semana",
        "b": "0.5kg/semana",
        "c": "0.75kg/semana",
        "d": "1.0kg/semana"
    }
    v_letra = rot.get('velocidade', 'a').lower()
    v_texto = mapa_velocidade.get(v_letra, "Não definida")

    print("\n🔄 ROTINA E METAS:")
    print(f"  > OBJETIVO: {str(rot.get('objetivo')).upper()}")
    print(f"  > EXERCÍCIO: {str(rot.get('nivel de exercicio')).upper()}")
    print(f"  > VELOCIDADE: {v_texto}") # Aqui exibe "0.3kg/semana"
    print(f"  > DOCE: {'SIM' if rot.get('gosta de doce') == 's' else 'NÃO'}")
    print(f"  > SUPLEMENTO:  {str(rot.get('suplemento')).upper()}")
    print(f"  > PADRÃO VEGETAIS: {rot.get('preferencia_vegetais', 100)}g")
    print(f"  > PADRÃO LEGUMES:  {rot.get('preferencia_legumes', 100)}g")
    
    # 3. Estrutura de Refeições
    ali = perfil.get("alimentacao_original", {})
    print("\n🍱 ESTRUTURA DE REFEIÇÕES:")
    for ref, status in ali.items():
        if ref not in ['contagem refeicao', 'doce', 'refeicao favorita']:
            msg = "ATIVA" if str(status).isdigit() else "PULAR / NÃO CONSOME"
            print(f"  - {ref.capitalize():20}: {msg}")
            

    print("-" * 58)

def escolher_template_favorito(perfil, nome_ref, caminho_perfil):
    """
    Busca no JSON: perfil['marmitas_semana']['nome_da_refeicao']
    Exemplo: perfil['marmitas_semana']['cafe da manha']
    """
    # 1. Acessamos direto a chave da refeição dentro de marmitas_semana
    # O .get() aqui evita erro se a chave não existir, retornando uma lista vazia
    templates = perfil.get("marmitas_semana", {}).get(nome_ref, [])

    # 2. Verificação de segurança: se não houver templates para essa refeição específica
    if not templates:
        print(f"\n📭 Você ainda não tem templates salvos para {nome_ref.upper()}.")
        return None

    print(f"\n" + "="*15 + f" TEMPLATES PARA {nome_ref.upper()} " + "="*15)
    
    # 3. Listagem dos templates encontrados
    for i, t in enumerate(templates, 1):
        # t é um dicionário com 'itens', 'quantidade' e 'tipo_dieta'
        itens_txt = " + ".join(t.get('itens', []))
        dieta = t.get('tipo_dieta', 'Proteina Animal')
        print(f"{i}. {itens_txt} [{dieta}]")
    
    print("99. EXCLUIR UM TEMPLATE") # <--- NOVA OPÇÃO
    print("0. Voltar e montar uma nova")

    # 4. Validação da escolha do usuário
    opcoes = [str(i) for i in range(len(templates) + 1)] + ["99"]
    escolha = validacao.validacao_texto("\nSelecione o template desejado: ", opcoes)

    if escolha == "0":
        return None

    if escolha == "99":
        idx_excluir = int(validacao.validacao_texto("Digite o número do template que deseja APAGAR: ", [str(i+1) for i in range(len(templates))])) - 1
        removido = templates.pop(idx_excluir)
        utilitarios.salvar_arquivo(caminho_perfil, perfil) # Salva a remoção no JSON
        print(f"\n✅ Template '{' + '.join(removido['itens'])}' removido!")
        return "RECOMEÇAR" # Sinaliza que deve recarregar a lista
    
    # 5. Retorno do template selecionado
    indice = int(escolha) - 1
    template_escolhido = templates[indice].copy() # .copy() evita alterar o histórico original
    
    # Perguntamos a quantidade específica para esta semana
    print(f"\nQuantas unidades de '{nome_ref}' você quer para esta semana?")
    template_escolhido['quantidade'] = validacao.validacao_numero("quantidade")
    
    return template_escolhido

def montagem_refeicao_guiada(caminho_usuario, nome_refeicao):
    """Fluxo de escolha de alimentos com correção de navegação (Voltar)."""
    mapa_cat_original, mapa_sub, mapa_ali = lista_de_categoria_subcategoria(database)
    tipos_dieta = {1: "Proteina Animal", 2: "Vegetariana (Apenas Vegetal)"}

    dieta_selecionada = pedir_escolha(tipos_dieta, f"DIETA PARA {nome_refeicao.upper()}", permite_voltar=False)
    dieta_num = 1 if dieta_selecionada == tipos_dieta[1] else 2
    mapa_cat_vigo = filtrar_por_dieta(dieta_num, mapa_cat_original)

    conjunto_final = []
    
    while True:
        categoria = pedir_escolha(mapa_cat_vigo, f"[{nome_refeicao.upper()}] CATEGORIA", permite_voltar=False, dieta_num=dieta_num)
        while True:
            sub_nome = pedir_escolha(mapa_sub.get(categoria, {}), f"TIPOS DE {categoria}", dieta_num=dieta_num)
            if sub_nome == "VOLTAR": break
                
            while True:
                alimento = pedir_escolha(mapa_ali.get(sub_nome, {}), f"ALIMENTOS EM {sub_nome}", dieta_num=dieta_num)
                if alimento == "VOLTAR": break
                
                conjunto_final.append(alimento.replace('_', ' '))
                print(f"\n✅ {alimento.replace('_', ' ')} adicionado!")
                
                resp = validacao.validacao_texto(f"Deseja mais itens ao {nome_refeicao}? (s/n): ", ["s", "n"])
                if resp == 's': break # Volta para categorias
                else:
                    conjunto_final = revisar_marmita(conjunto_final, mapa_cat_vigo, mapa_sub, mapa_ali, dieta_num)
                    print(f"\nQuantas unidades de {nome_refeicao} para a semana?")
                    qtd = validacao.validacao_numero("quantidade")
                    
                    dados = {"refeicao_alvo": nome_refeicao, "itens": conjunto_final, "quantidade": qtd, 
                             "tipo_dieta": "Vegetariana" if dieta_num == 2 else "Proteina Animal"}
                    utilitarios.salvar_marmita_no_perfil(caminho_usuario, dados)
                    return dados
            if resp == 's': break

def fluxo_refeicao_especifica(perfil, nome_ref, caminho_perfil):
    """ADS: Gerenciador com suporte a múltiplas variantes (ex: 2 tipos de café)."""
    escolhas_desta_ref = [] 

    while True:
        print(f"\n" + "="*15 + f" {nome_ref.upper()} " + "="*15)
        print("1. Usar um Template Favorito")
        print("2. Montar Nova Opção")
        print("0. Concluir / Voltar")
        
        opcao = validacao.validacao_texto("Escolha: ", ["1", "2", "0"])

        # Se escolher 0, ele retorna o que já escolheu (pode ser uma lista vazia ou com itens)
        if opcao == "0":
            return escolhas_desta_ref

        marmita = None
        if opcao == "1":
            marmita = escolher_template_favorito(perfil, nome_ref, caminho_perfil)
            if marmita == "RECOMEÇAR": continue 
        else:
            marmita = montagem_refeicao_guiada(caminho_perfil, nome_ref)

        if marmita:
            # IMPORTANTE: Adiciona a escolha na lista temporária
            escolhas_desta_ref.append(marmita)
            
            print(f"\n📍 {nome_ref.upper()} ADICIONADO: {marmita['quantidade']} unidades.")
            print("\nO QUE DESEJA FAZER?")
            print(f"1. Confirmar e adicionar OUTRA OPÇÃO de {nome_ref.upper()}")
            print(f"2. Confirmar e ir para a PRÓXIMA REFEIÇÃO")
            print(f"3. Refazer última escolha (Descartar {marmita['quantidade']} un.)")
            
            conf = validacao.validacao_texto("Escolha: ", ["1", "2", "3"])
            
            if conf == "1":
                print(f"\n[+] Ok! Vamos escolher mais uma variante para {nome_ref.upper()}...")
                continue # Volta para o topo do while e mantém o que já foi escolhido
            
            elif conf == "2":
                return escolhas_desta_ref # Sai da função levando a lista completa
            
            elif conf == "3":
                escolhas_desta_ref.pop() # Remove o último item adicionado
                print("\n[!] Última escolha descartada.")
                continue

def identificacao(nome, sobrenome):
    return os.path.join(Pasta_usuarios, f"{nome}_{sobrenome}.json")

# --- EXECUÇÃO PRINCIPAL ---

print("="*50 + "\n SISTEMA DE MARMITAS INTELIGENTE\n" + "="*50)
Nome_usuario = validacao.validacao_nome("Nome: ")
Sobrenome_usuario = validacao.validacao_nome("Sobrenome: ")
caminho = identificacao(Nome_usuario, Sobrenome_usuario)

status_ou_nivel, perfil = utilitarios.carregar_arquivo(caminho)

# Lógica de Cadastro/Continuação
if status_ou_nivel == "inexistente":
    perfil = Criar_alterar.fluxo_cadastro(Nome_usuario, Sobrenome_usuario, caminho)
    status_ou_nivel = 4
elif isinstance(status_ou_nivel, int) and status_ou_nivel < 4:
    perfil = Criar_alterar.continuar_cadastro(perfil, caminho)
    status_ou_nivel = 4


# LOOP DO MENU PRINCIPAL
if status_ou_nivel == 4:
    while True:
        exibir_resumo(perfil)
        print("1. Alterar Dados\n2. Planejar Semana\n3. Sair")
        res = validacao.validacao_texto("Escolha: ", ["1", "2", "3"])
        
        if res == "1": perfil = Criar_alterar.menu_alteracao(perfil, caminho)
        elif res == "2": 
            status_ou_nivel = 5
            break
        elif res == "3":
            print("\nSalvando... Até logo!")
            sys.exit()


# --- NOVO LOOP DE MONTAGEM CORRIGIDO ---
if status_ou_nivel == 5:
    # 1. Extração de dados (Igual ao seu)
    b, r = perfil["biometria"], perfil["rotina"]
    p, a, i, s = float(b["peso"]), float(b["altura"]), int(b["idade"]), b["sexo"].lower()
    ne, ob, doce, rf = r["nivel de exercicio"].lower(), r["objetivo"].lower(), r["gosta de doce"].lower(), r["refeicao preferida"]
    
    refeicoes_ativas = [
        ref for ref, valor in perfil['alimentacao_original'].items() 
        if str(valor).isdigit() and int(valor) > 0 
        and ref not in ['contagem refeicao', 'doce', 'refeicao favorita']
    ]

    plano_da_semana_temporario = [] 
    saldo_para_proxima = 0

    # 3. Fluxo de escolha e montagem
    for ref in refeicoes_ativas:
        marmitas_escolhidas = fluxo_refeicao_especifica(perfil, ref, caminho)
        
        if marmitas_escolhidas:
            lista_marmitas = marmitas_escolhidas if isinstance(marmitas_escolhidas, list) else [marmitas_escolhidas]
            
            for m in lista_marmitas:
                # Pegamos os dados da função (Ajuste para receber 4 valores agora)
                pesos_calculados, saldo_para_proxima, kcal_real, prot_real, resumo = exibir_resumo_compacto(perfil, m, saldo_anterior=saldo_para_proxima)
                
                # GUARDAMOS TUDO DENTRO DO DICIONÁRIO 'm'
                m['pesos'] = pesos_calculados
                m['kcal_final'] = kcal_real
                m['prot_final'] = prot_real
                m['nome_bonito'] = ref
                
                plano_da_semana_temporario.append(m)

    # 4. EXIBIÇÃO FINAL (AQUI QUE APARECEM TODAS!)
    print("\n" + "█"*20 + " RESUMO DO SEU PLANO SEMANAL " + "█"*20)
    
    pdf_plano_semanas = []

    for m in plano_da_semana_temporario:
        marmita_obj = {
        "titulo": f"{m['nome_bonito'].upper()} ({m['quantidade']} unidades)",
        "itens": [],
        "final": [f"Total: {round(m['kcal_final'])} kcal", "|", f"Prot: {round(m['prot_final'])}g"]}

        inicio = f"\n📍 {m['nome_bonito'].upper()} ({m['quantidade']} unidades):"
        print(inicio)
        for alimento, peso in m["pesos"].items():
            item_limpo = alimento.replace("_", " ").lower().strip()
            dados_ali = TABELA_ALIMENTOS.get(item_limpo, {})

            kcal_100g = dados_ali.get("calorias", 0)
            unidade = str(dados_ali.get("unidade_medida", "g")).lower().strip()

            if unidade == "ml":
                texto_quantidade = f"{round(peso)}ml"
                quantidade_calculo = peso
            else:
                texto_quantidade = f"{round(peso)}g"
                quantidade_calculo = peso

            kcal_item = (kcal_100g * quantidade_calculo) / 100

            texto_linha = f"   - {alimento.replace('_', ' ').capitalize()}: {texto_quantidade} ({round(kcal_item)} kcal)"
            print(texto_linha)
            marmita_obj["itens"].append(texto_linha) # Guarda cada alimento

        texto_total = f"   🔥 Total: {round(m['kcal_final'])} kcal | 🥩 Prot: {round(m['prot_final'])}g"
        print(texto_total)
        pdf_plano_semanas.append(marmita_obj) # Guarda o resumo daquela marmita
    

    print("\n" + "█" * 55)

    caminho_base = r"C:\Users\thais\Documents\Dieta\Marmitas\alimentos\base_alimentos.json"

    with open(caminho_base, 'r', encoding='utf-8') as f:
        base_alimentos = json.load(f)
    # Chamamos a lista de compras (Agora ela tem todos os itens salvos na lista)
    lista_compras, lista_compras_finais = gerar_lista_compras(plano_da_semana_temporario, TABELA_ALIMENTOS, base_alimentos)
    
    lista_compras = lista_compras
    # 2. Agora salvamos essa 'lista_compras' dentro do seu JSON de perfil
    try:
            # Carrega o perfil, adiciona a lista de textos e a lista de mercado, e salva
        with open(caminho, 'r', encoding='utf-8') as f:
            dados_usuario = json.load(f)

        dados_usuario["resumo_texto_plano"] = pdf_plano_semanas # A lista de frases que criaste
        dados_usuario["lista_compras_mercado"] = lista_compras_finais # O dicionário de somas
        #dados_usuario["lista_compras_mer"] = lista_compras 

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados_usuario, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Lista de compras sincronizada no perfil de {Nome_usuario}!")

    except Exception as e:
        print(f"⚠️ Erro ao atualizar JSON: {e}")
    

    # Cálculo dos indicadores diários
    res_final = calculo.calculo_principal(p, a, i, s, ne, ob, rf, refeicoes_ativas, doce, r.get("velocidade"))
    agua = calculo.agua_dia(p, i)

    print("\n" + "="*20 + " METAS DIÁRIAS (TEÓRICAS) " + "="*20)
    print(f"📊 Meta Calorias: {res_final['Caloria Diaria']:.0f} kcal")
    print(f"🥩 Meta Proteína: {res_final['Proteina Diaria']:.0f}g")
    print(f"💧 Água sugerida: {agua/1000:.2f}L")
    print("="*55)


