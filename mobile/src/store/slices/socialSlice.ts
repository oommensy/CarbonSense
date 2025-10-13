import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  name: string;
  avatar: string;
  isFollowing: boolean;
  followers: number;
  following: number;
  carbonSaved: number;
  level: number;
}

interface Achievement {
  id: string;
  title: string;
  points: number;
  icon: string;
}

interface CarbonImpact {
  amount: number;
  period: string;
  comparison: string;
}

interface Comment {
  id: string;
  user: User;
  text: string;
  createdAt: string;
  likes: number;
}

interface Post {
  id: string;
  user: User;
  text: string;
  media?: {
    url: string;
    type: 'image' | 'video';
  };
  achievement?: Achievement;
  carbonImpact?: CarbonImpact;
  type: 'achievement' | 'tip' | 'question' | 'milestone' | 'challenge';
  likes: number;
  isLiked: boolean;
  comments: Comment[];
  shares: number;
  createdAt: string;
  location?: string;
  tags: string[];
}

interface SocialState {
  feed: Post[];
  myPosts: Post[];
  following: User[];
  followers: User[];
  friendSuggestions: User[];
  isLoading: boolean;
  error: string | null;
  notifications: Array<{
    id: string;
    type: 'like' | 'comment' | 'follow' | 'achievement' | 'challenge';
    user: User;
    post?: Post;
    message: string;
    createdAt: string;
    read: boolean;
  }>;
}

const initialState: SocialState = {
  feed: [
    {
      id: 'post-1',
      user: {
        id: 'user-1',
        name: 'Alex Green',
        avatar: 'https://ui-avatars.com/api/?name=Alex+Green&background=22c55e&color=fff',
        isFollowing: false,
        followers: 1250,
        following: 380,
        carbonSaved: 2540,
        level: 8
      },
      text: 'Just completed my first car-free week! 🚲 Biked to work every day and discovered amazing routes through the park. My carbon savings this week: 45kg CO₂! Who else is up for the challenge?',
      achievement: {
        id: 'ach-1',
        title: 'Car-Free Warrior',
        points: 500,
        icon: '🚲'
      },
      carbonImpact: {
        amount: 45,
        period: 'this week',
        comparison: '90% less than usual'
      },
      type: 'achievement',
      likes: 127,
      isLiked: false,
      comments: [
        {
          id: 'comment-1',
          user: {
            id: 'user-2',
            name: 'Sarah Eco',
            avatar: 'https://ui-avatars.com/api/?name=Sarah+Eco&background=3b82f6&color=fff',
            isFollowing: true,
            followers: 890,
            following: 420,
            carbonSaved: 1890,
            level: 6
          },
          text: 'Amazing! I did the same challenge last month. The key is planning your routes ahead of time 💪',
          createdAt: '2 hours ago',
          likes: 23
        },
        {
          id: 'comment-2',
          user: {
            id: 'user-3',
            name: 'Mike Climate',
            avatar: 'https://ui-avatars.com/api/?name=Mike+Climate&background=f59e0b&color=fff',
            isFollowing: false,
            followers: 650,
            following: 290,
            carbonSaved: 3200,
            level: 12
          },
          text: 'Count me in for next week! Starting my bike commute journey 🌱',
          createdAt: '1 hour ago',
          likes: 45
        }
      ],
      shares: 34,
      createdAt: '3 hours ago',
      location: 'San Francisco, CA',
      tags: ['carfree', 'biking', 'transportation', 'challenge']
    },
    {
      id: 'post-2',
      user: {
        id: 'user-4',
        name: 'Emma Planet',
        avatar: 'https://ui-avatars.com/api/?name=Emma+Planet&background=10b981&color=fff',
        isFollowing: true,
        followers: 2100,
        following: 150,
        carbonSaved: 4200,
        level: 15
      },
      text: '🌱 Pro tip: Growing your own herbs can save 12kg CO₂ per year and tastes so much better! Here\'s my balcony herb garden setup. Basil, mint, and rosemary are thriving! 🌿',
      media: {
        url: 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400',
        type: 'image'
      },
      type: 'tip',
      likes: 89,
      isLiked: true,
      comments: [
        {
          id: 'comment-3',
          user: {
            id: 'user-1',
            name: 'Alex Green',
            avatar: 'https://ui-avatars.com/api/?name=Alex+Green&background=22c55e&color=fff',
            isFollowing: false,
            followers: 1250,
            following: 380,
            carbonSaved: 2540,
            level: 8
          },
          text: 'Love this! Just ordered some seeds. Any tips for beginners?',
          createdAt: '45 minutes ago',
          likes: 12
        }
      ],
      shares: 156,
      createdAt: '5 hours ago',
      location: 'Portland, OR',
      tags: ['gardening', 'food', 'diy', 'sustainable']
    },
    {
      id: 'post-3',
      user: {
        id: 'user-5',
        name: 'David Solar',
        avatar: 'https://ui-avatars.com/api/?name=David+Solar&background=eab308&color=fff',
        isFollowing: false,
        followers: 890,
        following: 320,
        carbonSaved: 5600,
        level: 18
      },
      text: 'Month 6 update: Solar panels + electric car = 🤯 Just hit 1 ton of CO₂ saved this year! The future is electric and it feels amazing. Initial investment paying off big time.',
      carbonImpact: {
        amount: 1000,
        period: 'this year',
        comparison: 'equivalent to planting 45 trees'
      },
      type: 'milestone',
      likes: 234,
      isLiked: false,
      comments: [
        {
          id: 'comment-4',
          user: {
            id: 'user-6',
            name: 'Lisa Wind',
            avatar: 'https://ui-avatars.com/api/?name=Lisa+Wind&background=8b5cf6&color=fff',
            isFollowing: true,
            followers: 1400,
            following: 200,
            carbonSaved: 3800,
            level: 14
          },
          text: 'Incredible milestone! What\'s your ROI timeline looking like?',
          createdAt: '1 hour ago',
          likes: 18
        }
      ],
      shares: 67,
      createdAt: '8 hours ago',
      location: 'Austin, TX',
      tags: ['solar', 'electric', 'milestone', 'investment']
    }
  ],
  myPosts: [],
  following: [],
  followers: [],
  friendSuggestions: [
    {
      id: 'suggestion-1',
      name: 'Climate Chris',
      avatar: 'https://ui-avatars.com/api/?name=Climate+Chris&background=ef4444&color=fff',
      isFollowing: false,
      followers: 567,
      following: 234,
      carbonSaved: 1200,
      level: 5
    },
    {
      id: 'suggestion-2',
      name: 'Green Grace',
      avatar: 'https://ui-avatars.com/api/?name=Green+Grace&background=06b6d4&color=fff',
      isFollowing: false,
      followers: 890,
      following: 345,
      carbonSaved: 2100,
      level: 9
    }
  ],
  isLoading: false,
  error: null,
  notifications: [
    {
      id: 'notif-1',
      type: 'like',
      user: {
        id: 'user-1',
        name: 'Alex Green',
        avatar: 'https://ui-avatars.com/api/?name=Alex+Green&background=22c55e&color=fff',
        isFollowing: false,
        followers: 1250,
        following: 380,
        carbonSaved: 2540,
        level: 8
      },
      message: 'liked your post about solar panels',
      createdAt: '2 hours ago',
      read: false
    },
    {
      id: 'notif-2',
      type: 'follow',
      user: {
        id: 'user-2',
        name: 'Sarah Eco',
        avatar: 'https://ui-avatars.com/api/?name=Sarah+Eco&background=3b82f6&color=fff',
        isFollowing: true,
        followers: 890,
        following: 420,
        carbonSaved: 1890,
        level: 6
      },
      message: 'started following you',
      createdAt: '4 hours ago',
      read: false
    }
  ]
};

const socialSlice = createSlice({
  name: 'social',
  initialState,
  reducers: {
    loadFeed: (state) => {
      state.isLoading = false;
      // In real app, this would fetch from API
    },
    
    createPost: (state, action: PayloadAction<{
      text: string;
      media?: any;
      type: Post['type'];
    }>) => {
      const newPost: Post = {
        id: `post-${Date.now()}`,
        user: {
          id: 'current-user',
          name: 'You',
          avatar: 'https://ui-avatars.com/api/?name=You&background=22c55e&color=fff',
          isFollowing: false,
          followers: 45,
          following: 120,
          carbonSaved: 890,
          level: 4
        },
        text: action.payload.text,
        media: action.payload.media,
        type: action.payload.type,
        likes: 0,
        isLiked: false,
        comments: [],
        shares: 0,
        createdAt: 'just now',
        tags: []
      };
      
      state.feed.unshift(newPost);
      state.myPosts.unshift(newPost);
    },
    
    likePost: (state, action: PayloadAction<string>) => {
      const post = state.feed.find(p => p.id === action.payload);
      if (post) {
        if (post.isLiked) {
          post.likes -= 1;
          post.isLiked = false;
        } else {
          post.likes += 1;
          post.isLiked = true;
        }
      }
    },
    
    commentOnPost: (state, action: PayloadAction<{
      postId: string;
      comment: string;
    }>) => {
      const post = state.feed.find(p => p.id === action.payload.postId);
      if (post) {
        const newComment: Comment = {
          id: `comment-${Date.now()}`,
          user: {
            id: 'current-user',
            name: 'You',
            avatar: 'https://ui-avatars.com/api/?name=You&background=22c55e&color=fff',
            isFollowing: false,
            followers: 45,
            following: 120,
            carbonSaved: 890,
            level: 4
          },
          text: action.payload.comment,
          createdAt: 'just now',
          likes: 0
        };
        post.comments.push(newComment);
      }
    },
    
    sharePost: (state, action: PayloadAction<string>) => {
      const post = state.feed.find(p => p.id === action.payload);
      if (post) {
        post.shares += 1;
      }
    },
    
    followUser: (state, action: PayloadAction<string>) => {
      // Update user's following status in feed
      state.feed.forEach(post => {
        if (post.user.id === action.payload) {
          post.user.isFollowing = true;
          post.user.followers += 1;
        }
      });
      
      // Add to following list
      const user = state.feed.find(p => p.user.id === action.payload)?.user;
      if (user && !state.following.find(f => f.id === action.payload)) {
        state.following.push(user);
      }
    },
    
    unfollowUser: (state, action: PayloadAction<string>) => {
      // Update user's following status in feed
      state.feed.forEach(post => {
        if (post.user.id === action.payload) {
          post.user.isFollowing = false;
          post.user.followers -= 1;
        }
      });
      
      // Remove from following list
      state.following = state.following.filter(f => f.id !== action.payload);
    },
    
    markNotificationRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    
    clearAllNotifications: (state) => {
      state.notifications = [];
    }
  }
});

export const {
  loadFeed,
  createPost,
  likePost,
  commentOnPost,
  sharePost,
  followUser,
  unfollowUser,
  markNotificationRead,
  clearAllNotifications
} = socialSlice.actions;

export default socialSlice.reducer;