from django.contrib import admin
from  .models import SiteSettings, AdminUser, Otp
# Register your models here.

admin.site.register(SiteSettings)
admin.site.register(AdminUser)
admin.site.register(Otp)



