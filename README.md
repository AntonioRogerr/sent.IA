# sent.IA

> Transforme Feedback em Ação com Insights Inteligentes

**sent.IA** é uma plataforma de código aberto projetada para otimizar a análise de feedback de clientes por meio de uma arquitetura escalável e conteinerizada construída em Django. Ele integra classificação de sentimento alimentada por IA.

**Construído com as seguintes ferramentas e tecnologias:**

  * Python
  * Ollama
  * Docker
  * GNU Bash
  * Markdown

-----

### **Sumário**

  * [Visão Geral](https://www.google.com/search?q=%23vis%C3%A3o-geral)
  * [Por que sent.IA?](https://www.google.com/search?q=%23por-que-sentia)
  * [Começando](https://www.google.com/search?q=%23come%C3%A7ando)
  * [Pré-requisitos](https://www.google.com/search?q=%23pr%C3%A9-requisitos)
  * [Instalação](https://www.google.com/search?q=%23instala%C3%A7%C3%A3o)
  * [Uso](https://www.google.com/search?q=%23uso)
  * [Testes](https://www.google.com/search?q=%23testes)

-----

### **Visão Geral**

sent.IA é uma plataforma de código aberto criada para agilizar a análise de feedback de clientes, utilizando uma arquitetura escalável e em contêineres baseada em Django. A plataforma integra análise de sentimento por meio de Inteligência Artificial.

### **Por que sent.IA?**

Este projeto capacita desenvolvedores a implantar e gerenciar rapidamente fluxos de trabalho de análise de sentimento. As principais características incluem:

  * **Configuração e Gerenciamento:** Utiliza `manage.py` e Docker Compose para configuração simplificada, migrações e orquestração do ambiente.
  * **Implantação em Contêineres:** Garante ambientes consistentes entre desenvolvimento e produção com Docker, Dockerfile e scripts de entrypoint.
  * **Integração com IA:** Aproveita a API do Ollama para classificação precisa de sentimentos, aprimorando os insights do feedback.
  * **Dashboards Interativos:** Fornece templates amigáveis para visualizar dados de sentimento e gerenciar sessões.
  * **Suporte Robusto ao Desenvolvimento:** Inclui frameworks de teste e interfaces de administração para um desenvolvimento confiável e escalável.

### **Começando**

#### **Pré-requisitos**

Este projeto requer as seguintes dependências:

  * **Linguagem de Programação:** Python
  * **Gerenciador de Pacotes:** Pip
  * **Runtime de Contêiner:** Docker

#### **Instalação**

Construa o sent.IA a partir do código-fonte e instale as dependências:

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/AntonioRogerr/sent.IA
    ```

2.  **Navegue até o diretório do projeto:**

    ```bash
    cd sent.IA
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

### **Uso**

Execute o projeto com:

**Usando Docker:**

```bash
docker run -it {nome_da_imagem}
```

**Usando Pip:**

```bash
python {entrypoint}
```

### **Testes**

O Sent.ia usa o framework de testes `{test_framework}`. Execute a suíte de testes com:

**Usando Docker:**

```bash
echo 'INSIRA-O-COMANDO-DE-TESTE-AQUI'
```

**Usando Pip:**

```bash
pytest
```
