import React from 'react';

interface RepoAnalysisProps {
  analysis: {
    repo_name: string;
    stars: number;
    forks: number;
    open_issues: number;
    watchers: number;
    score: number;
    narrative: string;
  };
}

const RepoAnalysis: React.FC<RepoAnalysisProps> = ({ analysis }) => {
  return (
    <div className="flex bg-black text-white p-4 rounded-lg">
      {/* Left column */}
      <div className="flex-1 pr-4">
        <h3 className="text-xl font-bold mb-4">{analysis.repo_name}</h3>
        <p className="mb-2">Created on: [Add creation date if available]</p>
        <p className="mb-2">Description: [Add repo description if available]</p>
        <p className="mb-2">Language: [Add primary language if available]</p>
        <p className="mb-2">Stars: {analysis.stars}</p>
        <p className="mb-2">Forks: {analysis.forks}</p>
        <p className="mb-2">Code Quality: [Add code quality metric if available]</p>
      </div>

      {/* Divider */}
      <div className="w-px bg-gray-600 mx-4"></div>

      {/* Right column */}
      <div className="flex-1 pl-4">
        <h4 className="text-lg font-semibold mb-3">Repo Summary</h4>
        <p>{analysis.narrative}</p>
      </div>
    </div>
  );
};

export default RepoAnalysis;
