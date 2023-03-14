# Previsão de Vendas - Farmácias Rossmann

- A Rossmann é uma rede de farmácias de origem Alemã e possui mais de 3.000 lojas em 7 países da Europa e cerca de 56 mil colaboradores. Durante uma reunião mensal para apresentação de resultados e acompanhamento de métricas, o CFO informou que as lojas serão reformadas para melhorar a estrutura das lojas e atender melhor o público. No entanto, é válido ressaltar que cada loja possui características distintas que influenciam diretamente na possível quantia investida na reforma (sazonalidade, localidade, feriados, etc). Dessa forma, para saber quanto destinar de orçamento para cada loja, ele gostaria da previsão de vendas de cada loja para as próximas 6 semanas.
- É fundamental, portanto, possibilitar o acesso às previsões por parte do CFO. Nesse sentido, um mecanismo desenvolvido durante o projeto foi um Bot do aplicativo Telegram.

# Tópicos iniciais:

## 0.1. Questão de Negócio:
- Realizar a previsão de vendas por cada loja para as próximas 6 semanas.

## 0.2. Entendimento do Negócio:
- Dificuldade do CFO em determinar a quantidade de dinheiro necessária para investir na reforma das lojas --> Causa Raiz do problema.

## 0.3 Premissas do Negócio:
- A consulta da previsão de vendas estará disponível 24/7, e será acessível via aplicativo do Telegram, onde o CFO digitará o código da loja, e como resposta, receberá o valor da previsão para as próximas 6 semanas.
- Foram consideradas para a previsão apenas as lojas que possuiam o valor de vendas superior a 0 na base de dados.
- Os dias em que as lojas estavam fechadas foram descartadas na realização da previsão.
- Lojas que não possuíam dados de competidores próximos tiveram o valor da distância fixada em 200.000 metros.
- O conjunto de dados contém as vendas realizadas entre 01/01/2013 e 31/07/2015.

## 0.4 Descrição de Variáveis:

## 0.5 Método de Solução:
