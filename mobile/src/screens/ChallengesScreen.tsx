// Challenges Screen - Social challenges and community competitions
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Image,
  RefreshControl,
  StyleSheet,
  Alert
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { theme } from '../styles/theme';
import {
  loadAvailableChallenges,
  joinChallenge,
  updateProgress,
  updateLeaderboard,
  abandonChallenge
} from '../store/slices/challengesSlice';

const ChallengesScreen = () => {
  const dispatch = useDispatch();
  const {
    activeChallenges,
    availableChallenges,
    completedChallenges,
    totalPoints,
    currentRank,
    leaderboard
  } = useSelector((state: any) => state.challenges);

  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'discover' | 'active' | 'leaderboard'>('discover');

  useEffect(() => {
    // Load demo data
    const demoLeaderboard = [
      { id: 'user-1', name: 'Alex Chen', points: 2850, rank: 1 },
      { id: 'user-2', name: 'Sarah Johnson', points: 2720, rank: 2 },
      { id: 'demo-user', name: 'You', points: 2650, rank: 3 },
      { id: 'user-4', name: 'Mike Rodriguez', points: 2540, rank: 4 },
      { id: 'user-5', name: 'Emma Wilson', points: 2480, rank: 5 }
    ];
    dispatch(updateLeaderboard(demoLeaderboard));
  }, [dispatch]);

  const onRefresh = async () => {
    setRefreshing(true);
    // In real app, would fetch from API
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleJoinChallenge = (challenge: any) => {
    dispatch(joinChallenge(challenge));
    Alert.alert('Challenge Joined!', `You've joined "${challenge.title}". Good luck! 🌱`);
  };

  const handleUpdateProgress = (challengeId: string, progress: number) => {
    dispatch(updateProgress({ id: challengeId, progress }));
    if (progress >= 100) {
      Alert.alert('Challenge Completed! 🎉', 'Congratulations on completing this challenge!');
    }
  };

  const renderChallenge = (challenge: any, isActive = false) => {
    const getDifficultyColor = (difficulty: string) => {
      switch (difficulty) {
        case 'easy': return '#22c55e';
        case 'medium': return '#f59e0b';
        case 'hard': return '#ef4444';
        default: return theme.colors.textSecondary;
      }
    };

    const getCategoryIcon = (category: string) => {
      switch (category) {
        case 'transport': return '🚗';
        case 'food': return '🍃';
        case 'energy': return '⚡';
        case 'consumption': return '🛍️';
        default: return '🌱';
      }
    };

    return (
      <View key={challenge.id} style={styles.challengeCard}>
        {/* Challenge Header */}
        <View style={styles.challengeHeader}>
          <View style={styles.challengeInfo}>
            <Text style={styles.challengeIcon}>{getCategoryIcon(challenge.category)}</Text>
            <View style={styles.challengeDetails}>
              <Text style={styles.challengeTitle}>{challenge.title}</Text>
              <Text style={styles.challengeType}>
                {challenge.type} • {challenge.duration} days
              </Text>
            </View>
          </View>
          <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(challenge.difficulty) }]}>
            <Text style={styles.difficultyText}>{challenge.difficulty}</Text>
          </View>
        </View>

        {/* Challenge Description */}
        <Text style={styles.challengeDescription}>{challenge.description}</Text>

        {/* Progress Bar (for active challenges) */}
        {isActive && (
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${challenge.progress}%` }
                ]} 
              />
            </View>
            <Text style={styles.progressText}>{challenge.progress}% complete</Text>
          </View>
        )}

        {/* Challenge Stats */}
        <View style={styles.challengeStats}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{challenge.points}</Text>
            <Text style={styles.statLabel}>Points</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{challenge.participants}</Text>
            <Text style={styles.statLabel}>Participants</Text>
          </View>
          {challenge.completionRate && (
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{challenge.completionRate}%</Text>
              <Text style={styles.statLabel}>Success Rate</Text>
            </View>
          )}
        </View>

        {/* Action Button */}
        <View style={styles.challengeActions}>
          {isActive ? (
            <View style={styles.activeActions}>
              <TouchableOpacity
                style={styles.progressButton}
                onPress={() => handleUpdateProgress(challenge.id, Math.min(100, challenge.progress + 25))}
              >
                <Text style={styles.progressButtonText}>Update Progress</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.abandonButton}
                onPress={() => {
                  Alert.alert(
                    'Abandon Challenge',
                    'Are you sure you want to abandon this challenge?',
                    [
                      { text: 'Cancel', style: 'cancel' },
                      { text: 'Abandon', style: 'destructive', onPress: () => dispatch(abandonChallenge(challenge.id)) }
                    ]
                  );
                }}
              >
                <Text style={styles.abandonButtonText}>Abandon</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity
              style={styles.joinButton}
              onPress={() => handleJoinChallenge(challenge)}
            >
              <Text style={styles.joinButtonText}>Join Challenge</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  const renderLeaderboardItem = (item: any, index: number) => (
    <View key={item.id} style={styles.leaderboardItem}>
      <View style={styles.rankContainer}>
        <Text style={styles.rankNumber}>#{item.rank}</Text>
        {index < 3 && (
          <Text style={styles.medalIcon}>
            {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
          </Text>
        )}
      </View>
      <Image 
        source={{ 
          uri: `https://ui-avatars.com/api/?name=${encodeURIComponent(item.name)}&background=22c55e&color=fff` 
        }} 
        style={styles.leaderboardAvatar} 
      />
      <View style={styles.leaderboardInfo}>
        <Text style={styles.leaderboardName}>{item.name}</Text>
        <Text style={styles.leaderboardPoints}>{item.points} points</Text>
      </View>
      {item.id === 'demo-user' && (
        <View style={styles.youBadge}>
          <Text style={styles.youBadgeText}>You</Text>
        </View>
      )}
    </View>
  );

  const renderTabContent = () => {
    switch (selectedTab) {
      case 'discover':
        return (
          <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
            {availableChallenges.length > 0 ? (
              availableChallenges.map(challenge => renderChallenge(challenge, false))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateIcon}>🎯</Text>
                <Text style={styles.emptyStateTitle}>No challenges available</Text>
                <Text style={styles.emptyStateSubtitle}>Check back later for new challenges!</Text>
              </View>
            )}
          </ScrollView>
        );

      case 'active':
        return (
          <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
            {activeChallenges.length > 0 ? (
              activeChallenges.map(challenge => renderChallenge(challenge, true))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateIcon}>🌱</Text>
                <Text style={styles.emptyStateTitle}>No active challenges</Text>
                <Text style={styles.emptyStateSubtitle}>Join a challenge from the Discover tab!</Text>
              </View>
            )}
          </ScrollView>
        );

      case 'leaderboard':
        return (
          <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
            <View style={styles.leaderboardHeader}>
              <Text style={styles.leaderboardTitle}>🏆 Global Leaderboard</Text>
              <Text style={styles.leaderboardSubtitle}>Top climate warriors this month</Text>
            </View>
            {leaderboard.map((item, index) => renderLeaderboardItem(item, index))}
          </ScrollView>
        );

      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      {/* Header with User Stats */}
      <View style={styles.header}>
        <Text style={styles.title}>Climate Challenges</Text>
        <View style={styles.userStats}>
          <Text style={styles.userStatValue}>{totalPoints}</Text>
          <Text style={styles.userStatLabel}>Total Points</Text>
        </View>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'discover' && styles.activeTab]}
          onPress={() => setSelectedTab('discover')}
        >
          <Text style={[styles.tabText, selectedTab === 'discover' && styles.activeTabText]}>
            Discover
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'active' && styles.activeTab]}
          onPress={() => setSelectedTab('active')}
        >
          <Text style={[styles.tabText, selectedTab === 'active' && styles.activeTabText]}>
            Active ({activeChallenges.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'leaderboard' && styles.activeTab]}
          onPress={() => setSelectedTab('leaderboard')}
        >
          <Text style={[styles.tabText, selectedTab === 'leaderboard' && styles.activeTabText]}>
            Leaderboard
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  userStats: {
    alignItems: 'center',
  },
  userStatValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  userStatLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
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
  challengeCard: {
    backgroundColor: theme.colors.surface,
    margin: 12,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  challengeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  challengeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  challengeIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  challengeDetails: {
    flex: 1,
  },
  challengeTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 4,
  },
  challengeType: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    textTransform: 'capitalize',
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  difficultyText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  challengeDescription: {
    fontSize: 14,
    color: theme.colors.text,
    lineHeight: 20,
    marginBottom: 16,
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressBar: {
    height: 8,
    backgroundColor: theme.colors.background,
    borderRadius: 4,
    marginBottom: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: theme.colors.primary,
    borderRadius: 4,
  },
  progressText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    textAlign: 'right',
  },
  challengeStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    paddingVertical: 12,
    backgroundColor: theme.colors.background,
    borderRadius: 8,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  challengeActions: {
    marginTop: 8,
  },
  activeActions: {
    flexDirection: 'row',
    gap: 8,
  },
  joinButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  joinButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  progressButton: {
    flex: 1,
    backgroundColor: theme.colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  progressButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  abandonButton: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.error,
    alignItems: 'center',
  },
  abandonButtonText: {
    color: theme.colors.error,
    fontSize: 14,
    fontWeight: '600',
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
  },
  leaderboardHeader: {
    padding: 16,
    alignItems: 'center',
  },
  leaderboardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 4,
  },
  leaderboardSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  leaderboardItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: theme.colors.surface,
    marginHorizontal: 12,
    marginBottom: 8,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  rankContainer: {
    width: 40,
    alignItems: 'center',
    marginRight: 12,
  },
  rankNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
  },
  medalIcon: {
    fontSize: 16,
    marginTop: 2,
  },
  leaderboardAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 12,
  },
  leaderboardInfo: {
    flex: 1,
  },
  leaderboardName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 2,
  },
  leaderboardPoints: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  youBadge: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  youBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
});

export default ChallengesScreen;