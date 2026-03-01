class Statistics:
    """
    Uma classe para realizar cálculos estatísticos em um conjunto de dados.

    Atributos
    ----------
    dataset : dict[str, list]
        O conjunto de dados, estruturado como um dicionário onde as chaves
        são os nomes das colunas e os valores são listas com os dados.
    """
    def __init__(self, dataset):
        """
        Inicializa o objeto Statistics.

        Parâmetros
        ----------
        dataset : dict[str, list]
            O conjunto de dados, onde as chaves representam os nomes das
            colunas e os valores são as listas de dados correspondentes.
        """
        self.dataset = dataset

    def mean(self, column):
   
        # 1. Puxa os dados da coluna do dataset
        data = self.dataset[column]
      
        # 2. Evita que haja uma divisão por zero, caso não haja dados
        if not data:
            return 0
        
        # 3. Soma os dados e divide pela quantidade
        return sum(data) / len(data)

    def median(self, column):
      
       # 1. Cria uma cópia ordenada dos dados listados para não mudar os originais
        if column == "priority":
            priority_map = {"baixa": 0, "media": 1, "alta": 2}
            data = sorted(self.dataset[column], key=lambda k: priority_map.get(k, 0))
        else:
            data = sorted(self.dataset[column])

        n = len(data)
        
        if n == 0:
            return None

        # Encontra o índice do meio
        mid_index = n // 2

        # 2. Verifica se a quantidade de itens é ímpar ou par
        if n % 2 == 1:
            # Ímpar: Retorna o valor do centro
            return data[mid_index]
        else:
            # Se for Par: Calcula a média dos dois dados do centro
            val1 = data[mid_index - 1]
            val2 = data[mid_index]
            
            # 3. Verifica se os dados são numeros para calcular a média 
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                return (val1 + val2) / 2
            else:
                # Se for texto 
                return val1
        

    def mode(self, column):
      
        data = self.dataset[column]
        counts = {}

        # 1. Vê quantos vezes o dado aparece 
        for item in data:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1
        
        # 2. Descobre qual foi a maior quantidade que apareceu
        if not counts:
            return []
            
        max_count = max(counts.values())

        # 3. Retorna todos os daos que tiverem essa mesma quantidade de aparições
       
        return [key for key, value in counts.items() if value == max_count]

    def variance(self, column):
      
        values = self.dataset[column]
        n = len(values)

        #Calcula a média aritmética para usar como centro de referencia
        mean_val = sum(values) / n

        #Acumula  a soma dos quadrados dos desvios em relaçao a média
        variance_acumulator = 0
        for x in values:
            variance_acumulator += (x - mean_val) ** 2 
        
        #Divide pelo total de elementos para obter a variancia populacional
        variance_value = variance_acumulator / n
       
        return variance_value

    def stdev(self, column):
       
        values = self.dataset[column]

        if len(values) == 0:
            return 0.0

        #Chama a função da variância e descobre a raiz quadrada dela 
        return self.variance(column) ** 0.5
    
    def covariance(self, column_a, column_b):
      
        #Pega os dados de duas colunas e conta os itens
        values_a = self.dataset[column_a]
        values_b = self.dataset[column_b]
        n = len(values_a)

        #Verifica se as duas colunas tem o mesmo tamanho
        if n != len(values_b):
            raise ValueError("As colunas devem ter o mesmo tamanho")
        
        if n < 2:
            return 0.0
        
        #Chama a função da Média
        mean_a = self.mean(column_a)
        mean_b = self.mean(column_b)

        sum_products = 0

        #Passa por todos os itens e verifica o quão longe os valores estão da media
        for i in range(n):
            diff_a = values_a[i] - mean_a
            diff_b = values_b[i] - mean_b

            sum_products += diff_a * diff_b
        
        return sum_products / (n - 1)
    
    def itemset(self, column):
       
        values = self.dataset[column]
        itemset = set(values)        

        return itemset

    def absolute_frequency(self, column):
        
        #Pega a lista de dados da coluna e cria um dicionario vazio para os resultados
        values = self.dataset[column] 
        frequency = {}

        #Roda item por item para saber quantas vezes eles aparecem  
        for item in values:
            if item in frequency:
                frequency[item] += 1
            else:
                frequency[item] = 1

        return frequency    

    def relative_frequency(self, column):
        
        #Chama a função de cima para pegar as contagens e olha o total
        abs_freq = self.absolute_frequency(column)
        total_itens = len(self.dataset[column])

        rel_freq = {}

        #Pega o dicionário e separa o nome do item da quantidade
        for item, count in abs_freq.items():
            rel_freq[item] = count / total_itens
        
        return rel_freq

    def cumulative_frequency(self, column, frequency_method='absolute'):
       
        #Decide se a base usada será relativa ou absoluta
        if frequency_method == 'relative':
            base_data = self.relative_frequency(column)
        else: 
            base_data = self.absolute_frequency(column)

        #Caso a coluna for "priority" ela não pode ser ordenada alfabeticamente
        if column == "priority":
            priority_map = {"baixa": 0, "media": 1, "alta":2}

            sorted_keys = sorted(base_data.keys(), key=lambda k: priority_map.get(k, 0))
        else: 
            sorted_keys = sorted(base_data.keys())

        cumulative = {}
        current_sum = 0

        #Roda item po item e acumula o valor
        for key in sorted_keys:
            current_sum += base_data[key]
            cumulative[key] = current_sum
        
        return cumulative
    
    def conditional_probability(self, column, value1, value2):
    
        if column not in self.dataset:
            raise ValueError("Coluna não encontrada no dataset.")

        values = self.dataset[column]

        if len(values) < 2:
            return 0.0 # Ou raise, dependendo da sua preferência

        count_b = 0
        count_ba = 0

        # Percorre os pares (atual, próximo)
        for current, next_val in zip(values[:-1], values[1:]):
            if current == value2:
                count_b += 1
                if next_val == value1:
                    count_ba += 1

        if count_b == 0:
            # Em vez de erro, é comum retornar 0.0 ou None em estatística
            # Mas manteremos o erro se for uma regra de negócio sua
            raise ValueError(f"O valor condicionante '{value2}' não ocorre na sequência.")

        return count_ba / count_b
    

    def quartiles(self, column):
      
        #Ordena os valores para aplicar a lógica de divisao por posicao
        values = sorted(self.dataset[column])
        n = len(values)
        mid = n // 2

        #Divide a lista em metade inferior e metade superior, e calcula o Q2 (mediana)
        #Para n par: Q2 é a média dos dois elementos centrais
        #Para n impar:Q2 é o elemento do meio, excluido das metades
        if n % 2 == 0:
            metInferior = values[:mid]
            metSuperior = values[mid:]
            Q2 = (values[mid - 1] + values[mid]) / 2
        else:
            metInferior = values[:mid]
            metSuperior = values[mid+1:]
            Q2 = values[mid]


        #Aplica mesma lógica acima, agora na metade inferior
        nInferior = len(metInferior)
        midIndexQ1 = nInferior // 2
        if nInferior % 2 == 0:
            Q1 = (metInferior[midIndexQ1 - 1] + metInferior[midIndexQ1]) / 2
        else:
            Q1 = metInferior[midIndexQ1]

        #Aplica a mesma lógica acima, agora na metade superior
        nSuperior = len(metSuperior)
        midIndexQ3 = nSuperior // 2
        if nSuperior % 2 == 0:
            Q3 = (metSuperior[midIndexQ3 - 1] + metSuperior[midIndexQ3]) / 2
        else:
            Q3 = metSuperior[midIndexQ3]

        #Retorna como dicionário
        return {"Q1": Q1, "Q2": Q2, "Q3": Q3}
            
    def histogram(self, column, bins):
      
        values = self.dataset[column]

        #Define o alcance dos dados e calcula a largura de cada intervalo
        min_values = min(values)
        max_values = max(values)
        width_value = (max_values - min_values) / bins

        #Inicializa os contadores de cada bin com zero
        contadoresBins= [0] * bins

        for x in values:
            #Calcula em qual bin o valor se encaixa pela sua posiçao relativa ao mínimo
            #O min() garante que o valor máximo caia no último bin e nào fora do intervalo
            index = min(int((x - min_values) / width_value), bins - 1)
            contadoresBins[index] += 1

        #Monta o dicionário final associando cada intervalo (tupla) a sua contagem
        dictIntervalos = {}
        for x in range(bins):
            inicioIntervalo = min_values + width_value * x
            fimIntervalo = inicioIntervalo + width_value
            intervaloTotal = (inicioIntervalo, fimIntervalo)
            dictIntervalos[intervaloTotal] = contadoresBins[x]
       
        return dictIntervalos
    
