import React, { useState, useRef, useEffect } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

import Axios from './Axios';
Axios.defaults.timeout = 17000;

const Form = ({ setNature, setSide, SetNatureVis, SetSideVis }) => {
    useEffect(() => {
        const clearLocalStorage = () => {
            localStorage.clear();
        };

        window.addEventListener('beforeunload', clearLocalStorage);

        return () => {
            window.removeEventListener('beforeunload', clearLocalStorage);
        };
    }, []);

    const [anchorEl, setAnchorEl] = useState(null);

    const [url, setUrl] = useState("");

    const open = Boolean(anchorEl);
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const buttonRef = useRef(null);

    const handleClose = (item) => {

        const extractedDate = url.slice(63, 73);

        if (typeof item === 'string') {
            if (localStorage.getItem(extractedDate)) {
                const data = JSON.parse(localStorage.getItem(extractedDate))
                const safeData = Object.values(data)
                if (item === "nature") {
                    setNature(safeData[0])
                    SetNatureVis(true);
                    SetSideVis(false);
                }
                if (item === "Side of Town") {
                    setSide(safeData[1]);
                    SetNatureVis(false);
                    SetSideVis(true);
                }

            } else {
                Axios.post('http://127.0.0.1:8000/playground/fetchIncidents/', {
                    // Axios.post('https://prateekabbi.pythonanywhere.com/playground/fetchIncidents/', {
                    url: url,
                    type: item
                }).then(function (response) {
                    const data = response.data

                    localStorage.setItem(extractedDate, JSON.stringify(data))

                    if (item === "nature") {
                        setNature(localStorage.getItem(Object.keys(extractedDate)[0]))
                        SetNatureVis(true);
                        SetSideVis(false);
                    }
                    if (item === "Side of Town") {
                        setSide(localStorage.getItem(extractedDate)['side']);
                        SetNatureVis(false);
                        SetSideVis(true);
                    }
                })
            }

        }

        setAnchorEl(null);
    };

    const setURLFunc = (event) => {
        setUrl(event.target.value);
    }


    return (
        <Box sx={{ flexGrow: 1 }}>
            <Grid container spacing={2}>
                <Grid item xs={8}>
                    <TextField id="standard" label="ENTER URL" variant="standard" sx={{
                        width: "100%", '& .MuiOutlinedInput-root': {
                            '& fieldset': {
                                borderColor: '#2c3e50', // Default border color
                            },
                            '&:hover fieldset': {
                                borderColor: '#2c3e50', // Hover border color
                            },
                            '&.Mui-focused fieldset': {
                                borderColor: '#2c3e50', // Focused border color
                            },
                            '&.Mui-focused .MuiInputBase-input': {
                                color: '#2c3e50', // Focused input text color
                            },
                        },
                        '& .MuiInputLabel-root': {
                            color: '#2c3e50', // Default label color
                        },
                        '& .MuiInputLabel-root.Mui-focused': {
                            color: '#2c3e50', // Focused label color
                        },
                        '& .MuiInputBase-input': {
                            color: '#2c3e50', // Default input text color
                        },
                    }} onChange={setURLFunc} value={url} />
                </Grid>
                <Grid item xs={4}>
                    <Button
                        ref={buttonRef}
                        id="basic-button"
                        variant='contained'
                        aria-controls={open ? 'basic-menu' : undefined}
                        aria-haspopup="true"
                        aria-expanded={open ? 'true' : undefined}
                        onClick={handleClick}
                        style={{
                            height: "100%",
                            backgroundColor: "#1abc9c",
                            color: "#2c3e50",
                            boxShadow: 'none'
                        }}
                    >
                        Choose to VISUALIZE
                    </Button>
                    <Menu
                        id="basic-menu"
                        anchorEl={anchorEl}
                        open={open}
                        style={{ width: "50%" }}
                        onClose={handleClose}
                        MenuListProps={{
                            'aria-labelledby': 'basic-button',
                        }}
                        PaperProps={{
                            style: {
                                minWidth: buttonRef.current ? buttonRef.current.offsetWidth : null,
                            },
                        }}
                    >
                        <MenuItem onClick={() => handleClose("nature")}>Nature of Incidents</MenuItem>
                        <MenuItem onClick={() => handleClose("Side of Town")}>Side of Town</MenuItem>
                    </Menu>
                </Grid>
            </Grid>

        </Box>
    )
}

export default Form