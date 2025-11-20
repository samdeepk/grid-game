// Generate a consistent color based on a string input (e.g. player ID or name)
export const getPlayerColor = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Modern, pleasing palette
  const colors = [
    '#FF6B6B', // Soft Red
    '#4ECDC4', // Teal
    '#45B7D1', // Sky Blue
    '#FFA07A', // Light Salmon
    '#98D8C8', // Mint
    '#F7DC6F', // Mellow Yellow
    '#BB8FCE', // Lilac
    '#F1948A', // Rose
    '#85C1E9', // Light Blue
    '#82E0AA', // Light Green
  ];

  const index = Math.abs(hash) % colors.length;
  return colors[index];
};

export const getPlayerContrastColor = (hexColor: string): string => {
  // specific overrides if needed, or generic brightness calc
  // For now, assuming all palette colors work well with white or dark gray
  return '#ffffff';
};


