from django.db import models
from django.utils import timezone

# Modelo para agrupar uma sessão de análise de feedbacks
class AnalysisSession(models.Model):
    """
    Representa um único evento de análise, que pode conter vários feedbacks.
    Ex: Um usuário colou 10 feedbacks e clicou em "Analisar" ou enviou um CSV.
    """
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data da Análise"
    )
    # Adicionamos um campo para o nome do arquivo CSV
    csv_filename = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Nome do Arquivo CSV"
    )

    def __str__(self):
        local_time = timezone.localtime(self.created_at)
        if self.csv_filename:
            return f"Análise do CSV '{self.csv_filename}' em {local_time.strftime('%d/%m/%Y às %H:%M')}"
        return f"Análise avulsa em {local_time.strftime('%d/%m/%Y às %H:%M')}"

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
        # Adicione um status 'UNKN' para "desconhecido" caso não consiga analisar
        UNKNOWN = 'UNKN', 'Desconhecido' 

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name="Sessão de Análise"
    )

    text = models.TextField(verbose_name="Texto do Feedback")
    sentiment = models.CharField(
        max_length=4, # Aumentado para 4 para UNKN
        choices=SentimentChoices.choices,
        default=SentimentChoices.UNKNOWN, # Default para desconhecido
        verbose_name="Sentimento"
    )
    
    # Novos campos para metadados do CSV
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
    # Exemplo de outro campo, ajuste conforme seu CSV
    product_area = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Área do Produto"
    )

    created_at = models.DateTimeField(auto_now_add=True) # Data de registro no sistema

    def __str__(self):
        # Limita o texto para evitar strings muito longas
        display_text = self.text if len(self.text) <= 50 else self.text[:47] + '...'
        return f"'{display_text}' - {self.get_sentiment_display()} (Sessão: {self.session.id})"

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-created_at'] # Ordem de criação do feedback no sistema