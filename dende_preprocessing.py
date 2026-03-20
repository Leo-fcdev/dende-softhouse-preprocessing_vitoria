from dende_statistics import Statistics
from typing import Dict, List, Set, Any

class MissingValueProcessor:
    """
    Processa valores ausentes (representados como None) no dataset.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        #Recebe o dicionário de dados
        self.dataset = dataset

    def _get_target_columns(self, columns: Set[str]) -> List[str]:
        """Retorna as colunas a serem processadas. Se 'columns' for vazio, retorna todas as colunas."""
        return list(columns) if columns else list(self.dataset.keys())

    def isna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Retorna um novo dataset contendo apenas as linhas que não possuem
        pelo menos um valor nulo (None) em uma das colunas especificadas.
        """

        target_cols = self._get_target_columns(columns)
        
        #Descobre o número de linha pegando o tamanho da primeira coluna
        row_count = len(next(iter(self.dataset.values())))

        index_nulo = []

        # Percorre o dataset linha por linha
        for i in range(row_count):
            # Para cada linha, verifica as colunas alvo
            for col in target_cols:
                # Se eu encontrar um nulo nesta linha, guarda o índice e pulo para a próxima
                if self.dataset[col][i] is None:
                    index_nulo.append(i)
                    break
        
        #Cria um novo dicionário com linha que falharam no teste 
        novo_dataset = {col: [] for col in self.dataset.keys()}
        for i in index_nulo:
            for col in self.dataset.keys():
                novo_dataset[col].append(self.dataset[col][i])

        return novo_dataset
        

    def notna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Retorna um novo dataset contendo apenas as linhas que não possuem
        valores nulos (None) em nenhuma das colunas especificadas.
        """
        target_cols = self._get_target_columns(columns)
        row_count = len(next(iter(self.dataset.values())))

        index_sem_nulo = []

        #Percorre o dataset linha por linha
        for i in range(row_count):
            tem_nulo = False
            for col in target_cols:
                if self.dataset[col][i] is None:
                    tem_nulo = True
                    break #Se achar um nulo não precisa percorrer o restante
            
            #Se passou limpa guarda o índice
            if not tem_nulo:
                index_sem_nulo.append(i)
        
        #Cria um dicionário com as linhas aprovadas
        novo_dataset = {col: [] for col in self.dataset.keys()}
        for i in index_sem_nulo:
            for col in self.dataset.keys():
                novo_dataset[col].append(self.dataset[col][i])

        return novo_dataset

    def fillna(self, columns: Set[str] = None, value: Any = 0) -> Dict[str, List[Any]]:
        """
        Preenche valores nulos (None) nas colunas especificadas com um valor fixo.
        Modifica o dataset da classe.
        """
        target_cols = self._get_target_columns(columns)
        row_count = len(next(iter(self.dataset.values())))

        for col in target_cols:
            #Onde encontrar None coloca um valor padrão
            for i in range(row_count):
                if self.dataset[col][i] is None:
                    self.dataset[col][i] = value
        
        return self.dataset

    def dropna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Remove as linhas que contêm valores nulos (None) nas colunas especificadas.
        Modifica o dataset da classe.
        """
        #O método notna() fica com a responsabilidade de achar linha limpas
        dataset_limpo = self.notna(columns)

        #Sobrescrevo as colunas sujas pelas limpas
        for col in self.dataset.keys():
            self.dataset[col] = dataset_limpo[col]

        return self.dataset
class Scaler:
    """
    Aplica transformações de escala em colunas numéricas do dataset.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset

    def _get_target_columns(self, columns: Set[str]) -> List[str]:
        return list(columns) if columns else list(self.dataset.keys())

    def minMax_scaler(self, columns: Set[str] = None) -> Dict[str, List[Any]]:

        """
        Aplica a normalização Min-Max ($X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$)
        nas colunas especificadas. Modifica o dataset.

        Args:
            columns (Set[str]): Colunas para aplicar o scaler. Se vazio, tenta aplicar a todas.
        """

        # Vê quais colunas o usuário quer processar
        colunas_alvo = self._get_target_columns(columns)

        #Criar um loop para passar por cada coluna
        for coluna in colunas_alvo:

            #Puxamos a lista de dados da coluna atual
            dados_coluna = self.dataset[coluna]

            #Pega apenas o números válidos, ignorados os nones
            valores_validos = [v for v in dados_coluna if v is not None]

            #Se a coluna tiver apenas None, pula ela
            if not valores_validos:
                continue

            valor_min = min(valores_validos)
            valor_max = max(valores_validos)

            denominador = valor_max - valor_min

            nova_lista = [] #Criar uma nova lista

            #Percorre por cada número da lista original
            for valor in dados_coluna:
                
                if valor is None:
                    nova_lista.append(None) #Deixa o vazio como vazip
                else:
                    if denominador == 0:
                        novo_valor = 0.0
                    else:
                        novo_valor = (valor - valor_min) / denominador

                    #Adiciona novo valor na nova lista
                    nova_lista.append(novo_valor)

            self.dataset[coluna] = nova_lista

        return self.dataset

    def standard_scaler(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Aplica a padronização Z-score ($X_{std} = \frac{X - \mu}{\sigma}$)
        nas colunas especificadas. Modifica o dataset.

        Args:
            columns (Set[str]): Colunas para aplicar o scaler. Se vazio, tenta aplicar a todas.
        """

        #Identifica qual coluna será processada
        colunas_alvo = self._get_target_columns(columns)

        #Instancia a classe estatistica pra reaproveitas os calculos de média
        stats = Statistics(self.dataset)

        #Passa por cada coluna que foi selecionada
        for coluna in colunas_alvo:
            
            #Criando nova lista
            nova_lista = []

            dados_coluna = self.dataset[coluna]

            valores_validos = [v for v in dados_coluna if v is not None]

            if not valores_validos:
                continue

            #Cria uma coluna temporária com números válidos, para ser utilizado no método stats
            self.dataset['__coluna_temporaria__'] = valores_validos

            #Calcula a média e desvio padrao da coluna atual
            media = stats.mean('__coluna_temporaria__')
            desvio_padrao = stats.stdev('__coluna_temporaria__')

            #Apaga a coluna temporária
            del self.dataset['__coluna_temporaria__']

            #Percorre numero por numero da coluna
            for valor in dados_coluna:

                if valor is None:
                    nova_lista.append(None)
                else:
                    #Tratamento para evitar erro de divisao por 0 (caso os dados nao sejam variados) 
                    if desvio_padrao == 0:
                        novo_valor = 0.0
                    else:
                        #Aplica a fórmula do Z Score
                        novo_valor = (valor - media) / desvio_padrao

                    #Adiciona valor a lista nova
                    nova_lista.append(novo_valor)

            #Substitui a lista antiga pela nova
            self.dataset[coluna] = nova_lista

        return self.dataset

        

class Encoder:
    """
    Aplica codificação em colunas categóricas.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset

    def label_encode(self, columns: Set[str]) -> Dict[str, List[Any]]:
        """
        Converte cada categoria em uma coluna em um número inteiro.
        Modifica o dataset.

        Args:
            columns (Set[str]): Colunas categóricas para codificar.
        """
        for col in columns:
            if col not in self.dataset:
                continue
            dados_coluna = self.dataset[col]
            
            # 1. Isola as categorias únicas 
            valores_unicos = []
            for valor in dados_coluna:
                if valor not in valores_unicos:
                    valores_unicos.append(valor)

            # 2. Atribui um número para cada categoria de texto 
            mapeamento = {valor: indice for indice, valor in enumerate(valores_unicos)}
            
            # 3. Substitui os valores antigos pelos novos números na coluna
            self.dataset[col] = [mapeamento[valor] for valor in dados_coluna]
            
        return self.dataset        

    def oneHot_encode(self, columns: Set[str]) -> Dict[str, List[Any]]:
        """
        Cria novas colunas binárias para cada categoria nas colunas especificadas (One-Hot Encoding).
        Modifica o dataset adicionando e removendo colunas.

        Args:
            columns (Set[str]): Colunas categóricas para codificar.
        """
        for col in columns:
            if col not in self.dataset:
                continue
            dados_coluna = self.dataset[col]
            
            # 1. Identifica todas as categorias exclusivas da coluna
            valores_unicos = set(dados_coluna)
            
            # 2. Cria uma nova coluna para cada categoria exclusiva encontrada
            for valor_unico in valores_unicos:
                nome_nova_coluna = f"{col}_{valor_unico}"
                
                # Preenche com 1 onde a categoria coincide e 0 onde não coincide
                self.dataset[nome_nova_coluna] = [
                    1 if valor == valor_unico else 0 for valor in dados_coluna
                ]
            
            # 3. Exclui a coluna original, mantendo apenas as colunas binárias geradas
            del self.dataset[col]
            
        return self.dataset


class Preprocessing:
    """
    Classe principal que orquestra as operações de pré-processamento de dados.
    Nota: Todos os métodos retornam o dicionário de dados (dataset), 
    o que encerra a possibilidade de encadeamento de métodos da classe.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset
        self._validate_dataset_shape()
        
        self.statistics = Statistics(self.dataset)
        self.missing_values = MissingValueProcessor(self.dataset)
        self.scaler = Scaler(self.dataset)
        self.encoder = Encoder(self.dataset)

    def _validate_dataset_shape(self):
        """
        Valida se todas as listas (colunas) no dicionário do dataset
        têm o mesmo comprimento.
        """
        if not self.dataset:
            return
        
        tamanho_base = len(next(iter(self.dataset.values())))

        for col_name, col_data in self.dataset.items():
            if len(col_data) != tamanho_base:
                raise ValueError(f"As colunas têm tamanhos diferentes. Coluna '{col_name}' tem {len(col_data)} itens.")

    def isna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Atalho para missing_values.isna(). 
        Retorna um dicionário contendo apenas as linhas com valores nulos.
        """
        return self.missing_values.isna(columns)

    def notna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Atalho para missing_values.notna(). 
        Retorna um dicionário contendo apenas as linhas sem valores nulos.
        """
        return self.missing_values.notna(columns)

    def fillna(self, columns: Set[str] = None, value: Any = 0) -> Dict[str, List[Any]]:
        """
        Atalho para missing_values.fillna(). 
        Modifica e retorna o dicionário de dados com valores preenchidos.
        """
        return self.missing_values.fillna(columns, value)

    def dropna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Atalho para missing_values.dropna(). 
        Modifica e retorna o dicionário de dados sem as linhas nulas.
        """
        return self.missing_values.dropna(columns)

    def scale(self, columns: Set[str] = None, method: str = 'minMax') -> Dict[str, List[Any]]:
        """
        Aplica escalonamento e retorna o dicionário de dados modificado.

        Args:
            columns (Set[str]): Colunas para aplicar o escalonamento.
            method (str): O método a ser usado: 'minMax' ou 'standard'.

        Returns:
            Dict[str, List[Any]]: O dataset com as colunas escalonadas.
        """
        if method == 'minMax':
            return self.scaler.minMax_scaler(columns)
        elif method == 'standard':
            return self.scaler.standard_scaler(columns)
        else:
            raise ValueError(f"Método de escalonamento '{method}' não suportado.")

    def encode(self, columns: Set[str], method: str = 'label') -> Dict[str, List[Any]]:
        """
        Aplica codificação e retorna o dicionário de dados modificado.

        Args:
            columns (Set[str]): Colunas para aplicar a codificação.
            method (str): O método a ser usado: 'label' ou 'oneHot'.
        
        Returns:
            Dict[str, List[Any]]: O dataset com as colunas codificadas.
        """
        if method == 'label':
            return self.encoder.label_encode(columns)
        elif method == 'oneHot':
            return self.encoder.oneHot_encode(columns)
        else:
            raise ValueError(f"Método de codificação '{method}' não suportado.")