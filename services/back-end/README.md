# Backend skeleton

Esqueleto inicial do backend em Python 3.12 + FastAPI, organizado por camadas inspiradas no MASA:

- `domain_models`: entidades, IDs, contratos e exceções de domínio
- `engines`: regras puras encapsuladas em classes sem estado
- `services`: orquestração por caso de uso
- `integrations`: adapters para banco, vector store, object store e APIs externas
- `delivery`: handlers HTTP e schemas de entrada/saída
- `bootstrap`: wiring explícito por construtor

O primeiro corte privilegia:

1. nomes semânticos
2. classes explícitas
3. fronteiras claras entre camadas
4. stubs seguros para evoluir depois
