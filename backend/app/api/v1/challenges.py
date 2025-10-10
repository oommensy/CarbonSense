from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

# Demo data for challenges
DEMO_CHALLENGES = [
    {
        "id": "challenge-1",
        "title": "Car-Free Week",
        "description": "Go 7 days without using a personal vehicle",
        "type": "individual",
        "difficulty": "medium",
        "points": 500,
        "duration": 7,
        "category": "transport",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(days=7),
        "participants": 1247,
        "completion_rate": 68,
        "rules": [
            "No personal car usage",
            "Public transit, walking, cycling allowed", 
            "Emergency exceptions permitted"
        ],
        "rewards": ["Carbon offset credits", "Green transportation badge"],
        "is_active": True
    },
    {
        "id": "challenge-2", 
        "title": "Plant-Based Week",
        "description": "Eat only plant-based meals for one week",
        "type": "individual",
        "difficulty": "easy",
        "points": 300,
        "duration": 7,
        "category": "food",
        "start_date": datetime.now() + timedelta(days=3),
        "end_date": datetime.now() + timedelta(days=10),
        "participants": 892,
        "completion_rate": 85,
        "rules": [
            "No meat, fish, or dairy products",
            "Plant-based alternatives encouraged",
            "Document meals with photos"
        ],
        "rewards": ["Nutrition badge", "Recipe collection"],
        "is_active": True
    },
    {
        "id": "challenge-3",
        "title": "Corporate Zero Waste",
        "description": "Office-wide challenge to eliminate single-use items",
        "type": "team", 
        "difficulty": "hard",
        "points": 1000,
        "duration": 30,
        "category": "general",
        "start_date": datetime.now() - timedelta(days=5),
        "end_date": datetime.now() + timedelta(days=25),
        "participants": 156,
        "completion_rate": 42,
        "rules": [
            "No single-use plastics in office",
            "Bring reusable containers",
            "Team tracking and reporting"
        ],
        "rewards": ["Corporate sustainability award", "Team lunch"],
        "is_active": True
    }
]

# Demo leaderboard data
DEMO_LEADERBOARD = [
    {"id": "user-1", "name": "Alex Chen", "points": 2850, "rank": 1, "streak": 15},
    {"id": "user-2", "name": "Sarah Johnson", "points": 2720, "rank": 2, "streak": 12},
    {"id": "demo-user", "name": "You", "points": 2650, "rank": 3, "streak": 8},
    {"id": "user-4", "name": "Mike Rodriguez", "points": 2540, "rank": 4, "streak": 10},
    {"id": "user-5", "name": "Emma Wilson", "points": 2480, "rank": 5, "streak": 6},
    {"id": "user-6", "name": "David Kim", "points": 2420, "rank": 6, "streak": 14},
    {"id": "user-7", "name": "Lisa Zhang", "points": 2380, "rank": 7, "streak": 9},
    {"id": "user-8", "name": "Carlos Mendez", "points": 2340, "rank": 8, "streak": 7},
    {"id": "user-9", "name": "Anna Petrov", "points": 2290, "rank": 9, "streak": 11},
    {"id": "user-10", "name": "James Taylor", "points": 2250, "rank": 10, "streak": 5}
]

@router.get("/")
async def get_challenges(
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True
):
    """Get available challenges with optional filtering"""
    challenges = DEMO_CHALLENGES.copy()
    
    if active_only:
        challenges = [c for c in challenges if c["is_active"]]
    if type:
        challenges = [c for c in challenges if c["type"] == type]
    if difficulty:
        challenges = [c for c in challenges if c["difficulty"] == difficulty]
    if category:
        challenges = [c for c in challenges if c["category"] == category]
    
    return challenges

@router.get("/{challenge_id}")
async def get_challenge(challenge_id: str):
    """Get specific challenge details"""
    challenge = next((c for c in DEMO_CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Add additional details for individual challenge view
    challenge["participants_details"] = [
        {"id": "user-1", "name": "Alex C.", "progress": 85, "joined_date": datetime.now() - timedelta(days=3)},
        {"id": "user-2", "name": "Sarah J.", "progress": 72, "joined_date": datetime.now() - timedelta(days=2)},
        {"id": "demo-user", "name": "You", "progress": 60, "joined_date": datetime.now() - timedelta(days=1)}
    ]
    
    return challenge

@router.post("/{challenge_id}/join")
async def join_challenge(challenge_id: str, user_id: str = "demo-user"):
    """Join a challenge"""
    challenge = next((c for c in DEMO_CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # In real app, would check if already joined and add to database
    return {
        "challenge_id": challenge_id,
        "user_id": user_id,
        "joined_at": datetime.now(),
        "status": "active",
        "progress": 0,
        "message": f"Successfully joined {challenge['title']}!"
    }

@router.post("/{challenge_id}/leave")
async def leave_challenge(challenge_id: str, user_id: str = "demo-user"):
    """Leave a challenge"""
    return {
        "challenge_id": challenge_id,
        "user_id": user_id,
        "left_at": datetime.now(),
        "status": "left",
        "message": "You have left the challenge"
    }

@router.put("/{challenge_id}/progress")
async def update_progress(challenge_id: str, progress: int, user_id: str = "demo-user"):
    """Update user's progress in a challenge"""
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="Progress must be between 0 and 100")
    
    challenge = next((c for c in DEMO_CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    completed = progress >= 100
    points_earned = challenge["points"] if completed else 0
    
    return {
        "challenge_id": challenge_id,
        "user_id": user_id,
        "progress": progress,
        "completed": completed,
        "points_earned": points_earned,
        "updated_at": datetime.now()
    }

@router.get("/leaderboard/global")
async def get_global_leaderboard(limit: int = 10):
    """Get global leaderboard"""
    return {
        "leaderboard": DEMO_LEADERBOARD[:limit],
        "total_participants": len(DEMO_LEADERBOARD),
        "updated_at": datetime.now(),
        "period": "all_time"
    }

@router.get("/leaderboard/friends")
async def get_friends_leaderboard(user_id: str = "demo-user"):
    """Get friends leaderboard"""
    # Demo friends data
    friends_leaderboard = [
        {"id": "friend-1", "name": "Best Friend", "points": 2600, "rank": 1},
        {"id": "demo-user", "name": "You", "points": 2650, "rank": 2},
        {"id": "friend-2", "name": "College Buddy", "points": 2400, "rank": 3},
        {"id": "friend-3", "name": "Coworker", "points": 2200, "rank": 4}
    ]
    
    return {
        "leaderboard": friends_leaderboard,
        "user_rank": 2,
        "total_friends": 3,
        "updated_at": datetime.now()
    }

@router.get("/user/{user_id}/achievements")
async def get_user_achievements(user_id: str):
    """Get user's challenge achievements"""
    achievements = [
        {
            "id": "ach-1",
            "title": "First Steps",
            "description": "Completed your first challenge",
            "icon": "trophy",
            "earned_date": datetime.now() - timedelta(days=10),
            "points": 100
        },
        {
            "id": "ach-2", 
            "title": "Week Warrior",
            "description": "Completed a 7-day challenge",
            "icon": "calendar",
            "earned_date": datetime.now() - timedelta(days=3),
            "points": 250
        },
        {
            "id": "ach-3",
            "title": "Community Leader",
            "description": "Top 10% in community challenges", 
            "icon": "users",
            "earned_date": datetime.now() - timedelta(days=1),
            "points": 500
        }
    ]
    
    return {
        "user_id": user_id,
        "achievements": achievements,
        "total_achievements": len(achievements),
        "total_points": sum(a["points"] for a in achievements)
    }

@router.get("/stats")
async def get_challenge_stats():
    """Get overall challenge statistics"""
    return {
        "total_challenges": len(DEMO_CHALLENGES),
        "active_challenges": len([c for c in DEMO_CHALLENGES if c["is_active"]]),
        "total_participants": sum(c["participants"] for c in DEMO_CHALLENGES),
        "average_completion_rate": round(
            sum(c["completion_rate"] for c in DEMO_CHALLENGES) / len(DEMO_CHALLENGES), 1
        ),
        "categories": {
            "transport": len([c for c in DEMO_CHALLENGES if c["category"] == "transport"]),
            "food": len([c for c in DEMO_CHALLENGES if c["category"] == "food"]),
            "energy": len([c for c in DEMO_CHALLENGES if c["category"] == "energy"]),
            "general": len([c for c in DEMO_CHALLENGES if c["category"] == "general"])
        },
        "difficulty_distribution": {
            "easy": len([c for c in DEMO_CHALLENGES if c["difficulty"] == "easy"]),
            "medium": len([c for c in DEMO_CHALLENGES if c["difficulty"] == "medium"]),
            "hard": len([c for c in DEMO_CHALLENGES if c["difficulty"] == "hard"])
        }
    }