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
    <div className="flex bg-black text-white p-8 border border-dashed border-[#80EE64] rounded-lg mx-16">
      {/* Left column (smaller) */}
      <div className="w-1/4 pr-4 flex flex-col">
        <h3 className="text-3xl font-bold mb-6">{analysis.repo_name}</h3>
        <p className="mb-2">Stars: {analysis.stars}</p>
        <p className="mb-2">Forks: {analysis.forks}</p>
        <p className="mb-2">Open Issues: {analysis.open_issues}</p>
        <p className="mb-2">Watchers: {analysis.watchers}</p>
        <p className="mb-2">Code Quality: {getCodeQuality(analysis.overall_score)}</p> 
      </div>

      {/* Divider */}
      <div className="w-px border-l border-dashed border-[#80EE64] mx-4 self-stretch"></div>

      {/* Right column (larger) */}
      <div className="w-3/4 pl-4 flex flex-col">
        <h3 className="text-3xl font-bold mb-6 invisible">{analysis.repo_name}</h3>
        {narrativeParagraphs.map((paragraph, index) => (
          <p key={index} className="mb-3">{paragraph}</p>
        ))}
      </div>
    </div>
  );
};

export default RepoAnalysis;
