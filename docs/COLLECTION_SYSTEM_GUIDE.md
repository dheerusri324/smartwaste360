# Collection Points & Criteria Guide

## 🗺️ Collection Points on Map

### **Where to Find Collection Points**

1. **Maps Page**: Navigate to `/maps` and click the "Collection Points" tab
2. **Collector Dashboard**: Click "Points" button on any colony card
3. **Interactive Map**: Shows all collection points with color-coded markers

### **Collection Points Locations**

Currently active collection points:

#### **Green Valley Colony**

- **Main Gate Collection Point** (28.6139°N, 77.2090°E)
  - Accepts: Plastic, Paper, Metal
  - Capacity: 150kg
- **Community Center Point** (28.6140°N, 77.2091°E)
  - Accepts: Glass, Textile
  - Capacity: 100kg

#### **Eco-Friendly Homes**

- **Park Collection Point** (28.6141°N, 77.2092°E)
  - Accepts: Plastic, Paper
  - Capacity: 120kg

#### **Sustainable Living Society**

- **Society Entrance Point** (28.6142°N, 77.2093°E)
  - Accepts: Metal, Glass
  - Capacity: 80kg

#### **Unknown Area**

- **Central Collection Hub** (28.6143°N, 77.2094°E)
  - Accepts: Plastic, Paper, Metal, Glass
  - Capacity: 200kg

### **Map Features**

- **Color-coded markers** by waste type priority
- **Interactive popups** with full details
- **Google Maps integration** for directions
- **Capacity indicators** and last collection dates
- **Waste type badges** for easy identification

---

## 📊 Collection Criteria

### **Colony Waste Thresholds**

Colonies appear in "Find Pickups" when they reach these thresholds:

| Waste Type          | Threshold | Status    |
| ------------------- | --------- | --------- |
| **Plastic**         | ≥5kg      | 🟢 Active |
| **Paper**           | ≥5kg      | 🟢 Active |
| **Metal**           | ≥1kg      | 🟢 Active |
| **Glass**           | ≥2kg      | 🟢 Active |
| **Textile**         | ≥1kg      | 🟢 Active |
| **Mixed Dry Waste** | ≥10kg     | 🟢 Active |

### **Current Colony Status**

#### **🟢 Ready for Collection**

1. **Green Valley Colony**

   - Primary: Plastic (6kg) + Paper (9kg) + Metal (1kg)
   - Total dry waste: 16kg
   - Status: Ready for plastic collection

2. **Unknown Area**

   - Primary: Plastic (3kg) + Metal (1kg)
   - Total dry waste: 4kg
   - Status: Ready for metal collection

3. **Eco-Friendly Homes**
   - Primary: Glass (2kg) + Metal (0.5kg)
   - Total dry waste: 2.5kg
   - Status: Ready for glass collection

### **How Thresholds Work**

1. **User classifies waste** → Waste totals update automatically
2. **Colony reaches threshold** → Appears in collector's "Find Pickups"
3. **Collector sees breakdown** → Can view specific waste types and amounts
4. **Collection points available** → Collector can see exact pickup locations

---

## 🚛 For Collectors

### **Finding Pickups**

1. **Login** to collector dashboard
2. **Set waste type preferences** in Profile Settings
3. **View filtered colonies** in "Find Pickups" section
4. **See detailed breakdown** of waste types and amounts
5. **Click "Points"** to view collection locations on map

### **Scheduling Pickups**

1. **Click "Schedule Pickup"** on any ready colony
2. **Select date and time slot**
3. **Booking appears** in "My Schedule" section
4. **View collection points** for efficient route planning

### **Collection Points Benefits**

- **Exact locations** for pickup within colonies
- **Waste type filtering** based on what each point accepts
- **Capacity tracking** to optimize collection routes
- **Google Maps integration** for navigation
- **Multiple points per colony** for efficient collection

---

## 🏠 For Users

### **Contributing to Collection**

1. **Classify waste** using the camera feature
2. **Your waste contributes** to colony totals automatically
3. **Help colonies reach thresholds** for collection
4. **Track impact** in your dashboard statistics

### **Viewing Collection Points**

1. **Go to Maps page**
2. **Click "Collection Points" tab**
3. **See all nearby collection points**
4. **Get directions** to drop off waste directly

---

## 🔧 Technical Details

### **Database Triggers**

- Automatic colony waste total updates when users classify waste
- Real-time threshold detection
- Waste category breakdown tracking

### **API Endpoints**

- `GET /api/collection-points/` - All collection points
- `GET /api/collection-points/colony/{id}` - Points for specific colony
- `GET /api/collector/ready-colonies` - Colonies ready for collection

### **Map Integration**

- Leaflet maps with OpenStreetMap tiles
- Custom markers for different waste types
- Interactive popups with full details
- Google Maps directions integration

---

## 🎯 System Flow

```
User Classifies Waste
        ↓
Colony Totals Update (Automatic)
        ↓
Threshold Reached?
        ↓
Appears in Collector "Find Pickups"
        ↓
Collector Views Collection Points
        ↓
Collector Schedules Pickup
        ↓
Collection Completed
```

The system ensures efficient waste collection by matching collectors with colonies that have sufficient waste quantities and providing exact collection point locations for optimal route planning.
