from datetime import datetime, timedelta
from openpyxl import Workbook

from django.shortcuts import render
from django.views.generic.base import View, TemplateResponseMixin
from django.http import HttpResponse

from customers.models import Customer
from organizations.models import CompanyUser


class CustomerListView(TemplateResponseMixin, View):
    template_name = 'customers/list.html'

    def get_date_range(self, range_type):
        today = datetime.today().date()
        start_date_methods = {
            "week": lambda: today - timedelta(days=6),
            "month": lambda: today.replace(day=1),
            "half-year": lambda: today.replace(month=1, day=1) if today.month > 6 else today.replace(
                year=today.year - 1, month=7, day=1),
            "year": lambda: today.replace(month=1, day=1)
        }
        start_date = start_date_methods.get(range_type, lambda: None)()
        return start_date, today

    def get(self, request, *args, **kwargs):
        branch_id = request.GET.get('branch', 'all')
        range_type = request.GET.get('range_type', 'month')
        start_date, end_date = self.get_date_range(range_type)

        base_filter = {
            'branch__company__companyuser__user': request.user,
            'created_at__range': (start_date, end_date),
        }
        if branch_id != 'all':
            base_filter['branch_id'] = branch_id
            branch_id = int(branch_id)
        customers = Customer.objects.filter(**base_filter)

        try:
            company_of_current_user = CompanyUser.objects.get(user=request.user).company
            branches = company_of_current_user.branches.all()
        except CompanyUser.DoesNotExist:
            return self.render_to_response({'error': "User is not associated with any company"})

        context = {
            'customers': customers,
            'branch_id': branch_id,
            'range_type': range_type,
            'branches': branches,
        }
        return self.render_to_response(context)


class ExportCustomersView(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="customers.xlsx"'

        wb = self._create_workbook()
        wb.save(response)
        return response

    def _create_workbook(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Клиенты"

        # Заголовки столбцов
        columns = ['#', 'Номер телефона', 'Филиал', 'Клиент с']
        for col_num, column_title in enumerate(columns, 1):
            col_letter = chr(64 + col_num)
            ws['{}1'.format(col_letter)] = column_title
            ws.column_dimensions[col_letter].width = 15

        customers = Customer.objects.all()
        for idx, customer in enumerate(customers, 2):
            ws.cell(row=idx, column=1, value=idx-1)
            ws.cell(row=idx, column=2, value=customer.phone_number)
            ws.cell(row=idx, column=3, value=customer.branch.title)
            ws.cell(row=idx, column=4, value=customer.created_at.strftime('%Y-%m-%d'))

        return wb
