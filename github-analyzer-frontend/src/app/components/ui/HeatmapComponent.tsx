import React from 'react';

interface HeatmapData {
  [date: string]: {
    total_commits: number;
    languages: { [language: string]: number };
    contribution_types: { [type: string]: number };
    insights: {
      most_used_language: string;
      significant_prs: boolean;
    };
  };
}

interface HeatmapComponentProps {
  heatmapData: HeatmapData;
}

const HeatmapComponent: React.FC<HeatmapComponentProps> = ({ heatmapData }) => {
  const dates = Object.keys(heatmapData).sort();
  const timeFrames = 10;
  const framesPerSection = Math.ceil(dates.length / timeFrames);

  const getLanguageColor = (language: string) => {
    const colors: { [key: string]: string } = {
      Python: '#FF0000',
      JavaScript: '#0000FF',
      TypeScript: '#00FF00',
      Java: '#FFA500',
      'C++': '#800080',
      Other: '#808080'
    };
    return colors[language] || colors.Other;
  };

  const maxCommits = Math.max(...Object.values(heatmapData).map(data => data.total_commits));
  const maxPRs = Math.max(...Object.values(heatmapData).map(data => data.contribution_types['pull_request'] || 0));

  return (
    <div className="heatmap-container bg-black p-4 rounded-lg">
      <h2 className="text-2xl font-bold mb-4 text-white">Contribution Heatmap</h2>
      <div className="relative h-64">
        {Array.from({ length: timeFrames }).map((_, index) => {
          const startDate = dates[index * framesPerSection];
          const endDate = dates[Math.min((index + 1) * framesPerSection - 1, dates.length - 1)];
          const sectionData = heatmapData[startDate];

          if (!sectionData) {
            console.warn(`No data for startDate: ${startDate}`);
            return null; // Skip this section if no data is available
          }

          const leftPosition = `${(index / (timeFrames - 1)) * 100}%`;
          const commitHeight = `${(sectionData.total_commits / maxCommits) * 100}%`;
          const prHeight = `${((sectionData.contribution_types['pull_request'] || 0) / maxPRs) * 100}%`;

          return (
            <div key={index} className="absolute bottom-0" style={{ left: leftPosition, width: `${100 / timeFrames}%` }}>
              <div 
                className="absolute bottom-0 w-full"
                style={{ 
                  backgroundColor: getLanguageColor(sectionData.insights.most_used_language),
                  height: '100%',
                  opacity: 0.5
                }}
              />
              <div 
                className="absolute bottom-0 w-full bg-black opacity-70"
                style={{ height: prHeight }}
              />
              <div 
                className="absolute bottom-0 w-1 bg-white left-1/2 transform -translate-x-1/2"
                style={{ height: commitHeight }}
              />
              <div className="absolute bottom-0 text-xs text-white transform -rotate-90 origin-bottom-left" style={{ left: '100%' }}>
                {startDate.split('-')[0]}
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 flex justify-between text-white">
        <span>Commits over time</span>
        <div>
          {['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Other'].map(lang => (
            <span key={lang} className="ml-2">
              <span 
                className="inline-block w-3 h-3 mr-1"
                style={{ backgroundColor: getLanguageColor(lang) }}
              />
              {lang}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HeatmapComponent;
