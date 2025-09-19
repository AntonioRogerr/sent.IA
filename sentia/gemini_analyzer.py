# sentia/gemini_analyzer.py

import os
import google.generativeai as genai
from .models import Feedback # Importar o modelo para usar as Choices

# Configura a API usando a chave da variável de ambiente
try:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    # Modelo escolhido: gemini-1.5-flash é rápido e eficiente para esta tarefa
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Erro ao configurar a API do Gemini: {e}")
    model = None

def analyze_sentiment_with_gemini(text: str):
    """
    Analisa o sentimento de um texto usando a API do Gemini.
    Retorna uma das choices do modelo Feedback (POS, NEG, NEU).
    """
    if not model:
        print("Modelo Gemini não inicializado. Retornando 'Desconhecido'.")
        return Feedback.SentimentChoices.UNKNOWN

    # Este é o "prompt". Instruímos o modelo sobre o que queremos.
    # Ser específico e limitar as opções de resposta é a chave para um bom resultado.
    prompt = f"""
    Você é um especialista em análise de sentimento de feedbacks de clientes.
    Sua tarefa é classificar o seguinte feedback.
    
    Feedback do cliente: "{text}"
    
    Analise o sentimento e responda APENAS com uma das seguintes três palavras:
    - Positivo
    - Negativo
    - Neutro
    """

    try:
        response = model.generate_content(prompt)
        
        # Limpa a resposta para garantir que temos apenas a palavra que queremos
        cleaned_response = response.text.strip().capitalize()

        # Mapeia a resposta de texto para as choices do nosso modelo Django
        if cleaned_response == 'Positivo':
            return Feedback.SentimentChoices.POSITIVE
        elif cleaned_response == 'Negativo':
            return Feedback.SentimentChoices.NEGATIVE
        elif cleaned_response == 'Neutro':
            return Feedback.SentimentChoices.NEUTRAL
        else:
            # Se o modelo responder algo inesperado, classificamos como desconhecido
            print(f"Resposta inesperada do Gemini: {cleaned_response}")
            return Feedback.SentimentChoices.UNKNOWN

    except Exception as e:
        # Lida com possíveis erros da API (ex: conteúdo bloqueado, problemas de conexão)
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return Feedback.SentimentChoices.UNKNOWN