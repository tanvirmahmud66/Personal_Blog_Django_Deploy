from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, PostDB, Verification, PostComments
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timesince import timesince
import uuid
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
# Create your views here.


# ----------------------------------------------------------------------------signin page
# @login_required(login_url='signin')
def signin_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            user_model = User.objects.get(username=username)
            if user_model:
                verify_model = Verification.objects.get(user=user_model)
                if verify_model.is_verified:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('home')
                    else:
                        messages.info(
                            request, "Invalid Username or Password!")
                        return redirect('signin')
                else:
                    messages.info(
                        request, 'Your email is not verified. Please verify your email first.')
                    return redirect('signin')
        except Exception as e:
            print(e)
            messages.info(request, "Invalid Username or Password!")
            return redirect('signin')

    return render(request, 'signin_page.html')


# --------------------------------------------------------------------signup page
# @login_required(login_url='signin')
def signup_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["confirm-password"]
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "username already taken")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "This email already used")
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                user.save()
                user_model = User.objects.get(username=username)
                token = str(uuid.uuid4())
                verify = Verification.objects.create(
                    user=user_model,
                    token=token,
                )
                verify.save()
                domain_name = get_current_site(request).domain
                link = f"http://{domain_name}/verify/{username}/{token}/"
                subject = "Email Verification"
                message = f"Please Click This Link {link} to verify your registration process. Thanks in Advanced."
                recipient_list = [email]
                email_from = settings.EMAIL_HOST_USER
                send_mail(
                    subject,
                    message,
                    email_from,
                    recipient_list,
                    fail_silently=False
                )
                messages.info(
                    request, "We have send a email for verification. Please check your email for complete registrations process.")
                return render(request, 'notification.html')
        else:
            messages.info(request, "Password not matched")
    return render(request, 'signup_page.html')


# ----------------------------------------------------------------------verify page
def verify(request, username, token):
    verify_model = Verification.objects.get(token=token)
    verify_model.is_verified = True
    verify_model.save()
    user_model = User.objects.get(username=username)
    new_profile = Profile.objects.create(
        user=user_model,
        userId=user_model.id,
    )
    new_profile.save()
    messages.success(request, 'Your Email Verified. Please Sign-In Again')
    verified = True
    return render(request, 'notification.html', {
        "verified": verified
    })


# -----------------------------------------------------------------------complete_profile
def complete_profile(request):
    if request.method == "POST":
        workplace = request.POST["workplace"]
        profession = request.POST["profession"]
        gender = request.POST["gender"]
        relationship = request.POST["relationship"]
        bio = request.POST["bio"]
        area = request.POST["district"]
        user = User.objects.get(id=request.user.id)
        if not user.is_staff:
            profile = Profile.objects.get(user=request.user)
            profile.workplace = workplace
            profile.profession = profession
            profile.gender = gender
            profile.relationStatus = relationship
            profile.bio = bio
            profile.area = area
            profile.save()
            return redirect('home')
    return render(request, 'complete_profile.html')


# -----------------------------------------------------------------logout_page
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('signin')


# -------------------------------------------------------------------home
@login_required(login_url='signin')
def home(request):
    profile = Profile.objects.get(user=request.user)
    notification = False
    if profile.bio is None or profile.workplace is None or profile.profession is None or profile.gender is None or profile.relationStatus is None or profile.area is None:
        notification = True
    if request.method == "POST":
        user_model = User.objects.get(username=request.user)
        post = request.POST['postInput']
        new_post = PostDB.objects.create(
            user=user_model, userId=user_model.id, post=post
        )
        new_post.save()
        return redirect('home')
    posts = PostDB.objects.all()
    post_comment = PostComments.objects.all()
    all_varified_users = Profile.objects.all()
    return render(request, 'home.html', {
        "posts": posts,
        "profile": profile,
        "notification": notification,
        "post_comment": post_comment,
        "all_user": all_varified_users,
    })


# -----------------------------------------------------------------profile page
@login_required(login_url='signin')
def profile_page(request, pk):
    user = User.objects.get(username=pk)
    user_post = PostDB.objects.filter(user=user)
    profile = Profile.objects.get(user=user)
    post_comment = PostComments.objects.all()
    if request.method == "POST":
        post = request.POST["postInput"]
        new_post = PostDB.objects.create(
            user=user,
            userId=user.id,
            post=post,
        )
        new_post.save()
        return redirect('profile', request.user.username)
    return render(request, 'profile_page.html', {
        "posts": user_post,
        "profile": profile,
        "post_comment": post_comment,
    })


# --------------------------------------------------------------Other user profile page
@login_required(login_url='singin')
def other_userprofile(request, pk):
    if pk == request.user.username:
        return redirect('profile', request.user.username)
    target_user = User.objects.get(username=pk)
    target_user_post = PostDB.objects.filter(user=target_user)
    target_user_profile = Profile.objects.get(user=target_user)
    current_user_profile = Profile.objects.get(user=request.user)
    post_comment = PostComments.objects.all()
    return render(request, 'other_user.html', {
        "user_posts": target_user_post,
        "user_profile": target_user_profile,
        "current_user_profile": current_user_profile,
        "post_comment": post_comment,
    })


# ------------------------------------------------------------edit profile
@login_required(login_url='signin')
def edit_profile(request):
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        workplace = request.POST["workplace"]
        profession = request.POST["profession"]
        gender = request.POST["gender"]
        relationship = request.POST["relationship"]
        bio = request.POST["bio"]
        area = request.POST["district"]
        profile.workplace = workplace
        profile.profession = profession
        profile.gender = gender
        profile.relationStatus = relationship
        profile.bio = bio
        profile.area = area
        profile.save()
        return redirect('profile', request.user.username)
    return render(request, 'edit_profile.html', {
        "user": user,
        "profile": profile,
    })


# ----------------------------------------------------------delete page
@login_required(login_url='signin')
def delete_post(request, pk):
    post = PostDB.objects.get(id=pk)
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        post.delete()
        return redirect('profile', request.user.username)
    return render(request, 'delete_post.html', {
        "post": post,
        "profile": profile,
    })


# ------------------------------------------------------edit post
@login_required(login_url='signin')
def edit_post(request, pk):
    posts = PostDB.objects.get(id=pk)
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        update_post = request.POST["editField"]
        posts.post = update_post
        posts.save()
        return redirect('profile', request.user.username)
    return render(request, 'edit_post.html', {
        "post": posts,
        "profile": profile,
    })


# --------------------------------------------------------edit profile
@login_required(login_url='signin')
def edit_pp(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        image = request.FILES["pp"]
        print(image)
        profile.profilePic = image
        profile.save()
        return redirect('profile', request.user.username)
    return render(request, 'editPP.html', {
        "profile": profile,
    })


# -------------------------------------------------------------Comment on Post
@login_required(login_url='signin')
def comment_post(request, pk):
    posts = PostDB.objects.get(id=pk)
    post_all_comment = PostComments.objects.filter(postId=pk)
    if request.method == "POST":
        comment = request.POST['comment']
        post_comment = PostComments.objects.create(
            postId=pk,
            commenter=request.user,
            comment=comment,
        )
        post_comment.save()
        return redirect('home')
    return render(request, 'comment_post.html', {
        "post": posts,
        "post_all_comment": post_all_comment,
    })
