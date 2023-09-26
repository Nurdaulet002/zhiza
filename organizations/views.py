from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, DateField, Count, Case, When
from django.db.models.functions import Cast, TruncMonth
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from accounts.models import CustomUser
from customer_request.models import CustomerRequest
from customers.models import Customer
from feedback.models import Rating
from organizations.forms import BranchForm, CustomUserForm, CustomUserUpdateForm
from organizations.models import CompanyUser, Branch


class FeedbackListView(TemplateResponseMixin, View):
    template_name = 'organization/branch/list.html'

    @staticmethod
    def get_date_range(period):
        today = datetime.today()
        if period == "all-time":
            earliest_date = Rating.objects.all().order_by('created').first().created.date()
            return earliest_date, today
        start_date_methods = {
            "week": lambda: today - timedelta(days=6),
            "month": lambda: today.replace(day=1),
            "quarter": lambda: today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1),
            "half-year": lambda: today.replace(month=1, day=1) if today.month > 6 else today.replace(
                year=today.year - 1, month=7, day=1),
            "year": lambda: today.replace(month=1, day=1)
        }
        start_date = start_date_methods.get(period, lambda: None)()

        return start_date, today

    def compute_ratings(self, branch, date_filter):
        customer_requests = CustomerRequest.objects.filter(branch=branch, **date_filter)
        average_rating = customer_requests.aggregate(Avg('rating__rating'))['rating__rating__avg'] or 0
        branch.average_rating = round(average_rating, 2)

        customer_requests_with_comment = customer_requests.filter(rating__comment__isnull=False).exclude(rating__comment__exact='')
        branch.num_ratings_with_comment = customer_requests_with_comment.count()

    def get(self, request, *args, **kwargs):
        branch_search = request.GET.get('branch_search')
        date_range = request.GET.get('date_range', "")

        company_user = get_object_or_404(CompanyUser, user=request.user)
        branches_query = company_user.company.branches.all()

        if branch_search and branch_search != 'all':
            branch_search = int(branch_search)
            branches_query = branches_query.filter(id=branch_search)

        start_date, end_date = self.get_date_range(date_range)
        date_filter = {}
        date_filter_rating = {}
        if start_date and end_date:
            date_filter = {"datetime__range": (start_date, end_date)}
            date_filter_rating = {"created__range": (start_date, end_date)}

        branches = list(branches_query)  # Execute the query only once

        for branch in branches:
            self.compute_ratings(branch, date_filter)

        branches_selectize = Branch.objects.filter(company__companyuser__user=request.user)
        ratings = Rating.objects.filter(customer_request__branch__company__companyuser__user=request.user,
                                        comment__isnull=False, **date_filter_rating).exclude(comment__exact='').order_by('-id')
        context = {
            'branches': branches,
            'branch_search': branch_search,
            'date_range': date_range,
            'branches_selectize': branches_selectize,
            'ratings': ratings
        }

        return self.render_to_response(context)


class BranchDetailView(TemplateResponseMixin, View):
    template_name = 'organization/branch/detail.html'

    @staticmethod
    def get_date_range(period):
        today = datetime.today()
        if period == "week":
            start_date = today - timedelta(days=6)
        elif period == "month":
            start_date = today.replace(day=1)
        elif period == "year":
            start_date = today.replace(day=1, month=1)
        else:
            return None, None
        return start_date, today

    def get(self, request, *args, **kwargs):
        branch_id = self.kwargs.get('branch_id')
        date_range = request.GET.get('date_range', "")
        print(date_range)
        branch = Branch.objects.get(pk=branch_id)
        start_date, end_date = self.get_date_range(date_range)
        date_filter = {}
        if start_date and end_date:
            date_filter = {"created__range": (start_date, end_date)}
        ratings = Rating.objects.filter(customer_request__branch_id=branch_id, comment__isnull=False, **date_filter).exclude(comment__exact='')
        rating_count = ratings.count()
        context = {
            'branch': branch,
            'ratings': ratings,
            'rating_count': rating_count,
            'date_range':date_range
        }
        return self.render_to_response(context)

import locale
locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')

class ReportView(TemplateResponseMixin, View):
    template_name = 'organization/report/report.html'

    def get_date_range(self, range_type):
        today = datetime.today().date()
        if range_type == "all-time":
            earliest_date = Rating.objects.all().order_by('created').first().created.date()
            return earliest_date, today, "month"
        start_date_methods = {
            "week": lambda: today - timedelta(days=6),
            "month": lambda: today.replace(day=1),
            "quarter": lambda: today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1),
            "half-year": lambda: today.replace(month=1, day=1) if today.month > 6 else today.replace(
                year=today.year - 1, month=7, day=1),
            "year": lambda: today.replace(month=1, day=1)
        }
        start_date = start_date_methods.get(range_type, lambda: None)()

        if range_type in ["year", "half-year", "quarter"]:
            aggregation_level = "month"
        else:
            aggregation_level = "day"

        return start_date, today, aggregation_level

    def get_base_filter(self, request, start_date, end_date, branch_id):
        base_filter = {
            'customer_request__branch__company__companyuser__user': request.user,
            'created__range': (start_date, end_date)
        }
        if branch_id != 'all':
            base_filter['customer_request__branch_id'] = branch_id
        return base_filter

    def get_rating_counts(self, base_filter):
        ratings_counts = {}
        for rating_value in range(1, 6):
            current_filter = base_filter.copy()
            current_filter['rating'] = rating_value
            ratings_counts[rating_value] = Rating.objects.filter(**current_filter).count()
        return ratings_counts

    def get_customer_data(self, branch_id):
        base_customer_filter = {
            'branch__company__companyuser__user': self.request.user
        }
        if branch_id != 'all':
            base_customer_filter['branch_id'] = branch_id

        customer_requests = CustomerRequest.objects.values('customer').annotate(request_count=Count('customer'))
        customers_purchase_only_once = customer_requests.filter(**base_customer_filter, request_count=1).count()
        customers_purchase_more_than_one = customer_requests.filter(**base_customer_filter, request_count__gt=1).count()

        return customers_purchase_only_once, customers_purchase_more_than_one

    def get(self, request, *args, **kwargs):
        range_type = request.GET.get('range_type', 'month')
        branch_id = request.GET.get('branch')
        start_date, end_date, aggregation_level = self.get_date_range(range_type)

        if not branch_id:
            branch_id = 'all'
        base_filter = self.get_base_filter(request, start_date, end_date, branch_id)

        if aggregation_level == "day":
            daily_avg_ratings = Rating.objects.filter(**base_filter).annotate(
                date=Cast('created', DateField())
            ).values('date').annotate(
                avg_rating=Avg('rating')
            ).order_by('date')
            dates = [item['date'].strftime('%Y-%m-%d') for item in daily_avg_ratings]
        else:  # month
            daily_avg_ratings = Rating.objects.filter(**base_filter).annotate(
                month=TruncMonth('created')
            ).values('month').annotate(
                avg_rating=Avg('rating')
            ).order_by('month')
            dates = [item['month'].strftime('%B %Y') for item in daily_avg_ratings]

        avg_ratings = [item['avg_rating'] for item in daily_avg_ratings]

        try:
            company_of_current_user = CompanyUser.objects.get(user=request.user).company
            branches = company_of_current_user.branches.all()
        except CompanyUser.DoesNotExist:
            return self.render_to_response({'error': "User is not associated with any company"})

        ratings_counts = self.get_rating_counts(base_filter)

        customers_purchase_only_once, customers_purchase_more_than_one = self.get_customer_data(branch_id)
        total_purchase = customers_purchase_only_once + customers_purchase_more_than_one
        purchase_frequency = round(total_purchase / customers_purchase_only_once, 2) if customers_purchase_only_once else 0
        repeat_purchase_frequency = round(customers_purchase_more_than_one / total_purchase, 2) if total_purchase else 0

        branch_ratings = (Branch.objects.filter(company__companyuser__user=self.request.user,
                                                customerrequest__rating__created__range=(start_date, end_date))
                          .annotate(avg_rating=Avg('customerrequest__rating__rating'),
                                    rating_1_count=Count(Case(When(customerrequest__rating__rating=1, then=1))),
                                    rating_2_count=Count(Case(When(customerrequest__rating__rating=2, then=1))),
                                    rating_3_count=Count(Case(When(customerrequest__rating__rating=3, then=1))),
                                    rating_4_count=Count(Case(When(customerrequest__rating__rating=4, then=1))),
                                    rating_5_count=Count(Case(When(customerrequest__rating__rating=5, then=1)))
                                    )
                          .values('title', 'avg_rating', 'rating_1_count', 'rating_2_count', 'rating_3_count', 'rating_4_count', 'rating_5_count')).order_by('-avg_rating')

        branch_ratings_dates = [item['title'] for item in branch_ratings]
        branch_ratings_avg_ratings = [item['avg_rating'] for item in branch_ratings]
        branch_ratings_1_count = [item['rating_1_count'] for item in branch_ratings]
        branch_ratings_2_count = [item['rating_2_count'] for item in branch_ratings]
        branch_ratings_3_count = [item['rating_3_count'] for item in branch_ratings]
        branch_ratings_4_count = [item['rating_4_count'] for item in branch_ratings]
        branch_ratings_5_count = [item['rating_5_count'] for item in branch_ratings]

        if branch_id != 'all':
            branch_id = int(branch_id)

        context = {
            'labels': dates,
            'data': avg_ratings,
            'range_type': range_type,
            'branches': branches,
            'branch_id': branch_id,
            'ratings_counts': ratings_counts,
            'customers_purchase_only_once': customers_purchase_only_once,
            'customers_purchase_more_than_one': customers_purchase_more_than_one,
            'purchase_frequency': purchase_frequency,
            'repeat_purchase_frequency': repeat_purchase_frequency,
            'branch_ratings_dates': branch_ratings_dates,
            'branch_ratings_avg_ratings': branch_ratings_avg_ratings,
            'branch_ratings_1_count': branch_ratings_1_count,
            'branch_ratings_2_count': branch_ratings_2_count,
            'branch_ratings_3_count': branch_ratings_3_count,
            'branch_ratings_4_count': branch_ratings_4_count,
            'branch_ratings_5_count': branch_ratings_5_count
        }
        return self.render_to_response(context)


class BranchMixin(LoginRequiredMixin):
    model = Branch
    success_url = reverse_lazy('organization:branch_list')


class BranchEditMixin(BranchMixin):
    form_class = BranchForm


# Список филиалов
class BranchListView(BranchMixin, ListView):
    template_name = 'settings/branches/list.html'
    context_object_name = 'branches'

    def get_queryset(self):
        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
        except CompanyUser.DoesNotExist:
            return Branch.objects.none()
        return company_user.company.branches.all()


# Создать филиал
class BranchCreateView(BranchEditMixin, CreateView):
    template_name = 'settings/branches/create.html'

    def form_valid(self, form):
        branch = form.save()

        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
            company_user.company.branches.add(branch)
        except CompanyUser.DoesNotExist:
            pass

        return super().form_valid(form)


# Обновить филиал
class BranchUpdateView(BranchEditMixin, UpdateView):
    template_name = 'settings/branches/update.html'


# Удалить филиал
class BranchDeleteView(BranchMixin, DeleteView):
    template_name = 'settings/branches/delete.html'


class EmployeeMixin(LoginRequiredMixin):
    model = CustomUser
    success_url = reverse_lazy('organization:employee_list')


class EmployeeEditMixin(EmployeeMixin):
    form_class = CustomUserForm


# Список филиалов
class EmployeeListView(EmployeeMixin, ListView):
    template_name = 'settings/employees/list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
            branches = company_user.company.branches.all()
        except CompanyUser.DoesNotExist:
            return Branch.objects.none()
        return CustomUser.objects.filter(branch__in=branches)

from django.contrib import messages
# Создать филиал
class EmployeeCreateView(EmployeeMixin, CreateView):
    template_name = 'settings/employees/create.html'
    form_class = CustomUserForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data['password'])
        user.save()

        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
            CompanyUser.objects.create(user=user, company=company_user.company)
        except CompanyUser.DoesNotExist:
            pass

        return super().form_valid(form)

    def get_form(self, form_class=None):
        return CustomUserForm(user=self.request.user, **self.get_form_kwargs())


# Обновить филиал
class EmployeeUpdateView(EmployeeMixin, UpdateView):
    template_name = 'settings/employees/update.html'
    form_class = CustomUserUpdateForm

    def form_valid(self, form):
        user = form.save(commit=False)

        # Ensure old_password is provided if there's a new password
        if form.cleaned_data['password'] and not form.cleaned_data['old_password']:
            form.add_error('old_password', 'You must enter your old password to change it.')
            return self.form_invalid(form)

        # Check if the old_password is correct
        if form.cleaned_data['old_password'] and not check_password(form.cleaned_data['old_password'], user.password):
            form.add_error('old_password', 'Old password is incorrect.')
            return self.form_invalid(form)

        # If password has changed, hash and update it
        if form.cleaned_data['password']:
            user.password = make_password(form.cleaned_data['password'])

        user.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        return CustomUserUpdateForm(user=self.request.user, **self.get_form_kwargs())


# Удалить филиал
class EmployeeDeleteView(EmployeeMixin, DeleteView):
    template_name = 'settings/employees/delete.html'



