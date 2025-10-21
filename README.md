# Personal Usage Data Analysis

Welcome to the **Personal Usage Data Analysis** project! This project helps you process and visualize your personal usage data from various social media platforms to uncover patterns and insights.

## Table of Contents

- [Overview](#overview)
- [Example Visualizations](#example-visualizations)
- [Part 1: Data Processing Pipeline](#part-1-data-processing-pipeline)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage-part-1)
  - [Data Privacy](#data-privacy)
  - [Contributing](#contributing)
- [Part 2: Social Media Data Visualization](#part-2-social-media-data-visualization)
  - [Features](#features-1)
  - [Getting Started](#getting-started)
  - [Adding New Datasets](#adding-new-datasets)
  - [Usage](#usage-part-2)
- [Project Structure](#project-structure)
- [Additional Notes](#additional-notes)
- [License](#license)

---

## Overview

This project is split into two main parts:

1. **Data Processing (Python):** Clean and prepare your raw usage data into CSV formats.
2. **Data Visualization (Processing):** Visualize the processed data to understand your usage patterns over time.

### Workflow

1. **Part 1 (Python):** Process your raw data into clean CSV files.
2. **Part 2 (Processing):** Visualize the CSV data to gain insights into your usage patterns.

---

## Example Visualizations

Check out some of the cool visualizations created with this project:

### Example 1: Total Time Spent

![Visualization Example 5](https://github.com/silmoon04/Visualise-Social-Media-Data/blob/main/Part2_Visualization/examples/java_zeRgmtTcRT.png?raw=true)

*This graph shows my total time spent throughout the year in different colors. I separated the time spent texting my girlfriend from texting others. It’s really interesting to see how I allocated my time over the year. I wanted to include TikTok usage but the data wasn’t available yet.*

### Example 2: Daily Social Media Usage

![Visualization Example 3](https://github.com/silmoon04/Visualise-Social-Media-Data/blob/main/Part2_Visualization/examples/java_A1DiLsyJsR.png?raw=true)

*This stacked view shows how much time I spent each day on social media, it gives me interesting insights into my daily habits.*

### Example 3: Communication Breakdown

![Visualization Example 2](https://github.com/silmoon04/Visualise-Social-Media-Data/blob/main/Part2_Visualization/examples/java_1uoMpAFlI6.png)

*This represents the time I spent texting, calling, or video calling my girlfriend throughout the year.*

### Example 4: Media Consumption

![Visualization Example 4](https://github.com/silmoon04/Visualise-Social-Media-Data/blob/main/Part2_Visualization/examples/java_K9axpIlgSc.png)

*This visualization shows the time I spent watching YouTube and reels/posts. It clearly shows that I need to reduce my time spent on reels.*

### Example 5: Scatter Plot of Usage Data

![Visualization Example 1](https://github.com/silmoon04/Visualise-Social-Media-Data/blob/main/Part2_Visualization/examples/java_0Wrjlg8KEA.png)

*This is a scatter plot of the same data, giving me a different perspective on my usage patterns.*

---

## Part 1: Data Processing Pipeline

In Part 1, you'll use Python scripts to convert your raw data (from Instagram, TikTok, YouTube, etc.) into manageable CSV files. These processed files will be used in Part 2 for visualization.

### Features

- **Combine and Clean Instagram Chat Data:** Merge and sanitize your Instagram messages.
- **Process Chat Interactions and Call Durations:** Analyze your communication patterns.
- **Export TikTok Watch Time:** Calculate the time spent on TikTok.
- **Process YouTube Watch History:** Use the YouTube Data API to analyze your watch history.
- **Export Instagram Reels Watch Time:** Track time spent on Instagram Reels from liked posts.

*Note: The algorithms were initially tailored for my use case, so some tweaking might be needed for others.*

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
   cd SocialMediaDataProcessing
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

   *Extract the archives into accessible directories and ensure they are in `.json` format.*

2. **Edit the `config.json`:**
   Set file paths, username, date ranges, playback speed, etc.

   **Example:**
   ```javascript
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
           "reading_speed_cpm": 1200, // Change according to your reading speed
           "typing_speed_cpm": 200 // Change according to your typing speed
       },
       "export_tiktok_watch_time": {
           "input_file": "path/to/your/tiktok/data.json",
           "output_csv": "tiktok_watch_time.csv",
           "default_video_duration_seconds": 15 // Change to 30 if needed
       },
       "youtube_watch_time": {
           "input_file": "path/to/your/youtube/watch-history.json",
           "output_csv": "youtube_watch_time.csv",
           "playback_speed": 1.0, // Adjust based on your usual playback speed
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

1. **Run the full processing pipeline**
   ```bash
   cd Part1_DataProcessing/scripts
   python pipeline.py
   ```

   The orchestrator reads the paths defined in `config.json`, writes results into the configured `output_folder`, and logs a
   concise summary for each task.

2. **Run individual scripts if needed**
   ```bash
   cd Part1_DataProcessing/scripts
   python parse_chats.py        # Chat effort analytics
   python parse_data_tiktok.py  # TikTok watch sessions
   python process_yt_watchtime.py  # YouTube watch history
   python parse_ig_likes.py     # Instagram reels usage
   ```

   *Each script writes CSV files into the `output` folder. Date ranges are inclusive of the `start_date` and exclusive of the
   `end_date`, so use the following day when you want a closed interval.*

3. **Move CSV Files to Part 2:**
   - Move the processed CSV files into the `Part2_Visualization/data` directory (or the directory expected by Part 2).

### Development

- **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- **Run the automated test suite**
  ```bash
  pytest
  ```

  The tests cover the most intricate data conversions, making it easier to evolve the pipeline with confidence.

### Data Privacy

- **Local Processing:** All data processing happens locally on your machine.
- **API Usage:** Only necessary data is uploaded to APIs (e.g., YouTube Data API).
- **Review Code:** Always review the code to ensure it aligns with your data privacy preferences.

---

## Part 2: Social Media Data Visualization

After preparing your data in Part 1, use Part 2 to visualize the cleaned CSV files with Processing. Explore interactive charts, toggleable datasets, stacked views, and export PDF reports.

### Features

- Interactive visualization of multiple datasets
- Toggle visibility of data categories
- Stacked view for combined data
- Easy addition or removal of datasets

### Getting Started

1. **Prerequisites:**
   - [Processing](https://processing.org/download/)
   - Processed CSV files from Part 1 placed in `Part2_Visualization/data/`
   - Fonts and other resources in their respective directories

2. **Installation:**
   - Ensure all CSV files from Part 1 are in the `data/` directory.
   - Open the `.pde` file in Processing.

3. **Running the Visualization:**
   - Click **Run** in Processing to start the sketch.

### Adding New Datasets

Enhance the visualization by adding new datasets using the modular `DataSet` class.

#### Prerequisites

- **Dataset Format:** CSV with the following headers:
  - `DayOfYear` (Integer): Day of the year (1-365)
  - `MinuteOfDay` (Integer): Minute of the day (0-1439)
  - `Duration` (Float): Duration in seconds

- **Color Selection:** Choose a distinct color for your dataset.

#### Step-by-Step Guide

1. **Prepare the Dataset:**
   - Ensure your CSV file is in the `data/` directory with the required headers.

2. **Assign a Color and Update `colorsMap`:**
   - Open the main `.pde` file.
   - Add your color to `colorsMap`.
     ```java
     colorsMap.put("New_DataKey", color(#AABBCC)); // Replace #AABBCC with your chosen color
     ```

3. **Create a New `DataSet` Instance:**
   - Add a new `DataSet` to the `dataSets` array.
     ```java
     dataSets = new DataSet[] {
       // Existing datasets...
       new DataSet("New_DataKey", "New Data Label", "data/new_data.csv", true, colorsMap.get("New_DataKey"), DAYS_IN_YEAR)
     };
     ```

4. **Adjust Additional Variables (Optional):**
   - Modify variables like months, canvas size, or existing colors as needed.

5. **Run and Verify:**
   - Save the changes and run the Processing sketch.
   - Your new dataset should appear in the legend and visualization.

#### Example: Adding "Whatsapp Message Time"

1. **Prepare the Dataset:**
   - Place `whatsapp_chat_time.csv` in the `data/` directory with the required headers.

2. **Choose a Color:**
   - Example: `#FF5722` (a shade of orange).

3. **Update the Code:**
   - **Add to `colorsMap`:**
     ```java
     colorsMap.put("Whatsapp_Time", color(#FF5722));
     ```
   - **Add to `dataSets` Array:**
     ```java
     dataSets = new DataSet[] {
       // Existing datasets...
       new DataSet("Whatsapp_Time", "Whatsapp Time", "data/whatsapp_time.csv", true, colorsMap.get("Whatsapp_Time"), DAYS_IN_YEAR)
     };
     ```

4. **Run the Sketch:**
   - Launch the Processing sketch.
   - "Instagram Stories" should now appear in the legend and visualization.

### Usage (Part 2)

- **Toggle Datasets:** Click on the colored squares in the legend to show or hide datasets.
- **Toggle Stacked View:** Click on the "Toggle View" legend item to switch between individual and stacked visualization modes.

---

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
├── Part1_DataProcessing/
│   ├── process_chat_data.py
│   ├── export_tiktok_watch_time.py
│   ├── youtube_watch_time.py
│   ├── export_reels_watch_time.py
│   └── config.json
│
├── Part2_Visualization/
│   ├── data/
│   ├── fonts/
│   ├── SocialMediaDataVisualization.pde
│   └── examples/
│       ├── java_zeRgmtTcRT.png
│       ├── java_A1DiLsyJsR.png
│       ├── java_1uoMpAFlI6.png
│       ├── java_K9axpIlgSc.png
│       └── java_0Wrjlg8KEA.png
│
└── README.md
```

- **data/**: Contains all CSV datasets.
- **fonts/**: Custom fonts used for labels.
- **Part1_DataProcessing/**: Python scripts and configuration for data processing.
- **Part2_Visualization/**: Processing sketch, data for visualization, and example images.
- **README.md**: Project documentation (this file).

---

## Additional Notes

- **Extensibility:** The modular design allows you to add as many datasets as needed without altering the core logic. Ensure each new dataset has a unique key and color.
  
- **Data Integrity:** Maintain consistency in your CSV files to prevent visualization errors. Each row should accurately represent `DayOfYear`, `MinuteOfDay`, and `Duration`.

---

### Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

### License

This project is licensed under the [MIT License](LICENSE).

---
