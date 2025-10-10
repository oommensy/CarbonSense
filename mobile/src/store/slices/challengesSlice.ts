import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'individual' | 'team' | 'community';
  difficulty: 'easy' | 'medium' | 'hard';
  points: number;
  duration: number; // days
  startDate: string;
  endDate: string;
  progress: number; // 0-100
  completed: boolean;
  participants: number;
  category: 'transport' | 'food' | 'energy' | 'consumption' | 'general';
}

interface ChallengesState {
  activeChallenges: Challenge[];
  completedChallenges: Challenge[];
  availableChallenges: Challenge[];
  totalPoints: number;
  currentRank: number;
  leaderboard: Array<{
    id: string;
    name: string;
    points: number;
    rank: number;
  }>;
}

const initialState: ChallengesState = {
  activeChallenges: [],
  completedChallenges: [],
  availableChallenges: [],
  totalPoints: 0,
  currentRank: 0,
  leaderboard: [],
};

const challengesSlice = createSlice({
  name: 'challenges',
  initialState,
  reducers: {
    joinChallenge: (state, action: PayloadAction<Challenge>) => {
      const challenge = { ...action.payload, progress: 0, completed: false };
      state.activeChallenges.push(challenge);
      state.availableChallenges = state.availableChallenges.filter(
        c => c.id !== action.payload.id
      );
    },
    
    updateProgress: (state, action: PayloadAction<{ id: string; progress: number }>) => {
      const challenge = state.activeChallenges.find(c => c.id === action.payload.id);
      if (challenge) {
        challenge.progress = action.payload.progress;
        
        if (challenge.progress >= 100) {
          challenge.completed = true;
          state.totalPoints += challenge.points;
          state.completedChallenges.push(challenge);
          state.activeChallenges = state.activeChallenges.filter(
            c => c.id !== action.payload.id
          );
        }
      }
    },
    
    loadAvailableChallenges: (state, action: PayloadAction<Challenge[]>) => {
      state.availableChallenges = action.payload;
    },
    
    updateLeaderboard: (state, action: PayloadAction<ChallengesState['leaderboard']>) => {
      state.leaderboard = action.payload;
      // Find current user's rank (this would be based on user ID in real implementation)
      const userEntry = action.payload.find(entry => entry.id === 'current-user');
      state.currentRank = userEntry?.rank || 0;
    },
    
    abandonChallenge: (state, action: PayloadAction<string>) => {
      const challenge = state.activeChallenges.find(c => c.id === action.payload);
      if (challenge) {
        state.activeChallenges = state.activeChallenges.filter(
          c => c.id !== action.payload
        );
        state.availableChallenges.push(challenge);
      }
    },
  },
});

export const {
  joinChallenge,
  updateProgress,
  loadAvailableChallenges,
  updateLeaderboard,
  abandonChallenge,
} = challengesSlice.actions;

export default challengesSlice.reducer;