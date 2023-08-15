from django.shortcuts import render
from django.views.generic.base import TemplateResponseMixin, View

from feedback.models import Rating
from organizations.models import CompanyUser, Branch


class BranchListView(TemplateResponseMixin, View):
    template_name = 'organization/branch/list.html'

    def get(self, request, *args, **kwargs):
        search_text = request.GET.get('search_text')
        company_user = CompanyUser.objects.get(user=request.user)
        branches = company_user.company.branches.all()
        if search_text:
            branches = company_user.company.branches.filter(title__icontains=search_text)
            context = {
                'branches': branches,
                'search_text': search_text
            }
            return self.render_to_response(context)
        context = {
            'branches': branches
        }
        return self.render_to_response(context)

class BranchDetailView(TemplateResponseMixin, View):
    template_name = 'organization/branch/detail.html'

    def get(self, request, *args, **kwargs):
        branch_id = self.kwargs.get('pk')
        branch = Branch.objects.get(pk=branch_id)
        ratings = Rating.objects.filter(customer_request__branch_id=branch_id)
        rating_count = ratings.count()
        context = {
            'branch': branch,
            'ratings': ratings,
            'rating_count': rating_count
        }
        return self.render_to_response(context)