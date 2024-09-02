export interface HeatmapData {
  [timeIndex: number]: {
    startDate: string;
    endDate: string;
    totalCommits: number;
    pullRequests: number;
    dominantLanguage: string;
  };
}

export interface UserProfile {
  username: string;
  avatar_url: string;
  years_on_github: number;
  public_repos: number;
  followers: number;
  following: number;
  bio: string;
}

export interface RepoAnalysis {
  name: string;
  language: string;
}

export interface ApiResponse {
  user_profile: UserProfile;
  repo_analysis: RepoAnalysis[];
  heatmap_data: HeatmapData;
}
