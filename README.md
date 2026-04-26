# 🌍 SmartWaste360 - AI-Powered Waste Management Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-🚀%20Visit%20Now-brightgreen)](https://smartwaste360-frontend.vercel.app/)
[![Backend API](https://img.shields.io/badge/API-🔧%20Live%20Backend-blue)](https://smartwaste360-backend.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![API Version](https://img.shields.io/badge/API-v6.0.0-orange)](https://smartwaste360-backend.onrender.com)

> **A comprehensive waste management solution leveraging AI for waste classification, IoT-powered smart bin monitoring, real-time collection tracking, and community engagement. Built for smart cities and environmentally conscious communities.**

## 🎯 **LIVE APPLICATION**

### 🌐 **Production URLs:**
- **🚀 Frontend Application**: [https://smartwaste360-frontend.vercel.app/](https://smartwaste360-frontend.vercel.app/)
- **🔧 Backend API**: [https://smartwaste360-backend.onrender.com](https://smartwaste360-backend.onrender.com)
- **📊 API Health Check**: [https://smartwaste360-backend.onrender.com/health](https://smartwaste360-backend.onrender.com/health)

## ✨ **Features**

### 🤖 **AI-Powered Waste Classification**
- Real-time waste type detection powered by **Google Gemini AI**
- Camera integration for instant waste identification
- Supports multiple categories: Plastic, Paper, Glass, Metal, Organic, E-waste, Textile
- Confidence scoring and disposal recommendations

### 📡 **IoT Smart Bin Monitoring**
- **ESP32 + HC-SR04 ultrasonic sensor** for real-time bin fill-level detection
- Live dashboard with fill percentage, estimated weight, and historical charts
- Automatic collection point status updates from sensor data
- Smart-send: data transmitted only when fill level changes (reduces bandwidth)
- Median filtering for noise-resistant sensor readings
- API key authentication for secure device communication

### 🗺️ **Interactive Maps & Collection Points**
- Real-time colony and collection point mapping with Leaflet
- Location-based waste collection scheduling
- Route optimization for collectors using TSP solver with 2-opt improvement
- Traffic-aware route planning with time-of-day adjustments

### 👥 **Multi-Role Platform**
- **Users**: Register, classify waste, book collections, track points, view waste history
- **Collectors**: Manage pickups, schedule collections, view optimized routes, analytics dashboard
- **Admins**: System management, user oversight, analytics, system health monitoring

### 📊 **Real-Time Analytics**
- Comprehensive waste collection statistics and dashboards
- Colony-wise performance tracking and leaderboards
- Environmental impact tracking (CO₂ saved, weight recycled)
- Weekly impact summary reports

### 🔔 **Smart Notifications**
- 7 notification types: reminders, achievements, colony threshold alerts, collection scheduled/completed, weekly summaries, streak milestones
- Automated inactivity reminders for engagement
- Colony threshold alerts when bins are near capacity

### 🏆 **Gamification & Community**
- Points-based reward system with configurable points per waste type
- Colony leaderboards and user rankings
- Achievement system with streak tracking
- Colony-based competition for waste reduction

## 🚀 **Quick Start**

### **For Users:**
1. Visit [SmartWaste360](https://smartwaste360-frontend.vercel.app/)
2. Register a new account
3. Start classifying waste with your camera
4. Book waste collections in your area

### **For Collectors:**
1. Go to [Collector Login](https://smartwaste360-frontend.vercel.app/collector/login)
2. Use your collector credentials
3. View available pickups on the map
4. Use the pickup scheduler for optimized routes
5. Complete collections and update status

### **For Admins:**
1. Access [Admin Panel](https://smartwaste360-frontend.vercel.app/admin/login)
2. Login with admin credentials
3. Manage collectors, view analytics, oversee system health

## 🏗️ **Project Structure**

```
smartwaste360/
├── app.py                          # Flask app factory (API v6.0.0)
├── start_app.py                    # Automated startup script
├── wsgi.py                         # WSGI entry point (Gunicorn)
├── Procfile                        # Render deployment command
├── render.yaml                     # Render service config
├── vercel.json                     # Vercel deployment config
├── Dockerfile                      # Container build
│
├── backend/
│   ├── config/
│   │   └── database.py             # PostgreSQL connection manager
│   ├── routes/                     # 20 Flask Blueprints
│   │   ├── auth.py                 # User/Collector/Admin authentication
│   │   ├── waste.py                # Waste classification (Gemini AI)
│   │   ├── booking.py              # Collection booking system
│   │   ├── collector.py            # Collector operations
│   │   ├── admin.py                # Admin dashboard endpoints
│   │   ├── analytics.py            # Analytics & reporting
│   │   ├── iot.py                  # IoT sensor data ingestion
│   │   ├── colony.py               # Colony management
│   │   ├── collection_points.py    # Collection point CRUD
│   │   ├── leaderboard.py          # Rankings & leaderboards
│   │   ├── camera.py               # Camera/image upload
│   │   ├── transaction.py          # User waste transactions
│   │   ├── health.py               # Health check endpoint
│   │   └── migration.py            # Database migration runner
│   ├── models/                     # 12 data models
│   │   ├── user.py, collector.py, colony.py, booking.py
│   │   ├── waste.py, collection_point.py, transaction.py
│   │   ├── admin.py, analytics.py, achievement.py
│   │   └── route_optimizer.py
│   ├── services/                   # Business logic layer
│   │   ├── ml_service.py           # Gemini AI integration
│   │   ├── analytics_service.py    # Analytics calculations
│   │   ├── notification_service.py # 7 notification types
│   │   ├── route_optimization.py   # TSP + 2-opt route solver
│   │   ├── realtime_service.py     # Live stats & system health
│   │   └── points_service.py       # Points reward system
│   └── utils/                      # Validation, geo, file utilities
│
├── frontend/                       # React 18 SPA
│   ├── src/
│   │   ├── pages/                  # 20 page components
│   │   │   ├── Home, Login, Register, Dashboard
│   │   │   ├── Camera, Maps, Leaderboard
│   │   │   ├── IoTMonitor                          # Live sensor dashboard
│   │   │   ├── PickupScheduler, AnalyticsDashboard  # Collector tools
│   │   │   ├── CollectorDashboard, CollectorSettings
│   │   │   ├── AdminLogin, AdminDashboard
│   │   │   ├── StatsPage, WasteHistoryPage, SettingsPage
│   │   │   └── NotFound
│   │   ├── components/             # 9 component groups
│   │   │   ├── admin/, auth/, camera/, collector/
│   │   │   ├── common/ (ProtectedRoute, LoginSelector)
│   │   │   ├── dashboard/, layout/, leaderboard/, maps/
│   │   ├── services/               # 11 API service modules
│   │   ├── hooks/                  # Custom hooks (useApi, useCamera, useLocation, useCollectorLocation)
│   │   ├── context/                # AuthContext (JWT management)
│   │   └── store/                  # Redux state slices
│
├── iot/                            # IoT Hardware
│   └── esp32_ultrasonic/
│       └── esp32_ultrasonic.ino    # ESP32 firmware (HC-SR04 sensor)
│
├── database/                       # Database management
│   ├── schema.sql                  # Full schema (13+ tables, triggers, views)
│   ├── iot_migration.sql           # IoT sensor_readings table
│   ├── migrations/                 # Versioned migrations
│   └── sample_data.sql             # Seed data
│
├── deployment/                     # Infrastructure
│   ├── Dockerfile.backend          # Backend container
│   ├── Dockerfile.frontend         # Frontend container
│   ├── docker-compose.yml          # Full stack (Nginx, Redis, Prometheus, Grafana)
│   ├── nginx.conf                  # Reverse proxy config
│   ├── deploy.sh / deploy.ps1      # Deploy scripts
│   └── cloud-deploy.md            # Cloud deployment guide
│
├── docs/                           # Detailed guides
│   ├── RUN_APPLICATION.md
│   ├── ADVANCED_FEATURES_GUIDE.md
│   ├── COLLECTION_SYSTEM_GUIDE.md
│   ├── COLLECTION_COMPLETION_GUIDE.md
│   ├── PICKUP-SCHEDULER-ALGORITHM.md
│   └── FEATURE_ROADMAP.md
│
├── tests/
│   └── test_suite.py               # API test suite
│
└── SECURITY.md                     # Security guidelines
```

## 🛠️ **Technology Stack**

### **Frontend**
- ⚛️ React 18 with modern hooks & context API
- 🎨 Tailwind CSS with Forms & Typography plugins
- 🗺️ Leaflet + React-Leaflet for interactive maps
- 📊 Recharts for data visualization
- 🔐 JWT authentication with role-based route protection
- 🧭 React Router v6 with protected routes
- 📡 Axios for API communication
- 🎯 Lucide React & React Icons for iconography

### **Backend**
- 🐍 Python Flask REST API (v6.0.0)
- 🤖 **Google Gemini AI** for waste classification
- 🗄️ PostgreSQL (Neon) with psycopg2
- 🔒 Flask-JWT-Extended for authentication & authorization
- 🔑 bcrypt for password hashing
- 📡 Flask-CORS for cross-origin requests
- 🚀 Gunicorn WSGI server for production

### **IoT Layer**
- 🔌 ESP32 DevKit V1 microcontroller
- 📏 HC-SR04 ultrasonic distance sensor
- 📶 WiFi (HTTP/HTTPS) for data transmission
- 🔐 API key authentication (`X-IoT-API-Key`)

### **Deployment**
- 🌐 **Frontend**: Vercel (auto-deploy from GitHub)
- 🔧 **Backend**: Render (Gunicorn, auto-deploy from GitHub)
- 🗄️ **Database**: Neon PostgreSQL (serverless)
- 🤖 **AI**: Google Gemini API
- 🐳 **Self-hosting**: Docker Compose (Nginx + Redis + Prometheus + Grafana)

## 📡 **IoT Integration**

### **Hardware Setup**
- **Microcontroller**: ESP32 DevKit V1
- **Sensor**: HC-SR04 Ultrasonic Distance Sensor
- **Purpose**: Real-time bin fill-level monitoring

### **Wiring Diagram**
```
HC-SR04 VCC  → ESP32 VIN (5V from USB)
HC-SR04 GND  → ESP32 GND
HC-SR04 TRIG → ESP32 GPIO 5
HC-SR04 ECHO → [1kΩ resistor] → ESP32 GPIO 18
                               ↓
                           [2kΩ resistor]
                               ↓
                              GND
```
> **Note**: The voltage divider on the ECHO pin is required because the HC-SR04 outputs 5V logic, but ESP32 GPIO pins are 3.3V tolerant.

### **Data Pipeline**
```
Sensor → ESP32 → WiFi → POST /api/iot/bin-level → PostgreSQL → IoT Monitor Dashboard
```

### **Key Features**
- **Median filtering**: Takes 5 samples per measurement, returns median (removes spikes)
- **Smart-send**: Only transmits when fill level changes by >2% (bandwidth efficient)
- **Auto-reconnect**: WiFi reconnection with retry logic
- **Error reporting**: After 5 consecutive sensor errors, sends a status report so the backend knows the device is alive
- **HTTPS support**: SSL for communication with deployed backend

### **IoT API Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/iot/bin-level` | Receive sensor data (auth required) |
| `GET` | `/api/iot/live/<point_name>` | Live fill level for dashboard (public) |
| `GET` | `/api/iot/readings/<colony_id>` | Historical readings for a colony |
| `GET` | `/api/iot/devices` | List all IoT devices with last reading |

## 🔗 **API Routes Overview**

| Blueprint | Prefix | Description |
|-----------|--------|-------------|
| `auth` | `/api/auth` | User/Collector/Admin registration & login |
| `waste` | `/api/waste` | Waste classification & logging |
| `booking` | `/api/booking` | Collection booking system |
| `collector` | `/api/collector` | Collector operations & management |
| `admin` | `/api/admin` | Admin dashboard endpoints |
| `analytics` | `/api/analytics` | Analytics & reporting |
| `iot` | `/api/iot` | IoT sensor data ingestion |
| `colony` | `/api/colony` | Colony management |
| `collection-points` | `/api/collection-points` | Collection point CRUD |
| `leaderboard` | `/api/leaderboard` | Rankings & leaderboards |
| `camera` | `/api/camera` | Camera/image upload |
| `transaction` | `/api/transaction` | Waste deposit transactions |
| `health` | `/health` | Health check |
| `migration` | `/api/migration` | Database migrations |

## 🗄️ **Database Schema**

The PostgreSQL database includes the following key tables:

| Table | Purpose |
|-------|---------|
| `users` | User accounts with points & colony assignment |
| `colonies` | Colony/community data with waste level tracking |
| `waste_logs` | Waste classification records with AI predictions |
| `collectors` | Collector profiles & assigned colonies |
| `collection_bookings` | Scheduled/completed waste pickups |
| `user_transactions` | Waste deposit records with verification codes |
| `notifications` | User notifications (7 types) |
| `points_config` | Configurable points per waste material |
| `collection_points` | Physical bin locations with capacity tracking |
| `sensor_readings` | IoT time-series data (fill %, weight, distance) |

Additional features: database triggers for automatic colony point/user count updates, leaderboard views, and performance indexes.

## 🎨 **User Experience**

### **Frontend Pages**
| Page | Route | Role | Description |
|------|-------|------|-------------|
| Home | `/` | Public | Landing page |
| Login / Register | `/login`, `/register` | Public | User authentication |
| Dashboard | `/dashboard` | User | Personal overview |
| Stats | `/dashboard/stats` | User | Waste statistics |
| Waste History | `/dashboard/history` | User | Past classifications |
| Settings | `/dashboard/settings` | User | Account settings |
| Camera | `/camera` | User | AI waste classification |
| Maps | `/maps` | Public | Interactive colony/collection point map |
| Leaderboard | `/leaderboard` | Public | Colony & user rankings |
| IoT Monitor | `/iot-monitor` | Public | Live bin fill-level dashboard |
| Collector Dashboard | `/collector/dashboard` | Collector | Pickup management |
| Pickup Scheduler | `/collector/scheduler` | Collector | Optimized route scheduling |
| Collector Analytics | `/collector/analytics` | Collector | Performance analytics |
| Collector Settings | `/collector/settings` | Collector | Profile management |
| Admin Dashboard | `/admin/dashboard` | Admin | System management & oversight |

### **Responsive Design**
- 📱 Fully optimized for mobile, tablet, and desktop devices
- 👆 Touch-friendly interfaces with intuitive navigation
- 📷 Native camera integration for waste classification
- 🌓 Clean, modern UI built with Tailwind CSS

### **Accessibility**
- ♿ Semantic HTML for screen reader compatibility
- ⌨️ Keyboard navigation support
- 🎯 High contrast UI elements for visibility
- 📏 Responsive text sizing

## 🔒 **Security & Privacy**

### **Authentication & Authorization**
- 🔐 JWT-based authentication with 24-hour token expiry
- 👮 Role-based route protection (`user`, `collector`, `admin`)
- 🔑 bcrypt password hashing
- 🚫 Debug routes gated behind `FLASK_DEBUG` (disabled in production)
- ✅ Production config validation — raises error if critical env vars are missing

### **API Security**
- ✅ CORS configuration for authorized origins
- 🔒 HTTPS encryption for all data transmission
- 🔐 IoT API key authentication (X-IoT-API-Key header)
- 📝 Comprehensive error handling without exposing system details

### **Data Protection**
- 🔑 Environment variables for all sensitive credentials (never hardcoded)
- 🚫 No storage of sensitive payment or personal identification data
- 📋 User data collection limited to essential information only
- See [SECURITY.md](SECURITY.md) for detailed security guidelines

## 🤖 **AI Classification**

### **How It Works**
- 🧠 Powered by **Google Gemini AI** for accurate waste type detection
- 📸 Users upload a photo → Gemini analyzes the image → returns waste category, confidence score, and disposal recommendations
- 📊 Supports multiple waste categories: Plastic, Paper, Glass, Metal, Organic, E-waste, Textile
- 🎯 Real-time image analysis with confidence scoring

### **Current Limitations**
- 🌐 Requires internet connectivity for AI classification
- 📸 Image quality affects classification accuracy
- 🔄 Accuracy depends on lighting and image clarity
- 💡 Best results with clear, well-lit photos of single items

## 📊 **Scalability & Performance**

### **Current Architecture**
- ⚡ Serverless frontend deployment on Vercel (auto-scaling)
- 🔧 Backend hosted on Render with Gunicorn (multi-worker)
- 🗄️ Neon PostgreSQL (serverless, auto-scaling)
- 📡 RESTful API design with Blueprint-based modular routes

### **Performance Considerations**
- ⏱️ Average API response time: < 500ms
- 🚀 Frontend optimized with code splitting and lazy loading
- 💾 Database connection pooling for concurrent users
- 📦 Image compression for faster uploads
- 🧮 Route optimization uses Haversine distance + 2-opt solver

### **Known Limitations**
- 🌐 Backend cold starts on Render free tier (~30s initial load)
- 📍 Map performance may vary with large datasets (>1000 points)
- 🔄 Real-time updates use polling (not WebSockets yet)

### **Scalability Roadmap**
- 🚀 Implement caching layer (Redis) for frequently accessed data
- 📡 WebSocket integration for real-time updates
- 🌍 CDN integration for global content delivery
- 📈 Database sharding for horizontal scaling

## 🐳 **Deployment**

### **Production (Current)**
- **Frontend** → Vercel (auto-deploy from `main` branch)
- **Backend** → Render (Gunicorn, auto-deploy from `main` branch)
- **Database** → Neon PostgreSQL (serverless)

### **Self-Hosting with Docker**
A full Docker Compose stack is available in `deployment/` with:
- 🔀 **Nginx** — reverse proxy & SSL termination
- 🐍 **Flask backend** — 2 replicas with resource limits
- ⚛️ **React frontend** — static build served by Nginx
- 🗄️ **PostgreSQL 15** — persistent data volume
- 🔴 **Redis 7** — caching & sessions
- 📈 **Prometheus** — metrics collection
- 📊 **Grafana** — monitoring dashboards

See [deployment/cloud-deploy.md](deployment/cloud-deploy.md) for detailed instructions.

## 🌍 **Environmental Impact**
SmartWaste360 helps communities:
- ♻️ Improve waste sorting accuracy with AI-powered classification
- 🚛 Optimize collection routes, reducing fuel consumption
- 📈 Track recycling progress with detailed analytics
- 🌱 Reduce environmental footprint through data-driven decisions
- 👥 Engage communities in sustainable waste management
- 📡 Monitor bin fill levels in real-time with IoT sensors

## 📚 **Documentation**

Detailed guides are available in the `docs/` directory:

| Guide | Description |
|-------|-------------|
| [RUN_APPLICATION.md](docs/RUN_APPLICATION.md) | How to run the application |
| [ADVANCED_FEATURES_GUIDE.md](docs/ADVANCED_FEATURES_GUIDE.md) | Advanced features walkthrough |
| [COLLECTION_SYSTEM_GUIDE.md](docs/COLLECTION_SYSTEM_GUIDE.md) | Waste collection workflow |
| [COLLECTION_COMPLETION_GUIDE.md](docs/COLLECTION_COMPLETION_GUIDE.md) | Collection completion process |
| [PICKUP-SCHEDULER-ALGORITHM.md](docs/PICKUP-SCHEDULER-ALGORITHM.md) | Route optimization algorithm details |
| [FEATURE_ROADMAP.md](docs/FEATURE_ROADMAP.md) | Planned features & future work |
| [SECURITY.md](SECURITY.md) | Security guidelines & best practices |

## ⚠️ **System Requirements**

### **For Users**
- 📱 Modern web browser (Chrome, Firefox, Safari, Edge)
- 📷 Device with camera for waste classification
- 🌐 Internet connection (3G or better recommended)
- 📍 Location services enabled for map features

### **For IoT Hardware**
- 🔌 ESP32 DevKit V1
- 📏 HC-SR04 Ultrasonic Sensor
- 🔧 1kΩ + 2kΩ resistors (voltage divider)
- 📶 WiFi network with internet access
- ⚡ 5V USB power supply

## 🐛 **Known Issues & Limitations**

### **Current Limitations**
- 🌐 Requires stable internet connection for full functionality
- 📸 AI classification accuracy varies with image quality (70-90% accuracy)
- 🗺️ Map features require location permissions
- ⏱️ First load may be slow due to free-tier hosting cold starts
- 📡 IoT sensor accuracy affected by temperature and humidity

### **Planned Improvements**
- 🔄 Offline mode for basic features
- 📱 Native mobile apps for better performance
- 🌍 Multi-language support
- 🔔 Push notifications for collection reminders
- 📊 Advanced analytics with predictive insights
- 📡 WebSocket integration for real-time IoT updates

## 📄 **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**
- Built with passion for environmental sustainability and smart city solutions
- AI classification powered by Google Gemini API
- Maps provided by OpenStreetMap and Leaflet
- Deployed on Vercel, Render, and Neon platforms
- IoT integration with ESP32 and HC-SR04

## 📞 **Support & Feedback**
- 🐛 Report issues on GitHub Issues
- 💡 Feature requests welcome
- 📧 Contact for enterprise deployments
- ⭐ Star this repo if you find it useful!

---

**🚀 Ready to make waste management smarter? [Start using SmartWaste360 now!](https://smartwaste360-frontend.vercel.app/)**
