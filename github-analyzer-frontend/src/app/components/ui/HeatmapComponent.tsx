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
        display: true,
        labels: {
          color: 'white',
        },
      },
      tooltip: {
        enabled: true,
      },
    },
  };

  return (
    <div className="heatmap-container p-4 rounded-lg" style={{ backgroundColor }}>
      <h2 className="text-2xl font-bold mb-4 text-white">Contribution Heatmap</h2>
      <div className="relative h-64">
        <ChartJS type="bar" data={data} options={options} />
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