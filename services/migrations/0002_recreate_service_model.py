
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Drop the existing service table
        migrations.DeleteModel(
            name="Service",
        ),
        # Create ServiceCategory model
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Service Category",
                "verbose_name_plural": "Service Categories",
                "db_table": "service_categories",
                "ordering": ["name"],
            },
        ),
        # Create new Service model
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "service_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("service_title", models.CharField(max_length=255)),
                ("service_description", models.TextField()),
                ("estimated_duration", models.PositiveIntegerField(default=1)),
                (
                    "duration_unit",
                    models.CharField(
                        choices=[
                            ("hours", "Hours"),
                            ("days", "Days"),
                            ("weeks", "Weeks"),
                            ("months", "Months"),
                        ],
                        default="days",
                        max_length=20,
                    ),
                ),
                (
                    "service_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("can_be_discussed", models.BooleanField(default=False)),
                (
                    "attachments",
                    cloudinary.models.CloudinaryField(
                        blank=True, null=True, verbose_name="file"
                    ),
                ),
                (
                    "service_location",
                    models.CharField(
                        choices=[
                            ("online", "Online"),
                            ("client_office", "Client's Office"),
                            ("my_office", "My Office"),
                            ("flexible", "Flexible"),
                        ],
                        default="online",
                        max_length=50,
                    ),
                ),
                ("availability_notes", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "service_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to="services.servicecategory",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Service",
                "verbose_name_plural": "Services",
                "db_table": "service",
            },
        ),
    ]
