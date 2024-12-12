# Personal Usage Data Analysis

This project is divided into two parts:

- **Part 1:** Data Processing using Python
- **Part 2:** Visualization using Processing

The intended workflow is:
1. **Part 1 (Python):** Process and prepare your raw personal usage data into clean CSV formats.
2. **Part 2 (Processing):** Visualize the processed CSV data to understand your patterns and usage over time.

---

## Part 1: Data Processing Pipeline for Personal Usage Analysis

In this part, you'll use Python scripts to convert your raw data (from Instagram, TikTok, YouTube, etc.) into manageable CSV files. These processed files serve as the input for the visualization step in Part 2.

### Features
- Combine and clean Instagram chat data
- Process chat interactions and call durations
- Export TikTok watch time
- Process YouTube watch history using the YouTube Data API
- Export Instagram Reels watch time from liked posts

### Prerequisites
- **Python 3.7+**
- Your exported personal data from various platforms (Instagram, TikTok, YouTube, etc.)
- A YouTube Data API key for processing watch history

#### Python Packages
- `google-api-python-client`
- `python-dotenv`
- `isodate`

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/silmoon04/SocialMediaDataProcessing.git
   cd your-repo-name
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   - Create a `.env` file in the root directory:
     ```bash
     touch .env
     ```
   - Add your YouTube API key to `.env`:
     ```env
     YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
     ```

### Configuration

1. **Download Your Personal Data:**
   - **Instagram:** [Request your data](https://help.instagram.com/181231772500920)
   - **TikTok:** [Request your data](https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/requesting-your-data)
   - **YouTube:** [Download your watch history](https://takeout.google.com/settings/takeout/custom/youtube)

   Extract the archives into accessible directories.

2. **Edit the `config.json`:**
   Set file paths, username, date ranges, playback speed, etc.

   Example:
   ```json
   {
       "global": {
           "output_folder": "output",
           "start_date": "2023-01-01",
           "end_date": "2023-12-31"
       },
       "clean_and_combine_json_files": {
           "input_folder": "path/to/your/instagram/messages/inbox",
           "output_file": "combined_messages.json"
       },
       "process_chat_data": {
           "chat_file": "output/combined_messages.json",
           "output_csv": "chat_data.csv",
           "calls_csv": "calls_data.csv",
           "your_name": "your_username",
           "reading_speed_cpm": 1200, //change according to your reading speed
           "typing_speed_cpm": 200 //change according to your typing speed
       },
       "export_tiktok_watch_time": {
           "input_file": "path/to/your/tiktok/data.json",
           "output_csv": "tiktok_watch_time.csv",
           "default_video_duration_seconds": 15 //you can change this to 30 if you think that it'd make a better estimate
       },
       "youtube_watch_time": {
           "input_file": "path/to/your/youtube/watch-history.json",
           "output_csv": "youtube_watch_time.csv",
           "playback_speed": 1.0, //you can change this based on your usual playback speed, i put 2.0 since that's the speed i watch videos in usually
           "api_key_env": "YOUTUBE_API_KEY"
       },
       "export_reels_watch_time": {
           "input_file": "path/to/your/instagram/liked_posts.json",
           "output_csv": "ig_reels_watch_time.csv",
           "default_video_duration_seconds": 30
       }
   }
   ```

### Usage (Part 1)
1. Run the Python scripts to process data:
   ```bash
   python process_chat_data.py
   python export_tiktok_watch_time.py
   python youtube_watch_time.py
   python export_reels_watch_time.py
   ```
   
   Each script outputs CSV files into the `output` folder.

2. Once processed, move these CSV files into the `Part2_Visualization/data` directory (or wherever your Part 2 expects them).

### Data Privacy
All processing occurs locally. No personal data is uploaded unless required by APIs (like the YouTube Data API). Review code to ensure comfort with data handling.

### Contributing
Contributions are welcome. Open an issue or submit a pull request.

### License
[MIT License](LICENSE)

---

## Part 2: Social Media Data Visualization

After preparing your data in Part 1, Part 2 allows you to visualize the cleaned CSV files using Processing. You'll see interactive charts, toggleable datasets, stacked views, and the option to export PDF reports.

### Features
- Interactive visualization of multiple datasets
- Toggle visibility of data categories
- Stacked view for combined data
- PDF export of the visualization
- Easy to add or remove datasets

### Getting Started

1. **Prerequisites:**
   - [Processing](https://processing.org/download/)
   - Processed CSV files from Part 1 placed in `Part2_Visualization/data/`
   - Fonts and other resources in their respective directories

2. **Installation:**
   - Ensure all CSV files from Part 1 are now in the `data/` directory.
   - Start Processing and open the `.pde` file.

3. **Running the Visualization:**
   - Click **Run** in Processing to start the sketch.

### Adding New Datasets (Part 2)

1. **Prepare the Dataset:**
   - Ensure your CSV has `DayOfYear`, `MinuteOfDay`, and `Duration` columns.

2. **Assign a Color and Update `DataSet`:**
   - Add a color in `colorsMap`.
   - Add a new `DataSet` entry to `dataSets` in the `.pde` file.

3. **Run and Verify:**
   - The new dataset should appear in the legend.
   - Toggle its visibility by clicking the legend box.

### Usage (Part 2)

- **Toggle Datasets:** Click on the legend’s colored boxes.
- **Toggle Stacked View:** Click on the "Toggle View" legend item.

### Project Structure

```
/PersonalUsageDataAnalysis
├── Part1_DataProcessing/
│   ├── scripts/*.py
│   ├── config.json
│   ├── requirements.txt
│   └── ...
└── Part2_Visualization/
    ├── data/
    ├── fonts/
    ├── output/
    ├── SocialMediaDataVisualization.pde
    └── README.md (this file)
```

---


## Adding New Datasets

Enhancing the visualization with new datasets is straightforward thanks to the modular `DataSet` class. Follow the steps below to integrate additional data sources seamlessly.

### Prerequisites

- **Dataset Format:** Ensure your dataset is in CSV format with the following headers:
  - `DayOfYear` (Integer): Represents the day of the year (1-365).
  - `MinuteOfDay` (Integer): Represents the minute of the day (0-1439).
  - `Duration` (Float): Duration in seconds.

- **Color Selection:** Choose a distinct color for your dataset to differentiate it from existing datasets.

### Step-by-Step Guide

1. **Define the Dataset:**
   - Open the main `.pde` file in Processing.
   - Locate the `setup()` function where datasets are initialized.

2. **Update the `colorsMap`:**
   - Assign a unique color to your new dataset.
   - Example:
     ```java
     colorsMap.put("New_DataKey", color(#AABBCC)); // Replace #AABBCC with your chosen color
     ```

3. **Create a New `DataSet` Instance:**
   - Add a new `DataSet` object to the `dataSets` array with appropriate parameters.
   - Parameters:
     - `key` (String): Unique identifier for the dataset.
     - `label` (String): Display name for the legend.
     - `filePath` (String): Path to the CSV file.
     - `show` (Boolean): Initial visibility state (`true` to display by default).
     - `colorValue` (Integer): Color assigned from `colorsMap`.
     - `daysInYear` (Integer): Typically `365`.

4. **Ensure Proper Ordering:**
   - Place the new `DataSet` within the `dataSets` array in the order you want it to appear in the legend.

5. **Save and Run:**
   - Save the changes and run the Processing sketch.
   - The new dataset should now appear in the visualization and legend.

### Example: Adding a New Dataset

Suppose you want to add a dataset for "Instagram Stories."

1. **Prepare the Dataset:**
   - Ensure your CSV file `instagram_stories.csv` is placed in the `data/` directory with the required headers.

2. **Choose a Color:**
   - Select a color, e.g., `#FF5722` (a shade of orange).

3. **Update the Code:**

   - **Add to `colorsMap`:**
     ```java
     colorsMap.put("Instagram_Stories", color(#FF5722));
     ```

   - **Add to `dataSets` Array:**
     ```java
     dataSets = new DataSet[] {
       new DataSet("Reels", "Reels", "data/reels_watch_time.csv", true, colorsMap.get("Reels"), DAYS_IN_YEAR),
       new DataSet("YouTube", "YouTube", "data/processed_watch_time.csv", true, colorsMap.get("YouTube"), DAYS_IN_YEAR),
       new DataSet("Chat_SO", "Chat SO", "data/chat_data.csv", true, colorsMap.get("Chat_SO"), DAYS_IN_YEAR),
       new DataSet("Other_Chats", "Other Chats", "data/chat_data_other.csv", true, colorsMap.get("Other_Chats"), DAYS_IN_YEAR),
       new DataSet("Regular_Calls", "Regular Calls", "data/call_durations.csv", true, colorsMap.get("Regular_Calls"), DAYS_IN_YEAR),
       new DataSet("Video_Calls", "Video Calls", "data/video_calls.csv", true, colorsMap.get("Video_Calls"), DAYS_IN_YEAR),
       new DataSet("Instagram_Stories", "Instagram Stories", "data/instagram_stories.csv", true, colorsMap.get("Instagram_Stories"), DAYS_IN_YEAR)
     };
     ```

4. **Run the Sketch:**
   - Launch the Processing sketch.
   - "Instagram Stories" should now appear as a new option in the legend and be visualized accordingly.

## Project Structure

```
/SocialMediaDataVisualization
│
├── data/
│   ├── reels_watch_time.csv
│   ├── processed_watch_time.csv
│   ├── chat_data.csv
│   ├── chat_data_other.csv
│   ├── call_durations.csv
│   ├── video_calls.csv
│   └── instagram_stories.csv
│
├── fonts/
│   ├── Poppins-Black.ttf
│   └── Poppins-Bold.ttf
 
│     
├── SocialMediaDataVisualization.pde
│
└── README.md
```

- **data/**: Contains all CSV datasets.
- **fonts/**: Custom fonts used for labels.
- **SocialMediaDataVisualization.pde**: Main Processing sketch.
- **README.md**: Project documentation (this file).

## Usage

- **Toggle Datasets:**
  - Click on the colored squares in the legend to show or hide respective datasets.
  
- **Toggle Stacked View:**
  - Click on the "Toggle View" legend item to switch between individual and stacked visualization modes.
  

---

## Additional Notes

- **Extensibility:** The modular design allows you to add as many datasets as needed without altering the core logic. Ensure each new dataset has a unique key and color.
  
- **Data Integrity:** Maintain consistency in your CSV files to prevent visualization errors. Each row should accurately represent `DayOfYear`, `MinuteOfDay`, and `Duration`.



If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

