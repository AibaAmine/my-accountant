from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Search")
    user_type = django_filters.ChoiceFilter(choices=User.USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ["search", "user_type"]

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(full_name__icontains=value)
                | Q(company_name__icontains=value)
                | Q(email__icontains=value)
            )
        return queryset

