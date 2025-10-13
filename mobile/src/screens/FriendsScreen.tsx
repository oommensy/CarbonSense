// Friends Screen - Manage social connections
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
  StyleSheet,
  FlatList
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { theme } from '../styles/theme';
import { followUser, unfollowUser } from '../store/slices/socialSlice';

const FriendsScreen = () => {
  const dispatch = useDispatch();
  const { following, followers, friendSuggestions } = useSelector((state: any) => state.social);
  const [activeTab, setActiveTab] = useState<'following' | 'followers' | 'discover'>('discover');
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    // In real app, would fetch updated friend lists
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleFollow = (userId: string) => {
    dispatch(followUser(userId));
    Alert.alert('Success', 'You are now following this user!');
  };

  const handleUnfollow = (userId: string) => {
    Alert.alert(
      'Unfollow User',
      'Are you sure you want to unfollow this user?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Unfollow', 
          style: 'destructive',
          onPress: () => dispatch(unfollowUser(userId))
        }
      ]
    );
  };

  const renderUserItem = (user: any, showFollowButton = true) => (
    <View key={user.id} style={styles.userItem}>
      <Image source={{ uri: user.avatar }} style={styles.userAvatar} />
      <View style={styles.userInfo}>
        <Text style={styles.userName}>{user.name}</Text>
        <View style={styles.userStats}>
          <Text style={styles.userStat}>Level {user.level}</Text>
          <Text style={styles.userStat}>•</Text>
          <Text style={styles.userStat}>{user.carbonSaved}kg CO₂ saved</Text>
        </View>
        <View style={styles.userMeta}>
          <Text style={styles.userMetaText}>{user.followers} followers</Text>
          <Text style={styles.userMetaText}>•</Text>
          <Text style={styles.userMetaText}>{user.following} following</Text>
        </View>
      </View>
      {showFollowButton && (
        <TouchableOpacity
          style={[
            styles.actionButton,
            user.isFollowing ? styles.unfollowButton : styles.followButton
          ]}
          onPress={() => user.isFollowing ? handleUnfollow(user.id) : handleFollow(user.id)}
        >
          <Text style={[
            styles.actionButtonText,
            user.isFollowing ? styles.unfollowButtonText : styles.followButtonText
          ]}>
            {user.isFollowing ? 'Following' : 'Follow'}
          </Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'following':
        return (
          <FlatList
            data={following}
            renderItem={({ item }) => renderUserItem(item, true)}
            keyExtractor={(item) => item.id}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            ListEmptyComponent={
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateIcon}>👥</Text>
                <Text style={styles.emptyStateTitle}>No one followed yet</Text>
                <Text style={styles.emptyStateSubtitle}>
                  Find climate warriors to follow in the Discover tab!
                </Text>
              </View>
            }
          />
        );

      case 'followers':
        return (
          <FlatList
            data={followers}
            renderItem={({ item }) => renderUserItem(item, false)}
            keyExtractor={(item) => item.id}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            ListEmptyComponent={
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateIcon}>🌱</Text>
                <Text style={styles.emptyStateTitle}>No followers yet</Text>
                <Text style={styles.emptyStateSubtitle}>
                  Share your climate achievements to attract followers!
                </Text>
              </View>
            }
          />
        );

      case 'discover':
        return (
          <ScrollView
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          >
            {/* Search Bar */}
            <View style={styles.searchContainer}>
              <TextInput
                style={styles.searchInput}
                placeholder="Search for climate warriors..."
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
            </View>

            {/* Friend Suggestions */}
            <Text style={styles.sectionTitle}>🔥 Climate Leaders to Follow</Text>
            {friendSuggestions.map(user => renderUserItem(user))}

            {/* Community Highlights */}
            <Text style={styles.sectionTitle}>🌟 Community Highlights</Text>
            <View style={styles.highlightCard}>
              <Text style={styles.highlightTitle}>Top Carbon Saver This Month</Text>
              <View style={styles.highlightUser}>
                <Image 
                  source={{ uri: 'https://ui-avatars.com/api/?name=Emma+Planet&background=10b981&color=fff' }} 
                  style={styles.highlightAvatar} 
                />
                <View>
                  <Text style={styles.highlightName}>Emma Planet</Text>
                  <Text style={styles.highlightStat}>Saved 2,340 kg CO₂ this month!</Text>
                </View>
              </View>
            </View>

            <View style={styles.highlightCard}>
              <Text style={styles.highlightTitle}>Challenge Champion</Text>
              <View style={styles.highlightUser}>
                <Image 
                  source={{ uri: 'https://ui-avatars.com/api/?name=David+Solar&background=eab308&color=fff' }} 
                  style={styles.highlightAvatar} 
                />
                <View>
                  <Text style={styles.highlightName}>David Solar</Text>
                  <Text style={styles.highlightStat}>Completed 15 challenges in a row!</Text>
                </View>
              </View>
            </View>

            {/* Join Communities */}
            <Text style={styles.sectionTitle}>🏘️ Join Communities</Text>
            <TouchableOpacity style={styles.communityCard}>
              <Text style={styles.communityIcon}>🚲</Text>
              <View style={styles.communityInfo}>
                <Text style={styles.communityName}>Bike Commuters</Text>
                <Text style={styles.communityMembers}>2,340 members</Text>
                <Text style={styles.communityDescription}>Share bike routes and car-free tips</Text>
              </View>
              <TouchableOpacity style={styles.joinButton}>
                <Text style={styles.joinButtonText}>Join</Text>
              </TouchableOpacity>
            </TouchableOpacity>

            <TouchableOpacity style={styles.communityCard}>
              <Text style={styles.communityIcon}>🌱</Text>
              <View style={styles.communityInfo}>
                <Text style={styles.communityName}>Urban Gardeners</Text>
                <Text style={styles.communityMembers}>1,890 members</Text>
                <Text style={styles.communityDescription}>Grow your own food and share tips</Text>
              </View>
              <TouchableOpacity style={styles.joinButton}>
                <Text style={styles.joinButtonText}>Join</Text>
              </TouchableOpacity>
            </TouchableOpacity>

            <TouchableOpacity style={styles.communityCard}>
              <Text style={styles.communityIcon}>⚡</Text>
              <View style={styles.communityInfo}>
                <Text style={styles.communityName}>Solar Enthusiasts</Text>
                <Text style={styles.communityMembers}>956 members</Text>
                <Text style={styles.communityDescription}>Solar installation tips and ROI discussions</Text>
              </View>
              <TouchableOpacity style={styles.joinButton}>
                <Text style={styles.joinButtonText}>Join</Text>
              </TouchableOpacity>
            </TouchableOpacity>
          </ScrollView>
        );

      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Climate Network</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'discover' && styles.activeTab]}
          onPress={() => setActiveTab('discover')}
        >
          <Text style={[styles.tabText, activeTab === 'discover' && styles.activeTabText]}>
            Discover
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'following' && styles.activeTab]}
          onPress={() => setActiveTab('following')}
        >
          <Text style={[styles.tabText, activeTab === 'following' && styles.activeTabText]}>
            Following ({following.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'followers' && styles.activeTab]}
          onPress={() => setActiveTab('followers')}
        >
          <Text style={[styles.tabText, activeTab === 'followers' && styles.activeTabText]}>
            Followers ({followers.length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <View style={styles.content}>
        {renderTabContent()}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.primary,
  },
  tabText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  activeTabText: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  searchContainer: {
    padding: 16,
  },
  searchInput: {
    backgroundColor: theme.colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
    fontSize: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginHorizontal: 16,
    marginTop: 24,
    marginBottom: 12,
  },
  userItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  userAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 12,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 4,
  },
  userStats: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  userStat: {
    fontSize: 12,
    color: theme.colors.primary,
    fontWeight: '600',
    marginRight: 4,
  },
  userMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userMetaText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginRight: 4,
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
  },
  followButton: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  unfollowButton: {
    backgroundColor: 'transparent',
    borderColor: theme.colors.border,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  followButtonText: {
    color: '#fff',
  },
  unfollowButtonText: {
    color: theme.colors.textSecondary,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
  },
  emptyStateSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  highlightCard: {
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  highlightTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.primary,
    marginBottom: 12,
  },
  highlightUser: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  highlightAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 12,
  },
  highlightName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 2,
  },
  highlightStat: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  communityCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  communityIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  communityInfo: {
    flex: 1,
  },
  communityName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 2,
  },
  communityMembers: {
    fontSize: 12,
    color: theme.colors.primary,
    fontWeight: '600',
    marginBottom: 4,
  },
  communityDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  joinButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  joinButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default FriendsScreen;