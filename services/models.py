import uuid
from django.db import models
from accounts.models import User


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_categories",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_categories"
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServiceAttachment(models.Model):
    """Separate model for handling multiple file attachments per service"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        "Service", on_delete=models.CASCADE, related_name="service_attachments"
    )
    file = models.FileField(upload_to="service_attachments/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "service_attachments"
        verbose_name = "Service Attachment"
        verbose_name_plural = "Service Attachments"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_filename} for {self.service.title}"

    def save(self, *args, **kwargs):
        if self.file:
            # Store original filename
            if not self.original_filename:
                self.original_filename = self.file.name
            # Store file size
            if not self.file_size:
                self.file_size = self.file.size
        super().save(*args, **kwargs)


class Service(models.Model):

    SERVICE_TYPE_CHOICES = [
        ("needed", "Service Needed"),  # Client posting what they need
        ("offered", "Service Offered"),  # Accountant posting what they provide
    
    ]

    DURATION_CHOICES = [
        ("hours", "Hours"),
        ("days", "Days"),
        ("weeks", "Weeks"),
        ("months", "Months"),
    ]

    DELIVERY_METHOD_CHOICES = [
        ("online", "Online"),
        ("in_person", "In Person"),
    ]

    WILAYA_CHOICES = [
        ("01", "Adrar"),
        ("02", "Chlef"),
        ("03", "Laghouat"),
        ("04", "Oum El Bouaghi"),
        ("05", "Batna"),
        ("06", "Béjaïa"),
        ("07", "Biskra"),
        ("08", "Béchar"),
        ("09", "Blida"),
        ("10", "Bouira"),
        ("11", "Tamanrasset"),
        ("12", "Tébessa"),
        ("13", "Tlemcen"),
        ("14", "Tiaret"),
        ("15", "Tizi Ouzou"),
        ("16", "Algiers"),
        ("17", "Djelfa"),
        ("18", "Jijel"),
        ("19", "Sétif"),
        ("20", "Saïda"),
        ("21", "Skikda"),
        ("22", "Sidi Bel Abbès"),
        ("23", "Annaba"),
        ("24", "Guelma"),
        ("25", "Constantine"),
        ("26", "Médéa"),
        ("27", "Mostaganem"),
        ("28", "M'Sila"),
        ("29", "Mascara"),
        ("30", "Ouargla"),
        ("31", "Oran"),
        ("32", "El Bayadh"),
        ("33", "Illizi"),
        ("34", "Bordj Bou Arréridj"),
        ("35", "Boumerdès"),
        ("36", "El Tarf"),
        ("37", "Tindouf"),
        ("38", "Tissemsilt"),
        ("39", "El Oued"),
        ("40", "Khenchela"),
        ("41", "Souk Ahras"),
        ("42", "Tipaza"),
        ("43", "Mila"),
        ("44", "Aïn Defla"),
        ("45", "Naâma"),
        ("46", "Aïn Témouchent"),
        ("47", "Ghardaïa"),
        ("48", "Relizane"),
        ("49", "El M'Ghair"),
        ("50", "El Meniaa"),
        ("51", "Ouled Djellal"),
        ("52", "Bordj Badji Mokhtar"),
        ("53", "Béni Abbès"),
        ("54", "Timimoun"),
        ("55", "Touggourt"),
        ("56", "Djanet"),
        ("57", "In Salah"),
        ("58", "In Guezzam"),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="services")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    
    is_course = models.BooleanField(default=False)
    
    

    # Core content
    title = models.CharField(max_length=255)
    description = models.TextField()
    categories = models.ManyToManyField(
        ServiceCategory, related_name="services", blank=False
    )

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    price_description = models.TextField(
        blank=True, help_text="Additional details about pricing"
    )

    # Timeline
    estimated_duration = models.PositiveIntegerField(default=1)
    duration_unit = models.CharField(
        max_length=20, choices=DURATION_CHOICES, default="days"
    )
    estimated_duration_description = models.TextField(
        blank=True,
    )

    tasks_and_responsibilities = models.JSONField(
        default=list,
        blank=True,
    )

    conditions_requirements = models.JSONField(default=list, blank=True)

    location = models.CharField(
        max_length=3,
        choices=WILAYA_CHOICES,
        blank=True,
        null=True,
    )

    location_description = models.TextField(
        blank=True,
    )

    # Delivery method
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES,
        default="online",
        help_text="How the service will be delivered",
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services"
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["service_type", "is_active"]),
            models.Index(fields=["user", "service_type"]),
        ]

    def __str__(self):
        return (
            f"{self.get_service_type_display()}: {self.title} by {self.user.full_name}"
        )

    def get_categories_display(self):
        """Return comma-separated list of category names"""
        return ", ".join([cat.name for cat in self.categories.all()])
