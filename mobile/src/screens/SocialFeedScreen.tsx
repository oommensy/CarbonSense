// Social Feed Screen - Main social media interface
import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  TouchableOpacity, 
  Image, 
  TextInput,
  Alert,
  RefreshControl,
  Modal,
  StyleSheet 
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { theme } from '../styles/theme';
import { 
  loadFeed, 
  createPost, 
  likePost, 
  commentOnPost, 
  sharePost,
  followUser,
  unfollowUser 
} from '../store/slices/socialSlice';

const SocialFeedScreen = () => {
  const dispatch = useDispatch();
  const { feed, isLoading, user } = useSelector((state: any) => ({
    feed: state.social.feed,
    isLoading: state.social.isLoading,
    user: state.user.profile
  }));

  const [refreshing, setRefreshing] = useState(false);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [newPostText, setNewPostText] = useState('');
  const [selectedMedia, setSelectedMedia] = useState(null);

  useEffect(() => {
    dispatch(loadFeed());
  }, [dispatch]);

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(loadFeed());
    setRefreshing(false);
  };

  const handleCreatePost = () => {
    if (!newPostText.trim()) {
      Alert.alert('Error', 'Please enter some content for your post');
      return;
    }

    dispatch(createPost({
      text: newPostText,
      media: selectedMedia,
      type: 'achievement' // or 'tip', 'question', 'milestone'
    }));

    setNewPostText('');
    setSelectedMedia(null);
    setShowCreatePost(false);
  };

  const handleLike = (postId: string) => {
    dispatch(likePost(postId));
  };

  const handleComment = (postId: string, comment: string) => {
    dispatch(commentOnPost({ postId, comment }));
  };

  const handleShare = (postId: string) => {
    dispatch(sharePost(postId));
  };

  const renderPost = (post: any) => (
    <View key={post.id} style={styles.postContainer}>
      {/* User Header */}
      <View style={styles.postHeader}>
        <Image source={{ uri: post.user.avatar }} style={styles.avatar} />
        <View style={styles.userInfo}>
          <Text style={styles.username}>{post.user.name}</Text>
          <Text style={styles.postTime}>{post.createdAt}</Text>
        </View>
        <TouchableOpacity 
          style={styles.followButton}
          onPress={() => dispatch(post.user.isFollowing ? unfollowUser(post.user.id) : followUser(post.user.id))}
        >
          <Text style={styles.followButtonText}>
            {post.user.isFollowing ? 'Following' : 'Follow'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Post Content */}
      <Text style={styles.postText}>{post.text}</Text>
      
      {/* Achievement Badge */}
      {post.achievement && (
        <View style={styles.achievementBadge}>
          <Text style={styles.achievementIcon}>🏆</Text>
          <Text style={styles.achievementText}>{post.achievement.title}</Text>
          <Text style={styles.achievementPoints}>+{post.achievement.points} points</Text>
        </View>
      )}

      {/* Carbon Impact Display */}
      {post.carbonImpact && (
        <View style={styles.carbonImpact}>
          <Text style={styles.carbonIcon}>🌱</Text>
          <Text style={styles.carbonText}>
            Saved {post.carbonImpact.amount} kg CO₂ this week
          </Text>
        </View>
      )}

      {/* Media */}
      {post.media && (
        <Image source={{ uri: post.media.url }} style={styles.postMedia} />
      )}

      {/* Engagement Stats */}
      <View style={styles.engagementStats}>
        <Text style={styles.statText}>{post.likes} likes</Text>
        <Text style={styles.statText}>{post.comments.length} comments</Text>
        <Text style={styles.statText}>{post.shares} shares</Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity 
          style={[styles.actionButton, post.isLiked && styles.likedButton]}
          onPress={() => handleLike(post.id)}
        >
          <Text style={styles.actionIcon}>👍</Text>
          <Text style={styles.actionText}>Like</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => {/* Show comment modal */}}
        >
          <Text style={styles.actionIcon}>💬</Text>
          <Text style={styles.actionText}>Comment</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => handleShare(post.id)}
        >
          <Text style={styles.actionIcon}>📤</Text>
          <Text style={styles.actionText}>Share</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionIcon}>🌱</Text>
          <Text style={styles.actionText}>Inspire</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Comments */}
      {post.comments.slice(0, 2).map((comment: any) => (
        <View key={comment.id} style={styles.comment}>
          <Text style={styles.commentUser}>{comment.user.name}</Text>
          <Text style={styles.commentText}>{comment.text}</Text>
        </View>
      ))}
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header with Create Post Button */}
      <View style={styles.header}>
        <Text style={styles.title}>🌍 Climate Feed</Text>
        <TouchableOpacity 
          style={styles.createButton}
          onPress={() => setShowCreatePost(true)}
        >
          <Text style={styles.createButtonText}>+ Share</Text>
        </TouchableOpacity>
      </View>

      {/* Feed */}
      <ScrollView
        style={styles.feed}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {feed.map(renderPost)}
      </ScrollView>

      {/* Create Post Modal */}
      <Modal
        visible={showCreatePost}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.createPostModal}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowCreatePost(false)}>
              <Text style={styles.modalCancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Share Your Impact</Text>
            <TouchableOpacity onPress={handleCreatePost}>
              <Text style={styles.modalPost}>Post</Text>
            </TouchableOpacity>
          </View>

          <TextInput
            style={styles.postInput}
            placeholder="Share your climate action, achievement, or tip..."
            multiline
            value={newPostText}
            onChangeText={setNewPostText}
            maxLength={500}
          />

          {/* Quick Action Buttons */}
          <View style={styles.quickActions}>
            <TouchableOpacity style={styles.quickAction}>
              <Text style={styles.quickActionIcon}>🏆</Text>
              <Text style={styles.quickActionText}>Achievement</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickAction}>
              <Text style={styles.quickActionIcon}>💡</Text>
              <Text style={styles.quickActionText}>Tip</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickAction}>
              <Text style={styles.quickActionIcon}>📊</Text>
              <Text style={styles.quickActionText}>Progress</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickAction}>
              <Text style={styles.quickActionIcon}>🤝</Text>
              <Text style={styles.quickActionText}>Challenge</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  createButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  createButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  feed: {
    flex: 1,
  },
  postContainer: {
    backgroundColor: theme.colors.surface,
    marginBottom: 8,
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  postHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 12,
  },
  userInfo: {
    flex: 1,
  },
  username: {
    fontWeight: '600',
    color: theme.colors.text,
    fontSize: 16,
  },
  postTime: {
    color: theme.colors.textSecondary,
    fontSize: 12,
  },
  followButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: theme.colors.primary,
  },
  followButtonText: {
    color: theme.colors.primary,
    fontSize: 12,
    fontWeight: '600',
  },
  postText: {
    fontSize: 16,
    lineHeight: 22,
    color: theme.colors.text,
    marginBottom: 12,
  },
  achievementBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3CD',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  achievementIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  achievementText: {
    flex: 1,
    fontWeight: '600',
    color: '#856404',
  },
  achievementPoints: {
    color: '#856404',
    fontSize: 12,
    fontWeight: '600',
  },
  carbonImpact: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#D4EDDA',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  carbonIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  carbonText: {
    color: '#155724',
    fontWeight: '600',
  },
  postMedia: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginBottom: 12,
  },
  engagementStats: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  statText: {
    color: theme.colors.textSecondary,
    fontSize: 12,
    marginRight: 16,
  },
  actionButtons: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    paddingTop: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 8,
  },
  likedButton: {
    backgroundColor: theme.colors.primaryLight,
  },
  actionIcon: {
    fontSize: 16,
    marginRight: 4,
  },
  actionText: {
    color: theme.colors.textSecondary,
    fontSize: 14,
  },
  comment: {
    flexDirection: 'row',
    marginTop: 8,
    paddingLeft: 12,
  },
  commentUser: {
    fontWeight: '600',
    color: theme.colors.text,
    marginRight: 8,
  },
  commentText: {
    color: theme.colors.text,
    flex: 1,
  },
  createPostModal: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  modalCancel: {
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
  },
  modalPost: {
    color: theme.colors.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  postInput: {
    flex: 1,
    padding: 16,
    fontSize: 16,
    textAlignVertical: 'top',
    color: theme.colors.text,
  },
  quickActions: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  quickAction: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
  },
  quickActionIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  quickActionText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
});

export default SocialFeedScreen;