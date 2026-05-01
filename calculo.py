import utilitarios

import utilitarios

REGRAS = utilitarios.carregar_regras()

def limitar_excesso_calorico(pesos_finais, meta_macros, tabela_alimentos):
    meta_kcal = meta_macros["calorias"]
    tolerancia = meta_kcal * 1.05

    def total_kcal():
        soma = 0
        for item, peso in pesos_finais.items():
            item_limpo = item.replace("_", " ").lower().strip()
            d = tabela_alimentos.get(item_limpo, {})
            soma += (peso * d.get("calorias", 0)) / 100
        return soma

    ordem_reducao = [6, 5, 4, 3, 2, 1]

    for prio_alvo in ordem_reducao:
        if total_kcal() <= tolerancia:
            break

        for item in list(pesos_finais.keys()):
            item_limpo = item.replace("_", " ").lower().strip()
            d = tabela_alimentos.get(item_limpo, {})
            if d.get("prio_ads", 4) != prio_alvo:
                continue

            kcal_100g = d.get("calorias", 0)
            if kcal_100g <= 0:
                continue

            while pesos_finais[item] > 0 and total_kcal() > tolerancia:
                pesos_finais[item] -= 10
                if pesos_finais[item] < 0:
                    pesos_finais[item] = 0

            if pesos_finais[item] == 0:
                del pesos_finais[item]

    return pesos_finais

def distribuir_proteina_refeicoes(proteina_diaria, refeicoes_ativas):
    pesos_base = {
        "cafe da manha": 0.20,
        "lanche da manha": 0.10,
        "almoco": 0.35,
        "lanche da tarde": 0.10,
        "janta": 0.25
    }

    pesos_ativos = {
        ref: pesos_base[ref]
        for ref in refeicoes_ativas
        if ref in pesos_base
    }

    soma_pesos = sum(pesos_ativos.values())

    if soma_pesos == 0:
        return {}

    distribuicao = {}
    for ref, peso in pesos_ativos.items():
        distribuicao[ref] = proteina_diaria * (peso / soma_pesos)

    return distribuicao

def arredondar_incremento(valor, incremento):
    if incremento <= 0:
        return valor
    return round(valor / incremento) * incremento

def descobrir_grupo_do_alimento(nome, dados):
    prio = dados.get("prio_ads", 4)
    unidade = dados.get("unidade_medida", "g")

    if prio == 1:
        return "Proteinaanimal"
    elif prio == 2:
        return "VegetaiseSaladas"
    elif prio in [3, 4]:
        return "Carboidratos"
    elif prio == 5:
        return "Hortifruti"
    elif prio == 6:
        if unidade == "ml":
            return "Bebidas"
        return "ComplementoseEspalhaveis"
    elif prio == 7:
        return "Sobremesas"

    return "Carboidratos"

def ajustar_peso_pelas_regras(nome_alimento, categoria, kcal_objetivo, info_alimento):
    """
    Calcula o peso ideal respeitando o regras_max_min.json usando busca em minúsculo.
    """
    kcal_por_100g = info_alimento.get('calorias', 0)
    if kcal_por_100g <= 0: return 0, 0, "g"
    
    nome_normalizado = nome_alimento.replace("_", " ").lower().strip()
    especificos = REGRAS.get("regras_por_item_especifico", {})

    regra = None
    for chave_regra, valor_regra in especificos.items():
        if chave_regra.replace("_", " ").lower().strip() == nome_normalizado:
            regra = valor_regra
            break

    if regra:
        if "peso_un" in regra:
            peso_base = regra["peso_un"]
            unidade = info_alimento.get("unidade_medida", "unidade")
            kcal_por_unidade = (kcal_por_100g * peso_base) / 100
            quantidade = kcal_objetivo / kcal_por_unidade if kcal_por_unidade > 0 else 0
            quantidade = max(regra.get("min_un", 0), min(quantidade, regra.get("max_un", 99)))

            if regra.get("min_un", 0) % 1 == 0 and regra.get("max_un", 99) % 1 == 0:
                quantidade = round(quantidade)
            else:
                quantidade = round(quantidade * 2) / 2

            peso_final = quantidade * peso_base
            return peso_final, quantidade, unidade

        if "peso_fatia" in regra:
            peso_base = regra["peso_fatia"]
            unidade = info_alimento.get("unidade_medida", "fatia")
            kcal_por_fatia = (kcal_por_100g * peso_base) / 100
            quantidade = kcal_objetivo / kcal_por_fatia if kcal_por_fatia > 0 else 0
            quantidade = max(regra.get("min_fatia", 0), min(quantidade, regra.get("max_fatia", 99)))
            quantidade = round(quantidade)
            peso_final = quantidade * peso_base
            return peso_final, quantidade, unidade

        if "min_g" in regra or "max_g" in regra:
            min_g = regra.get("min_g", 0)
            max_g = regra.get("max_g", 9999)
            incremento = regra.get("incremento", 5)

            peso_gramas = (kcal_objetivo / kcal_por_100g) * 100
            peso_final = max(min_g, min(peso_gramas, max_g))
            peso_final = arredondar_incremento(peso_final, incremento)
            return peso_final, None, "g"

    regras_grupo = REGRAS.get("regras_por_grupo", {})
    regra_grupo = regras_grupo.get(categoria, {"min_g": 30, "max_g": 200, "incremento": 5})

    unidade_medida = info_alimento.get("unidade_medida", "g")

    if unidade_medida == "ml":
        min_ml = regra_grupo.get("min_ml", 100)
        max_ml = regra_grupo.get("max_ml", 350)
        incremento = regra_grupo.get("incremento", 50)
        peso_ml = (kcal_objetivo / kcal_por_100g) * 100
        peso_final = max(min_ml, min(peso_ml, max_ml))
        peso_final = arredondar_incremento(peso_final, incremento)
        return peso_final, None, "ml"

    min_g = regra_grupo.get("min_g", 30)
    max_g = regra_grupo.get("max_g", 200)
    incremento = regra_grupo.get("incremento", 5)

    peso_gramas = (kcal_objetivo / kcal_por_100g) * 100
    peso_final = max(min_g, min(peso_gramas, max_g))
    peso_final = arredondar_incremento(peso_final, incremento)

    return peso_final, None, "g"

def calculo_principal(p, a, i, s, ne, ob, refe_pref, refeicoes_ativas, doce, velocidade):
    tmb = calcular_TMB(p, a, i, s)
    tdee = calcular_TDEE(tmb, ne)
    caloria_diaria = calorias_consumir(tdee, ob, doce, velocidade)
    proteina_diaria = proteina_basica(p, ne)

    calorias_distribuidas = distribuir_calorias(caloria_diaria, refeicoes_ativas, refe_pref)
    distribuicao_proteina = distribuir_proteina_refeicoes(proteina_diaria, refeicoes_ativas)

    mapa_macros_por_ref = {}
    mapa_nomes_json = {
        "Café": "cafe da manha",
        "Lanche manhã": "lanche da manha",
        "Almoço": "almoco",
        "Lanche tarde": "lanche da tarde",
        "Janta": "janta"
    }

    for nome_pt, kcal in calorias_distribuidas.items():
        chave_json = mapa_nomes_json.get(nome_pt, nome_pt.lower())
        proteina_ref = distribuicao_proteina.get(
            chave_json,
            proteina_diaria / max(len(refeicoes_ativas), 1)
        )
        mapa_macros_por_ref[chave_json] = macros_refeicao(kcal, proteina_ref)

    return {
        "Caloria Diaria": caloria_diaria,
        "Proteina Diaria": proteina_diaria,
        "Macros por Refeicao": mapa_macros_por_ref,
        "Caloria distribuida por refeicao": calorias_distribuidas
    }

def calcular_pesos_refeicao(meta_macros, itens_escolhidos, tabela_alimentos, pref_l, pref_v):
    pesos_finais = {}
    meta_kcal = meta_macros["calorias"]
    meta_prot = meta_macros.get("proteina", 0)
    tolerancia_kcal = 35
    tolerancia_prot = meta_prot * 1.10 if meta_prot > 0 else 999

    def normalizar(nome):
        return nome.lower().replace("_", " ").strip()

    def kcal_item(nome, peso):
        d = tabela_alimentos.get(normalizar(nome), {})
        return (peso * d.get("calorias", 0)) / 100

    def prot_item(nome, peso):
        d = tabela_alimentos.get(normalizar(nome), {})
        return (peso * d.get("proteina", 0)) / 100

    def categoria_regra(nome, dados):
        prio = dados.get("prio_ads", 4)
        unidade = dados.get("unidade_medida", "g")

        if prio == 1:
            return "Proteinaanimal"
        elif prio == 2:
            return "VegetaiseSaladas"
        elif prio in [3, 4]:
            return "Carboidratos"
        elif prio == 5:
            return "Hortifruti"
        elif prio == 6:
            if unidade == "ml":
                return "Bebidas"
            return "ComplementoseEspalhaveis"
        elif prio == 7:
            return "Sobremesas"

        return "Carboidratos"

    for item in itens_escolhidos:
        item_limpo = normalizar(item)
        dados = tabela_alimentos.get(item_limpo, {})

        if not dados:
            continue

        prio = dados.get("prio_ads", 4)

        if prio == 2:
            if any(x in item_limpo for x in ["alface", "folha", "salada", "rucula"]):
                peso_base = min(pref_v, 30)
            else:
                peso_base = min(pref_l, 50)
        else:
            categoria = categoria_regra(item, dados)
            peso_base, _, _ = ajustar_peso_pelas_regras(item, categoria, 1, dados)

            unidade = dados.get("unidade_medida", "g")
            peso_un = dados.get("peso_por_unidade", 0)

            if peso_base <= 0:
                if unidade == "ml":
                    peso_base = 100
                elif unidade != "g" and peso_un > 0:
                    peso_base = peso_un
                else:
                    peso_base = 20

        pesos_finais[item] = peso_base

    def total_kcal():
        return sum(kcal_item(nome, peso) for nome, peso in pesos_finais.items())

    def total_prot():
        return sum(prot_item(nome, peso) for nome, peso in pesos_finais.items())

    itens_proteina = []
    itens_outros = []

    for item in itens_escolhidos:
        dados = tabela_alimentos.get(normalizar(item), {})
        if dados.get("prio_ads", 4) == 1:
            itens_proteina.append(item)
        else:
            itens_outros.append(item)

    for item in itens_proteina + itens_outros:
        dados = tabela_alimentos.get(normalizar(item), {})
        if not dados:
            continue

        categoria = categoria_regra(item, dados)
        unidade = dados.get("unidade_medida", "g")
        peso_un = dados.get("peso_por_unidade", 0)
        item_limpo = normalizar(item)

        if unidade == "ml":
            passo = 50
        elif unidade != "g" and peso_un > 0:
            passo = peso_un
        else:
            passo = 5

        atual = pesos_finais[item]

        if categoria == "Bebidas":
            if any(x in item_limpo for x in ["zero", "diet", "light"]):
                teto_manual = 100
            else:
                teto_manual = 150

            while True:
                teste = atual + passo

                if teste > teto_manual:
                    break

                peso_teste, _, _ = ajustar_peso_pelas_regras(item, categoria, kcal_item(item, teste), dados)
                if peso_teste < teste:
                    break

                kcal_teste = total_kcal() - kcal_item(item, atual) + kcal_item(item, teste)

                if kcal_teste <= meta_kcal + tolerancia_kcal:
                    atual = teste
                    pesos_finais[item] = atual
                else:
                    break

            continue

        if categoria == "Sobremesas":
            teto_manual = 60

            while True:
                teste = atual + passo

                if teste > teto_manual:
                    break

                peso_teste, _, _ = ajustar_peso_pelas_regras(item, categoria, kcal_item(item, teste), dados)
                if peso_teste < teste:
                    break

                kcal_teste = total_kcal() - kcal_item(item, atual) + kcal_item(item, teste)

                if kcal_teste <= meta_kcal + tolerancia_kcal:
                    atual = teste
                    pesos_finais[item] = atual
                else:
                    break

            continue

        while True:
            teste = atual + passo
            peso_teste, _, _ = ajustar_peso_pelas_regras(item, categoria, kcal_item(item, teste), dados)

            if peso_teste < teste:
                break

            kcal_teste = total_kcal() - kcal_item(item, atual) + kcal_item(item, teste)
            prot_teste = total_prot() - prot_item(item, atual) + prot_item(item, teste)

            if categoria == "Proteinaanimal" and prot_teste > tolerancia_prot:
                break

            if kcal_teste <= meta_kcal + tolerancia_kcal:
                atual = teste
                pesos_finais[item] = atual
            else:
                break

    itens_ordenados = sorted(
        pesos_finais.keys(),
        key=lambda x: kcal_item(x, pesos_finais[x]),
        reverse=True
    )

    for item in itens_ordenados:
        if total_kcal() <= meta_kcal + tolerancia_kcal:
            break

        dados = tabela_alimentos.get(normalizar(item), {})
        if not dados:
            continue

        categoria = categoria_regra(item, dados)
        unidade = dados.get("unidade_medida", "g")
        peso_un = dados.get("peso_por_unidade", 0)

        if unidade == "ml":
            passo = 50
        elif unidade != "g" and peso_un > 0:
            passo = peso_un
        else:
            passo = 5

        minimo, _, _ = ajustar_peso_pelas_regras(item, categoria, 1, dados)
        if minimo <= 0:
            if unidade == "ml":
                minimo = 100
            elif unidade != "g" and peso_un > 0:
                minimo = peso_un
            else:
                minimo = 20

        while pesos_finais[item] - passo >= minimo and total_kcal() > meta_kcal + tolerancia_kcal:
            pesos_finais[item] -= passo

    return pesos_finais

def ajustar_metas_por_viabilidade(resultado, perfil, contagem_refeicoes=None, suplemento="n"):
    macros_ref = resultado.get("Macros por Refeicao", {})

    if not macros_ref:
        return resultado

    suplemento = str(suplemento).lower().strip()

    if isinstance(contagem_refeicoes, list):
        qtd_refeicoes = len(contagem_refeicoes)
    elif isinstance(contagem_refeicoes, tuple):
        qtd_refeicoes = len(contagem_refeicoes)
    elif isinstance(contagem_refeicoes, set):
        qtd_refeicoes = len(contagem_refeicoes)
    elif contagem_refeicoes is not None:
        qtd_refeicoes = int(contagem_refeicoes)
    else:
        qtd_refeicoes = len(macros_ref)

    chave_cafe = next(
        (k for k in macros_ref.keys() if "cafe da manha" in k.lower()),
        None
    )

    # REGRA 1:
    # Se a pessoa NÃO usa suplemento e faz até 3 refeições,
    # suavizamos as metas por refeição para algo mais executável com comida.
    if suplemento == "n" and qtd_refeicoes <= 3:
        for nome_ref, meta in macros_ref.items():
            prot_atual = meta.get("proteina", 0)
            nome = nome_ref.lower()

            if "cafe" in nome:
                meta["proteina"] = min(prot_atual, 20)
            elif "lanche" in nome:
                meta["proteina"] = min(prot_atual, 15)
            else:
                meta["proteina"] = min(prot_atual, 30)

        if chave_cafe:
            print("⚖️ Ajuste de Viabilidade: metas de proteína suavizadas para rotina sem suplemento.")

        return resultado

    # REGRA 2:
    # Nos outros casos, limita proteína do café e redistribui a sobra.
    if chave_cafe:
        meta_p_cafe = macros_ref[chave_cafe].get("proteina", 0)
        limite_ovos = 22

        if meta_p_cafe > limite_ovos:
            sobra = meta_p_cafe - limite_ovos
            macros_ref[chave_cafe]["proteina"] = limite_ovos

            outras_refeicoes = [k for k in macros_ref.keys() if k != chave_cafe]

            if outras_refeicoes:
                adicional = sobra / len(outras_refeicoes)

                for ref in outras_refeicoes:
                    nova_prot = macros_ref[ref].get("proteina", 0) + adicional
                    macros_ref[ref]["proteina"] = round(nova_prot)

                print(f"⚖️ Ajuste de Viabilidade: {round(sobra)}g de proteína movidos do {chave_cafe}.")
                print(f"➡️ Distribuído entre: {', '.join(outras_refeicoes)}")

    return resultado


# --- FUNÇÕES DE BIOMETRIA E SAÚDE ---

def calcular_TMB(peso, altura, idade, sexo):
    ajuste = -161 if sexo == "f" else 5
    return (10 * peso) + (6.25 * altura) - (5 * idade) + ajuste

def calcular_TDEE(taxa_metabolica, atividade):
    ajustes = {"s": 1.2, "l": 1.375, "m": 1.55, "ma": 1.725, "ea": 2.0}
    return taxa_metabolica * ajustes.get(atividade, 1.2)

def calcular_imc(peso, altura):
    imc = peso / ((altura/100) ** 2)
    if imc < 18.5: return "Abaixo do Peso"
    elif imc < 25: return "Peso adequado"
    elif imc < 30: return "Sobrepeso"
    else: return "Obesidade"

def agua_dia(peso, idade):
    ajuste = 40 if idade < 18 else 35 if idade < 55 else 30 if idade < 65 else 25
    return peso * ajuste

def cintura_risco(cintura, sexo):
    if sexo == "f":
        return "Baixo" if cintura < 80 else "Médio" if cintura < 88 else "Alto"
    return "Baixo" if cintura < 94 else "Médio" if cintura < 102 else "Alto"

# --- FUNÇÕES DE METAS E CALORIAS ---

def calorias_consumir(tdee, objetivo, doce, ajuste_velocidade):
    tabela_ajustes = {"a": 0.3, "b": 0.5, "c": 0.75, "d": 1.0}
    kg_semana = tabela_ajustes.get(ajuste_velocidade, 0.5)
    variacao_diaria = (kg_semana * 7700) / 7
    
    if objetivo == "pp": consumir = tdee - variacao_diaria
    elif objetivo == "gm": consumir = tdee + variacao_diaria
    else: consumir = tdee

    if doce == "s": consumir *= 0.95 
    return round(consumir)

def proteina_basica(peso, atividade):
    ajustes = {"s": 0.8, "l": 1.3, "m": 1.4, "ma": 1.8, "ea": 2.2}
    return peso * ajustes.get(atividade, 1.2)

def macros_refeicao(kcal_refeicao, proteina_refeicao):
    prot_g = proteina_refeicao
    prot_kcal = prot_g * 4
    kcal_restante = max(0, kcal_refeicao - prot_kcal)

    return {
        "proteina": round(prot_g),
        "carboidrato": round((kcal_restante * 0.5) / 4),
        "gorduras": round((kcal_restante * 0.3) / 9),
        "calorias": round(kcal_refeicao)
    }

def distribuir_calorias(total_cal, refeicoes_ativas, refeicao_preferida=None):
    pesos_base = {
        "cafe da manha": 0.20,
        "lanche da manha": 0.10,
        "almoco": 0.30,
        "lanche da tarde": 0.15,
        "janta": 0.25
    }

    nomes_exibicao = {
        "cafe da manha": "Café",
        "lanche da manha": "Lanche manhã",
        "almoco": "Almoço",
        "lanche da tarde": "Lanche tarde",
        "janta": "Janta"
    }

    mapa_pref = {
        "1": "cafe da manha",
        "2": "lanche da manha",
        "3": "almoco",
        "4": "lanche da tarde",
        "5": "janta"
    }

    pesos_ativos = {
        ref: pesos_base[ref]
        for ref in refeicoes_ativas
        if ref in pesos_base
    }

    soma_pesos = sum(pesos_ativos.values())
    if soma_pesos == 0:
        return {}

    pesos_normalizados = {
        ref: peso / soma_pesos
        for ref, peso in pesos_ativos.items()
    }

    ref_pref_real = mapa_pref.get(str(refeicao_preferida))
    if ref_pref_real in pesos_normalizados:
        boost = 0.05
        pesos_normalizados[ref_pref_real] += boost

        outras = [r for r in pesos_normalizados if r != ref_pref_real]
        if outras:
            reducao = boost / len(outras)
            for r in outras:
                pesos_normalizados[r] -= reducao

        soma_final = sum(pesos_normalizados.values())
        pesos_normalizados = {
            ref: peso / soma_final
            for ref, peso in pesos_normalizados.items()
        }

    res = {
        nomes_exibicao[ref]: round(total_cal * peso)
        for ref, peso in pesos_normalizados.items()
    }

    return res

# --- GRAMAGEM (CORRIGIDA COM CHAVES DO SEU JSON) ---

def calcular_total_real_marmita(pesos, tabela_alimentos):
    total_kcal = 0
    for item, gramas in pesos.items():
        item_busca = item.replace("_", " ").lower().strip()
        dados = tabela_alimentos.get(item_busca, {})
        kcal_por_100g = dados.get('calorias', 0)
        total_kcal += (kcal_por_100g * gramas) / 100
    return round(total_kcal)
