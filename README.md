# Image Metadata Comparator 🔍🖼️

A desktop GUI application developed in Python for digital forensics and file analysis. It allows investigators and analysts to inspect, extract, and comparatively evaluate EXIF and file metadata between two images, highlighting differences and discrepancies asynchronously.

---

## ✨ Features

- **Drag-and-Drop & File Picker**: Intuitive visual drop zones for loading images directly from the filesystem (`.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`).
- **Asynchronous Extraction**: Uses Qt multi-threading (`QThread`) to ensure the user interface remains responsive while extracting metadata.
- **Deep Metadata Parsing**: Powered by [PyExifTool](https://github.com/sarnold/pyexiftool) and Phil Harvey's [ExifTool](https://exiftool.org/) engine to read standard EXIF, IPTC, XMP, and vendor maker notes.
- **Side-by-Side Differential Analysis**:
  - 🟩 **Identical Values**: Visualized in green.
  - 🟨 **Different Values**: Visualized in amber/gold.
  - ⚪ **Unique Metadata**: Highlighted per individual image.
- **Statistical Summary**: Instant breakdown of total matching tags, conflicting values, and unique tags per image.

---

## 🛠️ Tech Stack & Requirements

- **Python**: 3.10+
- **GUI Framework**: PyQt6
- **Extraction Engine**: [PyExifTool](https://pypi.org/project/PyExifTool/) + [ExifTool](https://exiftool.org/) CLI binary

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Peppe03/image-metadata-comparator.git
cd image-metadata-comparator
```

### 2. Set up a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install PyQt6 PyExifTool
```

### 4. Install ExifTool
Ensure the standalone `exiftool` binary is available in your system path, or place `exiftool.exe` alongside the script on Windows:
- Download the executable from [ExifTool Official Website](https://exiftool.org/).
- Ensure `exiftool` can be invoked from the command line.

---

## 🖥️ Usage

Run the main application script:

```bash
python progetto_digital_forensics2.py
```

1. Drag two images into the left and right panels (or click each panel to select files).
2. The application will asynchronously extract metadata for both files.
3. Review the color-coded comparison view and final investigative statistics.
4. Click **Reset** to clear the session and analyze another pair.

---

## 📜 License
This project is open-source and intended for academic, educational, and digital forensics research purposes.