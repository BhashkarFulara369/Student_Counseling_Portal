from django.contrib import admin
from SCP_PORTAL.models import UserProfile
from SCP_PORTAL.models import StudentProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(StudentProfile) # Assuming you have a StudentProfile model as well 
