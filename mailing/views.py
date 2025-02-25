from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils import timezone
from .models import Recipient, Message, Mailing, SendAttempt
from .forms import RecipientForm, MessageForm, MailingForm


# CRUD для получателей (Recipient)

class RecipientListView(generic.ListView):
    model = Recipient
    template_name = 'recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(generic.CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipient_form.html'
    success_url = reverse_lazy('recipient_list')


class RecipientUpdateView(generic.UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipient_form.html'
    success_url = reverse_lazy('recipient_list')


class RecipientDeleteView(generic.DeleteView):
    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('recipient_list')


# CRUD для сообщений (Message)

class MessageListView(generic.ListView):
    model = Message
    template_name = 'message_list.html'
    context_object_name = 'messages'


class MessageCreateView(generic.CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message_form.html'
    success_url = reverse_lazy('message_list')


class MessageUpdateView(generic.UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message_form.html'
    success_url = reverse_lazy('message_list')


class MessageDeleteView(generic.DeleteView):
    model = Message
    template_name = 'message_confirm_delete.html'
    success_url = reverse_lazy('message_list')


# CRUD для рассылок (Mailing)

class MailingListView(generic.ListView):
    model = Mailing
    template_name = 'mailing_list.html'
    context_object_name = 'mailings'


class MailingCreateView(generic.CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_form.html'
    success_url = reverse_lazy('mailing_list')


class MailingUpdateView(generic.UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_form.html'
    success_url = reverse_lazy('mailing_list')


class MailingDeleteView(generic.DeleteView):
    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')


# Генерация отчета и отправка рассылки

class SendMailingView(generic.View):
    def post(self, request, mailing_id):
        mailing = self.get_object(mailing_id)
        recipients = mailing.recipients.all()

        # Инициация отправки
        for recipient in recipients:
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    'from@example.com',  # email from
                    [recipient.email],
                    fail_silently=False,
                )
                status = 'Успешно'
                server_response = 'Письмо отправлено успешно.'
            except Exception as e:
                status = 'Не успешно'
                server_response = str(e)

            # Сохранение попытки рассылки
            SendAttempt.objects.create(
                mailing=mailing,
                status=status,
                server_response=server_response
            )

        # Обновление статуса рассылки
        if mailing.status == 'Создана':
            mailing.status = 'Запущена'
            mailing.first_sent_at = timezone.now()
            mailing.save()

        return render(request, 'mailing_status.html', {'mailing': mailing})

    def get_object(self, mailing_id):
        return Mailing.objects.get(id=mailing_id)


# Главная страница

class HomeView(generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
        context['unique_recipients'] = Recipient.objects.count()
        return context