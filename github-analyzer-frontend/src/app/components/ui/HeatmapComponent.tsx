import React from 'react';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Chart as ChartJS, Line, Bar } from 'react-chartjs-2';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

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
  const commitsData = dates.map(date => heatmapData[date].total_commits);
  const prData = dates.map(date => heatmapData[date].contribution_types['pull_request'] || 0);

  // Ensure insights exist before accessing them
  const firstDate = dates[0];
  const dominantLanguage = heatmapData[firstDate]?.insights?.most_used_language || 'Other';  // Default to 'Other' if insights are missing
  const backgroundColor = getLanguageColor(dominantLanguage);  // Get the color for the dominant language

  const data = {
    labels: dates,
    datasets: [
      {
        type: 'line' as const,
        label: 'Commits',
        data: commitsData,
        borderColor: 'white',
        backgroundColor: 'white',
        fill: false,
        tension: 0.1,
        yAxisID: 'y',
      },
      {
        type: 'bar' as const,
        label: 'Pull Requests',
        data: prData,
        backgroundColor: 'black',
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    scales: {
      x: {
        type: 'category',
        labels: dates,
      },
      y: {
        beginAtZero: true,
        position: 'left' as const,
      },
      y1: {
        beginAtZero: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
    plugins: {
      legend: {
        display: false, // Hide the legend
      },
      tooltip: {
        enabled: true,
      },
    },
  };

  return (
    <div className="heatmap-container p-4 bg-black">
      {/* Title row */}
      <div className="w-full mb-6">
        <h2 className="text-4xl font-bold text-white">Heatmap</h2>
      </div>
      <div className="flex justify-center">
        <ChartJS type="bar" data={data} options={options} style={{ backgroundColor, width: '30%', height: '20%' }} />
      </div>
      <div className="mt-2 grid grid-cols-4 text-white" style={{ paddingLeft: '25%', paddingRight: '15%' }}>
        <div className="flex flex-col items-start">
          <span className="mb-1">
            <span className="inline-block w-2 h-2 mr-1" style={{ backgroundColor: 'white' }} />
            Commits
          </span>
          <span className="mb-1">
            <span className="inline-block w-2 h-2 mr-1" style={{ backgroundColor: 'black' }} />
            Pull Requests
          </span>
        </div>
        <div className="flex flex-col items-start">
          {['Python', 'JavaScript'].map(lang => (
            <span key={lang} className="mb-1">
              <span 
                className="inline-block w-2 h-2 mr-1"
                style={{ backgroundColor: getLanguageColor(lang) }}
              />
              {lang}
            </span>
          ))}
        </div>
        <div className="flex flex-col items-start">
          {['TypeScript', 'Java'].map(lang => (
            <span key={lang} className="mb-1">
              <span 
                className="inline-block w-2 h-2 mr-1"
                style={{ backgroundColor: getLanguageColor(lang) }}
              />
              {lang}
            </span>
          ))}
        </div>
        <div className="flex flex-col items-start">
          {['C++', 'Other'].map(lang => (
            <span key={lang} className="mb-1">
              <span 
                className="inline-block w-2 h-2 mr-1"
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

const languageColors: { [key: string]: string } = {
  Python: '#3572A5',
  JavaScript: '#f1e05a',
  TypeScript: '#2b7489',
  Java: '#b07219',
  'C++': '#f34b7d',
  Other: '#cccccc',  // Default color for other languages
};

const getLanguageColor = (language: string): string => {
  return languageColors[language] || languageColors['Other'];
};

export default HeatmapComponent;