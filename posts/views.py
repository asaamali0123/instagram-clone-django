import datetime
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, LikePost, Comment, Profile, FollowersCount, Reel
# Make sure 'Message' is added to the end of this list!
from .models import Post, LikePost, Comment, Profile, FollowersCount, Reel, Message
from .models import Post, LikePost, Comment, Profile, FollowersCount, Reel, Message, Notification

# 1. LOGIN VIEW
class CustomLoginView(LoginView):
    template_name = 'login.html'

# 2. SIGNUP LOGIC
def signup(request):
    if request.method == "POST":
        email_or_mobile = request.POST.get('mobile_or_email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        day = request.POST.get('day')
        month = request.POST.get('month')
        year = request.POST.get('year')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return redirect('signup')

        try:
            user = User.objects.create_user(username=username, password=password)
            if '@' in email_or_mobile:
                user.email = email_or_mobile
            user.save()

            birth_date = datetime.date(int(year), int(month), int(day))
            profile = Profile.objects.get(user=user)
            profile.full_name = full_name
            profile.birthday = birth_date
            profile.mobile_or_email = email_or_mobile
            profile.save()

            login(request, user)
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('signup')

    context = {'months': range(1, 13), 'days': range(1, 32), 'years': range(1950, 2025)}
    return render(request, 'signup.html', context)

# 3. HOME FEED (Filtered by Following)
@login_required(login_url='login')
def index(request):
    user_following_list = FollowersCount.objects.filter(follower=request.user.username)
    feed_list = [f.user for f in user_following_list]
    feed_list.append(request.user.username)

    posts = Post.objects.filter(user__username__in=feed_list).order_by('-created_at')
    notifications_count = Notification.objects.filter(to_user=request.user, is_read=False).count()

    all_users = User.objects.all()
    
    # 1. Get 15 random users to show in the Stories bar
    story_users = all_users.exclude(username=request.user.username).order_by('?')[:15]

    suggestions = [u for u in all_users if u.username != request.user.username and not FollowersCount.objects.filter(follower=request.user.username, user=u.username).exists()]

    return render(request, 'index.html', {
        'posts': posts, 
        'suggestions': suggestions[:5],
        'notifications_count': notifications_count,
        'story_users': story_users # Send this to the HTML
    })
# 4. SEARCH LOGIC
def search_user(request):
    query = request.GET.get('q')
    results = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query)) if query else []
    return render(request, 'search_results.html', {'results': results, 'query': query})

# 5. UPLOAD POST (Handles Photos AND Videos)
@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        user = request.user
        file = request.FILES.get('image_upload')
        caption = request.POST.get('caption')

        if file.name.lower().endswith(('.mp4', '.mov', '.mkv')):
            # Saves to video_file field (Make sure you added this to Post model)
            Post.objects.create(user=user, video_file=file, caption=caption)
        else:
            # Saves to image field
            Post.objects.create(user=user, image=file, caption=caption)
            
        return redirect('/')
    return redirect('/')

# 6. FOLLOW/UNFOLLOW
@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')
        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            FollowersCount.objects.get(follower=follower, user=user).delete()
        else:
            FollowersCount.objects.create(follower=follower, user=user)
            target_user = User.objects.get(username=user)
            Notification.objects.create(notification_type=2, from_user=request.user, to_user=target_user)
        return redirect('/profile/'+user)
    return redirect('/')

# 7. PROFILE PAGE
@login_required(login_url='login')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object).order_by('-created_at')
    
    # 1. Get the actual lists of followers and following
    followers = FollowersCount.objects.filter(user=pk)
    following = FollowersCount.objects.filter(follower=pk)

    # Counts
    follower_count = followers.count()
    following_count = following.count()

    # Follow button logic
    checker = FollowersCount.objects.filter(follower=request.user.username, user=pk).exists()
    button_text = 'Unfollow' if checker else 'Follow'

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': len(user_posts),
        'follower_count': follower_count,
        'following_count': following_count,
        'button_text': button_text,
        'followers_list': followers, # Add this
        'following_list': following, # Add this
    }
    return render(request, 'profile.html', context)

# 8. LIKE POST
@login_required(login_url='login')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1
    else:
        like_filter.delete()
        post.no_of_likes -= 1
    post.save()
    if like_filter is None:
        if post.user != request.user: # Don't notify if I like my own post
            Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.user, post=post)
    return redirect('/')

# 9. EDIT PROFILE SETTINGS (Unified Function Name)
@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        new_image = request.FILES.get('image')
        if new_image:
            user_profile.profileimg = new_image
        user_profile.full_name = request.POST.get('full_name')
        user_profile.bio = request.POST.get('bio')
        user_profile.website = request.POST.get('website')
        user_profile.gender = request.POST.get('gender')
        user_profile.save()
        return redirect('/profile/' + request.user.username)
    return render(request, 'settings.html', {'user_profile': user_profile})

# 10. DELETE POST
@login_required(login_url='login')
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('/')

# 11. EDIT POST CAPTION
@login_required(login_url='login')
def edit_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        new_caption = request.POST.get('caption')
        post = Post.objects.get(id=post_id)
        if post.user == request.user:
            post.caption = new_caption
            post.save()
    return redirect('/')

# 12. POST COMMENT
@login_required(login_url='login')
def post_comment(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')
        post = Post.objects.get(id=post_id)
        Comment.objects.create(post=post, user=request.user, text=comment_text)
    return redirect('/')

# 13. EXPLORE PAGE
@login_required(login_url='login')
def explore(request):
    all_posts = Post.objects.all().order_by('-created_at')
    return render(request, 'explore.html', {'all_posts': all_posts})

# 14. REELS PAGE (Unlimited Internet Demo + DB Reels)
@login_required(login_url='login')
def reels(request):
    # 1. Get all reels from the database
    all_reels_from_db = Reel.objects.all().order_by('-created_at')
    
    # 2. List of 10 different reliable internet videos
    video_pool = [
        'https://vjs.zencdn.net/v/oceans.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4',
        'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4'
    ]

    reels_data = []

    # 3. Loop through the DB reels and assign a random video if they are empty
    for index, reel in enumerate(all_reels_from_db):
        if reel.video:
            url = reel.video.url
        else:
            # This cycles through the 10 videos (User 1 gets vid 1, User 11 gets vid 1, etc.)
            url = video_pool[index % len(video_pool)]
        
        reels_data.append({
            'user': reel.user.username,
            'caption': reel.caption,
            'video_url': url,
            'likes': reel.no_of_likes
        })

    return render(request, 'reels.html', {'reels': reels_data})
# 15. MESSENGER VIEW
# 15. MESSENGER VIEW (Fixed Typo)
@login_required(login_url='login')
def messenger(request, username=None):
    # Get the list of people the current user follows
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    
    # FIX: Corrected the loop variable from 'f' to 'friend'
    friends = []
    for f in user_following:
        try:
            user_obj = User.objects.get(username=f.user)
            friends.append(user_obj)
        except User.DoesNotExist:
            continue
    
    active_chat_user = None
    chat_messages = []
    
    # If a specific user is selected to chat
    if username:
        active_chat_user = get_object_or_404(User, username=username)
        # Fetch messages between logged-in user and active_chat_user
        chat_messages = Message.objects.filter(
            Q(sender=request.user, receiver=active_chat_user) | 
            Q(sender=active_chat_user, receiver=request.user)
        ).order_by('timestamp')

    return render(request, 'messenger.html', {
        'friends': friends,
        'active_chat_user': active_chat_user,
        'chat_messages': chat_messages
    })
# 16. SEND MESSAGE LOGIC
@login_required(login_url='login')
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        receiver = User.objects.get(username=receiver_username)
        
        # 1. Create the actual message
        Message.objects.create(sender=request.user, receiver=receiver, content=content)

        # 2. ADD THIS: Create a notification for the receiver
        Notification.objects.create(
            notification_type=4, # Type 4 = Message
            from_user=request.user, 
            to_user=receiver
        )
        
        return redirect('/messages/' + receiver_username)
    return redirect('/messages/')
# Add this to views.py
@login_required(login_url='login')
def notifications(request):
    user_notifications = Notification.objects.filter(to_user=request.user).order_by('-timestamp')
    
    # Mark as read when they open this page
    user_notifications.update(is_read=True)
    
    return render(request, 'notifications.html', {'notifications': user_notifications})
# Add this function at the bottom
def logout_view(request):
    logout(request)
    return redirect('login')