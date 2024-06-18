import React from 'react'

import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

const Header = () => {
    return (
        <Box sx={{ flexGrow: 1, textAlign: "center" }}>
            <AppBar position="static" sx={{ backgroundColor: "#34495e" }}>
                <Toolbar>
                    <Typography variant="h4" component="div" sx={{ flexGrow: 1, color: "#eef2f3" }}>
                        NORMAND PD DATABSE VISUALIZATION
                    </Typography>
                </Toolbar>
            </AppBar>
        </Box>
    )
}

export default Header