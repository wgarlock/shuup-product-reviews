# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.templatetags.static import static

from shuup.utils.djangoenv import has_installed
from shuup.xtheme.resources import add_resource


def add_resources(context, content):
    if has_installed("shuup_product_reviews"):
        return

    request = context.get("request")
    if request:
        match = request.resolver_match
        if match and match.app_name == "shuup_admin":
            return

    add_resource(context, "head_end", "%s?v=0.3.6.css" % static("shuup_vendor_reviews/shuup_vendor_reviews.css"))
    add_resource(context, "body_end", "%s?v=0.3.6.js" % static("shuup_vendor_reviews/shuup_vendor_reviews.js"))
