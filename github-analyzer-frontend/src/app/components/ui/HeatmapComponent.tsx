import React from 'react';
import { HeatmapData } from '../../types';

interface HeatmapComponentProps {
  heatmapData: HeatmapData;
}

const HeatmapComponent: React.FC<HeatmapComponentProps> = ({ heatmapData }) => {
  const maxCommits = Math.max(...Object.values(heatmapData).map(data => data.totalCommits));
  const maxPRs = Math.max(...Object.values(heatmapData).map(data => data.pullRequests));

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

  return (
    <div className="heatmap-container bg-black p-4 rounded-lg">
      <h2 className="text-2xl font-bold mb-4 text-white">Contribution Heatmap</h2>
      <div className="relative h-64">
        {Object.entries(heatmapData).map(([timeIndex, data], index) => {
          const leftPosition = `${(index / 9) * 100}%`;
          const commitHeight = `${(data.totalCommits / maxCommits) * 100}%`;
          const prHeight = `${(data.pullRequests / maxPRs) * 100}%`;

          return (
            <div key={timeIndex} className="absolute bottom-0" style={{ left: leftPosition, width: '10%' }}>
              <div 
                className="absolute bottom-0 w-full"
                style={{ 
                  backgroundColor: getLanguageColor(data.dominantLanguage),
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
