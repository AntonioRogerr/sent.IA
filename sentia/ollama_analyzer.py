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
    Você é um especialista em análise de sentimentos de feedback de clientes.

    Sua tarefa é:
    1. Ler atentamente o seguinte feedback.
    2. Identificar o sentimento predominante.
    3. Responder de forma categórica usando **apenas uma única palavra** entre as três opções abaixo:
    - Positivo
    - Negativo
    - Neutro

    Feedback do cliente: "{text}"
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