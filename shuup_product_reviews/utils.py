# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import math

from django.db.models import Avg, Sum

from shuup.core.models import Order, Product, ProductMode
from shuup_product_reviews.models import ProductReviewAggregation

ACCEPTED_PRODUCT_MODES = [
    ProductMode.NORMAL,
    ProductMode.SIMPLE_VARIATION_PARENT,
    ProductMode.VARIABLE_VARIATION_PARENT,
    ProductMode.VARIATION_CHILD
]


def get_orders_for_review(request):
    """
    Returns an order queryset that contains all products that could be reviewed.
    It is basically any completed orders.
    """
    return Order.objects.complete().filter(
        shop=request.shop,
        customer__in=[request.customer, request.person]
    )


def get_pending_products_reviews(request):
    """
    Returns a Product queryset that contains all products
    that can be reviewed by the current request shop and contact
    """
    orders = Order.objects.complete().filter(
        shop=request.shop,
        customer__in=[request.customer, request.person]
    ).distinct()
    products = Product.objects.all_except_deleted(shop=request.shop).filter(
        order_lines__order__in=orders,
        mode__in=[ProductMode.NORMAL, ProductMode.VARIATION_CHILD]
    ).distinct()

    return products.exclude(product_reviews__reviewer=request.person)


def is_product_valid_mode(product):
    """
    Check whether product mode is valid for having reviews attached
    """
    return product.mode in ACCEPTED_PRODUCT_MODES


def get_reviews_aggregation_for_product(product):
    """
    Calculate the reviews totals for a giving product
    """
    product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
    return ProductReviewAggregation.objects.filter(product_id__in=product_ids).aggregate(
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


def render_product_review_ratings(product, customer_ratings_title=None, show_recommenders=False):
    """
    Render the star rating template for a given product and options.
    Returns None if no reviews exists for product
    """
    from django.template import loader

    if is_product_valid_mode(product):
        product_rating = get_reviews_aggregation_for_product(product)
        rating = product_rating["rating"]
        if rating:
            (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)
            context = {
                "half_star": half_star,
                "full_stars": full_stars,
                "empty_stars": empty_stars,
                "reviews": product_rating["reviews"],
                "rating": rating,
                "customer_ratings_title": customer_ratings_title,
                "show_recommenders": show_recommenders
            }
            return loader.render_to_string("shuup_product_reviews/plugins/star_rating.jinja", context=context)
