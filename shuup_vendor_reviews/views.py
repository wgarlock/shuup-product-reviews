# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView

from shuup.core.models import Supplier
from shuup.front.views.dashboard import DashboardViewMixin
from shuup_product_reviews.models import ReviewStatus
from shuup_product_reviews.views import BaseCommentsView
from shuup_vendor_reviews.models import VendorReview
from shuup_vendor_reviews.utils import get_pending_vendors_reviews


class VendorReviewForm(forms.Form):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), widget=forms.HiddenInput())
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "rating-input"}),
        max_value=5,
        min_value=1,
        required=False
    )
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2)))
    would_recommend = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(VendorReviewForm, self).__init__(*args, **kwargs)

    def save(self):
        data = self.cleaned_data
        if data.get("rating"):
            VendorReview.objects.update_or_create(
                supplier=data["supplier"],
                reviewer=self.request.person,
                shop=self.request.shop,
                defaults=dict(
                    rating=data["rating"],
                    comment=data["comment"],
                    would_recommend=data["would_recommend"],
                    status=ReviewStatus.PENDING
                )
            )


VendorReviewModelFormset = forms.formset_factory(VendorReviewForm, extra=0)


class VendorReviewsView(DashboardViewMixin, TemplateView):
    template_name = "shuup_vendor_reviews/vendor_reviews.jinja"

    def get_context_data(self, **kwargs):
        context = super(VendorReviewsView, self).get_context_data(**kwargs)
        pending_suppliers_reviews = get_pending_vendors_reviews(self.request)
        context["reviews"] = VendorReview.objects.for_reviewer(self.request.shop, self.request.person)

        if pending_suppliers_reviews.exists():
            initial_values = [
                dict(supplier=supplier)
                for supplier in pending_suppliers_reviews
            ]
            context["reviews_formset"] = VendorReviewModelFormset(
                form_kwargs=dict(request=self.request),
                initial=initial_values
            )

        return context

    def post(self, request):
        formset = VendorReviewModelFormset(request.POST, form_kwargs=dict(request=self.request))
        if formset.is_valid():
            with atomic():
                for form in formset.forms:
                    form.save()

        return HttpResponseRedirect(reverse("shuup:vendor_reviews"))


class VendorReviewCommentsView(BaseCommentsView):
    view_name = "vendor_review_comments"

    def get_reviews_page(self):
        supplier = Supplier.objects.filter(pk=self.kwargs["pk"], shops=self.request.shop).first()
        queryset = VendorReview.objects.approved().filter(
            supplier=supplier, shop=self.request.shop, comment__isnull=False
        ).order_by("-created_on")

        paginator = Paginator(queryset, settings.PRODUCT_REVIEWS_PAGE_SIZE)
        page = self.request.GET.get('page')

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)
