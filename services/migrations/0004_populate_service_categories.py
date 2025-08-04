
from django.db import migrations


def create_initial_categories(apps, schema_editor):
    ServiceCategory = apps.get_model("services", "ServiceCategory")

    categories = [
        {
            "name": "Tax Preparation",
            "description": "Tax filing and preparation services",
        },
        {
            "name": "Bookkeeping",
            "description": "Record keeping and bookkeeping services",
        },
        {
            "name": "Accounting Consulting",
            "description": "Professional accounting consultation",
        },
        {
            "name": "Financial Reporting",
            "description": "Financial statements and reporting",
        },
        {"name": "Corporate Finance", "description": "Corporate financial services"},
        {
            "name": "Budget Preparation",
            "description": "Budget planning and preparation",
        },
        {
            "name": "Auditing and Financial Review",
            "description": "Audit and financial review services",
        },
        {
            "name": "Inventory and Cost Management",
            "description": "Inventory tracking and cost analysis",
        },
        {
            "name": "Loan File Preparation",
            "description": "Loan documentation and file preparation",
        },
        {
            "name": "Accounting Training Courses",
            "description": "Professional accounting training and education",
        },
        {"name": "Legal Studies", "description": "Legal consultation and studies"},
        {
            "name": "Digital and Legal Representation",
            "description": "Digital services and legal representation",
        },
        {
            "name": "Custom Services",
            "description": "Customized services as per client requirements",
        },
    ]

    for category_data in categories:
        ServiceCategory.objects.get_or_create(
            name=category_data["name"],
            defaults={"description": category_data["description"]},
        )


def reverse_create_categories(apps, schema_editor):
    ServiceCategory = apps.get_model("services", "ServiceCategory")
    ServiceCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0002_recreate_service_model"),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, reverse_create_categories),
    ]
