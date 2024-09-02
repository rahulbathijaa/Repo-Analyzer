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
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Repository Analysis</h1>
      
      {/* Add the UserProfile component here */}
      <h2 className="text-2xl font-bold mb-4">User Profile</h2>
      {data?.user_profile ? (
        <UserProfile userProfile={data.user_profile} />
      ) : (
        <p>No user profile data available</p>
      )}

      {/* Keep the existing JSON output */}
      <h2 className="text-2xl font-bold mb-4 mt-8">User Profile (JSON)</h2>
      {data?.user_profile ? (
        <pre>{JSON.stringify(data.user_profile, null, 2)}</pre>
      ) : (
        <p>No user profile data available</p>
      )}

      <h2 className="text-2xl font-bold mb-4 mt-8">Repository Analysis</h2>
      {data?.repo_analysis ? (
        <RepoAnalysis analysis={data.repo_analysis} />
      ) : (
        <p>No repository analysis data available</p>
      )}
      <h2 className="text-2xl font-bold mb-4 mt-8">Contribution Heatmap</h2>
      {data?.heatmap_data ? (
        <HeatmapComponent heatmapData={data.heatmap_data} />
      ) : (
        <p>No heatmap data available</p>
      )}
    </div>
  );
}