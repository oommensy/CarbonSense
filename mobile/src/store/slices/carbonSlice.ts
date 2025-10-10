import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CarbonEntry {
  id: string;
  type: 'transport' | 'food' | 'energy' | 'consumption';
  amount: number;
  description: string;
  date: string;
  verified: boolean;
}

interface CarbonState {
  todayTotal: number;
  weekTotal: number;
  monthTotal: number;
  yearTotal: number;
  entries: CarbonEntry[];
  goals: {
    daily: number;
    weekly: number;
    monthly: number;
    yearly: number;
  };
}

const initialState: CarbonState = {
  todayTotal: 0,
  weekTotal: 0,
  monthTotal: 0,
  yearTotal: 0,
  entries: [],
  goals: {
    daily: 50, // kg CO2
    weekly: 350,
    monthly: 1500,
    yearly: 18000,
  },
};

const carbonSlice = createSlice({
  name: 'carbon',
  initialState,
  reducers: {
    addCarbonEntry: (state, action: PayloadAction<Omit<CarbonEntry, 'id'>>) => {
      const newEntry: CarbonEntry = {
        ...action.payload,
        id: Date.now().toString(),
      };
      state.entries.push(newEntry);
      
      // Update totals based on entry date
      const today = new Date().toDateString();
      const entryDate = new Date(action.payload.date).toDateString();
      
      if (entryDate === today) {
        state.todayTotal += action.payload.amount;
      }
      
      // Recalculate week, month, year totals
      // This is simplified - in production, you'd use proper date calculations
      state.weekTotal += action.payload.amount;
      state.monthTotal += action.payload.amount;
      state.yearTotal += action.payload.amount;
    },
    
    updateGoals: (state, action: PayloadAction<Partial<CarbonState['goals']>>) => {
      state.goals = { ...state.goals, ...action.payload };
    },
    
    verifyEntry: (state, action: PayloadAction<string>) => {
      const entry = state.entries.find(e => e.id === action.payload);
      if (entry) {
        entry.verified = true;
      }
    },
    
    clearTodayEntries: (state) => {
      state.todayTotal = 0;
      const today = new Date().toDateString();
      state.entries = state.entries.filter(
        entry => new Date(entry.date).toDateString() !== today
      );
    },
  },
});

export const { 
  addCarbonEntry, 
  updateGoals, 
  verifyEntry, 
  clearTodayEntries 
} = carbonSlice.actions;

export default carbonSlice.reducer;