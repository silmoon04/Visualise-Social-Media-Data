import java.util.HashMap;

class DataSet {
  String key;
  String label;
  String filePath;
  boolean show;
  int colorValue;
  Table table;
  float[] dailyData;

  DataSet(String key, String label, String filePath, boolean show, int colorValue, int daysInYear) {
    this.key = key;
    this.label = label;
    this.filePath = filePath;
    this.show = show;
    this.colorValue = colorValue;
    this.dailyData = new float[daysInYear];
  }

  void loadData() {
    table = loadTable(filePath, "header");
  }

  void resetDailyData() {
    for (int i = 0; i < dailyData.length; i++) {
      dailyData[i] = 0;
    }
  }

  void accumulateData(int day, float durationMinutes) {
    dailyData[day] += durationMinutes;
  }

  float getDailyData(int day) {
    return dailyData[day];
  }
}

// Constants
final int DAYS_IN_YEAR = 365;
final int MINUTES_IN_DAY = 288; // 5-minute intervals
final float TOP_MARGIN = 70;
final float BOTTOM_MARGIN = 70;
final float SIDE_MARGIN = 50;
final float SPACING = 20; // Minimum spacing between items
final float X_LABEL_FONT_SIZE = 12;
final float Y_LABEL_FONT_SIZE = 12;

// Month information
String[] months = { "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov"};
int[] monthDays = {0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365};

// Colors map for grid and function
HashMap<String, Integer> colorsMap;

// Font variables
PFont font;
PFont xLabelFont;
PFont yLabelFont;

float colWidth;
float minuteHeight;

// The stack view toggle
boolean showStackView = false;

// DataSets array to hold all data sources
DataSet[] dataSets;

// Accumulated times for stacked view output
float timeChat = 0;
float timeRegular_Calls = 0;
float timeVideoCalls = 0;
float youtubeTime = 0;

void setup() {
  size(1400, 900);
  font = createFont("Arial", 12);
  textFont(font);

  // Initialize color map
  colorsMap = new HashMap<String, Integer>();
  colorsMap.put("Reels", color(#81C784));
  colorsMap.put("YouTube", color(#64B5F6));
  colorsMap.put("Chat_SO", color(#FF8A80));
  colorsMap.put("Other_Chats", color(#FFD54F));
  colorsMap.put("Regular_Calls", color(#FFB74D));
  colorsMap.put("Video_Calls", color(#CE93D8));
  colorsMap.put("Grid", color(#DEDEDE));
  colorsMap.put("Function", color(#6F6F6F));

  // Calculate dimensions
  float usableWidth = width - 2 * SIDE_MARGIN;
  float usableHeight = height - (TOP_MARGIN + BOTTOM_MARGIN);
  colWidth = usableWidth / DAYS_IN_YEAR;
  minuteHeight = usableHeight / MINUTES_IN_DAY;
  noStroke();

  // Define datasets here; easily extended by adding more entries:
  dataSets = new DataSet[] {
    new DataSet("Reels", "Reels", "data/reels_watch_time.csv", true, colorsMap.get("Reels"), DAYS_IN_YEAR),
    new DataSet("YouTube", "YouTube", "data/processed_watch_time.csv", true, colorsMap.get("YouTube"), DAYS_IN_YEAR),
    new DataSet("Chat_SO", "Chat SO", "data/chat_data.csv", true, colorsMap.get("Chat_SO"), DAYS_IN_YEAR),
    new DataSet("Other_Chats", "Other Chats", "data/chat_data_other.csv", true, colorsMap.get("Other_Chats"), DAYS_IN_YEAR),
    new DataSet("Regular_Calls", "Regular Calls", "data/call_durations.csv", true, colorsMap.get("Regular_Calls"), DAYS_IN_YEAR),
    new DataSet("Video_Calls", "Video Calls", "data/video_calls.csv", true, colorsMap.get("Video_Calls"), DAYS_IN_YEAR),
  };

  // Load all data tables
  for (DataSet ds : dataSets) {
    ds.loadData();
  }

  xLabelFont = createFont("fonts/Poppins-Black.ttf", X_LABEL_FONT_SIZE);
  yLabelFont = createFont("fonts/Poppins-Bold.ttf", Y_LABEL_FONT_SIZE);
  textFont(xLabelFont);
}

void draw() {
  resetAllData();
  background(255);
  drawGrid();

  drawAllData();

  if (showStackView) {
    background(255);
    drawGrid();
    drawDataTogether();
  }

  drawAxes();
  drawLegend();

  noLoop();
}

void resetAllData() {
  for (DataSet ds : dataSets) {
    ds.resetDailyData();
  }
}

void drawAllData() {
  // Draw each dataset's data if visible
  for (int i = 0; i < dataSets.length; i++) {
    DataSet ds = dataSets[i];
    if (ds.show) {
      fill(ds.colorValue);
      for (TableRow row : ds.table.rows()) {
        drawData(row, ds);
      }
    }
  }
}

void drawData(TableRow row, DataSet ds) {
  int day = constrain(row.getInt("DayOfYear") - 1, 0, DAYS_IN_YEAR - 1);
  int minute = constrain(row.getInt("MinuteOfDay") / 5, 0, MINUTES_IN_DAY - 1);
  float durationSeconds = row.getFloat("Duration");

  float durationMinutes = durationSeconds / 60.0;
  float durationPixels = durationMinutes * (minuteHeight / 5.0);
  durationPixels = max(durationPixels, minuteHeight * 0.1);

  float x = SIDE_MARGIN + day * colWidth + colWidth;
  float y = TOP_MARGIN + minute * minuteHeight;

  float maxHeight = height - BOTTOM_MARGIN - y;
  durationPixels = min(durationPixels, maxHeight);
  if (durationPixels > 1) {
    rect(x, y, colWidth, durationPixels);
  } else {
    rect(x, y, colWidth, minuteHeight);
    durationMinutes = 1;
  }

  ds.accumulateData(day, durationMinutes);
}

void drawDataTogether() {
  timeChat = 0;
  timeRegular_Calls = 0;
  timeVideoCalls = 0;
  youtubeTime = 0;

  for (int day = 0; day < DAYS_IN_YEAR; day++) {
    float cumulativeY = height - BOTTOM_MARGIN; 
    for (DataSet ds : dataSets) {
      fill(ds.colorValue);
      float durationMinutes = ds.getDailyData(day);

      // Accumulate times for debugging output
      if (ds.key.equals("Chat_SO")) timeChat += durationMinutes;
      else if (ds.key.equals("Regular_Calls")) timeRegular_Calls += durationMinutes;
      else if (ds.key.equals("Video_Calls")) timeVideoCalls += durationMinutes;
      else if (ds.key.equals("YouTube")) youtubeTime += durationMinutes;

      float durationPixels = max(durationMinutes * (minuteHeight / 5.0), minuteHeight * 0.1);
      float x = SIDE_MARGIN + day * colWidth;
      float y = cumulativeY - durationPixels;

      if (durationPixels > 0) {
        rect(x, y, colWidth, durationPixels);
      }

      cumulativeY -= durationPixels;
    }
  }

  println("chat time: " + (int)(timeChat/60) + " hours, Regular_Calls time: " + (int)(timeRegular_Calls/60) 
    + " hours, video Calls time: " + (int)(timeVideoCalls/60) + " hours, youtube hours: " 
    + (int)(youtubeTime/60));
}

void drawLegend() {
  pushStyle();
  textAlign(LEFT, CENTER);
  textSize(12);

  float baseX = 50; 
  float baseY = 50; 
  float x = baseX;

  // Build legend array: each DataSet + "Toggle View"
  int totalItems = dataSets.length + 1;
  for (int i = 0; i < totalItems; i++) {
    String legendLabel;
    int colorToUse;
    boolean toggled;

    if (i < dataSets.length) {
      DataSet ds = dataSets[i];
      legendLabel = ds.label;
      toggled = ds.show;
      colorToUse = toggled ? ds.colorValue : colorsMap.get("Grid");
    } else {
      // Last is Toggle View
      legendLabel = "Toggle View";
      toggled = showStackView;
      colorToUse = toggled ? colorsMap.get("Function") : colorsMap.get("Grid");
    }

    float labelWidth = textWidth(legendLabel);
    float totalSpacing = SPACING + labelWidth + 10;
    float y = baseY;

    fill(colorToUse);
    rect(x, y, 15, 15);

    fill(0);
    text(legendLabel, x + 20, y + 7.5);

    x += totalSpacing;
  }

  popStyle();
}

void mousePressed() {
  float startX = 50; 
  int totalItems = dataSets.length + 1;

  for (int i = 0; i < totalItems; i++) {
    String legendLabel = (i < dataSets.length) ? dataSets[i].label : "Toggle View";
    float labelWidth = textWidth(legendLabel);
    float totalSpacing = SPACING + labelWidth + 10; 
    float boxX = startX;
    float boxY = 50;

    if (mouseX > boxX && mouseX < boxX + 15 && mouseY > boxY && mouseY < boxY + 15) {
      if (i < dataSets.length) {
        dataSets[i].show = !dataSets[i].show;
      } else {
        showStackView = !showStackView;
      }
      redraw();
      break;
    }

    startX += totalSpacing;
  }
}

void drawGrid() {
  stroke(colorsMap.get("Grid"));
  strokeWeight(2);

  for (int d = 0; d <= DAYS_IN_YEAR+1; d++) {
    float x = SIDE_MARGIN + d * colWidth;
    line(x, TOP_MARGIN, x, height - BOTTOM_MARGIN);
  }

  strokeWeight(1);
  int linesPerHour = 12; // 12 intervals = 60 minutes
  for (int m = 0; m <= MINUTES_IN_DAY / linesPerHour; m++) {
    float y = TOP_MARGIN + m * minuteHeight * linesPerHour;
    line(SIDE_MARGIN, y, width - SIDE_MARGIN, y);
  }
  noStroke();
}

void drawAxes() {
  pushStyle();
  stroke(0);

  // X-axis
  line(SIDE_MARGIN, height - BOTTOM_MARGIN, width - SIDE_MARGIN, height - BOTTOM_MARGIN);

  // Y-axis
  line(SIDE_MARGIN, TOP_MARGIN, SIDE_MARGIN, height - BOTTOM_MARGIN);

  textFont(xLabelFont);
  textSize(X_LABEL_FONT_SIZE);
  fill(0);
  textAlign(CENTER, TOP);

  for (int m = 0; m < 12; m++) {
    int day = monthDays[m];
    float x = SIDE_MARGIN + day * colWidth;
    line(x, height - BOTTOM_MARGIN, x, height - BOTTOM_MARGIN + 5);

    float totalDaysInMonth = (m < 11) ? monthDays[m + 1] - monthDays[m] : DAYS_IN_YEAR - monthDays[11];
    float centerDay = day + totalDaysInMonth / 2.0;
    float labelX = SIDE_MARGIN + centerDay * colWidth;
    text(months[m], labelX, height - BOTTOM_MARGIN + 10);
  }

  int intervalsPerHour = 60 / 5; // 12 intervals per hour
  int hoursInDay = 24;

  textFont(yLabelFont);
  textSize(Y_LABEL_FONT_SIZE);
  textAlign(RIGHT, CENTER);
  fill(0);

  for (int h = 0; h <= hoursInDay; h++) {
    float y = TOP_MARGIN + h * intervalsPerHour * minuteHeight;
    line(SIDE_MARGIN - 5, y, SIDE_MARGIN, y);

    String timeLabel = String.format("%02d:00", h % 24);
    text(timeLabel, SIDE_MARGIN - 10, y);
  }

  popStyle();
}
