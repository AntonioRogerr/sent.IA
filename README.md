# Sent.IA - Análise de Sentimento com IA

*Página principal para upload de arquivos.*

**Sent.IA** é uma aplicação web completa projetada para analisar o sentimento de feedbacks de clientes em massa. A ferramenta utiliza um modelo de linguagem rodando localmente via Ollama para classificar textos como positivos, negativos ou neutros, e apresenta os resultados em um dashboard interativo e visual.

## ✨ Principais Funcionalidades

  * **Análise de Sentimento:** Classifica o sentimento de textos usando um modelo de IA local (Ollama com Gemma:2b), garantindo privacidade e controle total sobre os dados.
  * **Upload Flexível:** Suporte para upload de arquivos nos formatos **CSV** e **JSON**, permitindo fácil integração com diferentes fontes de dados.
  * **Dashboard Interativo:** Visualize os dados analisados com estatísticas claras, gráficos de distribuição de sentimentos e uma tabela detalhada dos feedbacks.
  * **Filtragem Avançada:** Filtre os resultados por sessão de análise, sentimento ou área/produto específico para obter insights mais granulares.
  * **Exportação de Dados:** Exporte os dados filtrados do dashboard para **CSV** ou **JSON** com um único clique.
  * **Exportação de Gráficos:** Salve o gráfico de distribuição de sentimentos como uma imagem PNG, com informações de contexto da análise.
  * **Ambiente Containerizado:** Toda a aplicação é executada em contêineres Docker, simplificando a configuração e a implantação.

## 🚀 Tecnologias Utilizadas

  * **Backend:** Django
  * **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
  * **Banco de Dados:** PostgreSQL
  * **Análise de IA:** Ollama (rodando o modelo Gemma:2b)
  * **Containerização:** Docker e Docker Compose
  * **Visualização de Dados:** Chart.js

## ⚙️ Como Executar o Projeto Localmente

### Pré-requisitos

  * [Docker](https://www.docker.com/get-started)
  * [Docker Compose](https://docs.docker.com/compose/install/)

### Passos para Instalação

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/sent.IA.git
    cd sent.IA
    ```

2.  **Construa e inicie os contêineres:**
    O comando a seguir irá construir a imagem da aplicação Django, baixar as imagens do PostgreSQL e do Ollama, e iniciar todos os serviços.

    ```bash
    docker compose up --build
    ```

3.  **Acesse a aplicação:**
    Após a inicialização, a aplicação estará disponível no seu navegador em: `http://localhost:8000`

4.  **Baixando o modelo de IA (Primeira Vez):**
    Para que a análise funcione, o Ollama precisa baixar o modelo `gemma:2b`. Abra um novo terminal e execute o seguinte comando:

    ```bash
    docker exec -it sent.ia-ollama-1 ollama pull gemma:2b
    ```

    Aguarde o download ser concluído. A aplicação agora está pronta para uso\!

## 📋 Como Usar

1.  **Acesse a Página Principal:** Navegue para a página inicial (`/`).
2.  **Faça o Upload:** Arraste e solte ou clique para selecionar um arquivo `.csv` ou `.json` contendo os feedbacks que deseja analisar.
3.  **Estrutura do Arquivo:** Certifique-se de que seu arquivo contenha as colunas/chaves necessárias. Você pode baixar modelos de exemplo diretamente na página de upload.
      * **Obrigatória:** Uma coluna/chave com o texto do feedback (nomes aceitos: `feedback_text`, `Feedback`, `texto_feedback`, `comentario`).
      * **Opcionais:** `customer_name`, `feedback_date`, `product_area`.
4.  **Análise:** Clique em "Enviar e Analisar". A aplicação processará o arquivo e o redirecionará para o dashboard.
5.  **Explore o Dashboard:**
      * Visualize as estatísticas gerais e o gráfico de sentimentos.
      * Use os filtros para detalhar a análise por sessão, sentimento ou produto.
      * Exporte os dados filtrados ou o gráfico para seus relatórios.

*Dashboard com filtros, estatísticas e gráfico de sentimentos.*

-----

*Este projeto foi criado como uma ferramenta para demonstrar a integração de análise de sentimento com IA em uma aplicação web moderna.*
