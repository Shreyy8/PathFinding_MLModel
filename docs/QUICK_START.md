# 🚀 Quick Start Guide

## What You Have

✅ **Backend API** (Python Flask) - Fully implemented and tested
✅ **Frontend UI** (Next.js React) - Modern web interface  
✅ **Integration** - Complete end-to-end system

## Start in 3 Steps

### 1️⃣ Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd v0-road-mapping-interface-main/v0-road-mapping-interface-main
npm install
cd ../..
```

### 2️⃣ Start Servers

**Option A - Automated (Recommended):**
```bash
# Linux/Mac
./start_full_stack.sh

# Windows
start_full_stack.bat
```

**Option B - Manual:**
```bash
# Terminal 1 - Backend
python run_server.py

# Terminal 2 - Frontend
cd v0-road-mapping-interface-main/v0-road-mapping-interface-main
npm run dev
```

### 3️⃣ Open Browser

Navigate to: **http://localhost:3000**

## How to Use

1. **Upload** a satellite image
2. **Click** on a road to set start point (green marker)
3. **Click** on another road to set goal point (red marker)
4. **View** the computed shortest path (blue line)
5. **Clear** and try different points

## Ports

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

## Test Images

Use any satellite/aerial image with visible roads. Good sources:
- Google Earth screenshots
- OpenStreetMap imagery
- Your own drone/satellite photos

## Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt
```

**Frontend won't start:**
```bash
# Check Node version
node --version  # Should be 18+

# Clear and reinstall
cd v0-road-mapping-interface-main/v0-road-mapping-interface-main
rm -rf node_modules package-lock.json
npm install
```

**Can't connect:**
- Verify both servers are running
- Check browser console for errors
- Ensure ports 3000 and 5000 are not blocked

## Documentation

📖 **Complete Guide:** `README_FULLSTACK.md`
🏗️ **System Overview:** `SYSTEM_OVERVIEW.md`
🔗 **Frontend Integration:** `FRONTEND_INTEGRATION_GUIDE.md`
📋 **Spec Documents:** `.kiro/specs/interactive-road-mapping-interface/`

## Features

✅ AI-powered road detection
✅ Interactive point selection
✅ Shortest path computation
✅ Real-time visualization
✅ Responsive design
✅ Error handling
✅ Session management

## Next Steps

1. Try uploading different images
2. Experiment with different start/goal combinations
3. Adjust overlay opacity for better visibility
4. Review the code to understand the architecture
5. Run the test suite: `pytest tests/ -v`

## Support

- Check `README_FULLSTACK.md` for detailed troubleshooting
- Review API documentation in design.md
- Check browser console for frontend errors
- Check terminal output for backend errors

---

**Ready?** Start the servers and open http://localhost:3000! 🎉
