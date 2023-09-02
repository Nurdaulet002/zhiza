from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from newsletter.forms import NewsletterForm, BranchNewsletterForm, BranchNewsletterSelectForm
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
        form = NewsletterForm(request.POST, request.FILES, instance=instance)
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

    def get(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter_form = NewsletterForm(instance=newsletter)
        context = {
            'newsletter_id': newsletter_id,
            'newsletter_form': newsletter_form,
            'newsletter': newsletter
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        newsletter_form = NewsletterForm(request.POST, instance=newsletter)
        if newsletter_form.is_valid():
            newsletter_form.save()
            return redirect('newsletter:detail_summary', newsletter_id)
        context = {
            'newsletter_form': newsletter_form
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


class BranchNewsletterListView(TemplateResponseMixin, View):
    template_name = 'newsletter/detail/company_branches_list.html'

    def get(self, request, *args, **kwargs):
        newsletter_id = self.kwargs.get('pk')
        newsletter = Newsletter.objects.get(pk=newsletter_id)
        selected_branches = BranchNewsletter.objects.filter(newsletter=newsletter).values_list('branch__id', flat=True)

        form = BranchNewsletterSelectForm(initial={'branch_newsletter': selected_branches})

        context = {
            'form': form,
            'newsletter_id': newsletter_id,
            'selected_branches': selected_branches
        }

        return self.render_to_response(context)


class BranchNewsletterSaveView(View):

    def post(self, request, *args, **kwargs):
        newsletter_id = request.POST.get('newsletter_id')
        newsletter = Newsletter.objects.get(pk=newsletter_id)

        # Получаем выбранные филиалы из формы
        selected_branches = request.POST.getlist('branch_newsletter')

        # Если не выбрано ни одного филиала, удаляем все связанные записи
        if not selected_branches:
            BranchNewsletter.objects.filter(newsletter=newsletter).delete()
            return redirect('newsletter:recipient_create_update', newsletter_id)

        # Если выбраны филиалы, обновляем данные
        current_branches = BranchNewsletter.objects.filter(newsletter=newsletter)
        current_branch_ids = [branch.branch_id for branch in current_branches]

        # Добавляем новые филиалы, если они были выбраны
        for branch_id in selected_branches:
            if int(branch_id) not in current_branch_ids:
                BranchNewsletter.objects.create(newsletter=newsletter, branch_id=branch_id)

        # Удаляем те филиалы, которые были ранее выбраны, но сейчас не выбраны
        for branch in current_branches:
            if branch.branch_id not in [int(i) for i in selected_branches]:
                branch.delete()

        return redirect('newsletter:recipient_create_update', newsletter_id)