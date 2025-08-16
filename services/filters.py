import django_filters
from django_filters import rest_framework as filters
from .models import Service, ServiceCategory
from django.db.models import Q


class ServiceFilter(django_filters.FilterSet):
    # Search functionality
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # Category filters
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=ServiceCategory.objects.filter(is_active=True),
        field_name="category",
        to_field_name="id",
    )

    # Location preference filters
    location_preference = django_filters.MultipleChoiceFilter(
        choices=Service.LOCATION_CHOICES, field_name="location_preference"
    )

    # Experience level filters
    experience_level_required = django_filters.MultipleChoiceFilter(
        choices=Service.EXPERIENCE_LEVEL_CHOICES, field_name="experience_level_required"
    )

    # Urgency level filters
    urgency_level = django_filters.MultipleChoiceFilter(
        choices=Service.URGENCY_CHOICES, field_name="urgency_level"
    )

    # Price range filters
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Price negotiable filter
    price_negotiable = django_filters.BooleanFilter(field_name="price_negotiable")

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
            "category",
            "location_preference",
            "experience_level_required",
            "urgency_level",
            "min_price",
            "max_price",
            "price_negotiable",
            "duration_unit",
            "min_duration",
            "max_duration",
            "is_featured",
            "created_after",
            "created_before",
        ]

    def filter_search(self, queryset, name, value):
        """Search across multiple fields in services"""
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(description__icontains=value)
                | Q(skills_keywords__icontains=value)
                | Q(requirements_notes__icontains=value)
                | Q(user__full_name__icontains=value)
                | Q(user__company_name__icontains=value)
                | Q(category__name__icontains=value)
            )
        return queryset
