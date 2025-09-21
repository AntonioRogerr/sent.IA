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

            # Decodifica o arquivo e prepara para leitura
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            # --- Bloco de validação de cabeçalho ---
            header = reader.fieldnames
            required_cols_options = ['feedback_text', 'Feedback', 'texto_feedback', 'comentario']

            if not any(col in header for col in required_cols_options):
                error_msg = (
                    "O arquivo CSV precisa ter uma coluna para o feedback. "
                    f"Nenhuma das colunas esperadas foi encontrada: {', '.join(required_cols_options)}."
                )
                return render(request, 'sentia/pages/index.html', {'error_message': error_msg})
            # --- Fim do bloco ---

            next_number = AnalysisSession.objects.get_next_session_number()
            new_session = AnalysisSession.objects.create(
                csv_filename=csv_file.name,
                session_number=next_number
            )

            feedbacks_to_create = []

            # Itera sobre as linhas do CSV
            for row in reader:
                feedback_text = row.get('feedback_text', row.get('Feedback', '')).strip()
                if not feedback_text:
                    continue

                customer_name = row.get('customer_name', row.get('Cliente', '')).strip()
                feedback_date_str = row.get('feedback_date', row.get('Data', '')).strip()
                product_area = row.get('product_area', row.get('Area Produto', '')).strip()

                # --- LÓGICA DE DATA ATUALIZADA ---
                parsed_date = None
                if feedback_date_str:
                    # A lista de formatos agora inclui data e data+hora
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M'):
                        try:
                            # Converte para datetime e extrai apenas a data com .date()
                            parsed_date = datetime.strptime(feedback_date_str, fmt).date()
                            break
                        except ValueError:
                            pass
                # --- FIM DA ALTERAÇÃO ---

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

            if feedbacks_to_create:
                Feedback.objects.bulk_create(feedbacks_to_create)

            messages.success(request, f"CSV '{csv_file.name}' analisado com sucesso e salvo na sessão #{new_session.session_number}.")
            return redirect('dashboard')

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

    all_sessions = AnalysisSession.objects.with_feedback_counts().order_by('-created_at')
    all_product_areas = Feedback.objects.filter(product_area__isnull=False).values_list('product_area', flat=True).distinct()

    context = {
        'stats': stats,
        'all_feedbacks': all_feedbacks.order_by('-created_at'),
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
            session_number_to_display = session_to_delete.session_number
            session_to_delete.delete()
            messages.success(request, f'Sessão #{session_number_to_display} foi excluída com sucesso.')
        except AnalysisSession.DoesNotExist:
            messages.error(request, f'Sessão #{session_id} não encontrada.')
    return redirect('dashboard')