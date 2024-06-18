import React, { useState } from 'react'
import Form from './Form'

import Box from '@mui/material/Box';
import Graphs from './Graphs';

const Body = () => {

    const [nature, setNature] = useState([]);
    const [side, setSide] = useState([]);

    const [natureVis, SetNatureVis] = useState(false);
    const [sideVis, SetSideVis] = useState(false);

    return (
        <Box sx={{ padding: 5 }}>
            <Form setNature={setNature} setSide={setSide} SetNatureVis={SetNatureVis} SetSideVis={SetSideVis} />
            {console.log(nature)}
            {(nature.length > 0 || side.length > 0) && <Graphs nature={nature} side={side} natureVis={natureVis} sideVis={sideVis} />}
        </Box>
    )
}

export default Body