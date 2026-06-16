# BE2 File Dependency Analysis Report

## 📋 Current Architecture Status

**Analyzed Date**: August 7, 2025  
**Architecture Type**: WebSocket-Only  
**Main Entry Point**: `main.py` (181 lines)

## 🔗 Active File Dependencies (Currently Used)

### ✅ Core Files (IN USE)
```
main.py
├── services/database_service.py ✅
└── services/websocket_service.py ✅
    └── services/models_service.py ✅
        └── models/models.py ✅ (database operations for YOLO results)
            └── models/auth.py ✅ (Base class only)
```

### 📁 Folder Analysis

#### `/services/` - 6 files total
1. **✅ `database_service.py`** - USED by main.py, models.py
2. **✅ `websocket_service.py`** - USED by main.py 
3. **✅ `models_service.py`** - USED by websocket_service.py
4. **❌ `cctv_service.py`** - NOT USED (374 lines, IP camera functionality)
5. **❌ `video_service.py`** - NOT USED (301 lines, video upload processing)
6. **❌ `realtime_service.py`** - NOT USED (258 lines, alternative WebSocket impl)

#### `/models/` - 8 files total
1. **✅ `models.py`** - USED by models_service.py (YOLO results storage)
2. **✅ `auth.py`** - USED by models.py (Base class) + auth_controller.py
3. **❌ `admins.py`** - NOT USED (admin user management)
4. **❌ `attendance_logs.py`** - NOT USED (attendance tracking)
5. **❌ `devices.py`** - NOT USED (device management)
6. **❌ `notification_logs.py`** - NOT USED (notification system)
7. **❌ `settings.py`** - NOT USED (app settings)
8. **✅ `__init__.py`** - Standard Python package file

#### `/controller/` - 1 file total
1. **❌ `auth_controller.py`** - NOT USED (HTTP endpoints, has bugs)

#### `/schemas/` - 4 files total
1. **❌ `auth_schemas.py`** - NOT USED (Pydantic models for auth)
2. **❌ `faces_schemas.py`** - NOT USED (Face detection schemas)
3. **❌ `models_schemas.py`** - NOT USED (YOLO model schemas)
4. **❌ `video_schemas.py`** - NOT USED (Video processing schemas)

#### `/config/` - 3 files total
1. **❌ `db_helper.py`** - NOT USED (database configuration)
2. **❌ `mobiledb.py`** - NOT USED (mobile database config)
3. **❌ `settings.py`** - NOT USED (app settings)

## 🚨 Issues Found

### 1. **Dead Code (Unused Files)**
- **Total Unused**: 17 out of 22 files (77% unused)
- **Unused Lines**: Approximately 2,000+ lines of dead code
- **Impact**: Code bloat, maintenance overhead

### 2. **Import Errors in Models**
```python
# In models/devices.py, admins.py, etc.
from models.auth import Base  # ❌ Should be: from .auth import Base
```

### 3. **Controller Issues**
```python
# In auth_controller.py
async def sign_up_admin(websocket, msg: dict):
    password = msg.get("password")
    cek_user = await get_admin_by_username(username)  # ❌ 'username' not defined
```

### 4. **Schemas Not Connected**
- All Pydantic schemas exist but are never imported or used
- No FastAPI endpoints using these schemas

## 📊 Dependency Graph

### Current Active Chain
```
main.py (181 lines)
├── database_service.py (103 lines)
└── websocket_service.py (314 lines)
    └── models_service.py (162 lines)
        └── models.py (123 lines)
            └── auth.py (85 lines)
```

**Total Active Code**: ~968 lines  
**Total Project Code**: ~3,000+ lines  
**Efficiency**: ~32% of code is actually used

## 🎯 Recommendations

### Phase 1: Immediate Cleanup (High Priority)
```bash
# Remove unused files (saves ~2,000 lines)
DELETE:
├── controller/auth_controller.py
├── models/admins.py
├── models/attendance_logs.py
├── models/devices.py
├── models/notification_logs.py
├── models/settings.py
├── schemas/ (entire folder - 4 files)
├── services/cctv_service.py
├── services/video_service.py
├── services/realtime_service.py
└── config/ (entire folder - 3 files)
```

### Phase 2: Fix Import Issues
```python
# Fix relative imports in remaining model files
# models/auth.py is the only model file that should remain
```

### Phase 3: Code Architecture
```
Simplified Structure:
be2/app/
├── main.py ✅
├── services/
│   ├── database_service.py ✅
│   ├── websocket_service.py ✅
│   └── models_service.py ✅
├── models/
│   ├── auth.py ✅ (Base class only)
│   └── models.py ✅ (YOLO detection results)
└── yolo_models/ ✅
```

## 🔍 File Relationships Summary

### ✅ Connected Files (Keep)
1. **main.py** → database_service, websocket_service
2. **websocket_service.py** → models_service  
3. **models_service.py** → models.py
4. **models.py** → auth.py (Base class), database_service
5. **auth.py** → database_service

### ❌ Orphaned Files (Remove)
- All files in `/controller/`, `/schemas/`, `/config/`
- 5 out of 8 files in `/models/`
- 3 out of 6 files in `/services/`

## 📈 Expected Benefits After Cleanup

### Code Reduction
- **Lines of Code**: 3,000+ → ~1,000 (67% reduction)
- **Files**: 22 → 7 (68% reduction)  
- **Folders**: 5 → 3 (40% reduction)

### Performance Benefits
- Faster imports
- Reduced memory footprint
- Cleaner codebase
- Easier maintenance

### Architecture Benefits
- Single responsibility principle
- WebSocket-only focus
- No dead code confusion
- Clear dependency chain

## ⚠️ Files with Potential Future Use

If planning to add HTTP endpoints or additional features:

### Keep for Future HTTP API
- `schemas/` folder - for Pydantic models
- `controller/auth_controller.py` - fix bugs first

### Keep for Additional Features  
- `services/cctv_service.py` - for IP camera integration
- `services/video_service.py` - for video upload features
- Model files - for user management, attendance, etc.

## 🏁 Conclusion

**Current Status**: 77% of files are unused dead code  
**Recommendation**: Immediate cleanup to improve maintainability  
**Impact**: Reduced complexity, better performance, cleaner architecture

The WebSocket-only architecture only needs 7 core files out of 22 total files.
