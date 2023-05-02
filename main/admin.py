from django.contrib import admin
from .models import Profile, PostDB, Verification, PostComments

# Register your models here.


class ProfileView(admin.ModelAdmin):
    list_display = ('user', 'userId', 'bio', 'profession',
                    'workplace', 'gender', 'relationStatus', 'area', 'profilePic')


class PostDBView(admin.ModelAdmin):
    list_display = ('id', 'user', 'userId', 'post', 'created', 'updated')


class VerificationView(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_verified')


class PostCommentsView(admin.ModelAdmin):
    list_display = ('id', 'postId', 'commenter', 'comment', 'created')


admin.site.register(Profile, ProfileView)
admin.site.register(PostDB, PostDBView)
admin.site.register(Verification, VerificationView)
admin.site.register(PostComments, PostCommentsView)
