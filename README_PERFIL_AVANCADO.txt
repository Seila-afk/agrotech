PERFIL AVANÇADO - HUNGRELESS

Arquivos alterados:
- app.py
- perfil.html

O que foi adicionado:
- Campos novos no perfil: e-mail, cidade, estado, tipo de produção, tamanho da propriedade, experiência, foto e bio.
- API com GET /usuarios, GET /usuarios/<id>, POST /usuarios e PUT /usuarios/<id>.
- Migração automática do SQLite: se o banco antigo não tiver as colunas novas, o app.py cria as colunas sem apagar seus dados.
- O perfil continua salvando no localStorage para manter compatibilidade com as outras páginas.

Como rodar:
1. pip install -r requirements.txt
2. python app.py
3. Abra perfil.html no navegador.

A API deve responder em:
http://localhost:5000
