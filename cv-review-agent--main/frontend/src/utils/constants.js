export const ROUTES = {
  DASHBOARD: '/',
  CV_REVIEW: '/cv-review',
  DOWNLOAD: '/download',
  CHAT: '/chat',
};

export const ATS_SCORE_RANGES = {
  EXCELLENT: { min: 80, max: 100, label: 'Excellent', color: 'success' },
  GOOD: { min: 60, max: 79, label: 'Good', color: 'warning' },
  AVERAGE: { min: 40, max: 59, label: 'Average', color: 'warning' },
  POOR: { min: 0, max: 39, label: 'Poor', color: 'error' },
};

export const DATE_RANGE_OPTIONS = [
  { value: 1, label: 'Last 24 hours' },
  { value: 3, label: 'Last 3 days' },
  { value: 7, label: 'Last 7 days' },
  { value: 14, label: 'Last 14 days' },
  { value: 30, label: 'Last 30 days' },
  { value: 60, label: 'Last 60 days' },
  { value: 90, label: 'Last 90 days' },
];

export const SKILLS_CATEGORIES = [
  'Programming Languages',
  'Frameworks & Libraries',
  'Tools & Technologies',
  'Soft Skills',
  'Certifications',
];

export const CHAT_SUGGESTIONS = [
  'Show me all CVs received today',
  'Analyze CVs for Software Engineer position',
  'Download CVs from last week',
  'Find candidates with Python and React skills',
  'Show top 5 candidates by ATS score',
  'Send acknowledgment emails to all applicants',
];
