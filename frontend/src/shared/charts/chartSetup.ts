import {
  BarElement,
  CategoryScale,
  Chart,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'

// main code
// only what the analytics page draws, so the bundle does not carry every chart type
Chart.register(BarElement, CategoryScale, Legend, LinearScale, LineElement, PointElement, Tooltip)

Chart.defaults.font.family = getComputedStyle(document.body).fontFamily
Chart.defaults.color = '#52514e'

// validated as an adjacent pair for color-vision deficiencies; text never wears these colors
export const SERIES_COLORS = ['#2a78d6', '#eb6834']

export const GRID_COLOR = 'rgba(0, 0, 0, 0.06)'
