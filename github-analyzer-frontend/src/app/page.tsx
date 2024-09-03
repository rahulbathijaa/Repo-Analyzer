'use client';

import { useEffect, useState } from 'react';
import HeatmapComponent from './components/ui/HeatmapComponent';
import UserProfile from './components/ui/UserProfile';  
import RepoAnalysis from './components/ui/RepoAnalysis'; 

// Add this interface near the top of your file
interface AnalysisData {
  user_profile?: any;
  repo_analysis?: any;
  heatmap_data?: any;
}

export default function Home() {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [githubUrl, setGithubUrl] = useState<string>('');

  const extractUsername = (url: string) => {
    const match = url.match(/github\.com\/([^\/]+)/);
    return match ? match[1] : null;
  };

  const handleAnalyze = async () => {
    const username = extractUsername(githubUrl);
    if (!username) {
      setError('Invalid GitHub URL');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`https://rahulbathijaa--meta-llama-project-fastapi-app.modal.run/api/analyze?username=${username}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      console.log('Received data:', result);
      setData(result);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError(`Failed to fetch data: ${(error as Error).message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white p-8 md:p-12 lg:p-16">
      <div className="flex flex-col items-center">
        <input
          type="text"
          placeholder="Enter GitHub URL"
          value={githubUrl}
          onChange={(e) => setGithubUrl(e.target.value)}
          className="p-2 mb-4 text-black"
        />
        <button
          onClick={handleAnalyze}
          className="bg-[#80EE64] text-black p-2 rounded"
        >
          Analyze
        </button>
      </div>
      {isLoading && <div>Loading...</div>}
      {error && <div>{error}</div>}
      {!isLoading && !error && !data && <div>No data available</div>}
      {data && (
        <>
          <div className="profile-container mt-12 pb-12">
            {data.user_profile ? (
              <UserProfile userProfile={data.user_profile} />
            ) : (
              <p>No user profile data available</p>
            )}
          </div>
          <div className="repo-analysis mt-12 pb-12">
            {data.repo_analysis ? (
              <RepoAnalysis analysis={data.repo_analysis} />
            ) : (
              <p>No repository analysis data available</p>
            )}
          </div>
          <div className="contribution-heatmap mt-12">
            {data.heatmap_data ? (
              <HeatmapComponent heatmapData={data.heatmap_data} />
            ) : (
              <p>No heatmap data available</p>
            )}
          </div>
        </>
      )}
    </main>
  );
}