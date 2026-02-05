import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import type { MarketsServed } from '@/types/kompass';

interface MarketsServedChartProps {
  markets: MarketsServed | null;
  height?: number;
}

const MARKET_COLORS: Record<string, string> = {
  south_america: '#4caf50',
  north_america: '#2196f3',
  europe: '#9c27b0',
  asia: '#ff9800',
  other: '#607d8b',
};

const MARKET_LABELS: Record<string, string> = {
  south_america: 'South America',
  north_america: 'North America',
  europe: 'Europe',
  asia: 'Asia',
  other: 'Other',
};

const MarketsServedChart: React.FC<MarketsServedChartProps> = ({ markets, height = 200 }) => {
  if (!markets) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height,
          color: 'text.secondary',
        }}
      >
        <Typography variant="body2">No market data available</Typography>
      </Box>
    );
  }

  const chartData = Object.entries(markets)
    .filter(([, value]) => value !== undefined && value !== null && value > 0)
    .map(([key, value]) => ({
      market: MARKET_LABELS[key] || key,
      percentage: value as number,
      color: MARKET_COLORS[key] || '#888',
    }))
    .sort((a, b) => b.percentage - a.percentage);

  if (chartData.length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height,
          color: 'text.secondary',
        }}
      >
        <Typography variant="body2">No market data available</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 40, left: 5, bottom: 5 }}>
          <XAxis type="number" domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
          <YAxis
            dataKey="market"
            type="category"
            width={100}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value) => [`${value}%`, 'Market Share']}
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
          />
          <Bar dataKey="percentage" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
            <LabelList
              dataKey="percentage"
              position="right"
              formatter={(value) => `${value}%`}
              style={{ fontSize: 11, fill: '#666' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default MarketsServedChart;
