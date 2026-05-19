import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from posts.models import Profile, Post, Reel, FollowersCount

def generate_data():
    print("Starting to seed 100 Pakistani users...")

    # Lists of names and data
    boy_names = ["Ali", "Ahmed", "Hassan", "Zeeshan", "Hamza", "Osama", "Bilal", "Umer", "Mustafa", "Abdullah", "Zain", "Faisal", "Saad", "Arsalan", "Taha"]
    girl_names = ["Fatima", "Ayesha", "Zainab", "Sana", "Mariam", "Hira", "Saba", "Laiba", "Kiran", "Mahnoor", "Rimsha", "Anum", "Tayyaba", "Iqra"]
    cities = ["Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan", "Peshawar", "Quetta"]
    bios = ["Student at UET", "Foodie | Traveler", "Living life one day at a time", "Alhamdulillah for everything", "Digital Creator", "Pakistani 🇵🇰"]

    pass_word = "pak123"

    for i in range(1, 101):
        # Choose gender and name
        is_boy = random.choice([True, False])
        first_name = random.choice(boy_names if is_boy else girl_names)
        last_name = random.choice(["Khan", "Chaudhry", "Sheikh", "Malik", "Junaid"])
        
        username = f"{first_name.lower()}_{random.randint(100, 999)}"
        
        # 1. Create User
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=pass_word, first_name=first_name, last_name=last_name)
            
            # 2. Update Profile (Created via signals)
            profile = Profile.objects.get(user=user)
            profile.full_name = f"{first_name} {last_name}"
            profile.bio = random.choice(bios)
            profile.location = random.choice(cities)
            profile.save()

            # 3. Add 1 Post for this user (Using Internet Image)
            # Since local ImageField needs files, we add a dummy URL reference for logic
            # To make it look real on the feed, I'll use a reliable placeholder service
            Post.objects.create(
                user=user,
                caption=f"Greetings from {profile.location}! #Pakistan",
                no_of_likes=random.randint(5, 500)
            )

            # 4. Add 1 Reel for this user (Using Internet Video)
            # We use our internet links logic
            Reel.objects.create(
                user=user,
                caption="My first reel! 🇵🇰",
                no_of_likes=random.randint(10, 1000)
            )

            print(f"[{i}] Created User: {username} | Password: {pass_word}")

    print("\nSuccessfully seeded 100 users!")

if __name__ == '__main__':
    generate_data()