import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
  id: string | null;
  email: string | null;
  name: string | null;
  isAuthenticated: boolean;
  carbonScore: number;
  totalOffset: number;
  level: number;
  badges: string[];
}

const initialState: UserState = {
  id: null,
  email: null,
  name: null,
  isAuthenticated: false,
  carbonScore: 0,
  totalOffset: 0,
  level: 1,
  badges: [],
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    loginUser: (state, action: PayloadAction<{
      id: string;
      email: string;
      name: string;
      carbonScore: number;
      totalOffset: number;
      level: number;
      badges: string[];
    }>) => {
      state.id = action.payload.id;
      state.email = action.payload.email;
      state.name = action.payload.name;
      state.carbonScore = action.payload.carbonScore;
      state.totalOffset = action.payload.totalOffset;
      state.level = action.payload.level;
      state.badges = action.payload.badges;
      state.isAuthenticated = true;
    },
    logoutUser: (state) => {
      state.id = null;
      state.email = null;
      state.name = null;
      state.isAuthenticated = false;
      state.carbonScore = 0;
      state.totalOffset = 0;
      state.level = 1;
      state.badges = [];
    },
    updateCarbonScore: (state, action: PayloadAction<number>) => {
      state.carbonScore = action.payload;
    },
    addBadge: (state, action: PayloadAction<string>) => {
      if (!state.badges.includes(action.payload)) {
        state.badges.push(action.payload);
      }
    },
  },
});

export const { loginUser, logoutUser, updateCarbonScore, addBadge } = userSlice.actions;
export default userSlice.reducer;