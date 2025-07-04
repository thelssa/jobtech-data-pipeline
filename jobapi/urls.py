from django.urls import path
from .views import JobOfferListView
from .views import SalaryDailyView

urlpatterns = [
    path('offers/', JobOfferListView.as_view(), name='joboffer-list'),
    path('v1/salary-daily/', SalaryDailyView.as_view(), name='salary-daily'),
]
