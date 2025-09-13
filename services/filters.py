import django_filters
from django_filters import rest_framework as filters
from .models import Service, ServiceCategory
from django.db.models import Q


class ServiceFilter(django_filters.FilterSet):
    # Search functionality
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # Category filters
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=ServiceCategory.objects.filter(is_active=True),
        field_name="categories",
        to_field_name="id",
    )

    # Geographic location filter
    location = django_filters.MultipleChoiceFilter(
        choices=Service.WILAYA_CHOICES, field_name="location"
    )

    # Price range filters
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Duration filters
    duration_unit = django_filters.MultipleChoiceFilter(
        choices=Service.DURATION_CHOICES, field_name="duration_unit"
    )

    min_duration = django_filters.NumberFilter(
        field_name="estimated_duration", lookup_expr="gte"
    )
    max_duration = django_filters.NumberFilter(
        field_name="estimated_duration", lookup_expr="lte"
    )

    # Featured services
    is_featured = django_filters.BooleanFilter(field_name="is_featured")

    # Date filters
    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Service
        fields = [
            "search",
            "categories",
            "location",
            "min_price",
            "max_price",
            "duration_unit",
            "min_duration",
            "max_duration",
            "is_featured",
            "created_after",
            "created_before",
        ]

    # add profile search

    def filter_search(self, queryset, name, value):
        """Search across multiple fields in services"""
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(description__icontains=value)
                | Q(user__full_name__icontains=value)
                | Q(location__icontains=value)
                | Q(categories__name__icontains=value)
            ).distinct()
