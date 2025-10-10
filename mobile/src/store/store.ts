import { configureStore } from '@reduxjs/toolkit';
import userSlice from './slices/userSlice';
import carbonSlice from './slices/carbonSlice';
import challengesSlice from './slices/challengesSlice';

export const store = configureStore({
  reducer: {
    user: userSlice,
    carbon: carbonSlice,
    challenges: challengesSlice,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;