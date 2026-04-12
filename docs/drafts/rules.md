# Regras iniciais de metrificação da IA operadora

## Objetivo

Definir uma régua de avaliação com lógica parecida com NPS, mas aplicada à **qualidade percebida pelo cliente** em conversas com a IA operadora.

 - **Criação de um agente de análise e ferramentas auxiliares para contagem**
 - **O Agent irá usar uma tabela para processar os arquivos da conversa que está em um json no minio**

O foco principal desta avaliação é:

1. **Satisfação do cliente**
2. **Esforço exigido do cliente para chegar ao que queria**
3. **Capacidade da IA operadora de entender o objetivo da conversa**
4. **Capacidade da IA operadora de conduzir a conversa até uma conclusão útil**
5. **Mudanças comportamentais do cliente ao longo da sessão**
6. **Token usage por análise**
7. **Token usage no longo do tempo**

> Regra central: a leitura da conversa deve ser feita **pela perspectiva do cliente**, não pela perspectiva da IA operadora.

---

## Unidade de análise

A unidade padrão de avaliação é a **sessão** (`sessionId`).

Cada sessão deve gerar:

- uma classificação principal de satisfação (`ruim`, `neutro`, `bom`) com label map (`1-3`)
- métricas auxiliares de diagnóstico
- evidências textuais curtas que justifiquem a nota

---

## Métrica principal: satisfação do cliente

### Definição

A satisfação deve refletir se o cliente sentiu que:

- foi compreendido
- avançou no que buscava
- teve baixo atrito
- recebeu resposta útil ou encaminhamento coerente

### Classificação de satisfação (`ruim`, `neutro`, `bom`)

| Valor | Classe | Regra prática |
| --- | --- | --- |
| 3 | Bom | Cliente atingiu o objetivo ou aceitou claramente o próximo passo; a conversa fluiu com baixo atrito |
| 2 | Neutro | Houve progresso, mas com pequenas fricções, lacunas ou conclusão parcial |
| 1 | Ruim | Cliente precisou insistir, corrigir a IA operadora, repetir contexto, saiu sem resposta útil ou demonstrou frustração |

### Como inferir satisfação

Sinais fortes de **alta satisfação**:

- cliente agradece de forma espontânea e coerente com resolução
- cliente confirma que vai seguir o próximo passo proposto
- cliente para de pedir esclarecimentos porque a resposta foi suficiente
- IA operadora entende rapidamente o objetivo e não força desvios

Sinais fortes de **baixa satisfação**:

- cliente precisa repetir ou corrigir informações já dadas
- IA operadora responde algo desalinhado com o que foi pedido
- IA operadora insiste em fluxo inadequado ou faz perguntas que já foram respondidas
- cliente demonstra irritação, impaciência, confusão ou abandono
- a conversa termina sem resolução prática e sem encaminhamento claro

### Observação importante

**Agradecimento no fim ajuda, mas não fecha a avaliação sozinho.**  
Há clientes educados que agradecem mesmo sem terem sido bem atendidos.

---

## Cálculo resumido da operação

Depois de classificar cada sessão:

`INDICE_IA_OPERADORA = % bom - % ruim`

Onde:

- **bom** = sessões classificadas como `bom`
- **neutro** = sessões classificadas como `neutro`
- **ruim** = sessões classificadas como `ruim`

Esse indicador resume a experiência geral da operação em uma lógica inspirada em NPS, mas **não substitui** as métricas auxiliares.

---

## Métricas auxiliares

### 1. Esforço do cliente

### Pergunta que a métrica responde

Quanto trabalho o cliente precisou fazer para a IA operadora entregar o que ele queria?

### Escala sugerida (`1 a 5`)

| Nota | Interpretação |
| --- | --- |
| 1 | Muito baixo esforço |
| 2 | Baixo esforço |
| 3 | Esforço moderado |
| 4 | Alto esforço |
| 5 | Muito alto esforço |

### Sinais de alto esforço

- cliente reformula a mesma intenção várias vezes
- cliente reenvia resposta por falha de entendimento da IA operadora
- cliente precisa explicar contexto básico repetidamente
- IA operadora faz perguntas desnecessárias antes de responder algo simples
- cliente quer uma informação objetiva e recebe desvio excessivo

### Regra prática

Quanto mais o cliente precisar **corrigir, repetir, insistir ou simplificar** o pedido para ser entendido, maior o esforço.

---

### 2. Entendimento do objetivo da conversa

### Pergunta que a métrica responde

A IA operadora entendeu corretamente o que o cliente buscava?

### Escala sugerida (`0 a 2`)

| Nota | Interpretação |
| --- | --- |
| 2 | Entendeu corretamente e cedo |
| 1 | Entendeu parcialmente ou tarde |
| 0 | Não entendeu ou desviou a conversa |

### Exemplos de objetivo do cliente

- descobrir qual curso faz sentido
- entender grade / formato / cronograma
- saber valor
- comparar cursos
- avançar para matrícula

### Regra prática

O objetivo deve ser inferido a partir da **intenção dominante do cliente**, não apenas da última mensagem isolada.

---

### 3. Resolução ou avanço útil

### Pergunta que a métrica responde

A sessão terminou com progresso real para o cliente?

### Escala sugerida (`0 a 2`)

| Nota | Interpretação |
| --- | --- |
| 2 | Objetivo resolvido ou próximo passo claro e aceito |
| 1 | Avanço parcial |
| 0 | Sem avanço útil |

### Regras

- Se o cliente pediu uma informação que a IA operadora podia responder e respondeu bem, marcar alto.
- Se a IA operadora não podia responder diretamente, mas explicou a limitação e fez encaminhamento coerente, marcar parcial ou alto conforme a aceitação do cliente.
- Se houve transferência prematura, repetitiva ou sem adesão do cliente, marcar baixo.

### Regra especial para transferência

Transferir para humano **não é ruim por si só**.  
É ruim quando:

- acontece cedo demais
- substitui uma resposta que a IA operadora já poderia ter dado
- é repetida mesmo após resistência do cliente
- quebra o fluxo em vez de ajudar

---

### 4. Mudanças comportamentais do cliente

### Objetivo

Detectar se o comportamento do cliente melhorou, piorou ou permaneceu estável ao longo da sessão.

### Classificação sugerida

| Classe | Interpretação |
| --- | --- |
| Positiva | Cliente ficou mais engajado, objetivo ficou mais claro, aceitou avançar |
| Neutra | Comportamento estável, sem sinais claros de melhora ou piora |
| Negativa | Cliente ficou confuso, frustrado, cansado ou interrompeu o avanço |

### Sinais de mudança positiva

- começa vago e termina objetivo
- passa de exploratório para decisão
- aceita matrícula, transferência ou análise de material
- passa a responder de forma mais confiante e específica

### Sinais de mudança negativa

- começa colaborativo e depois corrige a IA operadora
- demonstra que a IA operadora não leu ou não entendeu mensagens anteriores
- perde interesse ou encerra sem avanço
- explicita desconforto, impaciência ou quebra de confiança

---

### 5. Sinal de fechamento da conversa

O final da conversa deve ser lido como um sinal complementar de sucesso.

### Indicadores positivos

- agradecimento espontâneo
- confirmação de próximo passo
- aceite de transferência
- aceite de matrícula
- promessa de retorno com contexto coerente

### Indicadores negativos

- reclamação explícita
- correção da IA operadora no fechamento
- abandono após atrito
- silêncio após proposta desalinhada
- resposta curta com tom de desgaste

### Regra prática

O fechamento só deve elevar a nota quando estiver **coerente com o restante da sessão**.

---

## Peso sugerido das métricas

Para uma nota composta da sessão:

| Métrica | Peso |
| --- | --- |
| Satisfação do cliente | 40% |
| Esforço do cliente | 20% |
| Entendimento do objetivo | 20% |
| Resolução / avanço útil | 20% |

> Mudança comportamental deve funcionar como **ajuste qualitativo**, não necessariamente como peso fixo na primeira versão.

---

## Regras de anotação

Cada sessão deve ser anotada com os seguintes campos:

| Campo | Descrição |
| --- | --- |
| `session_id` | Identificador da conversa |
| `objetivo_cliente` | O que o cliente buscava principalmente |
| `satisfacao` | Classificação principal: Ruim / Neutro / Bom |
| `satisfacao_label` | Label map da satisfação: 1 = Ruim, 2 = Neutro, 3 = Bom |
| `classe_resumo` | Ruim / Neutro / Bom |
| `esforco_1_5` | Quanto esforço o cliente teve |
| `entendimento_objetivo_0_2` | Se a IA operadora entendeu corretamente |
| `resolucao_0_2` | Se houve avanço útil |
| `mudanca_comportamental` | Positiva / Neutra / Negativa |
| `sinal_fechamento` | Positivo / Neutro / Negativo |
| `evidencias` | Trechos curtos da conversa que justificam a avaliação |

---

## Heurísticas práticas observadas nos exemplos

Pelos exemplos analisados, alguns padrões devem derrubar nota:

1. **Perguntar algo já respondido pelo cliente**
2. **Duplicar resposta ou responder duas vezes no mesmo ponto**
3. **Trocar o contexto do cliente por outro tema próximo, mas incorreto**
4. **Insistir em transferência quando o cliente quer apenas informação objetiva**
5. **Não reconhecer correções explícitas do cliente**

E alguns padrões devem elevar nota:

1. **Capturar rápido o contexto profissional do cliente**
2. **Relacionar o curso ao objetivo declarado**
3. **Ser transparente quando não puder informar algo**
4. **Encaminhar para próximo passo coerente com o momento da conversa**

---

## Regra operacional inicial

Se for preciso começar simples, usar esta ordem:

1. Identificar o **objetivo principal do cliente**
2. Avaliar se a IA operadora **entendeu esse objetivo**
3. Avaliar quanto **esforço** o cliente precisou fazer
4. Avaliar se houve **resolução ou avanço útil**
5. Classificar a **satisfação** em **ruim, neutro ou bom**

---

## Primeira hipótese de leitura

Nesta fase inicial, a melhor aproximação de um “NPS da IA operadora” é:

**“o quanto a conversa fez o cliente sentir que avançou com clareza, pouco atrito e com aderência ao que ele realmente buscava.”**

Essa hipótese pode ser refinada depois com:

- pesos calibrados em amostra anotada
- comparação entre anotadores
- separação por tipo de intenção (`informação`, `comparação`, `matrícula`, `transferência`)
- criação de rubricas mais duras para casos de erro de contexto e repetição
