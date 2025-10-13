import { configureStore } from '@reduxjs/toolkit';
import carbonReducer from './slices/carbonSlice';
import userReducer from './slices/userSlice';
import challengesReducer from './slices/challengesSlice';
import socialReducer from './slices/socialSlice';

export const store = configureStore({
  reducer: {
    carbon: carbonReducer,
    user: userReducer,
    challenges: challengesReducer,
    social: socialReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;