# apps/profiles/admin.py
from django.contrib import admin
from .models import (
    UserProfile, UserSkill, Education, 
    WorkExperience, PrivacySettings, ProfileView
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'is_profile_public', 'friends_count', 'posts_count', 'created_at']
    list_filter = ['is_profile_public', 'gender', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio', 'location']
    readonly_fields = ['posts_count', 'friends_count', 'followers_count', 'following_count', 'created_at', 'updated_at']


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'level', 'years_of_experience', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['user__username', 'name']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'degree', 'field_of_study', 'is_current', 'start_date']
    list_filter = ['degree', 'is_current', 'start_date']
    search_fields = ['user__username', 'institution', 'field_of_study']


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'position', 'employment_type', 'is_current', 'start_date']
    list_filter = ['employment_type', 'is_current', 'start_date']
    search_fields = ['user__username', 'company', 'position']


@admin.register(PrivacySettings)
class PrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_visibility', 'email_notifications', 'push_notifications']
    list_filter = ['profile_visibility', 'email_notifications', 'push_notifications']
    search_fields = ['user__username']


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ['viewer', 'viewed_profile', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['viewer__username', 'viewed_profile__username']
    date_hierarchy = 'viewed_at'