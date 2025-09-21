# sentia/views.py

import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AnalysisSession, Feedback
from .ollama_analyzer import analyze_sentiment_with_ollama

def index_view(request):
    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            
            # --- Bloco de validação ---
            if not csv_file:
                return render(request, 'sentia/pages/index.html', {
                    'error_message': 'Por favor, selecione um arquivo para enviar.'
                })
            if not csv_file.name.endswith('.csv'):
                return render(request, 'sentia/pages/index.html', {
                    'error_message': 'Por favor, envie um arquivo CSV válido.'
                })
            
            # --- ALTERAÇÃO AQUI: Bloco de Processamento com o novo número de sessão ---
            # 1. Busca o próximo número de sessão disponível
            next_number = AnalysisSession.objects.get_next_session_number()

            # 2. Cria a nova sessão com o número calculado
            new_session = AnalysisSession.objects.create(
                csv_filename=csv_file.name,
                session_number=next_number
            )
            
            # Decodifica o arquivo e prepara para leitura
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            feedbacks_to_create = []
            
            # Itera sobre as linhas do CSV
            for row in reader:
                feedback_text = row.get('feedback_text', row.get('Feedback', '')).strip()
                if not feedback_text:
                    continue
                
                # Extrai outros dados (se existirem)
                customer_name = row.get('customer_name', row.get('Cliente', '')).strip()
                feedback_date_str = row.get('feedback_date', row.get('Data', '')).strip()
                product_area = row.get('product_area', row.get('Area Produto', '')).strip()
                
                # Tenta converter a data em múltiplos formatos
                parsed_date = None
                if feedback_date_str:
                    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%Y-%m-%d', '%d/%m/%Y'):
                        try:
                            parsed_date = datetime.strptime(feedback_date_str, fmt)
                            break
                        except ValueError:
                            pass
                
                # Analisa o sentimento e prepara para salvar
                sentiment_result = analyze_sentiment_with_ollama(feedback_text)
                feedbacks_to_create.append(
                    Feedback(
                        session=new_session, 
                        text=feedback_text, 
                        sentiment=sentiment_result,
                        customer_name=customer_name if customer_name else None,
                        feedback_date=parsed_date, 
                        product_area=product_area if product_area else None
                    )
                )
            
            # Salva todos os feedbacks no banco de uma vez
            if feedbacks_to_create:
                Feedback.objects.bulk_create(feedbacks_to_create)

            # --- ALTERAÇÃO AQUI: Usa o session_number na mensagem ---
            # Adiciona a mensagem de sucesso e redireciona para o dashboard
            messages.success(request, f"CSV '{csv_file.name}' analisado com sucesso e salvo na sessão #{new_session.session_number}.")
            return redirect('dashboard')

    # Se a requisição não for POST, apenas renderiza a página de upload
    return render(request, 'sentia/pages/index.html')

def dashboard_view(request):
    all_feedbacks = Feedback.objects.all()
    selected_session_id = request.GET.get('session')
    selected_sentiment = request.GET.get('sentiment')
    selected_product_area = request.GET.get('product_area')
    
    if selected_session_id:
        all_feedbacks = all_feedbacks.filter(session__id=selected_session_id)
    if selected_sentiment:
        all_feedbacks = all_feedbacks.filter(sentiment=selected_sentiment)
    if selected_product_area:
        all_feedbacks = all_feedbacks.filter(product_area__icontains=selected_product_area)

    total_feedbacks = all_feedbacks.count()
    positive_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.POSITIVE).count()
    negative_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.NEGATIVE).count()
    neutral_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.NEUTRAL).count()
    unknown_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.UNKNOWN).count()

    stats = {
        'total': total_feedbacks, 'positive': positive_count, 'negative': negative_count, 'neutral': neutral_count,
        'unknown': unknown_count,
        'positive_percent': (positive_count / total_feedbacks * 100) if total_feedbacks else 0,
        'negative_percent': (negative_count / total_feedbacks * 100) if total_feedbacks else 0,
        'neutral_percent': (neutral_count / total_feedbacks * 100) if total_feedbacks else 0,
        'unknown_percent': (unknown_count / total_feedbacks * 100) if total_feedbacks else 0,
    }

    # Utiliza o seu manager otimizado para buscar as sessões
    all_sessions = AnalysisSession.objects.with_feedback_counts().order_by('-created_at')
    
    all_product_areas = Feedback.objects.filter(product_area__isnull=False).values_list('product_area', flat=True).distinct()

    context = {
        'stats': stats,
        'all_feedbacks': all_feedbacks.order_by('-created_at')[:10],
        'all_sessions': all_sessions,
        'all_product_areas': all_product_areas,
        'selected_session_id': selected_session_id,
        'selected_sentiment': selected_sentiment,
        'selected_product_area': selected_product_area,
        'sentiment_choices': Feedback.SentimentChoices.choices,
    }
    return render(request, 'sentia/pages/dashboard.html', context)


def delete_session_view(request, session_id):
    if request.method == 'POST':
        try:
            session_to_delete = AnalysisSession.objects.get(id=session_id)
            
            # Guarda o número da sessão ANTES de apagar o objeto
            session_number_to_display = session_to_delete.session_number
            
            # Apaga a sessão do banco de dados
            session_to_delete.delete()
            
            # Usa o número guardado para a mensagem de sucesso
            messages.success(request, f'Sessão #{session_number_to_display} foi excluída com sucesso.')

        except AnalysisSession.DoesNotExist:
            messages.error(request, f'Sessão #{session_id} não encontrada.')
    
    return redirect('dashboard')