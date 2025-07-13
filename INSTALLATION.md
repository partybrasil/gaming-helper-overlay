# Gaming Helper Overlay - Installation Guide

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB available space
- **Graphics**: DirectX 11 compatible graphics card

### Recommended Requirements
- **Operating System**: Windows 11 (latest version)
- **Python**: 3.11 or 3.12 (latest stable)
- **RAM**: 8GB or more
- **Storage**: 1GB available space (for plugins and data)
- **Graphics**: Modern graphics card with OpenGL 3.3+ support
- **CPU**: Multi-core processor for optimal threading performance

---

## 🚀 Quick Installation

### Method 1: Direct Download (Recommended)

1. **Download the Project**
   ```bash
   git clone https://github.com/partybrasil/gaming-helper-overlay.git
   cd gaming-helper-overlay
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

### Method 2: Virtual Environment (Advanced)

1. **Create Virtual Environment**
   ```bash
   python -m venv gaming-overlay-env
   gaming-overlay-env\Scripts\activate
   ```

2. **Clone and Install**
   ```bash
   git clone https://github.com/partybrasil/gaming-helper-overlay.git
   cd gaming-helper-overlay
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

---

## 📦 Detailed Installation Steps

### Step 1: Install Python

1. **Download Python**
   - Visit [python.org](https://python.org/downloads/)
   - Download Python 3.10+ for Windows
   - **Important**: Check "Add Python to PATH" during installation

2. **Verify Installation**
   ```bash
   python --version
   pip --version
   ```

### Step 2: Install Git (Optional but Recommended)

1. **Download Git**
   - Visit [git-scm.com](https://git-scm.com/download/win)
   - Install with default settings

2. **Verify Installation**
   ```bash
   git --version
   ```

### Step 3: Download Gaming Helper Overlay

#### Option A: Using Git (Recommended)
```bash
git clone https://github.com/partybrasil/gaming-helper-overlay.git
cd gaming-helper-overlay
```

#### Option B: Direct Download
1. Download ZIP from GitHub
2. Extract to desired folder
3. Open command prompt in the extracted folder

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you encounter permission errors, try:**
```bash
pip install --user -r requirements.txt
```

### Step 5: First Run

```bash
python main.py
```

---

## 🔧 Manual Dependency Installation

If automatic installation fails, install dependencies manually:

```bash
pip install PySide6>=6.5.0
pip install PyYAML>=6.0
pip install psutil>=5.9.0
pip install requests>=2.28.0
```

---

## 🎮 Gaming-Specific Setup

### For Steam Games
1. **Enable Steam Overlay** (if using Steam)
   - Steam → Settings → In-Game → Enable Steam Overlay
   - This ensures compatibility with gaming overlays

2. **Graphics Settings**
   - Set games to "Borderless Windowed" mode for best overlay compatibility
   - Fullscreen Exclusive mode may hide overlays

### For Other Game Launchers
1. **Epic Games Launcher**
   - No special configuration needed
   - Overlays work with most Epic games

2. **Battle.net**
   - Disable Battle.net overlay if conflicts occur
   - Gaming Helper Overlay should work normally

3. **Origin/EA App**
   - Similar to Battle.net, disable built-in overlays if needed

---

## 🛡️ Windows Security Settings

### Windows Defender
If Windows Defender blocks the application:

1. **Add Exclusion**
   - Windows Security → Virus & threat protection
   - Exclusions → Add an exclusion
   - Folder → Select gaming-helper-overlay directory

2. **Allow Through Firewall**
   - The app may request network access for updates
   - Allow if prompted

### UAC (User Account Control)
- Run as Administrator if you encounter permission issues
- Right-click `main.py` → Run as Administrator

---

## 📁 Directory Structure

After installation, your directory should look like:

```
gaming-helper-overlay/
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── config/                 # Configuration files
├── core/                   # Core application modules
├── ui/                     # User interface components
├── plugins/                # Built-in and custom plugins
├── assets/                 # Icons, sounds, images
├── data/                   # User data and logs
├── docs/                   # Documentation
└── README.md               # Main documentation
```

---

## 🔄 Updating the Application

### Method 1: Git Update (If installed via Git)
```bash
cd gaming-helper-overlay
git pull origin main
pip install -r requirements.txt
```

### Method 2: Manual Update
1. Download new version
2. Backup your `config/` and `data/` directories
3. Replace old files with new ones
4. Restore your backup directories
5. Run `pip install -r requirements.txt`

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Python Not Found
```
'python' is not recognized as an internal or external command
```
**Solution**: Add Python to PATH or use full path to python.exe

#### Module Import Errors
```
ModuleNotFoundError: No module named 'PySide6'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

#### Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Run as Administrator or use `--user` flag with pip

#### Application Won't Start
1. Check Python version: `python --version`
2. Verify all dependencies: `pip list`
3. Check error logs in `data/logs/`
4. Try running with `python -v main.py` for verbose output

#### Overlay Not Visible in Games
1. Set game to Borderless Windowed mode
2. Check if overlay is behind game window
3. Adjust overlay transparency settings
4. Ensure "Always on Top" is enabled

#### High CPU Usage
1. Enable "Low CPU Mode" in settings
2. Reduce FPS Counter update frequency
3. Disable unused plugins
4. Check Task Manager for background processes

### Getting Help

If you still have issues:

1. **Check Logs**
   - Look in `data/logs/` for error messages
   - Enable Debug mode in settings for more detailed logs

2. **GitHub Issues**
   - Search existing issues
   - Create new issue with:
     - Error message
     - Steps to reproduce
     - System specifications
     - Log files

3. **Community Support**
   - Join Discord server (link in README)
   - Ask questions in GitHub Discussions

---

## 🏃 Performance Optimization

### For Low-End Systems
1. **Reduce Update Rates**
   - FPS Counter: Update every 2-3 seconds
   - System Monitor: Update every 5 seconds

2. **Disable Visual Effects**
   - Turn off transparency
   - Disable animations
   - Use simple themes

3. **Limit Plugins**
   - Only enable plugins you actually use
   - Avoid running multiple monitoring plugins

### For High-End Systems
1. **Enable All Features**
   - Full transparency and effects
   - High-frequency updates
   - Multiple simultaneous plugins

2. **Advanced Features**
   - Enable all monitoring features
   - Use complex themes and animations

---

## 🔐 Security Considerations

### Antivirus Software
- Some antivirus software may flag Python executables
- Add the installation directory to exclusions if needed
- The application is open-source and safe to use

### Network Access
- The application may access the internet for:
  - Checking for updates
  - Plugin downloads (if enabled)
  - Steam API integration (if configured)
- All network access is logged and can be disabled in settings

### Privacy
- No personal data is collected or transmitted
- All data stays on your local machine
- Configuration and logs are stored locally only

---

*Installation Guide v1.0 - Last updated: 2024*
