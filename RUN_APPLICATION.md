# 🚀 How to Run SmartWaste360

## ✅ **Current Status: Ready to Run**

All fixes have been applied:
- ✅ Backend type conversion errors fixed
- ✅ Frontend icon import errors fixed  
- ✅ Database connections working
- ✅ All dependencies installed

## 🎯 **Step-by-Step Instructions**

### **Step 1: Start Backend Server**
Open **Terminal 1** and run:
```bash
python app.py
```

**Expected Output:**
```
[OK] Database connection pool created successfully for 'smartwaste360'.
[OK] ML Service initialized with Gemini model: 'gemini-2.5-flash'.
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### **Step 2: Start Frontend Server**  
Open **Terminal 2** and run:
```bash
cd frontend
npm start
```

**Expected Output:**
```
Starting the development server...
Compiled successfully!
Local: http://localhost:3000
```

### **Step 3: Access Application**
Open your browser and go to:
- **Main App**: http://localhost:3000
- **API Health**: http://localhost:5000/health

## 🧪 **Test the Application**

### **Quick API Test**
In **Terminal 3**, run:
```bash
python test_app.py
```

### **Manual Browser Testing**
1. **Register a new user** at http://localhost:3000
2. **Submit waste** using the camera feature
3. **Check leaderboard** and points system
4. **View analytics dashboard** (if collector/admin)

## 🔧 **Troubleshooting**

### **If Backend Won't Start:**
```bash
# Check Python environment
python --version
pip list | findstr flask

# Reinstall if needed
pip install -r requirements.txt
```

### **If Frontend Won't Start:**
```bash
# Check Node.js
node --version
npm --version

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### **If Port 3000 is Busy:**
```bash
# Start on different port
cd frontend
set PORT=3001 && npm start
```

## 📱 **Features to Test**

### **User Journey:**
1. Register → Login → Submit Waste → Check Points → View Leaderboard

### **Collector Journey:**  
1. Login → View Bookings → Complete Collections → Check Analytics

### **Admin Journey:**
1. Login → View Dashboard → Manage Users → Configure System

## 🎉 **Success Indicators**

✅ **Backend**: Console shows "Running on http://127.0.0.1:5000"  
✅ **Frontend**: Browser opens to http://localhost:3000  
✅ **Database**: No connection errors in console  
✅ **API**: Health endpoint returns success  

---

**The application is fully functional and ready for use!**