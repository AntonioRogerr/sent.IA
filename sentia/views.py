import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Count # Importar para agregação
from .models import AnalysisSession, Feedback

# Funções auxiliares (coloque no início do arquivo views.py)
def analyze_single_feedback(text):
    """
    Simula a análise de sentimento para um único texto.
    Substitua esta função pela sua lógica real de IA/NLP.
    """
    text_lower = text.lower()
    if any(word in text_lower for word in ['excelente', 'ótimo', 'amei', 'perfeito', 'bom', 'satisfeito']):
        return Feedback.SentimentChoices.POSITIVE
    elif any(word in text_lower for word in ['ruim', 'péssimo', 'odeio', 'lento', 'bug', 'problema', 'insatisfeito']):
        return Feedback.SentimentChoices.NEGATIVE
    else:
        return Feedback.SentimentChoices.NEUTRAL

def index_view(request):
    if request.method == 'POST':
        # Lidar com upload de arquivo CSV
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            
            # Validação básica de arquivo (pode expandir)
            if not csv_file.name.endswith('.csv'):
                return render(request, 'sentia/pages/index.html', {
                    'error_message': 'Por favor, envie um arquivo CSV válido.'
                })
            
            # Cria uma nova sessão de análise para este arquivo CSV
            new_session = AnalysisSession.objects.create(csv_filename=csv_file.name)
            
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string) # Usar DictReader para ler por nome de coluna
            
            feedbacks_to_create = []
            results_to_display = []

            for row in reader:
                # Mapeia colunas do CSV para campos do modelo
                # ATENÇÃO: Verifique se os nomes das colunas no seu CSV correspondem!
                # Ex: Seu CSV pode ter "Feedback Text", "Customer Name", "Date"
                feedback_text = row.get('feedback_text', row.get('Feedback', '')).strip() # Tenta várias colunas para o texto
                customer_name = row.get('customer_name', row.get('Cliente', '')).strip()
                feedback_date_str = row.get('feedback_date', row.get('Data', '')).strip()
                product_area = row.get('product_area', row.get('Area Produto', '')).strip()

                parsed_date = None
                if feedback_date_str:
                    try:
                        # Tente diferentes formatos de data
                        parsed_date = datetime.strptime(feedback_date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            parsed_date = datetime.strptime(feedback_date_str, '%d/%m/%Y %H:%M:%S')
                        except ValueError:
                            try:
                                parsed_date = datetime.strptime(feedback_date_str, '%Y-%m-%d')
                            except ValueError:
                                try:
                                    parsed_date = datetime.strptime(feedback_date_str, '%d/%m/%Y')
                                except ValueError:
                                    pass # Se falhar, parsed_date permanece None

                if feedback_text: # Só processa se houver texto de feedback
                    sentiment_result = analyze_single_feedback(feedback_text)
                    
                    feedbacks_to_create.append(
                        Feedback(
                            session=new_session,
                            text=feedback_text,
                            sentiment=sentiment_result,
                            customer_name=customer_name if customer_name else None,
                            feedback_date=parsed_date,
                            product_area=product_area if product_area else None,
                        )
                    )
                    results_to_display.append({
                        'text': feedback_text,
                        'sentiment': Feedback.SentimentChoices(sentiment_result).label,
                        'customer_name': customer_name,
                        'feedback_date': parsed_date,
                        'product_area': product_area,
                    })
            
            if feedbacks_to_create:
                Feedback.objects.bulk_create(feedbacks_to_create)

            return render(request, 'sentia/pages/index.html', {
                'results': results_to_display,
                'session_id': new_session.id, # Para vincular os resultados à sessão
                'message': f"CSV '{csv_file.name}' analisado com sucesso e salvo na sessão #{new_session.id}."
            })
        
        # Lidar com análise de texto direto (manter a funcionalidade anterior)
        elif 'feedbacks_text' in request.POST:
            feedbacks_text = request.POST.get('feedbacks_text', '')
            feedback_list = [line.strip() for line in feedbacks_text.splitlines() if line.strip()]
            
            results_to_display = []
            feedbacks_to_create = []

            if feedback_list:
                new_session = AnalysisSession.objects.create() # Sem nome de CSV
                for text in feedback_list:
                    sentiment_result = analyze_single_feedback(text)
                    
                    feedbacks_to_create.append(
                        Feedback(
                            session=new_session,
                            text=text,
                            sentiment=sentiment_result
                        )
                    )
                    results_to_display.append({
                        'text': text,
                        'sentiment': Feedback.SentimentChoices(sentiment_result).label
                    })
                Feedback.objects.bulk_create(feedbacks_to_create)

            return render(request, 'sentia/pages/index.html', {'results': results_to_display})

    return render(request, 'sentia/pages/index.html')


def dashboard_view(request):
    # Obtém todos os feedbacks do banco de dados
    all_feedbacks = Feedback.objects.all()

    # Filtros para o dashboard (implementaremos o HTML para eles)
    selected_session_id = request.GET.get('session')
    selected_sentiment = request.GET.get('sentiment')
    selected_product_area = request.GET.get('product_area')
    
    # Aplica filtros se existirem
    if selected_session_id:
        all_feedbacks = all_feedbacks.filter(session__id=selected_session_id)
    if selected_sentiment:
        all_feedbacks = all_feedbacks.filter(sentiment=selected_sentiment)
    if selected_product_area:
        all_feedbacks = all_feedbacks.filter(product_area=selected_product_area)

    total_feedbacks = all_feedbacks.count()
    positive_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.POSITIVE).count()
    negative_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.NEGATIVE).count()
    neutral_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.NEUTRAL).count()
    unknown_count = all_feedbacks.filter(sentiment=Feedback.SentimentChoices.UNKNOWN).count() # Novo

    # Calcula as porcentagens
    stats = {
        'total': total_feedbacks,
        'positive': positive_count,
        'negative': negative_count,
        'neutral': neutral_count,
        'unknown': unknown_count, # Novo
        'positive_percent': (positive_count / total_feedbacks * 100) if total_feedbacks else 0,
        'negative_percent': (negative_count / total_feedbacks * 100) if total_feedbacks else 0,
        'neutral_percent': (neutral_count / total_feedbacks * 100) if total_feedbacks else 0,
        'unknown_percent': (unknown_count / total_feedbacks * 100) if total_feedbacks else 0,
    }

    # Para os filtros:
    all_sessions = AnalysisSession.objects.all().order_by('-created_at')
    # Obter todas as áreas de produto distintas
    all_product_areas = Feedback.objects.filter(product_area__isnull=False).values_list('product_area', flat=True).distinct()

    context = {
        'stats': stats,
        'all_feedbacks': all_feedbacks.order_by('-created_at')[:10], # Mostrar os 10 feedbacks mais recentes
        'all_sessions': all_sessions,
        'all_product_areas': all_product_areas,
        'selected_session_id': selected_session_id,
        'selected_sentiment': selected_sentiment,
        'selected_product_area': selected_product_area,
        'sentiment_choices': Feedback.SentimentChoices.choices, # Para usar no filtro
    }

    return render(request, 'sentia/pages/dashboard.html', context)