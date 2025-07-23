import uuid
from django.db import models
from accounts.models import User


class Course(models.Model):

    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courses_taught"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=[
            ("active", "Active"),
            ("cancelled", "Cancelled"),
            ("completed", "Completed"),
        ],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.title


class CourseEnrollment(models.Model):

    enrollment_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    course_id = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    student_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
            ("pending", "Pending"),
        ],
        default="active",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_enrollment"
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"
        unique_together = ("course_id", "student_id")

    def __str__(self):
        return f"{self.student_id.username} enrolled in {self.course_id.title}"
