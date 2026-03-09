# Troubleshooting: "Failed to fetch" Error

## Problem
Frontend (localhost:3000) cannot connect to Backend (localhost:5000)

## Quick Checks

### 1. Is the Backend Running?

**Check if backend is running:**
```bash
# Open a new terminal and run:
python run_server.py
```

**Expected output:**
```
INFO - Backend API initialized successfully
INFO - CORS enabled for origins: ['http://localhost:*', 'http://127.0.0.1:*']
 * Running on http://localhost:5000
```

**Test backend directly:**
```bash
# In another terminal:
curl http://localhost:5000/api/state/test-id
```

If you get a response (even an error), the backend is running.

### 2. Check CORS Configuration

The backend needs to allow requests from localhost:3000.

**Verify CORS settings in `src/api/config.py`:**
```python
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:*,http://127.0.0.1:*"
).split(",")
```

The wildcard `*` should allow port 3000.

### 3. Check Frontend API URL

**Verify the API URL in `v0-road-mapping-interface-main/v0-road-mapping-interface-main/lib/api-client.ts`:**
```typescript
const DEFAULT_BASE_URL = 'http://localhost:5000/api'
```

### 4. Check Browser Console

Open browser DevTools (F12) and check:
- **Console tab:** Look for detailed error messages
- **Network tab:** Check if requests are being made and what the response is

## Common Issues & Solutions

### Issue 1: Backend Not Running
**Symptom:** `Failed to fetch` or `ERR_CONNECTION_REFUSED`

**Solution:**
```bash
# Start the backend
python run_server.py
```

### Issue 2: Wrong Port
**Symptom:** Backend running but frontend can't connect

**Solution:**
Check if backend is actually on port 5000:
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

If it's on a different port, update `lib/api-client.ts`

### Issue 3: CORS Blocked
**Symptom:** Browser console shows CORS error

**Solution:**
Update `src/api/config.py`:
```python
CORS_ORIGINS = "http://localhost:3000,http://localhost:*".split(",")
```

Then restart the backend.

### Issue 4: Firewall Blocking
**Symptom:** Connection timeout

**Solution:**
- Temporarily disable firewall
- Or add exception for ports 3000 and 5000

### Issue 5: Using 127.0.0.1 vs localhost
**Symptom:** Mixed usage causing issues

**Solution:**
Use consistent addressing. Either:
- Both use `localhost`
- Both use `127.0.0.1`

Update `lib/api-client.ts` if needed:
```typescript
const DEFAULT_BASE_URL = 'http://127.0.0.1:5000/api'
```

## Step-by-Step Debugging

### Step 1: Test Backend Directly

```bash
# Test if backend is accessible
curl http://localhost:5000/api/state/test-id

# Or use PowerShell on Windows
Invoke-WebRequest -Uri http://localhost:5000/api/state/test-id
```

**Expected:** Some JSON response (even an error is fine)
**If fails:** Backend is not running or not on port 5000

### Step 2: Check Backend Logs

Look at the terminal where you ran `python run_server.py`:
- Are there any error messages?
- Does it show "Running on http://localhost:5000"?
- Are requests being logged?

### Step 3: Test from Browser

Open browser and navigate to:
```
http://localhost:5000/api/state/test-id
```

**Expected:** JSON response (likely an error about invalid image_id)
**If fails:** Backend not accessible from browser

### Step 4: Check Network Tab

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try uploading an image in the frontend
4. Look for the request to `/api/load-image`
5. Check:
   - Status code
   - Response
   - Headers

### Step 5: Verify CORS Headers

In Network tab, check the response headers for:
```
Access-Control-Allow-Origin: http://localhost:3000
```

If missing, CORS is not configured correctly.

## Quick Fix Script

Create a test file to verify connectivity:

**test_connection.py:**
```python
import requests

try:
    response = requests.get('http://localhost:5000/api/state/test')
    print(f"✅ Backend is accessible")
    print(f"Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend")
    print("Make sure backend is running: python run_server.py")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
python test_connection.py
```

## Environment-Specific Solutions

### Windows
```bash
# Check if port is in use
netstat -ano | findstr :5000

# Kill process if needed (replace PID)
taskkill /PID <PID> /F

# Start backend
python run_server.py
```

### Linux/Mac
```bash
# Check if port is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>

# Start backend
python run_server.py
```

## Still Not Working?

### Option 1: Use Different Ports

**Backend - Change port in `src/api/config.py`:**
```python
PORT = int(os.getenv("API_PORT", "5001"))  # Changed from 5000
```

**Frontend - Update `lib/api-client.ts`:**
```typescript
const DEFAULT_BASE_URL = 'http://localhost:5001/api'  // Changed from 5000
```

### Option 2: Disable CORS Temporarily (Testing Only)

**In `src/api/app.py`, change CORS to allow all:**
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

⚠️ **Warning:** Only for testing! Don't use in production.

### Option 3: Check Antivirus/Security Software

Some security software blocks local connections:
- Temporarily disable antivirus
- Add exception for Python and Node.js
- Check Windows Defender Firewall

## Verification Checklist

- [ ] Backend is running (`python run_server.py`)
- [ ] Backend shows "Running on http://localhost:5000"
- [ ] Can access http://localhost:5000/api/state/test in browser
- [ ] Frontend is running (`npm run dev`)
- [ ] Frontend is on http://localhost:3000
- [ ] Browser console shows no CORS errors
- [ ] Network tab shows requests being made
- [ ] CORS_ORIGINS includes localhost:3000 or localhost:*

## Get More Help

If still stuck, provide:
1. Backend terminal output
2. Frontend terminal output
3. Browser console errors (F12 → Console)
4. Network tab screenshot (F12 → Network)
5. Operating system

## Quick Test Command

Run this to test everything:

```bash
# Terminal 1 - Start backend
python run_server.py

# Terminal 2 - Test backend
curl http://localhost:5000/api/state/test

# Terminal 3 - Start frontend
cd v0-road-mapping-interface-main/v0-road-mapping-interface-main
npm run dev

# Browser - Open
http://localhost:3000
```

If backend test (Terminal 2) works but frontend doesn't connect, it's a CORS or frontend configuration issue.
