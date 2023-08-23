from django.contrib import admin
from .models import Course, Lecture, Enroll, Discussion, Review


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "owner")
    list_display_links = ("title",)
    search_fields = ("title", "owner__email")

    @admin.display(empty_value="")
    def owner(self, obj):
        return obj.email


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "course")
    list_display_links = ("title",)
    search_fields = ("title", "course__title")

    @admin.display()
    def course(self, obj):
        return obj.title


@admin.register(Enroll)
class EnrollAdmin(admin.ModelAdmin):
    list_display = ("pk", "enrollment_no", "student", "course")
    list_display_links = ("enrollment_no",)
    search_fields = ("enrollment_no", "student__email", "course__title")
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("student", "course")},
        ),
    )


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ("pk", "discussion", "student", "lecture")
    list_display_links = ("pk", "discussion")
    search_fields = ("student__username", "lecture__pk")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "review", "rating", "owner", "course")
    list_display_links = ("pk", "review")
    search_fields = ("onwer__username", "course__pk")
