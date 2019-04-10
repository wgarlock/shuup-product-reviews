# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import math

from django.db.models import Avg, Sum

from shuup.core.models import Order, Supplier
from shuup_vendor_reviews.models import VendorReviewAggregation


def get_orders_for_review(request):
    """
    Returns an order queryset that contains all products that could be reviewed.
    It is basically any completed orders.
    """
    return Order.objects.complete().filter(
        shop=request.shop,
        customer__in=[request.customer, request.person]
    )


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


def get_stars_from_rating(rating):
    """
    Returns the number of full stars, empty stars and whether it has a half star
    """
    full_stars = math.floor(rating)
    empty_stars = math.floor(5 - rating)
    half_star = (full_stars + empty_stars) < 5
    return (full_stars, empty_stars, half_star)
