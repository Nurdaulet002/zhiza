import random
import string
from django.contrib import messages

from django.http import HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist

from customer_request.models import CustomerRequest
from customers.models import Customer
from organizations.models import CompanyUser, Branch
from raffle_prizes.apscheduler import schedule_send_winner_message
from raffle_prizes.forms import RafflePrizeForm, RafflePrizeSettingForm, ParticipatingBranchSelectForm
from raffle_prizes.models import RafflePrize, ParticipatingBranch, Winner, PromoCode, CheckingCode


class RafflePrizeListView(ListView):
    template_name = 'raffle_prizes/list.html'
    context_object_name = 'raffle_prizes'

    def get_queryset(self):
        company_user = get_object_or_404(CompanyUser, user=self.request.user)
        raffle_prizes = RafflePrize.objects.filter(company=company_user.company)

        for raffle_prize in raffle_prizes:
            participating_branches = ParticipatingBranch.objects.filter(raffle_prize=raffle_prize)
            customer_count = 0

            for participating_branch in participating_branches:
                customers = Customer.objects.filter(branch=participating_branch.branch)
                customer_count += customers.count()

            raffle_prize.customer_count = customer_count

            winners = Winner.objects.filter(raffle_prize=raffle_prize)
            raffle_prize.winners_count = winners.count()

        return raffle_prizes


class RufflePrizeCreateView(CreateView):
    model = RafflePrize
    form_class = RafflePrizeForm
    template_name = 'raffle_prizes/form.html'
    success_url = reverse_lazy('raffle_prizes:raffle_prize_list')

    def form_valid(self, form):
        form.instance.company = self.request.user.companyuser.company
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.request.GET.get('url')
        return context


class RufflePrizeUpdateView(UpdateView):
    model = RafflePrize
    form_class = RafflePrizeForm
    template_name = 'raffle_prizes/form.html'
    success_url = reverse_lazy('raffle_prizes:raffle_prize_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.request.GET.get('url')
        return context


class RufflePrizeDeleteView(DeleteView):
    model = RafflePrize
    template_name = 'raffle_prizes/delete.html'
    success_url = reverse_lazy('raffle_prizes:raffle_prize_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.request.GET.get('url')
        return context


class RufflePrizeSettingView(TemplateResponseMixin, View):
    template_name = 'raffle_prizes/detail/settings.html'

    def get(self, request, *args, **kwargs):
        raffle_prize_id = self.kwargs.get('pk')
        raffle_prize = RafflePrize.objects.get(pk=raffle_prize_id)
        context = {
            'raffle_prize': raffle_prize
        }
        return self.render_to_response(context)


class RufflePrizeSettingFormView(UpdateView):
    model = RafflePrize
    form_class = RafflePrizeSettingForm
    template_name = 'raffle_prizes/detail/settings_form.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['raffle_prize'] = RafflePrize.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_success_url(self, **kwargs):
        pk = self.kwargs.get('pk')
        return reverse_lazy('raffle_prizes:settings', kwargs={'pk': pk})




class ParticipatingBranchListView(TemplateResponseMixin, View):
    template_name = 'raffle_prizes/detail/company_branches_list.html'

    def get(self, request, *args, **kwargs):
        raffle_prize_id = self.kwargs.get('pk')
        raffle_prize = RafflePrize.objects.get(pk=raffle_prize_id)
        selected_branches = ParticipatingBranch.objects.filter(raffle_prize=raffle_prize).values_list('branch__id',
                                                                                                      flat=True)

        form = ParticipatingBranchSelectForm(initial={'participating_branches': selected_branches})

        context = {
            'form': form,
            'raffle_prize_id': raffle_prize_id,
            'selected_branches': selected_branches
        }

        return self.render_to_response(context)


class ParticipatingBranchSaveView(View):

    def post(self, request, *args, **kwargs):
        raffle_prize_id = request.POST.get('raffle_prize_id')
        raffle_prize = RafflePrize.objects.get(pk=raffle_prize_id)

        # Получаем выбранные филиалы из формы
        selected_branches = request.POST.getlist('participating_branches')

        # Если не выбрано ни одного филиала, удаляем все связанные записи
        if not selected_branches:
            ParticipatingBranch.objects.filter(raffle_prize=raffle_prize).delete()
            return redirect('raffle_prizes:settings', raffle_prize_id)

        # Если выбраны филиалы, обновляем данные
        current_branches = ParticipatingBranch.objects.filter(raffle_prize=raffle_prize)
        current_branch_ids = [branch.branch_id for branch in current_branches]

        # Добавляем новые филиалы, если они были выбраны
        for branch_id in selected_branches:
            if int(branch_id) not in current_branch_ids:
                ParticipatingBranch.objects.create(raffle_prize=raffle_prize, branch_id=branch_id)

        # Удаляем те филиалы, которые были ранее выбраны, но сейчас не выбраны
        for branch in current_branches:
            if branch.branch_id not in [int(i) for i in selected_branches]:
                branch.delete()

        return redirect('raffle_prizes:settings', raffle_prize_id)

class WinnersDetailView(TemplateResponseMixin, View):
    template_name = 'raffle_prizes/detail/winners.html'

    def get(self, request, *args, **kwargs):
        raffle_prize_id = self.kwargs.get('pk')
        raffle_prize = RafflePrize.objects.get(pk=raffle_prize_id)
        start_date = raffle_prize.date_start
        end_date = raffle_prize.date_end
        winners = Winner.objects.filter(raffle_prize=raffle_prize)


        customer_count = 0
        participating_branches = ParticipatingBranch.objects.filter(raffle_prize=raffle_prize)

        for participating_branch in participating_branches:
            customers = Customer.objects.filter(branch=participating_branch.branch, created_at__date__gte=start_date, created_at__date__lte=end_date)
            customer_count += customers.count()

        raffle_prize.customer_count = customer_count

        context = {
            'winners': winners,
            'raffle_prize': raffle_prize,
        }

        return self.render_to_response(context)


class ChoiceRandomWinner(View):
    def post(self, request, *args, **kwargs):
        raffle_prize_id = self.kwargs.get('pk')
        raffle_prize = RafflePrize.objects.get(pk=raffle_prize_id)
        start_date = raffle_prize.date_start
        end_date = raffle_prize.date_end

        participating_branches = ParticipatingBranch.objects.filter(raffle_prize=raffle_prize).values_list('branch_id',
                                                                                                           flat=True)
        customer_ids = list(Customer.objects.filter(
            branch_id__in=participating_branches,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values_list('id', flat=True))

        if not customer_ids:
            return redirect('raffle_prizes:participating_branch_winners', raffle_prize_id)

        attempts = len(customer_ids)  # максимальное количество попыток
        winner_created = False

        while attempts > 0:
            selected_customer_id = random.choice(customer_ids)
            selected_customer = Customer.objects.get(id=selected_customer_id)
            if not Winner.objects.filter(raffle_prize=raffle_prize, customer=selected_customer).exists():
                Winner.objects.create(raffle_prize=raffle_prize, customer=selected_customer)
                winner_created = True
                break
            else:
                customer_ids.remove(selected_customer_id)
                attempts -= 1

        if winner_created and raffle_prize.status == 2:
            raffle_prize.status = 1
            raffle_prize.save()

        if not winner_created:
            pass

        return redirect('raffle_prizes:participating_branch_winners', raffle_prize_id)


class PromoCodeView(TemplateResponseMixin, View):
    template_name = 'customer_request/promo_code/search_promocode.html'

    def get(self, request, *args, **kwargs):
        promocode = self.kwargs.get('promocode', None)
        if not promocode:
            promocode = request.GET.get('promocode', None)
        context = {
        }

        if promocode:
            try:
                promocode = promocode.replace(" ", "")
                promocode_obj = PromoCode.objects.get(promo_code=promocode)
                ruffle_prize = promocode_obj.winner.raffle_prize
                context = {
                    'promocode': promocode,
                    'ruffle_prize': ruffle_prize,
                    'promocode_obj': promocode_obj
                }
            except ObjectDoesNotExist:
                context = {
                    'promocode': promocode,
                }
        return self.render_to_response(context)


class GenerateCode(View):

    def post(self, request, *args, **kwargs):
        promocode = request.POST.get('promocode')
        winner_id = request.POST.get('winner_id')

        try:
            winner = Winner.objects.get(id=winner_id)
        except Winner.DoesNotExist:
            return HttpResponseServerError("Winner not found", status=500)



        characters = string.digits
        while True:
            # Попытка получить связанный объект CheckingCode
            try:
                checking_code = CheckingCode.objects.get(winner=winner)
            except CheckingCode.DoesNotExist:
                checking_code = None
            if checking_code is None:
                random_selection = ''.join(random.choice(characters) for _ in range(4))
                if not CheckingCode.objects.filter(code=random_selection).exists():
                    checking_code = CheckingCode.objects.create(code=random_selection, winner=winner)
                    message = str(checking_code.code)
                    data = {
                        'phone_number': checking_code.winner.customer.phone_number,
                        'message': message,
                        'instance_id': checking_code.winner.customer.branch.integration.instance_id,
                        'token': checking_code.winner.customer.branch.integration.token,
                    }
                    schedule_send_winner_message(data=data)
                    break
            else:
                try:
                    if checking_code is not None:
                        checking_code.delete()
                except Exception as e:
                    print(e)
        return redirect('raffle_prizes:checking_sms', promocode)


class CheckingSMSView(TemplateResponseMixin, View):
    template_name = 'customer_request/promo_code/checking_sms.html'

    def get(self, request, *args, **kwargs):
        promocode = self.kwargs.get('promocode')
        promocode_obj = PromoCode.objects.get(promo_code=promocode)
        return self.render_to_response({'promocode': promocode, 'promocode_obj': promocode_obj})

    def post(self, request, *args, **kwargs):
        promocode = self.kwargs.get('promocode')
        sms_code = request.POST.get('sms_code')
        winner_id = request.POST.get('winner_id')
        winner = Winner.objects.get(id=winner_id)
        digits_only = sms_code.replace(" ", "")
        try:
            CheckingCode.objects.get(code=digits_only, winner=winner)
            winner.status = 1
            winner.save()
            return redirect('raffle_prizes:search_promocode', promocode)
        except CheckingCode.DoesNotExist:
            messages.error(request, "Код не совпадает! Попробуйте еще раз")
        promocode_obj = PromoCode.objects.get(promo_code=promocode)
        return self.render_to_response({'promocode': promocode, 'promocode_obj': promocode_obj})