import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from fpdf import FPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- CONFIGURAÇÕES DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
TEMPLATES_DIR = os.path.join(ASSETS_DIR, "templates")

# Registro da Fonte
NOME_FONTE = "DancingScript-VariableFont_wght.ttf"
caminho_fonte = os.path.join(FONTS_DIR, NOME_FONTE)
if os.path.exists(caminho_fonte):
    pdfmetrics.registerFont(TTFont('LetraCorrida', caminho_fonte))
    FONTE_TITULO = 'LetraCorrida'
else:
    FONTE_TITULO = 'Times-Italic'

# ==============================================================================
# FUNÇÃO: LISTA DE COMPRAS (TEMPLATE FIXO)
# ==============================================================================
def preencher_template_compras(caminho_destino, lista_alimentos):
    caminho_img = os.path.join(TEMPLATES_DIR, "template_compras.png")
    c = canvas.Canvas(caminho_destino, pagesize=A4)

    if os.path.exists(caminho_img):
        c.drawImage(caminho_img, 0, 0, width=A4[0], height=A4[1])

    x_base, y_topo, espacamento = 65, 650, 22.5
    num_linhas_fixas = 25
    cor_bronze = (0.8, 0.6, 0.4)

    # --- Títulos ---
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(*cor_bronze)
    c.drawCentredString(x_base + 85, y_topo + 25, "PRODUTO")
    c.drawCentredString(x_base + 195, y_topo + 25, "VALOR")
    c.drawCentredString(x_base + 320, y_topo + 25, "PRODUTO")
    c.drawCentredString(x_base + 430, y_topo + 25, "VALOR")

    # --- Grade Bronze ---
    c.setStrokeColorRGB(*cor_bronze)
    for col in range(2):
        x_col = x_base + (col * 235)
        y_linha = y_topo
        for i in range(num_linhas_fixas):
            c.rect(x_col, y_linha + 2, 10, 10, stroke=1, fill=0)
            c.line(x_col + 15, y_linha, x_col + 160, y_linha)
            c.line(x_col + 170, y_linha, x_col + 225, y_linha)
            y_linha -= espacamento

    # --- Lógica de Captura (O que você já tinha) ---
    itens_para_imprimir = []
    if isinstance(lista_alimentos, dict):
        for item, info in lista_alimentos.items():
            if isinstance(info, dict) and "texto_casa" in info:
                itens_para_imprimir.append(info["texto_casa"])
            elif isinstance(info, dict) and "texto_formatado" in info:
                itens_para_imprimir.append(info["texto_formatado"])
            else:
                # Caso o valor seja apenas o número (fallback)
                valor = info.get("peso_bruto", info) if isinstance(info, dict) else info
                itens_para_imprimir.append(f"{item.replace('_',' ').capitalize()}: {round(valor)}g")
    else:
        itens_para_imprimir = [linha.replace(" - ", "") for linha in lista_alimentos]

    # --- O QUE FALTOU: O loop para DESENHAR o texto no PDF ---
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    x_texto, y_texto, contador = x_base + 18, y_topo + 4, 0

    for texto in itens_para_imprimir:
        if contador >= num_linhas_fixas * 2: break
        
        c.drawString(x_texto, y_texto, texto)
        
        y_texto -= espacamento
        contador += 1
        
        # Se encher a primeira coluna, pula para a segunda
        if contador == num_linhas_fixas:
            x_texto = x_base + 240 + 18
            y_texto = y_topo + 4

    c.save()
    print(f"✅ Lista gerada: {os.path.basename(caminho_destino)}")
# ==============================================================================
# FUNÇÃO: MARMITAS (DUAS COLUNAS)
# ==============================================================================
def preencher_template_marmitas(caminho_destino, dados_json, nome_usuario):
    caminho_img = os.path.join(TEMPLATES_DIR, "template_marmitas.png")
    c = canvas.Canvas(caminho_destino, pagesize=A4)

    if os.path.exists(caminho_img):
        c.drawImage(caminho_img, 0, 0, width=A4[0], height=A4[1])
    
    # Nome do Usuário no topo
    c.setFont(FONTE_TITULO, 70)
    c.setFillColor(colors.white)
    c.drawCentredString(297, 745, nome_usuario.title()) 

    # Pegamos a chave correta do seu JSON
    plano = dados_json.get("resumo_texto_plano", [])
    
    # Coordenadas das 2 colunas
    x_colunas = [30, 305]
    y_linhas = [628, 465, 302, 137]

    for i, bloco in enumerate(plano):
        if i >= 8: break 
        
        x = x_colunas[i % 2]
        y = y_linhas[i // 2]
        
        # 1. Pegamos o título do JSON e padronizamos para maiúsculas
        titulo_json = bloco.get("titulo", "").upper()

        # 2. Definimos o deslocamento horizontal (x) padrão
        deslocamento_x = 5 

        # 3. Verificamos qual é a refeição independente do número de unidades
        if "CAFE DA MANHA" in titulo_json:
            deslocamento_x = 37.5
        elif "ALMOCO" in titulo_json:
            deslocamento_x = 60
        elif "LANCHE DA MANHA" in titulo_json:
            deslocamento_x = 35
        elif "LANCHE DA TARDE" in titulo_json:
            deslocamento_x = 35
        elif "JANTA" in titulo_json:
            deslocamento_x = 55

        # 4. Desenhamos o título usando a variável de deslocamento
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.black)
        c.drawString(x + deslocamento_x, y + 18, titulo_json)

        # Itens da Marmita
        c.setFont("Helvetica", 10)
        y_item = y - 8
        
        # No seu JSON, os itens já são strings formatadas
        for linha in bloco.get("itens", []):
            # Remove espaços extras do início para alinhar no PDF
            texto_limpo = linha.strip() 
            c.drawString(x + 2, y_item, texto_limpo)
            y_item -= 12

        # Rodapé da marmita (Kcal e Proteína)
        c.setFont("Helvetica-Oblique", 9)
        info_final = " ".join(bloco.get("final", []))
        c.drawString(x + 5, y_item - 5, info_final)

    c.save()
    print(f"✅ PDF de Marmitas gerado com {len(plano)} blocos.")

# ==============================================================================
# PROCESSAMENTO INDIVIDUAL E GLOBAL
# ==============================================================================
def processar_impressao_usuario(nome, sobrenome):
    n_f, s_f = nome.strip().lower(), sobrenome.strip().lower()
    pasta_usuario = os.path.join(r"C:\Users\thais\Documents\Dieta\dados_usuarios")
    caminho_json = os.path.join(pasta_usuario, f"{n_f}_{s_f}.json")

    if not os.path.exists(caminho_json):
        print(f"❌ Perfil não encontrado: {caminho_json}")
        return None

    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Gera Marmita Individual
    pdf_marmita = os.path.join(pasta_usuario, f"Plano_Marmitas_{n_f}.pdf")
    preencher_template_marmitas(pdf_marmita, dados, n_f)
    
    # Retorna os pesos brutos para a soma da casa
    return dados.get("lista_compras_mercado", {})

def gerar_tudo_familia():
    print("\n🏠 --- GERADOR DE PLANEJAMENTO DA CASA ---")
    lista_mercados_brutos = []
    
    while True:
        n = input("\nNome: ")
        s = input("Sobrenome: ")
        mercado = processar_impressao_usuario(n, s)
        if mercado: lista_mercados_brutos.append(mercado)
        
        if input("\nAdicionar outro? (s/n): ").lower() != 's': break

    if lista_mercados_brutos:
        import re
        casa_unificada = {}
        
        # 1. UNIÃO E CÁLCULO DE PESO POR UNIDADE
        for mercado_individual in lista_mercados_brutos:
            for item, info in mercado_individual.items():
                if item not in casa_unificada:
                    # Cálculo da referência de peso por unidade (ex: 300g / 6 un = 50g cada)
                    peso_total_ref = info.get("peso_bruto", 0)
                    u_ref = info.get("unidade", "g")
                    
                    # Regex para pegar o número no "texto_formatado"
                    match = re.search(r'(\d+)', info.get("texto_formatado", ""))
                    qtd_ref = int(match.group(1)) if match else 1
                    
                    casa_unificada[item] = {
                        "peso": 0, 
                        "unidade": u_ref,
                        "peso_por_unidade": peso_total_ref / qtd_ref if qtd_ref > 0 else 0
                    }
                
                # Soma o peso bruto de todos os moradores (agora dentro do loop correto)
                casa_unificada[item]["peso"] += info.get("peso_bruto", 0)

        # 2. FORMATAÇÃO DO TEXTO FINAL PARA O PDF
        for item, info in casa_unificada.items():
            p = info["peso"]
            u = info["unidade"]
            ppu = info["peso_por_unidade"]
            nome = item.replace('_', ' ').capitalize()

            # Lógica para Unidades/Fatias (Divisão)
            if u in ["unidade", "fatia", "un"] and ppu > 0:
                qtd_total = round(p / ppu)
                plural = "s" if qtd_total > 1 else ""
                unidade_texto = f"{u}{plural}"
                valor_txt = f"{qtd_total} {unidade_texto} (~{round(p)}g)"
            
            # Lógica para Líquidos
            elif u == "ml":
                valor_txt = f"{p/1000:.2f}L" if p >= 1000 else f"{round(p)}ml"
            
            # Lógica para Peso (G/KG)
            else:
                valor_txt = f"{p/1000:.2f}kg" if p >= 1000 else f"{round(p)}g"
            
            # Salva o texto que a função preencher_template_compras vai ler
            info["texto_casa"] = f"{nome}: {valor_txt}"

        # 3. GERAÇÃO DO PDF
        caminho_casa = os.path.join(BASE_DIR, "Lista_MERCADO_CASA.pdf")
        preencher_template_compras(caminho_casa, casa_unificada)
        print(f"\n✨ TUDO PRONTO! Marmitas nas pastas e Lista da Casa em: {caminho_casa}")

if __name__ == "__main__":
    gerar_tudo_familia()