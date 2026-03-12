<div align="center">
  <img src="https://img.icons8.com/color/96/000000/bot.png" width="80" alt="Bot Icon"/>
  <h1>🤖 AutomateHub - Reddit Scraper & Email Notifier</h1>
  <p><i>Um laboratório de aprendizado contínuo sobre automações e IA.</i></p>
</div>

---

## 🚀 Sobre o Projeto

Este projeto nasceu de um desejo de explorar e testar o mundo das automações baseadas em dados e inteligência artificial. Trabalhando em colaboração **eu (Gabriel)** e a IA **(Antigravity / Google)**, desenvolvemos esta ferramenta interativa em Python. 

A ideia principal era simples, porém poderosa: **"Como extrair automaticamente o melhor conteúdo do Reddit todos os dias, gerar um painel bonito na minha máquina, e me enviar esses insights por e-mail?"**

O que começou como um laboratório de aprendizado e testes, evoluiu para essa ferramenta totalmente funcional.

---

## 🛠️ Como Funciona?

O fluxo da automação foi dividido em camadas lógicas:
1. **Python `scrape_reddit.py`**: Acessa os subreddits desejados (como `r/n8n`), raspa os 100 posts mais recentes e usa um algoritmo para classificar "O que bombou mais hoje" cruzando *Likes* e *Comentários*.
2. **Python `generate_dashboard.py`**: Pega esses dados brutos do Reddit e injeta em um template HTML dinâmico hiper-responsivo e cheio de gradientes.
3. **HTML / EmailJS `send_email.py`**: O painel HTML abre automaticamente. De lá posso selecionar os posts que quero ler depois e apertar um botão que dispara um E-mail bonito, formatado em HTML (com uma estética super clean) diretamente na minha Caixa de Entrada através da API REST do EmailJS.

---

## 💻 Como executar (Setup)

Caso queira rodar a automação localmente, aqui está o passo a passo que definimos:

### 1. Pré-Requisitos
Você precisará ter o Python instalado na sua máquina.

Vá no terminal da pasta do projeto e instale as bibliotecas que usamos:
```bash
pip install praw python-dotenv requests
```

### 2. Configurando Segredos
Como construímos o sistema seguindo boas práticas de segurança, nenhuma de nossas chaves foi enviada para o GitHub. Para rodar, você precisará criar um arquivo `.env` na pasta raiz do projeto com o seguinte formato:

```env
# Variáveis do Reddit (Você precisa criar um app no Reddit Dev)
REDDIT_CLIENT_ID=sua_chave_reddit_aqui
REDDIT_CLIENT_SECRET=seu_secret_reddit_aqui
REDDIT_USER_AGENT=sua_descricao_do_app

# Variáveis do EmailJS (Crie uma conta gratuita no EmailJS)
EMAILJS_SERVICE_ID=seu_service_id_aqui
EMAILJS_TEMPLATE_ID=seu_template_id_aqui
EMAILJS_PUBLIC_KEY=sua_public_key_aqui
EMAILJS_PRIVATE_KEY=sua_private_key_opcional_aqui
```

### 3. Executando a Máquina

Com tudo pronto, é só alegria! No Windows, usamos um script `.bat` para rodar todos os passos sequencialmente e já abrir o Dashboard automaticamente:

```bash
.\run_automation.bat
```

Se for no Mac/Linux:
```bash
python execution/scrape_reddit.py
python execution/generate_dashboard.py
python execution/generate_log_viewer.py
open reddit_dashboard.html
```

---

<div align="center">
  <p>Construído por <b>Gabriel</b> & <b>Antigravity AI</b> 🪐 - 2026</p>
</div>