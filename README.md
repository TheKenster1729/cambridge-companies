# Cambridge Life Sciences and Technology Companies Map

This is a Python Dash application that displays the locations of all Life Sciences and Information Technology companies in Cambridge, MA from the provided CSV dataset. I'm using it to scan for companies I might be interested in working in.

## Installation

1. Make sure you have Python 3.7+ installed on your system, I used 3.12.7

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure the CSV file `Life_Sciences_and_Information_Technology_Company_Listing__March_2024_20250628.csv` is in the same directory as the app

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your web browser and navigate to `http://127.0.0.1:8050`

## Data Source

The app uses the CSV file `Life_Sciences_and_Information_Technology_Company_Listing__March_2024_20250628.csv` which contains:
- Company names and addresses
- Business types and descriptions
- Geographic coordinates (latitude/longitude)
- Website URLs
- Year established

## Technical Details

- Built with Dash (Python web framework)
- Uses Plotly for interactive maps
- Pandas for data processing
- OpenStreetMap for map tiles
- Responsive design that works on desktop and mobile

## Watch out
- Some of the information is outdated, apparently one of the biotech companies' websites got acquired by someone else and it redirects to some kind of foreign gambling website