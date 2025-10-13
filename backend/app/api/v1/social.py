from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

class CreatePostRequest(BaseModel):
    text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    type: str = "general"  # achievement, tip, question, milestone, challenge
    location: Optional[str] = None
    tags: List[str] = []

class CommentRequest(BaseModel):
    text: str

class User(BaseModel):
    id: str
    name: str
    avatar: str
    level: int
    carbon_saved: float
    followers: int
    following: int
    is_following: bool = False

class Post(BaseModel):
    id: str
    user: User
    text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    type: str
    likes: int
    is_liked: bool = False
    comments_count: int
    shares: int
    created_at: datetime
    location: Optional[str] = None
    tags: List[str] = []

# Demo users for social features
DEMO_USERS = {
    "user-1": User(
        id="user-1",
        name="Alex Green",
        avatar="https://ui-avatars.com/api/?name=Alex+Green&background=22c55e&color=fff",
        level=8,
        carbon_saved=2540,
        followers=1250,
        following=380
    ),
    "user-2": User(
        id="user-2", 
        name="Sarah Eco",
        avatar="https://ui-avatars.com/api/?name=Sarah+Eco&background=3b82f6&color=fff",
        level=6,
        carbon_saved=1890,
        followers=890,
        following=420
    ),
    "user-3": User(
        id="user-3",
        name="Mike Climate", 
        avatar="https://ui-avatars.com/api/?name=Mike+Climate&background=f59e0b&color=fff",
        level=12,
        carbon_saved=3200,
        followers=650,
        following=290
    ),
    "user-4": User(
        id="user-4",
        name="Emma Planet",
        avatar="https://ui-avatars.com/api/?name=Emma+Planet&background=10b981&color=fff",
        level=15,
        carbon_saved=4200,
        followers=2100,
        following=150
    ),
    "user-5": User(
        id="user-5",
        name="David Solar",
        avatar="https://ui-avatars.com/api/?name=David+Solar&background=eab308&color=fff",
        level=18,
        carbon_saved=5600,
        followers=890,
        following=320
    )
}

# Demo posts for social feed
DEMO_POSTS = [
    {
        "id": "post-1",
        "user_id": "user-1",
        "text": "Just completed my first car-free week! 🚲 Biked to work every day and discovered amazing routes through the park. My carbon savings this week: 45kg CO₂! Who else is up for the challenge?",
        "type": "achievement",
        "likes": 127,
        "comments_count": 23,
        "shares": 34,
        "created_at": datetime.now() - timedelta(hours=3),
        "location": "San Francisco, CA",
        "tags": ["carfree", "biking", "transportation", "challenge"],
        "achievement": {
            "title": "Car-Free Warrior",
            "points": 500,
            "icon": "🚲"
        },
        "carbon_impact": {
            "amount": 45,
            "period": "this week",
            "comparison": "90% less than usual"
        }
    },
    {
        "id": "post-2", 
        "user_id": "user-4",
        "text": "🌱 Pro tip: Growing your own herbs can save 12kg CO₂ per year and tastes so much better! Here's my balcony herb garden setup. Basil, mint, and rosemary are thriving! 🌿",
        "media_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400",
        "media_type": "image",
        "type": "tip",
        "likes": 89,
        "comments_count": 15,
        "shares": 156,
        "created_at": datetime.now() - timedelta(hours=5),
        "location": "Portland, OR",
        "tags": ["gardening", "food", "diy", "sustainable"]
    },
    {
        "id": "post-3",
        "user_id": "user-5", 
        "text": "Month 6 update: Solar panels + electric car = 🤯 Just hit 1 ton of CO₂ saved this year! The future is electric and it feels amazing. Initial investment paying off big time.",
        "type": "milestone",
        "likes": 234,
        "comments_count": 42,
        "shares": 67,
        "created_at": datetime.now() - timedelta(hours=8),
        "location": "Austin, TX",
        "tags": ["solar", "electric", "milestone", "investment"],
        "carbon_impact": {
            "amount": 1000,
            "period": "this year", 
            "comparison": "equivalent to planting 45 trees"
        }
    }
]

# User interactions storage (in real app, would be in database)
user_likes = {}  # {user_id: [post_ids]}
user_follows = {}  # {user_id: [followed_user_ids]}
post_comments = {}  # {post_id: [comments]}

@router.get("/feed")
async def get_social_feed(
    limit: int = 20,
    offset: int = 0,
    user_id: str = "demo-user"
):
    """Get social media feed with posts from followed users and trending content"""
    
    # In real app, would filter based on user's following list
    posts = []
    for post_data in DEMO_POSTS[offset:offset+limit]:
        user = DEMO_USERS[post_data["user_id"]]
        
        # Check if current user liked this post
        is_liked = user_id in user_likes.get(post_data["id"], [])
        
        # Check if current user follows this user
        user.is_following = post_data["user_id"] in user_follows.get(user_id, [])
        
        post = {
            **post_data,
            "user": user.dict(),
            "is_liked": is_liked,
            "comments": post_comments.get(post_data["id"], [])[:2]  # Show first 2 comments
        }
        posts.append(post)
    
    return {
        "posts": posts,
        "has_more": offset + limit < len(DEMO_POSTS),
        "total_count": len(DEMO_POSTS)
    }

@router.post("/posts")
async def create_post(
    post_request: CreatePostRequest,
    user_id: str = "demo-user"
):
    """Create a new social media post"""
    
    new_post = {
        "id": f"post-{datetime.now().timestamp()}",
        "user_id": user_id,
        "text": post_request.text,
        "media_url": post_request.media_url,
        "media_type": post_request.media_type,
        "type": post_request.type,
        "likes": 0,
        "comments_count": 0,
        "shares": 0,
        "created_at": datetime.now(),
        "location": post_request.location,
        "tags": post_request.tags
    }
    
    # In real app, would save to database
    DEMO_POSTS.insert(0, new_post)
    
    return {
        "message": "Post created successfully",
        "post_id": new_post["id"],
        "created_at": new_post["created_at"]
    }

@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, user_id: str = "demo-user"):
    """Like or unlike a post"""
    
    # Find the post
    post = next((p for p in DEMO_POSTS if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Toggle like
    if post_id not in user_likes:
        user_likes[post_id] = []
    
    if user_id in user_likes[post_id]:
        # Unlike
        user_likes[post_id].remove(user_id)
        post["likes"] = max(0, post["likes"] - 1)
        liked = False
    else:
        # Like
        user_likes[post_id].append(user_id)
        post["likes"] += 1
        liked = True
    
    return {
        "post_id": post_id,
        "liked": liked,
        "total_likes": post["likes"]
    }

@router.post("/posts/{post_id}/comment")
async def comment_on_post(
    post_id: str,
    comment_request: CommentRequest,
    user_id: str = "demo-user"
):
    """Add a comment to a post"""
    
    # Find the post
    post = next((p for p in DEMO_POSTS if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create comment
    comment = {
        "id": f"comment-{datetime.now().timestamp()}",
        "user_id": user_id,
        "user_name": "Demo User",  # In real app, would get from user profile
        "text": comment_request.text,
        "created_at": datetime.now(),
        "likes": 0
    }
    
    # Add to comments
    if post_id not in post_comments:
        post_comments[post_id] = []
    post_comments[post_id].append(comment)
    
    # Update post comment count
    post["comments_count"] += 1
    
    return {
        "message": "Comment added successfully",
        "comment_id": comment["id"],
        "total_comments": post["comments_count"]
    }

@router.post("/posts/{post_id}/share")
async def share_post(post_id: str, user_id: str = "demo-user"):
    """Share a post"""
    
    # Find the post
    post = next((p for p in DEMO_POSTS if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment share count
    post["shares"] += 1
    
    return {
        "message": "Post shared successfully",
        "post_id": post_id,
        "total_shares": post["shares"]
    }

@router.post("/users/{target_user_id}/follow")
async def follow_user(target_user_id: str, user_id: str = "demo-user"):
    """Follow a user"""
    
    if target_user_id not in DEMO_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id not in user_follows:
        user_follows[user_id] = []
    
    if target_user_id not in user_follows[user_id]:
        user_follows[user_id].append(target_user_id)
        DEMO_USERS[target_user_id].followers += 1
        
        return {
            "message": f"Successfully followed {DEMO_USERS[target_user_id].name}",
            "following": True
        }
    else:
        return {
            "message": "Already following this user",
            "following": True
        }

@router.delete("/users/{target_user_id}/follow")
async def unfollow_user(target_user_id: str, user_id: str = "demo-user"):
    """Unfollow a user"""
    
    if target_user_id not in DEMO_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id in user_follows and target_user_id in user_follows[user_id]:
        user_follows[user_id].remove(target_user_id)
        DEMO_USERS[target_user_id].followers = max(0, DEMO_USERS[target_user_id].followers - 1)
        
        return {
            "message": f"Successfully unfollowed {DEMO_USERS[target_user_id].name}",
            "following": False
        }
    else:
        return {
            "message": "Not following this user",
            "following": False
        }

@router.get("/users/{user_id}/followers")
async def get_user_followers(user_id: str, limit: int = 20):
    """Get user's followers"""
    
    # In real app, would query database for followers
    # For demo, return subset of demo users
    followers = list(DEMO_USERS.values())[:limit]
    
    return {
        "followers": [user.dict() for user in followers],
        "total_count": len(followers)
    }

@router.get("/users/{user_id}/following")
async def get_user_following(user_id: str, limit: int = 20):
    """Get users that this user follows"""
    
    following_ids = user_follows.get(user_id, [])
    following_users = [DEMO_USERS[uid] for uid in following_ids if uid in DEMO_USERS]
    
    return {
        "following": [user.dict() for user in following_users],
        "total_count": len(following_users)
    }

@router.get("/discover/users")
async def discover_users(limit: int = 10, user_id: str = "demo-user"):
    """Discover new users to follow"""
    
    # Return users not currently followed
    following_ids = user_follows.get(user_id, [])
    suggested_users = [
        user for uid, user in DEMO_USERS.items() 
        if uid not in following_ids and uid != user_id
    ]
    
    return {
        "suggested_users": [user.dict() for user in suggested_users[:limit]],
        "total_count": len(suggested_users)
    }

@router.get("/trending")
async def get_trending_topics():
    """Get trending hashtags and topics"""
    
    trending = [
        {"tag": "carfree", "posts": 1247, "growth": "+15%"},
        {"tag": "solar", "posts": 892, "growth": "+23%"},
        {"tag": "gardening", "posts": 634, "growth": "+8%"},
        {"tag": "biking", "posts": 445, "growth": "+12%"},
        {"tag": "zerowaste", "posts": 389, "growth": "+19%"},
    ]
    
    return {
        "trending_topics": trending,
        "updated_at": datetime.now()
    }

@router.get("/notifications")
async def get_notifications(user_id: str = "demo-user", limit: int = 50):
    """Get user notifications"""
    
    # Demo notifications
    notifications = [
        {
            "id": "notif-1",
            "type": "like",
            "user": DEMO_USERS["user-1"].dict(),
            "message": "liked your post about solar panels",
            "created_at": datetime.now() - timedelta(hours=2),
            "read": False
        },
        {
            "id": "notif-2", 
            "type": "follow",
            "user": DEMO_USERS["user-2"].dict(),
            "message": "started following you",
            "created_at": datetime.now() - timedelta(hours=4),
            "read": False
        },
        {
            "id": "notif-3",
            "type": "comment",
            "user": DEMO_USERS["user-3"].dict(), 
            "message": "commented on your achievement",
            "created_at": datetime.now() - timedelta(hours=6),
            "read": True
        }
    ]
    
    return {
        "notifications": notifications[:limit],
        "unread_count": len([n for n in notifications if not n["read"]]),
        "total_count": len(notifications)
    }

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    
    return {
        "message": "Notification marked as read",
        "notification_id": notification_id
    }