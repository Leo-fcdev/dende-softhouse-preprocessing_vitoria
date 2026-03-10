#Importações
import csv 
import os
from dende_preprocessing import Preprocessing

#Função de carregamento
def carregar_dados_spotify(caminho_arquivo):
    dataset = {}

    #Verifica se o arquivo existe no local informado
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: o arquivo '{caminho_arquivo}' não foi encontrado nessa pasta. Verifique se o nome do arquivo está correto e se está na mesma pasta do script.")
        return None
    
    #Abrindo o arquivo
    try:
        #'with open' Forma segura de abrir arquivos (Ele mesmo fecha depois)
        # 'r' = read (leitura), 'utf-8' = aceita acentos.
        with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f) #DircReader lê cada linha como um dicionário

            #Cria as colunas
            if reader.fieldnames:
                for col in reader.fieldnames:
                    dataset[col] = []

            #Preenche os dados (Conversão)
            for row in reader:
                for col, valor in row.items():
                    texto = valor.strip() # Remove espaços em branco acidentais
                    
                    # 1. VERIFICAÇÃO DE NULOS: Se for vazio ou N/A, guarda como None
                    if texto == "" or texto.upper() == "N/A":
                        dataset[col].append(None)
                    else:
                        try:
                            #Se tem ponto tenta converter para decimal (float)
                            if '.' in texto:
                                dataset[col].append(float(texto))
                            #Se não tem tenta converter para inteiro (int)
                            else:
                                dataset[col].append(int(texto))
                        
                        #Caso der erro guarda como texto
                        except ValueError:
                            dataset[col].append(texto)
        
        print(f"Sucesso! {len(dataset)} colunas carregadas.")
        return dataset
    
    #Caso der erro na abertura do arquivo
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

#Garante que esse código só rode neste arquivo.     
if __name__ == "__main__":
    print("\n" + "="*30)
    print(" Iniciando pipiline de Pré-processamento (Spotify)")
    print("="*50 + "\n")

    #Carrega os dados
    dados = carregar_dados_spotify('./spotify_data.csv')

    if dados:
        #Instancia a classe de Pré-processamento
        prep = Preprocessing(dados)

        #Conta as linha originais
        total_linhas_originais = len(next(iter(prep.dataset.values())))
        print(f"1. Total de músicas (linhas) originais no CVS: {total_linhas_originais}")

        #TRATAMENTO DE VALORES NULOS

        nulos = prep.isna()
        linhas_com_nulos = len(next(iter(nulos.values()))) if nulos else 0
        print(f"Músicas que contêm dados sujos (N/A): {linhas_com_nulos}")

        #Aplica limpeza
        prep.dropna()

        total_linhas_limpas = len(next(iter(prep.dataset.values())))
        print(f"Restaram {total_linhas_limpas} músicas limpas para a análise.")

        #ESCALONAMENTO DE DADOS
        col_escala = 'track_popularity'

        if col_escala in prep.dataset:
            max_antigo = max(prep.dataset[col_escala])
            print(f"Valor máximo antigo da popularidade: {max_antigo}")

            #Roda o MinMaxScaler
            prep.scale(columns={col_escala}, method='minMax')

            #VErifica o resultado
            max_novo = max(prep.dataset[col_escala])
            min_novo = min(prep.dataset[col_escala])
            print(f"Nova escala criada! Mínimo: {min_novo:.1f} | Máximo: {max_novo:.1f}")

        #CODIFICAÇÃO DE CATEGORIAS

        col_categ = 'album_type'

        if col_categ in prep.dataset:
            print(f"Primeiros tipos de álbum (Texto): {prep.dataset[col_categ][:5]}")

            #Roda o label Enconder
            prep.encode(columns={col_categ}, method='label')

            #Verifica o resultado
            print(f"Textos convertidos para IDs numéricos: {prep.dataset[col_categ][:5]}")
        
        print("\n" + "="*50)
        print(" PIPELINE CONCLUÍDO COM SUCESSO!")
        print("="*50 + "\n")
