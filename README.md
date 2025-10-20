# Desafio Unisoma — AURA - Chatbot baseado em RAG

Este projeto é uma pequena aplicação Flask que oferece um chatbot baseado em RAG (Retrieval-Augmented Generation). Ele usa documentos (TXT/PDF) para responder perguntas com contexto. Pensado para ser fácil de usar e entender.

Principais pontos
- Backend em Flask (porta padrão 5001).
- Chatbot com embeddings + vectorstore em memória.
- Adição de arquivos (temporária ou persistente) para enriquecer a base de conhecimento.
- Histórico por sessão (até 10 interações).

Pré-requisitos
- Python 3.10+ (recomendado)
- Conta/Chave OpenAI válida

Executando
- Rodar o executável (se for o caso)
- Basta colar a chave da OpenAI no local designado. Então clicar no link gerado.
- Iniciar servidor:
  python app.py
- A aplicação roda em http://0.0.0.0:5001/ (ou http://localhost:5001).

O que tem na interface
- Página principal (/) com campo de busca.
- Página de chat (/chat) com histórico de conversa na sessão.
- Upload de arquivos pela interface (ou API) para enriquecer a base.

Endpoints úteis (API)
- POST /api/chat
  - Body JSON: { "message": "sua pergunta" }
  - Retorna resposta do chatbot e fontes (se houver).
- POST /api/search
  - Mesmo formato de /api/chat, pensado para a página principal.
- POST /api/upload
  - Envia multipart/form-data com campo `file`.
  - Campo opcional `save_to_default`: '1' para salvar em `arquivos_ong/` (persistente). Se omitido, o arquivo é adicionado temporariamente.
- POST /api/clear-history
  - Limpa o histórico da sessão atual.
- POST /api/contact
  - Envia formulário de contato (nome, email, mensagem).

Exemplos rápidos (curl)
- Chat:
  curl -X POST http://localhost:5001/api/chat -H "Content-Type: application/json" -d '{"message":"Olá"}'
- Upload (salvar na pasta arquivos_ong):
  curl -X POST http://localhost:5001/api/upload -F "file=@./meuarquivo.pdf" -F "save_to_default=1"

Arquivos salvos
- Quando `save_to_default=1`, arquivos são salvos em `arquivos_ong/` e indexados.
- Uploads temporários são adicionados apenas à vectorstore em memória.

Notas e dicas
- A primeira vez que o app roda, ele tenta indexar arquivos encontrados em `arquivos_ong/`. Pode demorar se houver muitos PDFs.
- Limite de histórico por sessão: 10 interações (configurado no app).
- Se faltar a variável OPENAI_API_KEY o app vai falhar.

Estrutura principal
- app.py — servidor Flask e rotas.
- chatbot.py — lógica do RAG, leitura de arquivos e vectorstore.
- templates/ — páginas HTML (index, chat).
- static/ — CSS/JS/imagens.
- arquivos_ong/ — (opcional) pasta para documentos persistentes.



