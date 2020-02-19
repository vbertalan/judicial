Para executar o script:

Abra o console e navegar atá a pasta onde se encontra o script e execute-o 

	python .\crawler.py

Para obter a lista de possíveis parâmetros de entrada execute o comando:

	python .\crawler.py -h

Exemplo de filtro: 

	python .\crawler.py --dataInicio="01/08/2018" --dataFim="11/08/2018" --assunto="Homicídio Simples"

O resultado será disponibilizado na mesma pasta em que o script se encontra com o nome: "resultado_pesquisa_ano_mes_dia_hora_minuto_segundo.csv"