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
    if (score > 75) return 'Excellent';  // Changed thresholds to match 0-100 scale
    if (score > 50) return 'Good';
    if (score > 25) return 'Fair';
    return 'Needs Improvement';
  };

  const narrativeParagraphs = analysis.narrative.split('\n\n');

  return (
    <div className="bg-black text-white rounded-lg pl-8 pr-24">
      {/* Title row */}
      <div className="w-full mb-6">
        <h2 className="text-4xl font-bold">{analysis.repo_name} Score: {getCodeQuality(analysis.overall_score)}</h2>
      </div>

      {/* Content row */}
      <div className="flex">
        {/* Left column */}
        <div className="w-1/4 pr-4 flex flex-col">
          <p className="mb-3">Stars: {analysis.stars}</p>
          <p className="mb-3">Forks: {analysis.forks}</p>
          <p className="mb-3">Open Issues: {analysis.open_issues}</p>
          <p className="mb-3">Watchers: {analysis.watchers}</p>
        </div>
        {/* Right column */}
        <div className="w-3/4 pl-4 flex flex-col">
          {narrativeParagraphs.map((paragraph, index) => (
            <p key={index} className="mb-3">{paragraph}</p>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RepoAnalysis;
