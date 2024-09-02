'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        const response = await fetch('https://rahulbathijaa--meta-llama-project-fastapi-app.modal.run/api/analyze?username=rahulbathijaa');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        console.log('Received data:', result);  // Log the received data
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
    <div>
      <h1>Repository Analysis</h1>
      <h2>User Profile</h2>
      {data?.user_profile ? (
        <pre>{JSON.stringify(data.user_profile, null, 2)}</pre>
      ) : (
        <p>No user profile data available</p>
      )}
      <h2>Repository Analysis</h2>
      {data?.repo_analysis ? (
        <pre>{JSON.stringify(data.repo_analysis, null, 2)}</pre>
      ) : (
        <p>No repository analysis data available</p>
      )}
    </div>
  );
}