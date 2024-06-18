import React from 'react';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import { Typography } from '@mui/material';

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar, Pie } from "react-chartjs-2";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
);

const Graphs = ({ nature, side, natureVis, sideVis }) => {

    const natureMap = {}
    const sideMap = {}

    var barChart = {}
    var barOptions = {}

    var pieChart = {}
    var pieOptions = {}

    if (nature.length) {
        nature.forEach((ele) => {
            if (ele in natureMap) {
                natureMap[ele] += 1;
            } else {
                natureMap[ele] = 1;
            }
        });

        barChart = {
            labels: Object.keys(natureMap),
            datasets: [
                {
                    label: "Nature",
                    data: Object.values(natureMap),
                    backgroundColor: "#9b59b6",
                    borderColor: '#9b59b6',
                    borderWidth: 1,
                }
            ]
        };

        barOptions = {
            plugins: {
                beforeDraw: (chart) => {
                    const ctx = chart.canvas.getContext('2d');
                    ctx.save();
                    ctx.globalCompositeOperation = 'destination-over';
                    ctx.fillStyle = 'black'; // Set your background color here
                    ctx.fillRect(0, 0, chart.width, chart.height);
                    // ctx.restore();
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        };
    }

    if (side.length) {
        side.forEach((ele) => {

            if (ele in sideMap) {
                sideMap[ele] += 1;
            } else {
                sideMap[ele] = 1;
            }
        });

        pieChart = {
            labels: Object.keys(sideMap),
            datasets: [
                {
                    label: "Incidents",
                    data: Object.values(sideMap),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)',
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                    ],
                    borderWidth: 1,
                }
            ],

        };

        pieOptions = {
            plugins: {
                beforeDraw: (chart) => {
                    const ctx = chart.canvas.getContext('2d');
                    ctx.save();
                    ctx.globalCompositeOperation = 'destination-over';
                    ctx.fillStyle = 'black'; // Set your background color here
                    ctx.fillRect(0, 0, chart.width, chart.height);
                    // ctx.restore();
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        };


    }

    return (
        <Box sx={{ minWidth: 275, marginTop: 5 }}>
            {
                natureVis && nature.length > 0 ?
                    <Card style={{ padding: 5 }}>
                        <Bar data={barChart} options={barOptions} />
                    </Card> :
                    <Card style={{ padding: 5, height: 650, width: 650, margin: "auto" }}>
                        {sideVis && side.length > 0 && <Pie data={pieChart} options={pieOptions} />}
                    </Card>
            }
            {nature.length > 0 && <Typography sx={{ marginTop: 2, color: "#4E342E" }}>Please Note that, Bars without labels are unknown nature of incidents</Typography>}
        </Box>
    )
}

export default Graphs