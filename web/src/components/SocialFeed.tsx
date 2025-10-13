// Social Feed Component for Web Dashboard
'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';

interface User {
  id: string;
  name: string;
  avatar: string;
  level: number;
  carbonSaved: number;
  isFollowing?: boolean;
}

interface Post {
  id: string;
  user: User;
  text: string;
  media?: {
    url: string;
    type: 'image' | 'video';
  };
  achievement?: {
    title: string;
    points: number;
    icon: string;
  };
  carbonImpact?: {
    amount: number;
    period: string;
    comparison: string;
  };
  type: 'achievement' | 'tip' | 'question' | 'milestone' | 'challenge';
  likes: number;
  isLiked: boolean;
  comments: Array<{
    id: string;
    user: User;
    text: string;
    createdAt: string;
  }>;
  shares: number;
  createdAt: string;
  location?: string;
  tags: string[];
}

const SocialFeed = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [newPostText, setNewPostText] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load demo posts
    const demoPosts: Post[] = [
      {
        id: 'post-1',
        user: {
          id: 'user-1',
          name: 'Alex Green',
          avatar: 'https://ui-avatars.com/api/?name=Alex+Green&background=22c55e&color=fff',
          level: 8,
          carbonSaved: 2540,
          isFollowing: false
        },
        text: 'Just completed my first car-free week! 🚲 Biked to work every day and discovered amazing routes through the park. My carbon savings this week: 45kg CO₂! Who else is up for the challenge?',
        achievement: {
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
              level: 6,
              carbonSaved: 1890
            },
            text: 'Amazing! I did the same challenge last month. The key is planning your routes ahead of time 💪',
            createdAt: '2 hours ago'
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
          level: 15,
          carbonSaved: 4200,
          isFollowing: true
        },
        text: '🌱 Pro tip: Growing your own herbs can save 12kg CO₂ per year and tastes so much better! Here\'s my balcony herb garden setup. Basil, mint, and rosemary are thriving! 🌿',
        media: {
          url: 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400',
          type: 'image'
        },
        type: 'tip',
        likes: 89,
        isLiked: true,
        comments: [],
        shares: 156,
        createdAt: '5 hours ago',
        location: 'Portland, OR',
        tags: ['gardening', 'food', 'diy', 'sustainable']
      }
    ];

    setPosts(demoPosts);
    setLoading(false);
  }, []);

  const handleLike = (postId: string) => {
    setPosts(posts.map(post => 
      post.id === postId 
        ? { 
            ...post, 
            isLiked: !post.isLiked, 
            likes: post.isLiked ? post.likes - 1 : post.likes + 1 
          }
        : post
    ));
  };

  const handleShare = (postId: string) => {
    setPosts(posts.map(post => 
      post.id === postId 
        ? { ...post, shares: post.shares + 1 }
        : post
    ));
    // In real app, would open share modal
    alert('Post shared to your feed!');
  };

  const handleCreatePost = () => {
    if (!newPostText.trim()) return;

    const newPost: Post = {
      id: `post-${Date.now()}`,
      user: {
        id: 'current-user',
        name: 'You',
        avatar: 'https://ui-avatars.com/api/?name=You&background=22c55e&color=fff',
        level: 4,
        carbonSaved: 890
      },
      text: newPostText,
      type: 'general' as any,
      likes: 0,
      isLiked: false,
      comments: [],
      shares: 0,
      createdAt: 'just now',
      tags: []
    };

    setPosts([newPost, ...posts]);
    setNewPostText('');
    setShowCreatePost(false);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Create Post Section */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-4 mb-4">
          <Image
            src="https://ui-avatars.com/api/?name=You&background=22c55e&color=fff"
            alt="Your avatar"
            width={40}
            height={40}
            className="rounded-full"
          />
          <h2 className="text-lg font-semibold text-gray-900">Share Your Climate Action</h2>
        </div>
        
        {showCreatePost ? (
          <div className="space-y-4">
            <textarea
              value={newPostText}
              onChange={(e) => setNewPostText(e.target.value)}
              placeholder="Share your achievements, tips, or ask the community..."
              className="w-full p-3 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              rows={3}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowCreatePost(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreatePost}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Share
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowCreatePost(true)}
            className="w-full p-3 text-left text-gray-500 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            What climate action did you take today?
          </button>
        )}
      </div>

      {/* Posts Feed */}
      <div className="space-y-6">
        {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-xl shadow-sm overflow-hidden">
            {/* Post Header */}
            <div className="p-6 pb-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <Image
                    src={post.user.avatar}
                    alt={post.user.name}
                    width={40}
                    height={40}
                    className="rounded-full"
                  />
                  <div>
                    <h3 className="font-semibold text-gray-900">{post.user.name}</h3>
                    <p className="text-sm text-gray-500">
                      Level {post.user.level} • {post.createdAt}
                    </p>
                  </div>
                </div>
                {!post.user.isFollowing && post.user.id !== 'current-user' && (
                  <button className="px-4 py-1 text-sm text-green-600 border border-green-600 rounded-full hover:bg-green-50 transition-colors">
                    Follow
                  </button>
                )}
              </div>

              {/* Post Content */}
              <p className="text-gray-800 mb-4 leading-relaxed">{post.text}</p>

              {/* Achievement Badge */}
              {post.achievement && (
                <div className="flex items-center space-x-3 bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                  <span className="text-2xl">{post.achievement.icon}</span>
                  <div>
                    <p className="font-semibold text-yellow-800">{post.achievement.title}</p>
                    <p className="text-sm text-yellow-600">+{post.achievement.points} points earned</p>
                  </div>
                </div>
              )}

              {/* Carbon Impact */}
              {post.carbonImpact && (
                <div className="flex items-center space-x-3 bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                  <span className="text-2xl">🌱</span>
                  <div>
                    <p className="font-semibold text-green-800">
                      Saved {post.carbonImpact.amount} kg CO₂ {post.carbonImpact.period}
                    </p>
                    <p className="text-sm text-green-600">{post.carbonImpact.comparison}</p>
                  </div>
                </div>
              )}

              {/* Media */}
              {post.media && (
                <div className="mb-4">
                  <Image
                    src={post.media.url}
                    alt="Post media"
                    width={500}
                    height={300}
                    className="w-full h-64 object-cover rounded-lg"
                  />
                </div>
              )}

              {/* Location & Tags */}
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                {post.location && (
                  <span>📍 {post.location}</span>
                )}
                <div className="flex space-x-2">
                  {post.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="text-green-600">#{tag}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* Engagement Stats */}
            <div className="px-6 py-2 border-t border-gray-100">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{post.likes} likes</span>
                <div className="space-x-4">
                  <span>{post.comments.length} comments</span>
                  <span>{post.shares} shares</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="px-6 py-3 border-t border-gray-100">
              <div className="flex justify-around">
                <button
                  onClick={() => handleLike(post.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    post.isLiked 
                      ? 'text-green-600 bg-green-50' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <span>👍</span>
                  <span>Like</span>
                </button>
                <button className="flex items-center space-x-2 px-4 py-2 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors">
                  <span>💬</span>
                  <span>Comment</span>
                </button>
                <button
                  onClick={() => handleShare(post.id)}
                  className="flex items-center space-x-2 px-4 py-2 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <span>📤</span>
                  <span>Share</span>
                </button>
                <button className="flex items-center space-x-2 px-4 py-2 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors">
                  <span>🌱</span>
                  <span>Inspire</span>
                </button>
              </div>
            </div>

            {/* Comments */}
            {post.comments.length > 0 && (
              <div className="px-6 py-4 border-t border-gray-100">
                {post.comments.slice(0, 2).map((comment) => (
                  <div key={comment.id} className="flex items-start space-x-3 mb-3 last:mb-0">
                    <Image
                      src={comment.user.avatar}
                      alt={comment.user.name}
                      width={32}
                      height={32}
                      className="rounded-full"
                    />
                    <div className="flex-1">
                      <p className="text-sm">
                        <span className="font-semibold text-gray-900">{comment.user.name}</span>
                        {' '}
                        <span className="text-gray-700">{comment.text}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{comment.createdAt}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SocialFeed;