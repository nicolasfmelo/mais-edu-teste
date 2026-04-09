## Steps iniciais

 - Avaliação da proposta
 - Avaliar Dados (20 samples)

## anotações
 - Basicamente a proposta é um NPS
 - O operador é uma IA
 - Definir regras de metrificação (começar com satisfação do usuário)
 - Definir regra de satisfação (Se o operador ficou satisfeito com o atendimento)
 - identificar 'alterações comportamentais'
 - perspectiva de atendimento é com base na visão cliente
 - verificar esforço do cliente para o operador entregar o que ele pediu
 - verificar objetivo da conversa proposta pelo cliente ( o que ele busca)
 - verificar se é comum os clientes agradecerem ou reclamar no final da conversa (isso ajuda a direcionar se a 'atividade' foi completada com sucesso)
 - Dados extras, quais cursos mais 'buscados' 
 - melhorias na qualidade das respostas dos clientes (muita abreviação, isso impacta em prompt)
 - identficar possíveis prompt injection
 - identificar numero de tokens médios / cliente e tokens médios / ia
 - 1 user pode ter várias sessões
 - tratar drifting


## Dúvidas
 - Quantos clientes usam a solução?
 - Transferências considerar como concluído ou não ? (assumirei que sim)

## Proposta Inicial
 - Linguagem Python (devido a não necessidade explícita de performance massiva) e Typescript para front
 - framewoks, Langchain+Langgraph (melhor controle de fluxo do mercado)
 - DB Postgres (Facilidade, Estabilidade, Aceita Vetores e JsonB)
 - Front-end para dashboard e outras funcionalidades (Bun, Typescript, React e Shadcn)
 - Docker para virtualização (buildar com base em imagens alpine)

## Escala
 - considerar inicialmente após os calculos de tokens/req de usuários, a cada 1000 usuários com N requisições.

 - montar uma proposta pra uns 10mil usuários incialmente, e depois pensar em hiper escalas (aqui já vou de orientado a eventos)


## Cobertura de testes
 - testes unitários
 - testes integrados (happy path e wrong path)
 - testes end-to-end
 - testes de carga


## Inferencia
 - Uso de LLM para inferenciar (devido a solução de ML requerer datasets)
 - Testar com LLM e SLM (buscar melhor custo e benefício)
 - Fazer uns testes com Whisper para transcrição

## Arquitetura
 - Montar desenho inicial
 - Calculadora de cloud (escolher alguma das 3 grandes)
 - Arquitetura de código (para manutenção contínua, desacoplamento e implementações futuras)
 - Cloud Buscar o que fornece estabilidade, facilidade de manutenção contínua e menor custo.

## Observabilidade e LLMOps
 - Logs e Tracing com OTEL e Clickhouse ?
 - Loki e Prometheus ?
 - Visualização com Grafana
 - Tokens por minuto
 - Latencia
 - Tokens por request
 - Tokens por usuário
 - planejar esteira de drifting
 - Batch Process (baixa custo pra caramba)
 - Esteira de anotação
 - Esteira de prompt engineering
 - Métricas de Desempenho (métricas do negócio)


## Para replicar
 - isso vai ser chatinho, vou pensar em um gerador de chave de API baseado em senha já que precisa reproduzir nas mesmas condições que eu testei.
 - limitar até 5 testers com N requisições?
 - mandar a senha pro RH ^^


## Emulação
 - vou tentar emular o whatsapp ^^ (montar 2 soluções)


## Considerações
 - Duas linguagens podem ser útil, Go ou Python para o backend.
 - Necessidade de Microserviços, devido a equipes distintas normalmente a melhor saída é microserviços.
 - Monolito modular muito raro a necessidade


## drafts
 - MinIO ? aponta as transcrições pra lá (isso facilita escala e não arrebenta com o DB claro que no longo prazo ^^)
 - Autenticação (Basic auth ou JWT)
 - Abordar a pipe completa? até metodologia do desenvolvimento? esteira de devops?