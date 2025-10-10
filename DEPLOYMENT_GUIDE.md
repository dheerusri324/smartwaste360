# 🚀 SmartWaste360 Deployment Guide

## 📋 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
python start_app.py
```

### Option 2: Manual Startup
```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

## 🔧 Prerequisites

### Backend Dependencies
```bash
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

## 🌐 Application URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main React application |
| **Backend API** | http://localhost:5000 | Flask REST API |
| **Health Check** | http://localhost:5000/health | API status |

## 🧪 Testing

### Run Test Suite
```bash
python test_app.py
```

### Manual API Testing
```bash
# Test basic connectivity
curl http://localhost:5000/

# Test health endpoint
curl http://localhost:5000/health
```

## 📱 Features Ready for Testing

### 👤 User Features
- ✅ **User Registration/Login**
- ✅ **Waste Submission with Camera**
- ✅ **Points & Leaderboard System**
- ✅ **Personal Dashboard & Stats**
- ✅ **Interactive Colony Map**

### 🚛 Collector Features  
- ✅ **Collection Booking Management**
- ✅ **Real-time Performance Analytics**
- ✅ **Route Optimization**
- ✅ **Transaction Processing**

### 👨‍💼 Admin Features
- ✅ **System Analytics Dashboard**
- ✅ **User & Collector Management**
- ✅ **Points Configuration**
- ✅ **Waste Category Management**

## 🔍 Troubleshooting

### Backend Issues
```bash
# Check if Flask dependencies are installed
python -c "import flask, flask_cors, flask_jwt_extended; print('OK')"

# Check database connection
python -c "from app import app; print('Database OK')"
```

### Frontend Issues
```bash
# Check if Node.js dependencies are installed
cd frontend && npm list --depth=0

# Clear cache and reinstall
cd frontend && rm -rf node_modules package-lock.json && npm install
```

### Port Conflicts
```bash
# Check what's running on ports
netstat -an | findstr :3000
netstat -an | findstr :5000

# Kill processes if needed
taskkill /F /PID <process_id>
```

## 📊 Database Schema

The application uses SQLite with the following main tables:
- `users` - User accounts and profiles
- `collectors` - Waste collector information  
- `waste_logs` - Waste submission records
- `bookings` - Collection scheduling
- `transactions` - Payment processing
- `colonies` - Geographic waste collection points

## 🔐 Environment Configuration

Create `.env` file in root directory:
```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///smartwaste360.db
```

## 🚀 Production Deployment

### Backend (Flask)
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (React)
```bash
# Build for production
cd frontend
npm run build

# Serve with nginx or Apache
```

## 📈 Performance Monitoring

### Key Metrics to Monitor
- API response times
- Database query performance  
- Frontend bundle size
- User engagement metrics
- Waste collection efficiency

### Logging
- Backend logs: `backend/logs/`
- Frontend console: Browser DevTools
- Database queries: Enable SQL logging

## 🔄 Development Workflow

1. **Start Development Servers**
   ```bash
   python start_app.py
   ```

2. **Make Changes**
   - Backend: Files auto-reload with Flask debug mode
   - Frontend: Hot reload with React dev server

3. **Test Changes**
   ```bash
   python test_app.py
   ```

4. **Commit & Deploy**
   ```bash
   git add .
   git commit -m "Feature: description"
   git push origin main
   ```

## 🆘 Support

### Common Issues
1. **Port already in use**: Change ports in configuration
2. **Database locked**: Restart application
3. **CORS errors**: Check frontend/backend URLs match
4. **Icon import errors**: Verify lucide-react icons exist

### Getting Help
- Check console logs for detailed error messages
- Use browser DevTools for frontend debugging
- Review Flask debug output for backend issues
- Test API endpoints with curl or Postman

---

**🎉 SmartWaste360 is ready for development and testing!**