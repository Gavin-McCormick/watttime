from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from pages.models import Article, Supporter, Award


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'published_on', 'outlet')

class AwardAdmin(OrderedModelAdmin):
    list_display = ('order', 'award_name', 'contest_name', 'move_up_down_links')

class SupporterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(Supporter, SupporterAdmin)
