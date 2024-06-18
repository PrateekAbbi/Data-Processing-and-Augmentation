## Data Processing and Augmentation

### Introduction

This application is engineered to enhance data extracted from public police department PDF files, offering additional context and insights for comprehensive analysis. It supplements each incident record with several attributes, including temporal and weather data, location and nature rankings, and EMS status. Currently, users can visualize the various types of incidents and their locations, specifically identifying the frequency of incidents in different areas of the town.

### Installation

#### Backend

```bash
cd Backend
```

Ensure you have Python installed on your machine. To download the dependencies you can use the following command:

```bash
pip install -r requirements.txt
```

For Mac Users, you can replace pip with pip3.

#### Frontend

- Check your working directory using the following command:

```bash
pwd
```

If you are in the Backend directory, run the following set of commands:

```bash
cd ../Frontend/frontend
npm install
```

If you are in the root directory, run the following set of commands:

```bash
cd Frontend/frontend
npm install
```

### How to Run

#### Backend

- Before executing the backend, ensure that your Google Maps API key is correctly inserted at lines 276 and 362 of the `main.py` file located in the `playground` directory. Should you not possess a Google Maps API key, it is imperative to comment out the function calls on lines 505, 508, and 511 within the same file.

To run the backend, go to the backend directory and run the following command

```bash
pyton manage.py runserver
```

For Mac Users, you can replace pyton with pyton3.

#### Frontend

To run the Frontend, go to the frontend directory and run the following command

```bash
npm start
```

- Please note that, if you have commented out the lines 505, 508 and 511 of the main.py file within the playground directory of backend, you won't be able to visualize the location of incidents.

### Assumptions and Bugs

- It is assumed that the URLs and are in a consistent format for data extraction.
- The program uses hardcoded paths for saving temporary files and databases, which may need to be adjusted based on the operating system and user permissions.
- The weather data relies on external API services; thus, an active internet connection and a valid API key are required.
- Known bugs: Sometimes Google maps API is not able to detect the coordinates of the location and we need to handle those cases specially.

### External Resources

- Python documentation: https://docs.python.org/3/
- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- Google Maps API: https://developers.google.com/maps/documentation
- OpenMeteo API: https://open-meteo.com/
- React-chartJS2 documentation: https://react-chartjs-2.js.org
- MUI Documentation: https://mui.com

### Acknowledgments

This application was developed as part of the coursework for CIS 6930. I would like to thank the course instructors and teaching assistants for their guidance and support.
