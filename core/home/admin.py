from django.contrib import admin
from .models import *
admin.site.register(CustomUser)
admin.site.register(Plan)
# admin.site.register(Blog)
admin.site.register(LiveSession)
admin.site.register(LuckyDraw)
admin.site.register(Category)
admin.site.register(UserAttendance)
admin.site.register(tracker)
admin.site.register(luckyparticipate)
# class BlogAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'author', 'description', 'category', 'date_added')
# admin.site.register(Blog, BlogAdmin)

admin.site.register(Blog)