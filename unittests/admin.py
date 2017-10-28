# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import (
    TestType,
    Operator,
    PolarimeterTest,
    AdcOffset,
    DetectorOutput
)

for x in (TestType,
          Operator,
          PolarimeterTest,
          AdcOffset,
          DetectorOutput):
    admin.site.register(x)
