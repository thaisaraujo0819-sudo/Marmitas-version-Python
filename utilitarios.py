import os
import json

#Definindo em que pasta sera salva dos dados
Pasta_usuarios = "dados_usuarios"

#Criando a pasta
if not os.path.exists(Pasta_usuarios):
    os.makedirs(Pasta_usuarios)

#salvar arquivo/atualizacoes
def salvar_arquivo(caminho, dados):
    try:
        with open(caminho, 'w', encoding='utf-8') as f: # O 'w' é CRUCIAL
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False


# Esta é a única lista que você precisará alterar no futuro!
# No utilitarios.py

REGRAS_CADASTRO = {
    "biometria": {
        "peso": {"pergunta": "Informe seu peso (kg):", "opcoes": None},
        "altura": {"pergunta": "Informe sua altura (cm):", "opcoes": None},
        "idade": {"pergunta": "Informe sua idade:", "opcoes": None},
        "sexo": {"pergunta": "Sexo (f/m):", "opcoes": ["f", "m"]},
        "circuferencia cintura": {"pergunta": "Circunferência da cintura (cm):", "opcoes": None}
    },
    "rotina": {
        "objetivo": {
            "pergunta": "Seu objetivo será: \nMP = Manter Peso\nPP = Perder Peso\nGM = Ganhar Massa", 
            "opcoes": ["mp", "pp", "gm"]
        },
        "nivel de exercicio": {
            "pergunta": "Informe o nível de atividade física: \ns = Sedentário \nl = Leve \nm = Moderado \nma = Muito Ativo \nea = Extremamente Ativo", 
            "opcoes": ["s", "l", "m", "ma", "ea"]
        },
        "gosta de doce": {
            "pergunta": "Gosta de doce? (s/n):", 
            "opcoes": ["s", "n"]
        },
        "refeicao preferida": {
            "pergunta": "Qual refeição você prefere focar? \n1-Café \n2-Lanche M. \n3-Almoço \n4-Lanche T. \n5-Janta", 
            "opcoes": ["1", "2", "3", "4", "5"]
        },
        "velocidade": {
            "pergunta": "Qual a intensidade da sua meta? \na - 0.3kg/semana , b- 0.5kg/semana, c- 0.75kg/semana, d- 1.0kg/semana, e- 0.0kg/semana", 
            "opcoes": ["a", "b", "c", "d", "e"]
        },"preferencia_vegetais": {
        "pergunta": "Qual o peso padrão de vegetais que você usa nas marmitas (g)? \n[Pressione Enter para usar valor padrao]", 
            "opcoes": None # Aceita qualquer número ou vazio
        },"preferencia_legumes": {
        "pergunta": "Qual o peso padrão de legumes que você usa nas marmitas (g)? \n[Pressione Enter para usar valor padrao]", 
            "opcoes": None # Aceita qualquer número ou vazio
        },"suplementos": {
        "pergunta": "Utiliza algum tipo de suplemento proteico?(Whey)(s/n) \n ", 
            "opcoes": ["s", "n"]# Aceita qualquer número ou vazio
        },
    },

    "alimentacao_original": {
        "cafe da manha": {
            "pergunta": "Nível do Café da Manhã: \n1 - Simples (Carbo + Gordura + Bebida) [Ex: Pão com manteiga e café]\n2 - Médio (Carbo + Proteína + Bebida) [Ex: Pão com ovo e café]\n3 - Completo (Carbo + Proteína + Fruta + Bebida) [Ex: Pão, ovo, maçã e café]\n0 - Nao Consome", 
            "opcoes": ["1", "2", "3", "0"]
        },
        "lanche da manha": {
            "pergunta": "Nível do Lanche da Manhã: \n1 - Rápido (Fruta ou Bebida) [Ex: Uma maçã ou um iogurte]\n2 - Intermediário (Carbo + Proteína) [Ex: Sanduíche de queijo ou iogurte com aveia]\n3 - Reforçado (Carbo + Proteína + Fruta) [Ex: Sanduíche natural + vitamina de fruta]\n0 - Nao Consome",
            "opcoes": ["1", "2", "3", "0"]
        },
        "almoco": {
            "pergunta": "Nível do Almoço: \n1 - Prático (Carbo + Proteína) [Ex: Arroz com frango grelhado]\n2 - Padrão (Carbo + Proteína + Legumes/Salada) [Ex: Arroz, feijão, carne e salada]\n3 - Completo (Carbo + Proteína + Legumes + Salada + Suco/Sobremesa) [Ex: Prato cheio + fruta de sobremesa]\n0 - Nao Consome", 
            "opcoes": ["1", "2", "3", "0"]
        },
        "lanche da tarde": {
            "pergunta": "Nível do Lanche da Tarde: \n1 - Rápido (Fruta ou Bebida) [Ex: Uma maçã ou um iogurte]\n2 - Intermediário (Carbo + Proteína) [Ex: Sanduíche de queijo ou iogurte com aveia]\n3 - Reforçado (Carbo + Proteína + Fruta) [Ex: Sanduíche natural + vitamina de fruta]\n0 - Nao Consome", 
            "opcoes": ["1", "2", "3", "0"]
        },
        "janta": {
            "pergunta": "Nível da Janta: \n1 - Prático (Carbo + Proteína) [Ex: Arroz com frango grelhado]\n2 - Padrão (Carbo + Proteína + Legumes/Salada) [Ex: Arroz, feijão, carne e salada]\n3 - Completo (Carbo + Proteína + Legumes + Salada + Suco/Sobremesa) [Ex: Prato cheio + fruta de sobremesa]\n0 - Nao Consome", 
            "opcoes": ["1", "2", "3", "0"]
        }
    }
}


def carregar_arquivo(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            perfil = json.load(arquivo)
            
        # 0 = biometria, 1 = rotina, 2 = alimentacao_original, 3 = lista de marmita, 4 = lista de mercado
        # Verifica se todas as chaves estão no dicionário
        nivel = 1
        # Percorre as chaves em ordem de importância
        for gaveta, campo  in REGRAS_CADASTRO.items():
            if gaveta in perfil:
                # Verifica se todos os campos daquela gaveta existem e não são vazios
                if all(perfil[gaveta].get(c) not in [None, "", "null"] for c in campo):
                    nivel += 1
                else:
                    break
            else:
                break
        return nivel, perfil
    
    except FileNotFoundError:
        return "inexistente", None
    except json.JSONDecodeError:
        return "corrompido", None
    
import json

def salvar_marmita_no_perfil(caminho_arquivo, dados_marmita):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            perfil = json.load(f)
        
        # Garante que a chave principal existe
        if "marmitas_semana" not in perfil:
            perfil["marmitas_semana"] = {}
            
        # Pega o nome da refeição (ex: 'Café', 'Almoço')
        ref_alvo = dados_marmita.get("refeicao_alvo", "Outros")
        
        # Se a "caixa" daquela refeição não existir, cria uma lista vazia
        if ref_alvo not in perfil["marmitas_semana"]:
            perfil["marmitas_semana"][ref_alvo] = []
            
        # Adiciona os dados na caixa correspondente
        # Removemos a chave 'refeicao_alvo' de dentro dos dados para não ficar repetitivo
        dados_salvar = dados_marmita.copy()
        perfil["marmitas_semana"][ref_alvo].append(dados_salvar)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(perfil, f, indent=4, ensure_ascii=False)
            
        print(f"\n✅ Marmita salva com sucesso na categoria: {ref_alvo}!")
        
    except Exception as e:
        print(f"Erro ao salvar marmita: {e}")

def carregar_base_alimentos():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio, "alimentos", "base_alimentos.json")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados_brutos = json.load(f)

        tabela_limpa = {}

        for nivel in dados_brutos.values():
            if not isinstance(nivel, dict):
                continue

            for categoria in nivel.values():
                if not isinstance(categoria, dict):
                    continue

                prio_da_categoria = categoria.get("prioridade", 4)

                for nome_alimento, info in categoria.items():
                    if nome_alimento == "prioridade":
                        continue

                    if not isinstance(info, dict):
                        continue

                    nome_ajustado = nome_alimento.replace("_", " ").lower().strip()

                    info_limpa = info.copy()
                    info_limpa["prio_ads"] = prio_da_categoria

                    tabela_limpa[nome_ajustado] = info_limpa

        print(f"✅ Sucesso: {len(tabela_limpa)} alimentos mapeados com prioridades!")
        return tabela_limpa

    except Exception as e:
        print(f"❌ Erro ao processar JSON: {e}")
        return {}

    
    
def carregar_regras():
    # 1. Descobre onde o script atual está (C:\Users\thais\Documents\Dieta\Marmitas)
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Monta o caminho entrando na pasta 'alimentos'
    caminho_arquivo = os.path.join(diretorio_script, "alimentos", "regras_max_min.json")
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
            # Normaliza as chaves específicas para minúsculo
            especificos = dados.get("regras_por_item_especifico", {})
            especificos_norm = {k.lower(): v for k, v in especificos.items()}
            dados["regras_por_item_especifico"] = especificos_norm
            
            return dados
    except FileNotFoundError:
        return {}

# Uso:
REGRAS = carregar_regras()
