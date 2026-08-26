# PRD — RealSense Dataset Collector Backend

**Version:** 1.0
**Backend:** Python + Flask
**Camera SDK:** Intel RealSense SDK / `pyrealsense2`
**Image Processing:** OpenCV
**Numerical Processing:** NumPy
**Communication:** REST API + WebSocket
**Storage:** Local Filesystem
**Environment:** Fully Offline / Local Machine
**Frontend:** Vue.js

---

# 1. Product Overview

RealSense Dataset Collector Backend adalah aplikasi Python lokal yang bertanggung jawab menghubungkan frontend Vue.js dengan kamera Intel RealSense.

Backend menjadi pusat pengelolaan:

* koneksi kamera;
* RGB stream;
* depth stream;
* camera configuration;
* capture operation;
* burst capture;
* continuous capture;
* RGB image saving;
* depth data saving;
* RGB-depth synchronization;
* dataset management;
* label management;
* storage management;
* metadata;
* capture statistics;
* WebSocket realtime events.

Backend berjalan sepenuhnya pada komputer yang terhubung dengan kamera.

Tidak diperlukan koneksi internet.

---

# 2. System Architecture

Arsitektur utama:

```text
                    Intel RealSense
                           │
                          USB
                           │
                           ▼
                  ┌─────────────────┐
                  │ Camera Manager  │
                  │  pyrealsense2   │
                  └────────┬────────┘
                           │
                     Frame Pipeline
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
          RGB Frame              Depth Frame
                │                     │
                └──────────┬──────────┘
                           ▼
                    Capture Manager
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
            PNG Writer            NPY Writer
                │                     │
                └──────────┬──────────┘
                           ▼
                    Dataset Manager
                           │
                           ▼
                    Local Filesystem


Frontend Vue.js
       │
       ├──────── REST API ────────► Flask
       │
       └────── WebSocket ─────────► Flask
```

---

# 3. Backend Responsibilities

Backend bertanggung jawab terhadap seluruh operasi hardware dan filesystem.

Frontend hanya bertanggung jawab terhadap UI.

### Backend harus:

* mengakses RealSense;
* mengontrol stream;
* mengambil frame;
* melakukan synchronization;
* menyimpan file;
* membuat folder;
* membuat filename;
* membaca storage;
* menjaga dataset state;
* mengirim realtime event.

### Backend tidak bertanggung jawab terhadap:

* rendering UI;
* layout;
* styling;
* frontend routing;
* frontend state management.

---

# 4. Core Backend Components

Backend disarankan memiliki struktur:

```text
backend/
│
├── app.py
├── config.py
├── requirements.txt
│
├── camera/
│   ├── camera_manager.py
│   ├── frame_manager.py
│   ├── camera_settings.py
│   └── depth_manager.py
│
├── capture/
│   ├── capture_manager.py
│   ├── capture_worker.py
│   └── capture_result.py
│
├── dataset/
│   ├── dataset_manager.py
│   ├── label_manager.py
│   ├── metadata_manager.py
│   └── statistics.py
│
├── storage/
│   ├── storage_manager.py
│   └── file_manager.py
│
├── api/
│   ├── camera_routes.py
│   ├── capture_routes.py
│   ├── dataset_routes.py
│   └── storage_routes.py
│
├── websocket/
│   └── events.py
│
└── data/
    └── app_config.json
```

---

# 5. Camera Manager

Camera Manager merupakan komponen utama yang berkomunikasi dengan Intel RealSense.

Library utama:

```text
pyrealsense2
```

Responsibilities:

* detect camera;
* connect camera;
* disconnect camera;
* start pipeline;
* stop pipeline;
* configure RGB stream;
* configure depth stream;
* retrieve frames;
* expose camera information;
* handle camera errors.

---

# 6. Camera Connection

Backend harus mendeteksi apakah Intel RealSense tersedia.

Possible states:

```text
DISCONNECTED
CONNECTING
CONNECTED
ERROR
RECONNECTING
```

Contoh response:

```json
{
  "status": "connected",
  "device": {
    "name": "Intel RealSense",
    "serial_number": "XXXXXXXX",
    "firmware": "X.X.X"
  }
}
```

Serial number hanya digunakan secara internal dan tidak perlu ditampilkan penuh pada UI kecuali diperlukan.

---

# 7. Automatic Camera Lifecycle

Ketika backend dijalankan:

```text
Backend Start
     │
     ▼
Detect RealSense
     │
     ├── Found
     │     │
     │     ▼
     │   Initialize
     │     │
     │     ▼
     │   Start Stream
     │
     └── Not Found
           │
           ▼
       Wait / Retry
```

Backend tidak boleh crash hanya karena kamera belum terhubung.

---

# 8. RGB Stream

Backend harus menyediakan RGB frame.

Default:

```text
Resolution: 640 × 480
FPS: 30
Format: BGR8
```

Namun konfigurasi harus dapat disesuaikan berdasarkan capability kamera.

Backend harus memvalidasi apakah konfigurasi yang dipilih didukung oleh device.

---

# 9. Depth Stream

Backend harus menyediakan depth frame.

Default:

```text
Resolution: 640 × 480
FPS: 30
Format: Z16
```

Depth frame harus tetap dalam format numeric sehingga dapat disimpan tanpa kehilangan precision.

---

# 10. RGB-Depth Synchronization

Ini merupakan requirement penting.

Backend harus memastikan RGB dan depth yang disimpan berasal dari frame yang sama atau pasangan frame yang valid.

Pipeline:

```text
wait_for_frames()
       │
       ▼
get_color_frame()
       │
       ├────────► RGB
       │
       └────────► Depth
```

Backend harus menggunakan frame set dari RealSense, bukan mengambil RGB dan depth secara terpisah melalui dua proses independen.

---

# 11. Frame Processing

Frame pipeline harus berjalan secara asynchronous terhadap Flask request.

Jangan menggunakan pola:

```text
HTTP Request
    ↓
Camera Capture
    ↓
HTTP Response
```

untuk setiap frame.

Gunakan:

```text
Camera Worker
     │
     ▼
Frame Buffer
     │
     ├── Preview
     └── Capture
```

Dengan demikian preview tetap realtime dan Flask tetap responsive.

---

# 12. Frame Buffer

Backend harus memiliki buffer frame terbaru.

Minimal:

```text
latest_rgb_frame
latest_depth_frame
latest_frame_timestamp
```

Frame buffer digunakan untuk:

* preview;
* depth information;
* capture;
* monitoring.

Backend tidak perlu menyimpan semua frame realtime ke memory.

Hanya frame terbaru yang diperlukan untuk preview.

---

# 13. Preview Streaming

Frontend membutuhkan RGB dan depth preview.

Backend dapat menggunakan WebSocket atau MJPEG/local streaming.

Recommended:

```text
Camera Worker
      │
      ▼
WebSocket
      │
      ▼
Vue.js
```

Untuk setiap preview event:

```json
{
  "event": "camera.frame",
  "rgb": "...",
  "depth": "...",
  "timestamp": 123456789
}
```

Implementasi encoding frame harus memperhatikan bandwidth dan CPU.

Preview tidak harus memiliki kualitas/resolusi yang sama dengan file dataset.

**Preview dan dataset capture harus dipisahkan.**

---

# 14. Capture Manager

Capture Manager bertanggung jawab terhadap seluruh operasi capture.

Supported modes:

```text
SINGLE
BURST
CONTINUOUS
```

Input:

```json
{
  "mode": "burst",
  "count": 10,
  "interval_ms": 200,
  "dataset": "rice_disease",
  "label": "brownspot"
}
```

---

# 15. Single Capture

Single capture:

```text
CAPTURE
   │
   ▼
Get synchronized frame
   │
   ├── RGB
   └── Depth
   │
   ▼
Save
```

Output:

```text
000001.png
000001.npy
```

---

# 16. Burst Capture

Contoh:

```text
count = 10
interval = 200ms
```

Backend:

```text
Capture
 │
 ├── 000001
 ├── wait 200ms
 ├── 000002
 ├── wait 200ms
 ├── 000003
 ...
 └── 000010
```

Backend harus mengirim progress realtime:

```json
{
  "event": "capture.progress",
  "current": 7,
  "total": 10
}
```

---

# 17. Continuous Capture

Continuous capture berjalan sampai frontend mengirim stop.

```text
START
  │
  ▼
Capture
  │
  ▼
Capture
  │
  ▼
Capture
  │
  ▼
...
  │
  ▼
STOP
```

Backend harus menjaga agar hanya ada satu continuous capture aktif.

---

# 18. Capture State Machine

Backend harus memiliki state yang jelas:

```text
IDLE
 │
 ▼
STARTING
 │
 ▼
CAPTURING
 │
 ├── COMPLETED
 │
 ├── STOPPED
 │
 └── ERROR
```

Backend tidak boleh menerima capture baru ketika state:

```text
STARTING
CAPTURING
```

---

# 19. Capture Interval

Interval dikontrol backend, bukan frontend.

Frontend hanya mengirim:

```json
{
  "count": 10,
  "interval_ms": 200
}
```

Backend bertanggung jawab terhadap timing capture.

Hal ini penting agar timing tidak bergantung pada browser.

---

# 20. Dataset Storage Structure

Backend harus membuat struktur dataset secara otomatis.

Recommended:

```text
dataset_root/
│
└── rice_disease/
    │
    ├── brownspot/
    │   ├── rgb/
    │   │   ├── 000001.png
    │   │   └── 000002.png
    │   │
    │   └── depth/
    │       ├── 000001.npy
    │       └── 000002.npy
    │
    ├── bacterialblight/
    │   ├── rgb/
    │   └── depth/
    │
    └── leafsmut/
        ├── rgb/
        └── depth/
```

---

# 21. Automatic File Naming

Backend bertanggung jawab menentukan ID.

Format:

```text
000001
000002
000003
```

ID harus unik dalam dataset/label.

Backend harus mencari ID berikutnya dengan aman.

Tidak boleh terjadi:

```text
000127
000127
```

akibat race condition.

---

# 22. RGB Saving

RGB disimpan sebagai:

```text
PNG
```

Example:

```text
rgb/000001.png
```

Backend menggunakan OpenCV atau library image processing yang sesuai.

Dataset RGB harus menggunakan frame asli yang diperoleh dari camera pipeline.

---

# 23. Depth Saving

Depth disimpan sebagai:

```text
NumPy .npy
```

Example:

```text
depth/000001.npy
```

Backend menggunakan:

```python
numpy.save()
```

Depth harus mempertahankan dtype asli dari depth frame.

Jangan melakukan normalisasi atau konversi ke 8-bit sebelum menyimpan dataset.

---

# 24. Depth Scale

Backend harus mengambil depth scale dari RealSense device.

Contoh:

```text
depth_scale = 0.001
```

Metadata harus menyimpan nilai tersebut.

Dengan demikian user dapat mengkonversi:

```text
raw_depth × depth_scale = distance_in_meters
```

---

# 25. RGB-Depth Pairing

Setiap capture harus menghasilkan:

```text
000001.png
000001.npy
```

Backend harus memastikan kedua file berhasil disimpan sebelum capture dianggap sukses.

Result:

```json
{
  "id": "000001",
  "rgb": {
    "saved": true,
    "path": "rgb/000001.png"
  },
  "depth": {
    "saved": true,
    "path": "depth/000001.npy"
  },
  "paired": true
}
```

Jika salah satu gagal:

```json
{
  "paired": false
}
```

Backend harus melakukan cleanup terhadap file parsial jika diperlukan.

---

# 26. Metadata

Backend harus menyimpan metadata dataset.

Recommended:

```text
metadata.json
```

Contoh:

```json
{
  "capture_id": "000001",
  "dataset": "rice_disease",
  "label": "brownspot",
  "timestamp": "2026-08-26T18:00:00",
  "rgb": "rgb/000001.png",
  "depth": "depth/000001.npy",
  "rgb_resolution": [640, 480],
  "depth_resolution": [640, 480],
  "fps": 30,
  "depth_scale": 0.001
}
```

Metadata tidak boleh mengganggu proses capture utama.

---

# 27. Dataset Manager

Dataset Manager bertanggung jawab terhadap:

* create dataset;
* list dataset;
* create label;
* list label;
* validate dataset;
* calculate statistics.

API:

```text
GET    /api/datasets
POST   /api/datasets
GET    /api/datasets/:id
POST   /api/datasets/:id/labels
GET    /api/datasets/:id/statistics
```

---

# 28. Storage Manager

Storage Manager bertanggung jawab terhadap:

* current storage path;
* available disk space;
* dataset size;
* folder creation;
* file existence;
* storage validation.

API:

```text
GET /api/storage
POST /api/storage/path
```

Response:

```json
{
  "path": "D:/Datasets/RealSense",
  "total_bytes": 500000000000,
  "free_bytes": 350000000000,
  "dataset_bytes": 1240000000
}
```

---

# 29. Storage Validation

Sebelum capture:

```text
Validate Storage
       │
       ├── Path exists?
       ├── Writable?
       ├── Enough space?
       └── Dataset folder available?
```

Jika gagal:

```json
{
  "can_capture": false,
  "reason": "insufficient_storage"
}
```

---

# 30. Low Storage Protection

Backend harus memiliki minimum free storage threshold.

Contoh:

```text
Minimum free space:
5 GB
```

Jika:

```text
free < threshold
```

backend harus menolak capture baru dan mengirim:

```text
storage.low
```

---

# 31. Delete Capture

API:

```text
DELETE /api/captures/:capture_id
```

Backend harus menghapus:

```text
000127.png
000127.npy
```

dan metadata terkait.

Delete harus bersifat atomic semaksimal mungkin.

---

# 32. Retake Capture

Retake harus memiliki semantics yang jelas.

Recommended flow:

```text
Previous Capture
       │
       ▼
Retake
       │
       ▼
New Capture
       │
       ▼
Replace Previous
```

Backend harus memastikan tidak ada dua capture menggunakan ID yang sama secara tidak sengaja.

---

# 33. Camera Settings API

Backend menyediakan:

```text
GET  /api/camera/settings
POST /api/camera/settings
```

Settings minimal:

```json
{
  "rgb_resolution": [640, 480],
  "depth_resolution": [640, 480],
  "fps": 30,
  "exposure": "auto",
  "white_balance": "auto"
}
```

Backend harus memvalidasi settings terhadap capability camera.

---

# 34. Camera Capability

Backend harus dapat mengetahui mode yang didukung kamera.

Contoh:

```json
{
  "rgb_resolutions": [
    [640, 480],
    [1280, 720]
  ],
  "depth_resolutions": [
    [640, 480],
    [1280, 720]
  ],
  "fps": [15, 30, 60]
}
```

Frontend menggunakan informasi ini untuk membuat dropdown.

Jangan hardcode seluruh capability kamera di frontend.

---

# 35. Depth Information API

Backend harus menyediakan informasi depth berdasarkan koordinat.

Request:

```text
GET /api/depth?x=321&y=241
```

Response:

```json
{
  "x": 321,
  "y": 241,
  "depth_raw": 840,
  "depth_scale": 0.001,
  "distance_m": 0.84,
  "valid": true
}
```

Backend melakukan kalkulasi distance.

Frontend hanya menampilkan hasilnya.

---

# 36. Dataset Statistics

Backend harus menghitung:

```text
total captures
capture count per label
RGB count
Depth count
paired count
dataset size
```

Contoh:

```json
{
  "total": 378,
  "labels": {
    "brownspot": 127,
    "bacterialblight": 132,
    "leafsmut": 119
  },
  "paired": 378
}
```

---

# 37. WebSocket Events

Backend harus menyediakan realtime event channel.

Minimal events:

```text
camera.status
camera.frame
camera.depth
capture.started
capture.progress
capture.completed
capture.failed
storage.updated
dataset.updated
camera.settings.changed
error
```

---

# 38. Camera Status Event

Example:

```json
{
  "event": "camera.status",
  "status": "connected"
}
```

Disconnect:

```json
{
  "event": "camera.status",
  "status": "disconnected"
}
```

---

# 39. Capture Progress Event

Example:

```json
{
  "event": "capture.progress",
  "capture_id": "000127",
  "current": 7,
  "total": 10,
  "status": "capturing"
}
```

---

# 40. Capture Completed Event

Example:

```json
{
  "event": "capture.completed",
  "capture_id": "000127",
  "rgb_saved": true,
  "depth_saved": true,
  "paired": true
}
```

---

# 41. Error Handling

Backend tidak boleh crash karena error hardware biasa.

Error categories:

```text
CAMERA_NOT_FOUND
CAMERA_DISCONNECTED
CAMERA_CONFIGURATION_ERROR
RGB_FRAME_ERROR
DEPTH_FRAME_ERROR
CAPTURE_ERROR
STORAGE_ERROR
INSUFFICIENT_STORAGE
INVALID_DATASET
INVALID_LABEL
INVALID_CAPTURE_CONFIGURATION
WEBSOCKET_ERROR
```

Response standard:

```json
{
  "success": false,
  "error": {
    "code": "CAMERA_NOT_FOUND",
    "message": "Intel RealSense camera was not detected."
  }
}
```

---

# 42. REST API Contract

Minimal endpoint:

## Camera

```text
GET  /api/camera/status
GET  /api/camera/info
GET  /api/camera/capabilities
GET  /api/camera/settings
POST /api/camera/settings
POST /api/camera/connect
POST /api/camera/disconnect
```

## Capture

```text
POST /api/capture
POST /api/capture/start
POST /api/capture/stop
GET  /api/capture/status
GET  /api/captures/latest
DELETE /api/captures/:id
POST /api/captures/:id/retake
```

## Dataset

```text
GET  /api/datasets
POST /api/datasets
GET  /api/datasets/:id
GET  /api/datasets/:id/labels
POST /api/datasets/:id/labels
GET  /api/datasets/:id/statistics
```

## Storage

```text
GET  /api/storage
POST /api/storage/path
```

## Depth

```text
GET /api/depth?x={x}&y={y}
```

---

# 43. API Response Standard

Successful response:

```json
{
  "success": true,
  "data": {}
}
```

Failed response:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

Frontend harus dapat menggunakan format ini secara konsisten.

---

# 44. Concurrency Requirements

Backend harus aman terhadap request bersamaan.

Contoh:

```text
User clicks Capture
       │
       ▼
Capture running
       │
User clicks Capture again
       │
       ▼
Backend rejects request
```

Response:

```json
{
  "success": false,
  "error": {
    "code": "CAPTURE_IN_PROGRESS",
    "message": "Another capture operation is currently running."
  }
}
```

Hanya satu capture operation yang boleh aktif.

---

# 45. Threading / Background Worker

Capture dan camera loop tidak boleh blocking Flask.

Recommended architecture:

```text
Flask Main Thread
       │
       ├── REST API
       │
       └── WebSocket
       
Camera Worker
       │
       └── RealSense pipeline

Capture Worker
       │
       └── Dataset writing
```

Gunakan thread-safe state atau queue untuk komunikasi antar worker.

---

# 46. Thread Safety

Shared state seperti:

```text
camera_status
latest_frame
capture_state
capture_progress
current_dataset
current_label
```

harus aman ketika diakses oleh:

* Flask;
* WebSocket;
* Camera Worker;
* Capture Worker.

Gunakan mekanisme synchronization yang sesuai seperti:

```text
threading.Lock
queue.Queue
Event
```

jika diperlukan.

---

# 47. Offline Requirement

Backend tidak boleh membutuhkan internet.

Semua dependency harus tersedia secara lokal:

```text
Flask
Flask-SocketIO
pyrealsense2
numpy
opencv-python
```

Backend harus dapat dijalankan:

```bash
python app.py
```

tanpa koneksi internet setelah dependencies terinstall.

---

# 48. Configuration

Backend menggunakan local configuration.

Contoh:

```text
config/
└── config.json
```

Isi:

```json
{
  "host": "127.0.0.1",
  "port": 5000,
  "storage_path": "D:/Datasets/RealSense",
  "minimum_free_space_gb": 5
}
```

Jangan menyimpan konfigurasi sensitif karena aplikasi bersifat lokal.

---

# 49. Startup Flow

Saat backend dijalankan:

```text
Start Flask
     │
     ▼
Load Configuration
     │
     ▼
Initialize Storage
     │
     ▼
Initialize Camera Manager
     │
     ▼
Detect Camera
     │
     ├── Found → Start Pipeline
     │
     └── Not Found → Wait
     │
     ▼
Start WebSocket
     │
     ▼
Backend Ready
```

---

# 50. Graceful Shutdown

Ketika backend dihentikan:

```text
Stop Capture
      │
      ▼
Stop Camera Worker
      │
      ▼
Stop RealSense Pipeline
      │
      ▼
Close WebSocket
      │
      ▼
Shutdown Flask
```

Tidak boleh meninggalkan camera pipeline dalam kondisi aktif.

---

# 51. Data Integrity

Backend harus memprioritaskan integritas dataset.

Sebelum menyatakan capture berhasil:

```text
RGB saved?
      │
      ▼
Depth saved?
      │
      ▼
Files exist?
      │
      ▼
Metadata updated?
      │
      ▼
Pair valid?
      │
      ▼
CAPTURE SUCCESS
```

Jika salah satu tahap gagal, capture dianggap gagal.

---

# 52. Dataset Validation

Backend menyediakan validasi dataset.

Contoh masalah:

```text
Missing RGB
Missing Depth
Unpaired files
Corrupted PNG
Invalid NPY
Duplicate ID
```

Output:

```json
{
  "valid": false,
  "issues": [
    {
      "id": "000127",
      "issue": "missing_depth"
    }
  ]
}
```

---

# 53. Performance Requirements

Backend harus memprioritaskan:

1. Camera stability
2. Frame synchronization
3. Dataset integrity
4. Capture timing
5. UI responsiveness

Preview tidak boleh mengganggu proses penyimpanan dataset.

Jika diperlukan, preview dapat menggunakan resolusi/quality lebih rendah dibandingkan dataset.

---

# 54. USB / Camera Performance

Backend harus menggunakan RealSense SDK secara langsung melalui USB.

Tidak boleh melakukan:

```text
RealSense → browser → Flask
```

Gunakan:

```text
RealSense → pyrealsense2 → Camera Worker
```

Dengan demikian USB bandwidth digunakan langsung oleh camera pipeline.

Backend harus mendeteksi jika konfigurasi stream tidak didukung oleh koneksi USB atau device.

---

# 55. Security

Karena aplikasi offline dan hanya berjalan pada local machine:

* bind default ke `127.0.0.1`;
* jangan expose Flask ke public network secara default;
* tidak membutuhkan authentication;
* tidak membutuhkan HTTPS untuk localhost;
* jangan mengizinkan arbitrary filesystem access melalui API.

Storage path harus divalidasi oleh backend.

---

# 56. Logging

Backend harus memiliki logging.

Minimal:

```text
INFO
WARNING
ERROR
```

Contoh:

```text
[INFO] RealSense connected
[INFO] Stream started
[INFO] Capture started: count=10
[INFO] Saved capture 000127
[WARNING] Storage below threshold
[ERROR] Depth frame unavailable
```

Log tidak boleh menyimpan data gambar atau depth secara langsung.

---

# 57. Testing Requirements

Backend harus memiliki test untuk:

### Camera

* camera detection;
* connect;
* disconnect;
* stream configuration.

### Capture

* single capture;
* burst capture;
* continuous capture;
* stop capture;
* invalid capture;
* concurrent capture.

### Dataset

* create dataset;
* create label;
* filename generation;
* RGB-depth pairing;
* delete;
* retake.

### Storage

* valid path;
* invalid path;
* insufficient storage;
* write permission.

### API

* success response;
* error response;
* invalid request.

---

# 58. Mock Camera Mode

Backend sebaiknya menyediakan:

```text
MOCK_CAMERA=true
```

Mode ini memungkinkan frontend dikembangkan tanpa kamera fisik.

Mock mode dapat menggunakan:

```text
mock_rgb.png
mock_depth.npy
```

Dengan demikian developer dapat menjalankan:

```text
Vue.js
   │
   ▼
Flask
   │
   ▼
Mock Camera
```

tanpa Intel RealSense.

Ini sangat disarankan untuk development dan automated testing.

---

# 59. Definition of Done

Backend dianggap selesai apabila:

* [ ] RealSense dapat dideteksi.
* [ ] Camera dapat connect/disconnect.
* [ ] RGB stream dapat diakses.
* [ ] Depth stream dapat diakses.
* [ ] RGB dan depth synchronized.
* [ ] Camera settings dapat diubah.
* [ ] Camera capabilities dapat diperoleh.
* [ ] Single capture bekerja.
* [ ] Burst capture bekerja.
* [ ] Continuous capture bekerja.
* [ ] Capture interval bekerja.
* [ ] Capture progress dikirim realtime.
* [ ] RGB disimpan sebagai PNG.
* [ ] Depth disimpan sebagai NPY.
* [ ] RGB-depth pairing terjamin.
* [ ] Automatic filename bekerja.
* [ ] Dataset dan label management bekerja.
* [ ] Dataset statistics tersedia.
* [ ] Storage path dapat dikonfigurasi.
* [ ] Storage monitoring tersedia.
* [ ] Low-storage protection tersedia.
* [ ] Delete capture bekerja.
* [ ] Retake capture bekerja.
* [ ] Metadata tersimpan.
* [ ] Depth information tersedia.
* [ ] WebSocket bekerja.
* [ ] REST API bekerja.
* [ ] Error handling tersedia.
* [ ] Logging tersedia.
* [ ] Graceful shutdown tersedia.
* [ ] Mock camera tersedia.
* [ ] Backend dapat berjalan sepenuhnya offline.

---

# 60. End-to-End Application Flow

Setelah frontend dan backend digabungkan, workflow lengkap harus menjadi:

```text
                    USER
                     │
                     ▼
              Vue.js Dashboard
                     │
          ┌──────────┴──────────┐
          │                     │
       REST API             WebSocket
          │                     │
          └──────────┬──────────┘
                     ▼
                Flask Backend
                     │
              Camera Manager
                     │
                     ▼
              Intel RealSense
                     │
             ┌───────┴───────┐
             ▼               ▼
           RGB             Depth
             │               │
             └───────┬───────┘
                     ▼
              Capture Manager
                     │
              ┌──────┴──────┐
              ▼             ▼
             PNG           NPY
              │             │
              └──────┬──────┘
                     ▼
               Dataset Manager
                     │
                     ▼
              Local Filesystem
```

---

# 61. Final Product Principle

Backend harus dirancang dengan prinsip:

> **RealSense is the source of truth for camera data. Flask is the control layer. The filesystem is the source of truth for dataset files. Vue.js is the presentation layer.**

Jangan memindahkan pekerjaan hardware atau dataset processing ke browser.

Pembagian tanggung jawab final:

```text
┌────────────────────────────────────────────┐
│                  VUE.JS                    │
│                                            │
│ UI / UX                                    │
│ Dashboard                                  │
│ Settings                                   │
│ Capture Controls                           │
│ Preview                                    │
│ Statistics                                 │
└─────────────────────┬──────────────────────┘
                      │
                REST / WebSocket
                      │
┌─────────────────────▼──────────────────────┐
│                  FLASK                     │
│                                            │
│ API / State / Orchestration                │
│                                            │
│   ┌────────────────────────────────────┐   │
│   │ Camera Manager                     │   │
│   │ pyrealsense2                       │   │
│   └────────────────┬───────────────────┘   │
│                    │                       │
│   ┌────────────────▼───────────────────┐   │
│   │ Capture Manager                    │   │
│   └────────────────┬───────────────────┘   │
│                    │                       │
│   ┌────────────────▼───────────────────┐   │
│   │ Dataset / Storage Manager           │   │
│   └────────────────────────────────────┘   │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
              Intel RealSense
                      │
                      ▼
               Local Dataset
```

Dengan kontrak ini, **frontend PRD dan backend PRD dapat dikembangkan secara terpisah tetapi tetap dapat disatukan menjadi satu aplikasi utuh**.
