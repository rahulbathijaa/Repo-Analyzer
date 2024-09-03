'use client';

import { useEffect, useState } from 'react';
import HeatmapComponent from './components/ui/HeatmapComponent';
import UserProfile from './components/ui/UserProfile';  // Add this import
import { ApiResponse } from './types';
import RepoAnalysis from './components/ui/RepoAnalysis';  // Create this component

export default function Home() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        const response = await fetch('https://rahulbathijaa--meta-llama-project-fastapi-app.modal.run/api/analyze?username=rahulbathijaa');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result: ApiResponse = await response.json();
        console.log('Received data:', result);
        setData(result);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setError(`Failed to fetch data: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  if (!data) {
    return <div>No data available</div>;
  }

  return (
    <main className="min-h-screen bg-black text-white p-8 md:p-12 lg:p-16"> {/* Added padding classes */}
      <div className="profile-container mt-6 pb-24"> {/* Added mb-12 for 48px bottom margin */}
        {data?.user_profile ? (
          <UserProfile userProfile={data.user_profile} />
        ) : (
          <p>No user profile data available</p>
        )}
      </div>
      <div className="w-px border-l border-dashed border-[#80EE64] mx-4 self-stretch"></div>
      <h2 className="text-xl font-bold ml-8 mb-4">Repository Analysis (first 3 repos)</h2>
      <div className="repo-analysis mt-12 pb-12"> {/* Added my-12 for 48px top and bottom margin */}
        {data?.repo_analysis ? (
          <RepoAnalysis analysis={data.repo_analysis} />
        ) : (
          <p>No repository analysis data available</p>
        )}
      </div>
      <div className="w-px border-l border-dashed border-[#80EE64] mx-4 self-stretch"></div>
      <div className="contribution-heatmap mt-12"> {/* Added mt-12 for 48px top margin */}
        {data?.heatmap_data ? (
          <HeatmapComponent heatmapData={data.heatmap_data} />
        ) : (
          <p>No heatmap data available</p>
        )}
      </div>
    </main>
  );
}