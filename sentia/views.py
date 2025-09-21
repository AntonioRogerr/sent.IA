# sentia/views.py

import csv
import io
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse # Adicionar JsonResponse
from .models import AnalysisSession, Feedback
from .ollama_analyzer import analyze_sentiment_with_ollama

def index_view(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']

            # --- Bloco de validação ---
            if not uploaded_file:
                return render(request, 'sentia/pages/index.html', {
                    'error_message': 'Por favor, selecione um arquivo para enviar.'
                })
            
            is_csv = uploaded_file.name.endswith('.csv')
            is_json = uploaded_file.name.endswith('.json')

            if not is_csv and not is_json:
                return render(request, 'sentia/pages/index.html', {
                    'error_message': 'Por favor, envie um arquivo CSV ou JSON válido.'
                })

            # --- LÓGICA DE DECODIFICAÇÃO E LEITURA ---
            try:
                decoded_file = uploaded_file.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                return render(request, 'sentia/pages/index.html', {
                    'error_message': 'Não foi possível decodificar o arquivo. Tente salvá-lo com a codificação UTF-8.'
                })

            feedbacks_data = []
            if is_csv:
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                feedbacks_data = list(reader)
            elif is_json:
                try:
                    feedbacks_data = json.loads(decoded_file)
                except json.JSONDecodeError:
                    return render(request, 'sentia/pages/index.html', {
                        'error_message': 'Erro ao decodificar o arquivo JSON. Verifique a formatação.'
                    })
            
            # --- Validação de cabeçalho/chaves ---
            if not feedbacks_data:
                 return render(request, 'sentia/pages/index.html', {
                    'error_message': 'O arquivo enviado está vazio ou mal formatado.'
                })
            
            first_item = feedbacks_data[0]
            required_cols_options = ['feedback_text', 'Feedback', 'texto_feedback', 'comentario']
            if not any(col in first_item for col in required_cols_options):
                error_msg = (
                    f"O arquivo {('CSV' if is_csv else 'JSON')} precisa ter uma chave/coluna para o feedback. "
                    f"Nenhuma das esperadas foi encontrada: {', '.join(required_cols_options)}."
                )
                return render(request, 'sentia/pages/index.html', {'error_message': error_msg})

            next_number = AnalysisSession.objects.get_next_session_number()
            new_session = AnalysisSession.objects.create(
                csv_filename=uploaded_file.name,
                session_number=next_number
            )

            feedbacks_to_create = []

            for item in feedbacks_data:
                feedback_text = item.get('feedback_text', item.get('Feedback', '')).strip()
                if not feedback_text:
                    continue

                customer_name = item.get('customer_name', item.get('Cliente', '')).strip()
                feedback_date_str = item.get('feedback_date', item.get('Data', '')).strip()
                product_area = item.get('product_area', item.get('Area Produto', '')).strip()

                parsed_date = None
                if feedback_date_str:
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M'):
                        try:
                            parsed_date = datetime.strptime(feedback_date_str, fmt).date()
                            break
                        except ValueError:
                            pass

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

            messages.success(request, f"Arquivo '{uploaded_file.name}' analisado com sucesso e salvo na sessão #{new_session.session_number}.")
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


def export_filtered_data_view(request):
    """
    Exporta os feedbacks filtrados para um arquivo CSV.
    """
    feedbacks_query = Feedback.objects.select_related('session').all()
    
    selected_session_id = request.GET.get('session')
    selected_sentiment = request.GET.get('sentiment')
    selected_product_area = request.GET.get('product_area')

    if selected_session_id:
        feedbacks_query = feedbacks_query.filter(session__id=selected_session_id)
    if selected_sentiment:
        feedbacks_query = feedbacks_query.filter(sentiment=selected_sentiment)
    if selected_product_area:
        feedbacks_query = feedbacks_query.filter(product_area__icontains=selected_product_area)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="feedbacks_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'ID do Feedback', 'Texto', 'Sentimento', 'Cliente', 
        'Data do Feedback', 'Área do Produto', 'Sessão', 'Analisado em'
    ])

    for feedback in feedbacks_query.order_by('-created_at'):
        writer.writerow([
            feedback.id,
            feedback.text,
            feedback.get_sentiment_display(),
            feedback.customer_name or 'N/A',
            feedback.feedback_date.strftime('%d/%m/%Y') if feedback.feedback_date else 'N/A',
            feedback.product_area or 'N/A',
            f"Sessão #{feedback.session.session_number}",
            feedback.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    return response

# --- NOVA VIEW PARA EXPORTAR JSON ---
def export_filtered_data_json_view(request):
    """
    Exporta os feedbacks filtrados para um arquivo JSON.
    """
    feedbacks_query = Feedback.objects.select_related('session').all()
    
    selected_session_id = request.GET.get('session')
    selected_sentiment = request.GET.get('sentiment')
    selected_product_area = request.GET.get('product_area')

    if selected_session_id:
        feedbacks_query = feedbacks_query.filter(session__id=selected_session_id)
    if selected_sentiment:
        feedbacks_query = feedbacks_query.filter(sentiment=selected_sentiment)
    if selected_product_area:
        feedbacks_query = feedbacks_query.filter(product_area__icontains=selected_product_area)

    # Converte o queryset em uma lista de dicionários
    data_to_export = list(feedbacks_query.values(
        'id', 'text', 'sentiment', 'customer_name', 
        'feedback_date', 'product_area', 'session__session_number', 'created_at'
    ))

    # Prepara a resposta JSON
    response = JsonResponse(data_to_export, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    response['Content-Disposition'] = 'attachment; filename="feedbacks_export.json"'
    
    return response