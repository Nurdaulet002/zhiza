from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from newsletter.forms import NewsletterForm, BranchNewsletterForm
from newsletter.models import Newsletter, BranchNewsletter
from django.views.generic.base import TemplateResponseMixin
from django.views import View



class NewsletterCreateView(CreateView):
    model = Newsletter
    template_name = 'newsletter/create.html'
    fields = ['title']

    def get_success_url(self):
        return reverse('newsletter:draft_list')


class NewsletterDetailSummaryView(DetailView):
    model = Newsletter
    template_name = 'newsletter/detail/summary.html'
    context_object_name = 'newsletter'

class NewsletterDetailMessageView(DetailView):
    model = Newsletter
    template_name = 'newsletter/detail/message.html'
    context_object_name = 'newsletter'


from django.shortcuts import get_object_or_404


class NewsletterMessageCreateUpdateView(TemplateResponseMixin, View):
    template_name = "newsletter/detail/message_create.html"

    def get(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        instance = Newsletter.objects.get(id=newsletter_id) if newsletter_id else None
        form = NewsletterForm(instance=instance)
        context = {
            'newsletter_id': newsletter_id,
            'form': form,
            'newsletter': instance
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        instance = get_object_or_404(Newsletter, id=newsletter_id) if newsletter_id else None
        form = NewsletterForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('newsletter:detail_summary', newsletter_id)
        context = {
            'newsletter_id': newsletter_id,
            'form': form
        }
        return self.render_to_response(context)

class DraftListView(ListView):
    template_name = 'newsletter/draft/list.html'
    model = Newsletter
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=1)
        return queryset


class RecipientDataBaseCreateUpdateView(TemplateResponseMixin, View):
    template_name = "newsletter/detail/recipient.html"
    NewsletterFormSet = inlineformset_factory(
        Newsletter,
        BranchNewsletter,
        form=BranchNewsletterForm,
        extra=0, can_delete=True
    )

    def get(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        recipient_form_set = self.NewsletterFormSet(instance=newsletter, prefix='branches')
        newsletter_form = NewsletterForm(instance=newsletter)
        context = {
            'recipient_form_set': recipient_form_set,
            'newsletter_id': newsletter_id,
            'newsletter_form': newsletter_form,
            'newsletter': newsletter
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        recipient_form_set = self.NewsletterFormSet(request.POST, instance=newsletter, prefix='branches')
        newsletter_form = NewsletterForm(request.POST, instance=newsletter)
        if recipient_form_set.is_valid() and newsletter_form.is_valid():
            recipient_form_set.save()
            newsletter_form.save()
            return redirect('newsletter:detail_summary', newsletter_id)
        context = {
            'recipient_form_set': recipient_form_set
        }
        return self.render_to_response(context)

class UnderReviewListView(ListView):
    template_name = 'newsletter/under_review/list.html'
    model = Newsletter
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=2)
        return queryset

class UnderReviewConfirmView(TemplateResponseMixin, View):
    template_name = "newsletter/under_review/confirm.html"

    def get(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        context = {
            'newsletter': newsletter
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter.status = 2
        newsletter.save()
        return redirect('newsletter:detail_summary', newsletter_id)

class UnderReviewCancelConfirmView(TemplateResponseMixin, View):
    template_name = "newsletter/under_review/cancel_confirm.html"

    def get(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        context = {
            'newsletter': newsletter
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter.status = 1
        newsletter.save()
        return redirect('newsletter:detail_summary', newsletter_id)

class ReadyToStartListView(ListView):
    template_name = 'newsletter/ready_to_start/list.html'
    model = Newsletter
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=3)
        return queryset

class StartNewsletterView(TemplateResponseMixin, View):
    template_name = 'newsletter/ready_to_start/start_newsletter.html'

    def get(self, request, *args, **kwargs):
        newsletter_id = request.GET.get('newsletter_id')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        context = {
            'newsletter': newsletter
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        newsletter_id = request.POST.get('newsletter_id')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter.status = 5
        newsletter.save()
        return redirect('newsletter:detail_summary', newsletter_id)

class InProgressListView(ListView):
    template_name = 'newsletter/in_progress/list.html'
    model = Newsletter
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=5)
        return queryset

class CompletedListView(ListView):
    template_name = 'newsletter/completed/list.html'
    model = Newsletter
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=6)
        return queryset