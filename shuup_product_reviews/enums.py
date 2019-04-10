# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class ReviewStatus(Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3

    class Labels:
        PENDING = _("Pending")
        APPROVED = _("Approved")
        REJECTED = _("Rejected")
