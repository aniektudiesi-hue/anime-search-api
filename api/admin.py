from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from blogs.models import BlogPost,Comment
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('updated_at',)
    ordering = ('-updated_at',)
    fieldsets = (
        (None, {'fields': ('title', 'content', 'updated_at')}),
        ('Permissions', {'fields': ('is_active',)}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    readonly_fields = ('updated_at',)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'content', 'updated_at')
    search_fields = ('name', 'email')
    list_filter = ('updated_at',)
    ordering = ('-updated_at',)
