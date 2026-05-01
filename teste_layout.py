import imprimir
import os


# 1. DADOS DE TESTE (MOCK DATA)
# Criando uma lista de compras de exemplo
dados_compras_teste = {
    "Frango_File": 1500,
    "Arroz_Integral": 1000,
    "Batata_Doce": 2000,
    "Brocolis": 800,
    "Azeite_de_Oliva": 500,
    "Patinho_Moido": 1200,
    "Oos": 600,
    "Dieta": 1500,
    "Arroz": 1000,
    "Batata": 2000,
    "Brocols": 800,
    "AzeiteOliva": 500,
    "Patinho": 1200,
    "Ovo": 600,
    "FrangoFile": 1500,
    "Arrozntegral": 1000,
    "Batataoce": 2000,
    "Brocis": 800,
    "Azeite_deOliva": 500,
    "PatinhoMoido": 1200,
    "vos": 600,
    "FrangoFile": 1500,
    "Arroz_ntegral": 1000,
    "Batata_oce": 2000,
    "Brocoli": 800,
    "Azeite_e_Oliva": 500,
    "Patinh_Moido": 1200,
    "Ov": 600
}

# Criando marmitas de exemplo (Formato que o seu código usa)
dados_marmitas_teste = [
    {
        "nome_bonito": "Almoço Segunda",
        "quantidade": 3,
        "pesos": {"Frango": 150, "Arroz": 100, "Brocolis": 80},
        "kcal_final": 450.5,
        "prot_final": 35.2
    },
    {
        "nome_bonito": "Jantar Segunda",
        "quantidade": 3,
        "pesos": {"Patinho": 120, "Batata_Doce": 150},
        "kcal_final": 520.0,
        "prot_final": 30.0
    },
    {
        "nome_bonito": "Jantar Segunda",
        "quantidade": 3,
        "pesos": {"Patinho": 200, "Batata_Doce": 150},
        "kcal_final": 520.0,
        "prot_final": 30.0
    },
    {
        "nome_bonito": "Almoço Segunda",
        "quantidade": 3,
        "pesos": {"Frango": 200, "Arroz": 100, "Brocolis": 80},
        "kcal_final": 450.5,
        "prot_final": 35.2
    },
    {
        "nome_bonito": "Jantar Segunda",
        "quantidade": 3,
        "pesos": {"Patinho": 200, "Batata_Doce": 150},
        "kcal_final": 520.0,
        "prot_final": 30.0
    },
    {
        "nome_bonito": "Almoço Segunda",
        "quantidade": 3,
        "pesos": {"Frango": 200, "Arroz": 100, "Brocolis": 80},
        "kcal_final": 450.5,
        "prot_final": 35.2
    },
    {
        "nome_bonito": "Jantar Segunda",
        "quantidade": 3,
        "pesos": {"Patinho": 200, "Batata_Doce": 150},
        "kcal_final": 520.0,
        "prot_final": 30.0
    },
    {
        "nome_bonito": "Almoço Segunda",
        "quantidade": 3,
        "pesos": {"Frango": 200, "Arroz": 100, "Brocolis": 80},
        "kcal_final": 450.5,
        "prot_final": 35.2
    }
]

# 2. EXECUTANDO O TESTE
print("🚀 Iniciando teste de geração de PDF...")

try:
    # Gerando a Lista de Compras
    imprimir.preencher_template_compras("TESTE_LISTA.pdf", dados_compras_teste)
    print("✅ Arquivo 'TESTE_LISTA.pdf' gerado!")

    # Gerando o Layout de Marmitas
    imprimir.preencher_template_marmitas("TESTE_MARMITAS.pdf", dados_marmitas_teste, "THAIS")
    print("✅ Arquivo 'TESTE_MARMITAS.pdf' gerado!")

    print("\n👉 Verifique os arquivos na pasta do seu projeto!")

except Exception as e:
    print(f"❌ Ocorreu um erro no teste: {e}")