import json
import cv2
import matplotlib

# Configurar backend antes de importar pyplot
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================

caminho_imagem = "figura.png"

# Quanto maior o epsilon, maior a simplificação.
EPSILON_PERCENTUAL = 0.001

# Espessura das linhas na imagem final
ESPESSURA_LINHA = 2

# Cor BGR para desenhar as aproximações
COR_APROXIMACAO = (255, 0, 0)  # azul

# Número de segmentos reais esperados (para filtrar os artefatos minúsculos)
NUMERO_SEGMENTOS_ESPERADO = 19


# ==============================================================================
# 1. CARREGAR IMAGEM
# ==============================================================================

imagem = cv2.imread(caminho_imagem)

if imagem is None:
    print(
        f"Erro: Não foi possível carregar a imagem em '{caminho_imagem}'."
    )
    raise SystemExit


# ==============================================================================
# 2. PRÉ-PROCESSAMENTO
# ==============================================================================

imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

imagem_suave = cv2.GaussianBlur(
    imagem_cinza,
    (5, 5),
    0
)


# ==============================================================================
# 3. BINARIZAÇÃO
# ==============================================================================

_, imagem_limiar = cv2.threshold(
    imagem_suave,
    200,
    255,
    cv2.THRESH_BINARY_INV
)


# ==============================================================================
# 4. EXTRAIR CONTORNOS EXTERNOS E FILTRAR ARTEFATOS
# ==============================================================================

contornos_brutos, _ = cv2.findContours(
    imagem_limiar,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

print(f"\nContornos brutos encontrados: {len(contornos_brutos)}")

# --------------------------------------------------------------------------
# FILTRAGEM DOS ARTEFATOS
# Como sabemos que existem 18 segmentos reais e 2 artefatos minúsculos,
# ordenamos os contornos por área (do maior para o menor) e mantemos apenas
# os 18 primeiros.
# --------------------------------------------------------------------------

contornos_externos = sorted(
    contornos_brutos, 
    key=cv2.contourArea, 
    reverse=True
)[:NUMERO_SEGMENTOS_ESPERADO]

print(f"Contornos válidos após remoção de artefatos: {len(contornos_externos)}")


# ==============================================================================
# 5. APLICAÇÃO DO RDP
# ==============================================================================

contornos_aproximados = []

total_pontos_originais = 0
total_pontos_aproximados = 0


for index, contorno in enumerate(contornos_externos):

    # Quantidade de pontos antes da simplificação
    quantidade_original = len(contorno)

    total_pontos_originais += quantidade_original

    # --------------------------------------------------------------------------
    # Perímetro do contorno
    # --------------------------------------------------------------------------

    perimetro = cv2.arcLength(
        contorno,
        True
    )

    # --------------------------------------------------------------------------
    # epsilon do Ramer-Douglas-Peucker
    # --------------------------------------------------------------------------

    epsilon = EPSILON_PERCENTUAL * perimetro

    # --------------------------------------------------------------------------
    # RDP
    # --------------------------------------------------------------------------

    contorno_aproximado = cv2.approxPolyDP(
        contorno,
        epsilon,
        True
    )

    quantidade_aproximada = len(contorno_aproximado)

    total_pontos_aproximados += quantidade_aproximada

    contornos_aproximados.append(
        contorno_aproximado
    )

    reducao = (
        100.0
        * (1 - quantidade_aproximada / quantidade_original)
    )

    print(
        f"Artéria {index + 1}: "
        f"{quantidade_original} pontos -> "
        f"{quantidade_aproximada} pontos "
        f"({reducao:.2f}% de redução)"
    )


# ==============================================================================
# 6. ESTATÍSTICAS GERAIS
# ==============================================================================

reducao_total = (
    100.0
    * (1 - total_pontos_aproximados / total_pontos_originais)
)

print("\n==============================================")
print("RESULTADO DA SIMPLIFICAÇÃO RDP")
print("==============================================")

print(
    f"Pontos originais:    {total_pontos_originais}"
)

print(
    f"Pontos aproximados:  {total_pontos_aproximados}"
)

print(
    f"Redução total:       {reducao_total:.2f}%"
)

print(
    f"Fator de redução:    "
    f"{total_pontos_originais / total_pontos_aproximados:.2f}x"
)


# ==============================================================================
# 7. CRIAR IMAGEM COM A APROXIMAÇÃO
# ==============================================================================

resultado_rdp = np.ones_like(imagem) * 255

cv2.drawContours(
    resultado_rdp,
    contornos_aproximados,
    -1,
    COR_APROXIMACAO,
    ESPESSURA_LINHA
)


# ==============================================================================
# 8. SALVAR IMAGEM DA APROXIMAÇÃO
# ==============================================================================

nome_arquivo_resultado = "aproximacao_rdp.png"

plt.figure(figsize=(10, 10))

plt.title(
    f"Contornos aproximados - RDP "
    f"({reducao_total:.1f}% de redução)"
)

plt.imshow(
    cv2.cvtColor(
        resultado_rdp,
        cv2.COLOR_BGR2RGB
    )
)

plt.axis("off")

plt.savefig(
    nome_arquivo_resultado,
    bbox_inches="tight",
    dpi=300
)

plt.close()

print(
    f"\nImagem da aproximação salva em "
    f"'{nome_arquivo_resultado}'"
)


# ==============================================================================
# 9. COMPARAÇÃO ORIGINAL x APROXIMAÇÃO
# ==============================================================================

comparacao = np.ones_like(imagem) * 255

# Contornos originais em vermelho
cv2.drawContours(
    comparacao,
    contornos_externos,
    -1,
    (0, 0, 255),
    1
)

# Aproximações em azul
cv2.drawContours(
    comparacao,
    contornos_aproximados,
    -1,
    (255, 0, 0),
    2
)

nome_comparacao = "comparacao_rdp.png"

plt.figure(figsize=(10, 10))

plt.title(
    "RDP: vermelho = contorno original | azul = aproximação"
)

plt.imshow(
    cv2.cvtColor(
        comparacao,
        cv2.COLOR_BGR2RGB
    )
)

plt.axis("off")

plt.savefig(
    nome_comparacao,
    bbox_inches="tight",
    dpi=300
)

plt.close()

print(
    f"Comparação salva em '{nome_comparacao}'"
)


# ==============================================================================
# 10. EXPORTAR PONTOS PARA JSON
# ==============================================================================

altura, largura = imagem.shape[:2]

dados_json = {
    "dimensoes": {
        "largura": largura,
        "altura": altura
    },

    "metodo": "Ramer-Douglas-Peucker",

    "epsilon_percentual": EPSILON_PERCENTUAL,

    "total_arterias": len(contornos_aproximados),

    "total_pontos_originais": total_pontos_originais,

    "total_pontos_aproximados": total_pontos_aproximados,

    "reducao_percentual": reducao_total,

    "arterias": []
}


for index, contorno_aproximado in enumerate(
    contornos_aproximados
):

    # Converter [[[x, y]], ...] para [[x, y], ...]
    pontos_aproximados = (
        contorno_aproximado
        .reshape(-1, 2)
        .tolist()
    )

    # Pontos originais correspondentes
    contorno_original = contornos_externos[index]

    pontos_originais = (
        contorno_original
        .reshape(-1, 2)
        .tolist()
    )

    dados_json["arterias"].append({

        "id": f"arteria_{index + 1}",

        "quantidade_pontos_original":
            len(pontos_originais),

        "quantidade_pontos_aproximados":
            len(pontos_aproximados),

        "pontos_originais":
            pontos_originais,

        "pontos_aproximados":
            pontos_aproximados
    })


# ==============================================================================
# 11. SALVAR JSON
# ==============================================================================

nome_arquivo_json = "pontos_arterias_rdp.json"

with open(
    nome_arquivo_json,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dados_json,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"JSON RDP salvo em '{nome_arquivo_json}'"
)


# ==============================================================================
# 12. EXPORTAR SVG
# ==============================================================================

nome_arquivo_svg = "arterias_rdp.svg"


with open(
    nome_arquivo_svg,
    "w",
    encoding="utf-8"
) as svg:

    svg.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
    )

    svg.write(
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        f'width="{largura}" '
        f'height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">\n'
    )

    svg.write(
        '  <rect '
        f'width="{largura}" '
        f'height="{altura}" '
        'fill="white"/>\n'
    )

    for index, contorno in enumerate(
        contornos_aproximados
    ):

        pontos = (
            contorno
            .reshape(-1, 2)
        )

        # Montar string de pontos do SVG
        pontos_svg = " ".join(
            f"{int(x)},{int(y)}"
            for x, y in pontos
        )

        svg.write(
            f'  <polygon '
            f'id="arteria_{index + 1}" '
            f'points="{pontos_svg}" '
            'fill="none" '
            'stroke="blue" '
            'stroke-width="2" '
            'stroke-linejoin="round" '
            'stroke-linecap="round"/>\n'
        )

    svg.write("</svg>\n")


print(
    f"SVG simplificado salvo em '{nome_arquivo_svg}'"
)


# ==============================================================================
# 13. MOSTRAR RESULTADO FINAL
# ==============================================================================

plt.figure(figsize=(10, 10))

plt.imshow(
    cv2.cvtColor(
        resultado_rdp,
        cv2.COLOR_BGR2RGB
    )
)

plt.title(
    "Aproximação anatômica das coronárias - RDP"
)

plt.axis("off")

plt.tight_layout()

plt.show()
