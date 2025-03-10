# Recovering Data from Google Timeline

Suddenly, I lost all the data from my **Google Timeline**, which I had been keeping for over 10 years. After reaching out to Google Support, I was informed that even though I had exported my entire **Location History (Timeline)** using **Google Takeout**, there was no way to reload that data back into Google’s system.

This was extremely frustrating since I had carefully preserved this data for years. To avoid losing it completely, I looked for a DIY solution that would allow me to at least read and consult the data whenever needed.

## 📂 Analyzing the Exported Data

Inside the **Location History (Timeline)** folder, I found:

- The **Records.json** file (in my case, over 1GB in size).
- A subfolder called **Semantic Location History**, which contains year-based directories, each holding monthly JSON files (e.g., `2024_OCTOBER.json`).

## 🛠️ The Conversion Script

To make this data more accessible, I wrote a script that takes the path of a directory corresponding to a specific year (e.g., 2024) and performs the following tasks:

1. Reads and merges the contents of all JSON files for that year.
2. Generates a **readable CSV file**, sorted by date, with all movement details.
3. Creates a **KML file** (usable with tools like Google Earth).  
   - ⚠️ The KML file is not very practical since it displays all locations in a cluttered and unreadable manner.

## 🚀 How to Run the Script

The script can be executed using the following command:

```bash
python3 googletimeline_converter_cet_cest.py 2024
```

## 🔑 Key Features

### 🕒 Time Conversion
- The timestamps in the JSON files are stored in **UTC**.
- The script automatically converts them to **Italian time (CET/CEST)** for better readability.

### 📍 Nearby Locations
- You can define a list of locations with their **GPS coordinates** and a **proximity threshold**.
- If a location lacks a **Place Name** but falls within the specified range, the script will automatically assign the predefined **Place Name**.

### 📊 CSV Output
- The script generates a **CSV file** containing all your movement data, organized by date.
- The CSV format makes it easy to analyze your past locations using spreadsheet software.

### 🌍 KML Output (Google Earth)
- The script also creates a **KML file** for visualization in Google Earth.
- However, since it places all locations at once, the result may not be very readable.

---

📜 **License:** This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

💡 **Contributions:** If you find this useful or have ideas for improvements, feel free to **open an issue** or submit a **pull request**!

🚀 **Enjoy your recovered timeline data!**
