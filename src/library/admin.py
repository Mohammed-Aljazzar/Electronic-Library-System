from django.contrib import admin
from django.utils.html import format_html
from library.models import Book, Category, Comment

admin.site.register(Category)
admin.site.register(Comment)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('display_image', 'title', 'author', 'views_count', 'status')
    list_display_links = ('title', 'author')
    readonly_fields = ('views_count', 'download_count')

    def display_image(self, obj):
        return format_html('<img src="{}" width="50" height="75" />', obj.poster_image.url)

    display_image.short_description = 'Poster Image'

    search_fields = ('title', 'author', 'category__name')
    list_filter = ('status', 'category', 'language')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'author', 'category', 'poster_image')
        }),
        ('Additional Information', {
            'fields': ('book_file', 'link', 'publish_date', 'total_pages', 'language', 'status', 'quote')
        }),
        ('Statistics', {
            'fields': ('views_count', 'download_count')
        }),
    )