export const theme = {
  colors: {
    primary: '#2E7D32', // Forest Green
    secondary: '#4CAF50', // Light Green
    accent: '#FF8A65', // Coral
    background: '#F5F5F5',
    surface: '#FFFFFF',
    text: '#333333',
    textSecondary: '#666666',
    error: '#F44336',
    success: '#4CAF50',
    warning: '#FF9800',
    info: '#2196F3',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: 'bold' as const,
      lineHeight: 40,
    },
    h2: {
      fontSize: 24,
      fontWeight: 'bold' as const,
      lineHeight: 32,
    },
    h3: {
      fontSize: 20,
      fontWeight: '600' as const,
      lineHeight: 28,
    },
    body: {
      fontSize: 16,
      fontWeight: 'normal' as const,
      lineHeight: 24,
    },
    caption: {
      fontSize: 12,
      fontWeight: 'normal' as const,
      lineHeight: 16,
    },
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
  },
};