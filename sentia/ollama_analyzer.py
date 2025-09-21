# sentia/ollama_analyzer.py

import requests
import json
from .models import Feedback 

def analyze_sentiment_with_ollama(text: str):
    """
    Analisa o sentimento de um texto usando a API do Ollama.
    Retorna uma das choices do modelo Feedback (POS, NEG, NEU).
    """
    
    prompt = f"""
    Você é um analista de sentimentos altamente preciso. Sua tarefa é seguir um processo de três passos para classificar o feedback de um cliente.

    **Passo 1: Analise o Feedback**
    Leia o feedback do cliente fornecido dentro da tag `<feedback>` e identifique as emoções, opiniões e fatos principais.

    **Passo 2: Raciocine e Justifique**
    Com base na sua análise, escreva um raciocínio curto para decidir entre 'Positivo', 'Negativo' e 'Neutro'.
    - **Negativo:** Priorize esta classificação se houver qualquer sinal de crítica, insatisfação, problema ou frustração (ex: "lento", "confuso", "não gostei", "problema").
    - **Positivo:** Use esta classificação se o texto expressar claramente elogio, satisfação ou sucesso, e não contiver críticas.
    - **Neutro:** Use esta classificação apenas se o feedback for puramente informativo, uma pergunta, ou uma sugestão sem forte carga emocional.

    **Passo 3: Dê a Resposta Final**
    Forneça sua classificação final dentro de uma tag `<sentiment>`, usando apenas uma das três palavras: Positivo, Negativo ou Neutro.

    **Exemplo de Execução:**
    <feedback>A interface é um pouco confusa, mas funciona.</feedback>
    
    **Raciocínio:** O feedback aponta um problema ("confusa"), o que indica um sentimento negativo, mesmo que também mencione que funciona. A crítica tem prioridade.
    <sentiment>Negativo</sentiment>

    ---

    **Tarefa Atual:**
    <feedback>{text}</feedback>
    
    **Raciocínio:**
    """

    try:
        response = requests.post(
            'http://ollama:11434/api/generate',
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2 
                }
            }
        )
        response.raise_for_status() 

        response_text = json.loads(response.text)['response'].strip().lower()

        print(f"Resposta bruta do Ollama: '{response_text}'")

        if 'positivo' in response_text:
            return Feedback.SentimentChoices.POSITIVE
        elif 'negativo' in response_text:
            return Feedback.SentimentChoices.NEGATIVE
        elif 'neutro' in response_text:
            return Feedback.SentimentChoices.NEUTRAL
        else:
            print(f"Nenhuma palavra-chave encontrada na resposta do Ollama.")
            return Feedback.SentimentChoices.UNKNOWN

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro ao chamar a API do Ollama: {e}")
        return Feedback.SentimentChoices.UNKNOWN