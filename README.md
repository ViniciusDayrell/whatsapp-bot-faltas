# WhatsApp Bot Faltas

Bot em Python que envia mensagens automaticamente pelo WhatsApp para alunos que faltaram no dia, usando a planilha de presença como base.

## Por que eu fiz isso

Trabalho como instrutor e, todo dia, o processo para entrar em contato com alunos faltosos era abrir o WhatsApp, procurar o contato, escrever a mensagem, mandar, repetir pro próximo aluno. Nada complicado, mas chato e repetitivo — e automação é basicamente isso: tirar do seu dia o trabalho que não precisa de você pensando nele.

## Como funciona, na prática

1. Lê a planilha de presença (`.xls`) que o sistema do trabalho gera.
2. Pra cada aluno com falta, pega nome e telefone.
3. Normaliza o telefone pro formato que o WhatsApp Web espera (usando a lib `phonenumbers`, porque planilha de sistema legado vem com telefone de todo jeito: com DDD, sem DDD, com espaço, sem espaço).
4. Monta um link do WhatsApp Web já com o número e a mensagem preenchidos.
5. Abre esse link no navegador.
6. Espera a página carregar, procura o botão de enviar na tela (reconhecimento de imagem com pyautogui) e clica.
7. Fecha a aba e vai pro próximo aluno.

Se não conseguir localizar o botão (WhatsApp não carregou, número inválido, etc.), ele não trava — só registra o problema num `erros.csv` e segue pro próximo.

## Sobre o formato .xls (e por que não usei openpyxl)

Isso mereceu destaque porque não foi uma escolha, foi uma limitação que tive que contornar.

O sistema de presença que uso no trabalho só exporta relatório em `.xls` (o formato antigo do Excel, pré-2007). Não tem opção de exportar em `.xlsx`. E aí esbarrei num problema: a lib mais usada hoje pra mexer com planilha em Python, a `openpyxl`, **não lê `.xls`** — só `.xlsx`. Ela simplesmente não foi feita pra isso.

A solução foi usar a `xlrd`, que ainda tem suporte a `.xls`. Porém, a partir da versão 2.0 da `xlrd`, também foi retirado o suporte a `.xls` e deixaram só `.xlsx` (o que meio que inverteu os papéis das duas libs). Por isso no `requirements.txt` a versão está travada em `xlrd==1.2.0` — é a última versão que ainda lê o formato antigo. Sem isso travado, quem for instalar do zero vai pegar a versão mais nova e o código quebra sem motivo aparente.

## O que mais deu trabalho

- **Telefone bagunçado na planilha**: usei a lib `phonenumbers` pra normalizar tudo pro padrão internacional (E.164), porque sem isso o link do WhatsApp simplesmente não abre a conversa certa.
- **Confundir o botão de enviar com o botão de "nova conversa"**: os dois são círculos verdes parecidos. Com confidence baixo, o reconhecimento às vezes clicava no botão errado. Resolvi restringindo a busca a uma região específica da tela (canto onde a seta de enviar sempre fica) em vez de deixar buscar a tela inteira.
- **Escala de tela do Windows**: se o Windows está em 125%/150% de escala, o recorte da imagem salvo não bate mais em tamanho com o que aparece na tela, então o reconhecimento falha mesmo com o botão bem na frente.

## Rodando o projeto

```bash
git clone https://github.com/SEU_USUARIO/whatsapp-bot-faltas.git
cd whatsapp-bot-faltas
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Coloque sua planilha de presença na pasta (o formato esperado está em `alunos_exemplo.xls`, com colunas `Nome Aluno` e `Telefone Aluno`), deixe o WhatsApp Web logado no navegador padrão, e roda:

```bash
python app.py
```

Não tem parâmetro de linha de comando — as configurações (nome do arquivo, texto da mensagem) ficam direto no `app.py`.

## Sobre os dados

Os arquivos de exemplo (`alunos_exemplo.xls`) têm nomes e telefones fictícios, só pra mostrar o formato que a planilha precisa ter. Dado real de aluno não entra nesse repositório — isso já está garantido no `.gitignore`.

## O que ainda quero melhorar

- Log melhor de quem não recebeu a mensagem, pra eu saber quem precisa de reenvio manual sem precisar abrir o `erros.csv` e procurar.
- Confirmar de verdade que a mensagem saiu, não só que o clique aconteceu.
- Trocar o reconhecimento de imagem pela API oficial do WhatsApp Business em algum momento, pra parar de depender de posição de tela.

## Limitações

Só testei em Windows. Depende de reconhecimento visual, então qualquer mudança no layout do WhatsApp Web ou zoom do navegador pode quebrar o clique.

## Licença

MIT — veja o arquivo LICENSE.
