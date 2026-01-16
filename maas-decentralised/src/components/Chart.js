import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Chart = ({ type, data, title, options = {} }) => {
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: !!title,
        text: title,
      },
    },
    ...options
  };

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <Bar data={data} options={defaultOptions} />;
      case 'line':
        return <Line data={data} options={defaultOptions} />;
      case 'doughnut':
        return <Doughnut data={data} options={defaultOptions} />;
      default:
        return <div>Unsupported chart type: {type}</div>;
    }
  };

  return (
    <div className="chart-container">
      <div style={{ height: '300px' }}>
        {renderChart()}
      </div>
    </div>
  );
};

export default Chart;
