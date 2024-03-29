from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user',)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
