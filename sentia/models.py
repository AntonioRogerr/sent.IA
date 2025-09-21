# Arquivo: sentia/models.py

from django.db import models
from django.utils import timezone
from django.db.models import Count, Q

# --- Manager Personalizado ---
class AnalysisSessionManager(models.Manager):
    def with_feedback_counts(self):
        """
        Retorna o QuerySet de AnalysisSession com contagens de feedback
        anotadas. Isso é extremamente eficiente para listas.
        """
        return self.get_queryset().annotate(
            total_feedbacks=Count('feedbacks'),
            positive_feedbacks=Count(
                'feedbacks',
                filter=Q(feedbacks__sentiment=Feedback.SentimentChoices.POSITIVE)
            ),
            negative_feedbacks=Count(
                'feedbacks',
                filter=Q(feedbacks__sentiment=Feedback.SentimentChoices.NEGATIVE)
            ),
            neutral_feedbacks=Count(
                'feedbacks',
                filter=Q(feedbacks__sentiment=Feedback.SentimentChoices.NEUTRAL)
            )
        )

    # --- NOVO MÉTODO ADICIONADO AQUI ---
    def get_next_session_number(self):
        """
        Calcula o próximo número de sessão disponível, encontrando a primeira
        lacuna na sequência de números existentes.
        """
        # Pega todos os números de sessão existentes em ordem.
        existing_numbers = self.get_queryset().values_list('session_number', flat=True).order_by('session_number')
        
        # Se não houver nenhum, começa com 1.
        if not existing_numbers:
            return 1

        # Procura pela primeira lacuna na sequência.
        expected_number = 1
        for number in existing_numbers:
            if number > expected_number:
                # Encontramos uma lacuna (ex: números são 1, 3 -> a lacuna é 2)
                return expected_number
            expected_number += 1
        
        # Se não houver lacunas (ex: 1, 2, 3), retorna o próximo da sequência.
        return expected_number

# --- Modelo Principal ---
class AnalysisSession(models.Model):
    """
    Representa um único evento de análise.
    """
    # --- NOVO CAMPO ADICIONADO AQUI ---
    session_number = models.IntegerField(unique=True, verbose_name="Número da Sessão")

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data da Análise"
    )
    csv_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Arquivo CSV"
    )

    objects = AnalysisSessionManager()

    def __str__(self):
        local_time = timezone.localtime(self.created_at)
        display_number = f" (Sessão #{self.session_number})" if self.session_number else ""
        if self.csv_filename:
            return f"Análise do CSV '{self.csv_filename}' em {local_time.strftime('%d/%m/%Y às %H:%M')}{display_number}"
        return f"Análise avulsa em {local_time.strftime('%d/%m/%Y às %H:%M')}{display_number}"

    class Meta:
        verbose_name = "Sessão de Análise"
        verbose_name_plural = "Sessões de Análise"
        ordering = ['-created_at']

# Modelo para cada feedback individual
class Feedback(models.Model):
    """
    Representa um único feedback com seu texto e o sentimento classificado,
    incluindo metadados do CSV.
    """
    
    class SentimentChoices(models.TextChoices):
        POSITIVE = 'POS', 'Positivo'
        NEGATIVE = 'NEG', 'Negativo'
        NEUTRAL = 'NEU', 'Neutro'
        UNKNOWN = 'UNKN', 'Desconhecido' 

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name="Sessão de Análise"
    )

    text = models.TextField(verbose_name="Texto do Feedback")
    sentiment = models.CharField(
        max_length=4,
        choices=SentimentChoices.choices,
        default=SentimentChoices.UNKNOWN,
        verbose_name="Sentimento"
    )
    
    customer_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Nome do Cliente"
    )
    feedback_date = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Data do Feedback"
    )
    product_area = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Área do Produto"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        display_text = self.text if len(self.text) <= 50 else self.text[:47] + '...'
        return f"'{display_text}' - {self.get_sentiment_display()} (Sessão: {self.session.id})"

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-created_at']