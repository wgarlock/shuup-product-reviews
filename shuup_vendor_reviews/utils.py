# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.db.models import Avg, Sum

from shuup.core.models import Supplier
from shuup_product_reviews.utils import get_orders_for_review
from shuup_vendor_reviews.models import VendorReviewAggregation


def get_pending_vendors_reviews(request):
    return Supplier.objects.enabled().filter(shops=request.shop).filter(
        order_lines__order__in=get_orders_for_review(request)
    ).distinct()


def get_reviews_aggregation_for_supplier(supplier):
    return VendorReviewAggregation.objects.filter(supplier=supplier).aggregate(
        rating=Avg("rating"),
        reviews=Sum("review_count"),
        would_recommend=Sum("would_recommend")
    )
