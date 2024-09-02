import React from 'react';

interface RepoAnalysisProps {
  analysis: {
    repo_name: string;
    stars: number;
    forks: number;
    open_issues: number;
    watchers: number;
    overall_score: number;  // Changed from 'score' to 'overall_score'
    narrative: string;
  };
}

const RepoAnalysis: React.FC<RepoAnalysisProps> = ({ analysis }) => {
  const getCodeQuality = (score: number) => {
    if (score > 90) return 'Excellent';  // Changed thresholds to match 0-100 scale
    if (score > 70) return 'Good';
    if (score > 50) return 'Fair';
    return 'Needs Improvement';
  };

  const narrativeParagraphs = analysis.narrative.split('\n\n');

  return (
    <div className="flex bg-black text-white p-4 rounded-lg">
      {/* Left column */}
      <div className="flex-1 pr-4">
        <h3 className="text-xl font-bold mb-4">{analysis.repo_name}</h3>
        <p className="mb-2">Stars: {analysis.stars}</p>
        <p className="mb-2">Forks: {analysis.forks}</p>
        <p className="mb-2">Open Issues: {analysis.open_issues}</p>
        <p className="mb-2">Watchers: {analysis.watchers}</p>
        <p className="mb-2">Code Quality: {getCodeQuality(analysis.overall_score)}</p> 
      </div>

      {/* Divider */}
      <div className="w-px bg-gray-600 mx-4"></div>

      {/* Right column */}
      <div className="flex-1 pl-4">
        <h4 className="text-lg font-semibold mb-3">Repo Summary</h4>
        {narrativeParagraphs.map((paragraph, index) => (
          <p key={index} className="mb-2">{paragraph}</p>
        ))}
      </div>
    </div>
  );
};

export default RepoAnalysis;
