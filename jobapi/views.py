from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import JobOffer
from .serializers import JobOfferSerializer
from django.utils import timezone
import numpy as np

class JobOfferListView(generics.ListAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company', 'sector', 'skills', 'country']
    ordering_fields = ['salary_min', 'salary_max']

class SalaryDailyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        country = request.GET.get('country')
        skill = request.GET.get('skill')
        today = timezone.now().date()
        qs = JobOffer.objects.all()
        if country:
            qs = qs.filter(country=country)
        if skill:
            qs = qs.filter(skills__icontains=skill)
        salaries = qs.values_list('salary_min', 'salary_max')
        all_salaries = []
        for sal_min, sal_max in salaries:
            if sal_min and sal_max:
                all_salaries.append((sal_min + sal_max) / 2)
            elif sal_min:
                all_salaries.append(sal_min)
            elif sal_max:
                all_salaries.append(sal_max)
        if not all_salaries:
            return Response({"date": str(today), "count": 0, "median": None, "distribution": []})
        median = float(np.median(all_salaries))
        distribution = np.histogram(all_salaries, bins=10)[0].tolist()
        count = len(all_salaries)
        return Response({
            "date": str(today),
            "count": count,
            "median": median,
            "distribution": distribution,
        })
