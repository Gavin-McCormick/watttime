from pages.models import Article
from django.contrib import admin


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'published_on', 'outlet')


admin.site.register(Article, ArticleAdmin)
