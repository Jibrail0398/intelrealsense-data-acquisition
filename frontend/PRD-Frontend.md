# Product Requirements Document (PRD)

## RealSense Dataset Collector — Frontend

**Version:** 1.0
**Platform:** Web-based Local Application
**Frontend:** Vue.js
**Backend:** Flask — out of scope for this document
**Camera:** Intel RealSense
**Environment:** Offline / Local Machine

---

# 1. Product Overview

RealSense Dataset Collector adalah aplikasi lokal untuk membantu pengguna mengambil dataset RGB dan depth menggunakan kamera Intel RealSense.

Frontend bertanggung jawab menyediakan antarmuka untuk:

* melihat stream RGB dan depth secara realtime;
* mengatur konfigurasi pengambilan dataset;
* menentukan lokasi penyimpanan;
* menentukan dataset dan label;
* melakukan single/burst/continuous capture;
* melihat status kamera dan proses capture;
* memonitor jumlah dataset;
* melakukan retake atau menghapus hasil capture;
* mengatur parameter kamera;
* melihat informasi depth;
* mengelola session dataset.

Frontend tidak bertanggung jawab terhadap komunikasi langsung dengan kamera.

Semua komunikasi kamera dan filesystem dilakukan oleh backend Flask melalui API/WebSocket.

---

# 2. Product Goals

Frontend harus:

1. Mempermudah proses pengambilan dataset dibandingkan menggunakan Intel RealSense Viewer.
2. Memungkinkan pengguna mengambil RGB dan depth secara bersamaan.
3. Memberikan feedback realtime mengenai kondisi kamera dan proses capture.
4. Meminimalkan pekerjaan manual dalam pengelolaan dataset.
5. Menyediakan UI yang sederhana untuk proses capture berulang dalam jumlah besar.
6. Tetap dapat digunakan sepenuhnya secara offline.
7. Memiliki arsitektur frontend yang siap terhubung dengan Flask API/WebSocket.

---

# 3. Target User

Target utama adalah:

* developer computer vision;
* mahasiswa/peneliti;
* machine learning engineer;
* researcher;
* pengguna yang membutuhkan dataset RGB-D dari Intel RealSense.

User diasumsikan memiliki pengetahuan dasar mengenai kamera dan dataset, tetapi tidak seharusnya membutuhkan pengetahuan teknis mengenai filesystem atau API untuk melakukan capture.

---

# 4. Functional Requirements

Total terdapat **18 fitur utama**.

---

## FR-01 — Storage Path

### Description

Pengguna dapat menentukan lokasi penyimpanan dataset.

### UI

Settings atau Dataset Configuration menyediakan:

```text
Storage Path

[ D:/Datasets/RealSense             ] [ Browse ]

Storage Status
Available: 350 GB
Used by Dataset: 1.24 GB
```

### Requirements

* Menampilkan path aktif.
* Menyediakan tombol Browse.
* Menampilkan status storage.
* Menampilkan warning ketika storage hampir penuh.
* Path tidak boleh diubah ketika capture sedang berlangsung.
* Frontend menerima informasi path dari backend.
* Frontend tidak melakukan akses filesystem secara langsung.

---

# FR-02 — Capture Button

### Description

Tombol utama untuk mengambil dataset.

### UI

```text
[ 📷 CAPTURE ]
```

### Requirements

* Tombol harus menjadi primary action pada halaman utama.
* Capture hanya dapat dilakukan ketika kamera connected.
* Tombol disabled ketika kamera disconnected.
* Tombol disabled selama konfigurasi belum valid.
* Saat capture berlangsung, tombol berubah menjadi state progress.
* Setelah capture selesai, frontend menampilkan hasil capture terakhir.

### States

```text
Ready
Capturing
Success
Error
Disabled
```

---

# FR-03 — Capture Count

### Description

Pengguna menentukan berapa banyak frame yang diambil dalam satu operasi capture.

### UI

```text
Number of Captures

[ 10 ]
```

### Requirements

* Mendukung minimal 1 capture.
* Mendukung input number.
* Menampilkan nilai yang sedang aktif.
* Validasi input.
* Tidak dapat diubah ketika capture sedang berjalan.

Contoh:

```text
Count: 10

[ CAPTURE ]

→ 10 RGB images
→ 10 Depth files
```

---

# FR-04 — RGB Preview

### Description

Menampilkan live RGB stream dari kamera.

### UI

```text
┌─────────────────────────┐
│                         │
│      RGB PREVIEW        │
│                         │
└─────────────────────────┘

Skema Warna: Pendekatan dominan monokrom (background netral keabu-abuan) dengan panel putih, dipadukan aksen biru untuk aksi utama dan merah untuk peringatan kritis atau penghapusan.

Tata Letak Geometris: Menggunakan struktur berbasis Grid yang memisahkan layar menjadi dua zona utama: area pratinjau visual yang mendominasi dan panel samping untuk kontrol parameter.

Estetika Elemen: Formulir dan tombol menggunakan sudut yang membulat halus (rounded-md), ruang kosong yang luas (whitespace), dan menghindari penggunaan bayangan atau gradasi yang berlebihan.

```

### Requirements

* Menampilkan stream realtime.
* Menampilkan resolution.
* Menampilkan FPS.
* Menampilkan loading state ketika stream belum tersedia.
* Menampilkan error state ketika RGB stream gagal.
* Tidak menampilkan gambar stale tanpa indikasi.

Informasi:

```text
RGB
640 × 480
30 FPS
```

---

# FR-05 — Depth Preview

### Description

Menampilkan live depth stream.

### UI

```text
┌─────────────────────────┐
│                         │
│     DEPTH PREVIEW       │
│                         │
└─────────────────────────┘
```

### Requirements

* Menampilkan depth stream realtime.
* Menampilkan resolution.
* Menampilkan FPS.
* Menampilkan status depth stream.
* Menampilkan error jika depth stream tidak tersedia.
* Menyediakan indikator apakah depth frame valid.

---

# FR-06 — Capture Mode

### Description

Pengguna dapat memilih metode capture.

### Modes

```text
Single
Burst
Continuous
```

### UI

```text
Capture Mode

[ Burst ▼ ]
```

### Behavior

#### Single

Satu operasi capture menghasilkan satu frame.

#### Burst

Mengambil sejumlah frame sesuai Capture Count.

#### Continuous

Capture berjalan terus sampai user menekan Stop.

### Continuous UI

```text
[ START CAPTURE ]

Capturing...

Frames: 127

[ STOP ]
```

---

# FR-07 — Capture Interval

### Description

Menentukan interval antar capture.

### UI

```text
Capture Interval

[ 200 ] ms
```

### Requirements

* Hanya relevan untuk Burst dan Continuous mode.
* Tidak relevan untuk Single mode.
* Menampilkan unit secara eksplisit.
* Tidak dapat diubah saat capture berlangsung.
* Nilai harus divalidasi.

Contoh:

```text
Count: 10
Interval: 500 ms
```

menghasilkan 10 capture dengan interval 500 ms.

---

# FR-08 — Dataset / Label Management

### Description

Pengguna dapat menentukan dataset dan label tanpa mengelola folder secara manual.

### UI

```text
Dataset

[ Rice Disease ▼ ]

Label

[ Brownspot ▼ ]

[ + New Label ]
```

### Requirements

* Dataset dapat dipilih.
* Label dapat dipilih.
* User dapat membuat label baru.
* Label aktif ditampilkan secara jelas.
* Perubahan label tidak boleh terjadi ketika capture sedang berlangsung.
* Frontend harus mempertahankan selected dataset dan label sebagai application state.

Contoh:

```text
Rice Disease
├── Brownspot
├── Bacterialblight
└── Leafsmut
```

---

# FR-09 — RGB + Depth Pairing

### Description

Frontend harus memahami bahwa satu capture menghasilkan pasangan RGB dan depth.

### Expected Dataset

```text
000001.png
000001.npy

000002.png
000002.npy
```

### Requirements

Frontend harus:

* menampilkan jumlah RGB dan depth yang berhasil;
* mendeteksi jika backend melaporkan pasangan tidak lengkap;
* menampilkan warning jika pairing gagal;
* tidak menganggap capture sukses jika pasangan data tidak lengkap.

UI:

```text
Last Capture

RGB    ✓
Depth  ✓
Pair   ✓
```

Error:

```text
RGB    ✓
Depth  ✕
Pair   ✕
```

---

# FR-10 — Automatic File Naming

### Description

Frontend tidak meminta user menentukan nama file setiap kali capture.

### Expected naming

```text
000001
000002
000003
```

### Requirements

Frontend hanya menampilkan informasi filename yang diberikan backend.

Contoh:

```text
Last Capture

RGB:
rgb/000127.png

Depth:
depth/000127.npy
```

Frontend tidak bertanggung jawab membuat filename secara fisik.

---

# FR-11 — Dataset Counter

### Description

Menampilkan jumlah dataset yang sudah dikumpulkan.

### UI

```text
Dataset Statistics

Brownspot          127
Bacterialblight    132
Leafsmut           119

Total              378
```

### Requirements

* Counter harus realtime.
* Dapat difilter berdasarkan label.
* Menampilkan total dataset.
* Counter diperbarui setelah capture berhasil.
* Menampilkan loading state ketika statistics sedang diambil.

---

# FR-12 — Delete / Retake

### Description

Pengguna dapat menghapus hasil capture yang tidak valid.

### UI

```text
Last Capture

000127

[ RETAKE ]
[ DELETE ]
```

### Requirements

Delete harus meminta confirmation.

```text
Delete capture 000127?

[ Cancel ] [ Delete ]
```

Retake:

```text
[ RETAKE ]

→ previous capture marked for replacement
→ new capture
```

Frontend harus memberikan feedback sukses/gagal.

---

# FR-13 — Camera Settings

### Description

Frontend menyediakan interface konfigurasi kamera.

### Settings

Minimal:

```text
RGB Resolution
[ 640 × 480 ▼ ]

Depth Resolution
[ 640 × 480 ▼ ]

FPS
[ 30 ▼ ]

Exposure
[ Auto ▼ ]

White Balance
[ Auto ▼ ]
```

### Requirements

* Settings diperoleh dari backend.
* Hanya menampilkan opsi yang didukung kamera.
* Validasi configuration.
* Menampilkan warning jika perubahan membutuhkan restart stream.
* Tidak dapat mengubah konfigurasi ketika capture berlangsung.

---

# FR-14 — Depth Information

### Description

Menampilkan informasi depth secara realtime.

### UI

```text
Depth Information

Resolution : 640 × 480
FPS        : 30
Min Depth  : 0.21 m
Max Depth  : 3.42 m
```

Jika cursor diarahkan ke depth preview:

```text
X: 321
Y: 241

Distance:
0.84 m
```

### Requirements

* Menampilkan coordinate cursor.
* Menampilkan distance.
* Menampilkan depth stream status.
* Menampilkan unit secara jelas.
* Tidak menampilkan data jika pixel depth invalid.

---

# FR-15 — Capture Preview

### Description

Setelah capture selesai, user dapat melihat hasil terakhir.

### UI

```text
Last Capture

┌──────────────────────┐
│                      │
│      RGB IMAGE       │
│                      │
└──────────────────────┘

Capture ID: 000127

RGB      ✓
Depth    ✓
Pair     ✓

[ RETAKE ] [ DELETE ]
```

### Requirements

* Menampilkan capture terakhir.
* Menampilkan Capture ID.
* Menampilkan status RGB.
* Menampilkan status depth.
* Menampilkan timestamp jika tersedia.
* Menyediakan Retake dan Delete.

---

# FR-16 — Keyboard Shortcuts

### Description

Menyediakan shortcut untuk mempercepat proses dataset acquisition.

### Shortcuts

```text
SPACE
Capture

R
Retake

DELETE
Delete last capture

ESC
Cancel / Stop

S
Start / Stop continuous capture
```

### Requirements

* Shortcut hanya aktif ketika tidak sedang mengetik pada input.
* Shortcut harus memiliki visual indication.
* User dapat melihat daftar shortcut melalui Help/Keyboard Shortcuts.

Contoh:

```text
Keyboard Shortcuts

Space    Capture
R        Retake
S        Start/Stop
Esc      Stop
```

---

# FR-17 — Camera Status

### Description

Menampilkan kondisi kamera secara realtime.

### UI

```text
● Camera Connected

RGB   ✓
Depth ✓

640 × 480 @ 30 FPS
```

### States

```text
Connected
Connecting
Disconnected
Error
Reconnecting
```

### Requirements

* Status harus realtime.
* Jika kamera disconnect, capture otomatis disabled.
* UI harus memberikan informasi yang jelas.
* Tidak boleh menganggap kamera connected hanya karena backend aktif.

---

# FR-18 — Storage Monitoring

### Description

Menampilkan penggunaan storage.

### UI

```text
Storage

Used       120 GB
Available  350 GB

Dataset
1.24 GB

██████████░░░░░░
```

### Requirements

* Menampilkan available storage.
* Menampilkan dataset size.
* Menampilkan storage usage.
* Memberikan warning jika storage hampir penuh.
* Warning harus terlihat sebelum user melakukan capture.

Contoh:

```text
⚠ Low Storage

Only 4.2 GB remaining.
```

---

# 5. Main Dashboard

Semua fitur utama harus terintegrasi pada dashboard utama.

Recommended layout:

```text
┌───────────────────────────────────────────────────────────┐
│ RealSense Dataset Collector                    ⚙ Settings │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ● Camera Connected                                      │
│                                                           │
│  ┌────────────────────────┐  ┌────────────────────────┐  │
│  │                        │  │                        │  │
│  │         RGB            │  │        DEPTH           │  │
│  │                        │  │                        │  │
│  │                        │  │                        │  │
│  └────────────────────────┘  └────────────────────────┘  │
│                                                           │
│  640×480 • 30 FPS             640×480 • 30 FPS            │
│                                                           │
├───────────────────────────────────────────────────────────┤
│ Dataset       [ Rice Disease ▼ ]                          │
│ Label         [ Brownspot ▼ ]                             │
│                                                           │
│ Capture Mode  [ Burst ▼ ]                                 │
│ Count         [ 10 ]                                      │
│ Interval      [ 200 ms ]                                  │
│                                                           │
│                    [ 📷 CAPTURE ]                         │
│                                                           │
├───────────────────────────────────────────────────────────┤
│ Captured: 127        Storage: 1.24 GB                     │
│                                                           │
│ Last Capture: 000127   RGB ✓  Depth ✓  Pair ✓            │
│                                                           │
│                 [ RETAKE ] [ DELETE ]                     │
└───────────────────────────────────────────────────────────┘
```

---

# 6. Settings Page

Settings page harus menyediakan:

### Camera

* RGB resolution
* Depth resolution
* FPS
* Exposure
* White balance

### Storage

* Dataset storage path
* Storage information

### Capture

* Default capture mode
* Default count
* Default interval

### Keyboard

* Keyboard shortcuts

---

# 7. Dataset Page

Dataset page digunakan untuk melihat hasil dataset.

Contoh:

```text
Dataset: Rice Disease

┌──────────────────────────────────────────┐
│ Label          Count                     │
├──────────────────────────────────────────┤
│ Brownspot      127                       │
│ Bacterialblight 132                     │
│ Leafsmut       119                       │
└──────────────────────────────────────────┘
```

User dapat memilih label dan melihat capture.

---

# 8. Application States

Frontend harus memiliki state management yang jelas.

Minimal state:

```text
cameraStatus
rgbStreamStatus
depthStreamStatus

selectedDataset
selectedLabel

captureMode
captureCount
captureInterval

isCapturing
captureProgress

lastCapture

datasetStatistics

storageInfo

cameraSettings

depthInformation
```

---

# 9. Global Error Handling

Frontend harus memiliki error state untuk:

### Camera error

```text
Unable to connect to RealSense camera.
```

### Capture error

```text
Capture failed.
RGB frame could not be saved.
```

### Depth error

```text
Depth frame unavailable.
```

### Storage error

```text
Unable to save dataset.
Check storage path.
```

### Backend error

```text
Unable to communicate with local backend.
```

Error harus menggunakan notification/toast yang jelas dan tidak mengganggu workflow.

---

# 10. Loading States

Frontend tidak boleh menampilkan UI kosong ketika menunggu backend.

Gunakan loading state untuk:

* connecting camera;
* loading datasets;
* loading labels;
* loading statistics;
* changing camera settings;
* starting capture;
* deleting capture;
* loading storage information.

---

# 11. WebSocket Requirements

Frontend harus siap menerima realtime events dari backend.

Contoh event:

```text
camera.status
camera.frame
capture.started
capture.progress
capture.completed
capture.failed
storage.updated
dataset.updated
depth.updated
```

Contoh:

```json
{
  "event": "capture.progress",
  "current": 7,
  "total": 10
}
```

Frontend harus mengubah progress UI secara realtime.

---

# 12. API Abstraction

Frontend tidak boleh memanggil `fetch()` secara langsung dari setiap component.

Gunakan service layer:

```text
src/
├── services/
│   ├── cameraService
│   ├── captureService
│   ├── datasetService
│   └── storageService
```

Components hanya berinteraksi dengan service/store.

---

# 13. Recommended Frontend Architecture

```text
src/
│
├── components/
│   ├── camera/
│   │   ├── RGBPreview
│   │   ├── DepthPreview
│   │   ├── CameraStatus
│   │   └── DepthInformation
│   │
│   ├── capture/
│   │   ├── CaptureButton
│   │   ├── CaptureSettings
│   │   ├── CaptureProgress
│   │   └── LastCapture
│   │
│   ├── dataset/
│   │   ├── DatasetSelector
│   │   ├── LabelSelector
│   │   └── DatasetStatistics
│   │
│   └── storage/
│       ├── StoragePath
│       └── StorageMonitor
│
├── views/
│   ├── Dashboard
│   ├── Dataset
│   └── Settings
│
├── stores/
│   ├── cameraStore
│   ├── captureStore
│   ├── datasetStore
│   └── storageStore
│
├── services/
│   ├── api
│   ├── websocket
│   ├── cameraService
│   ├── captureService
│   ├── datasetService
│   └── storageService
│
└── types/
    ├── camera
    ├── capture
    ├── dataset
    └── storage
```

---

# 14. UX Principles

Frontend harus mengikuti prinsip:

### 1. Capture-first

Capture adalah aktivitas utama.

User tidak boleh harus melewati banyak halaman untuk mengambil dataset.

### 2. Minimal manual operation

Hindari:

* mengetik filename;
* memilih folder setiap capture;
* melakukan save manual;
* melakukan pairing RGB/depth manual.

### 3. Realtime feedback

User harus selalu mengetahui:

* kamera connected atau tidak;
* capture sedang berlangsung atau tidak;
* berapa frame sudah diambil;
* apakah RGB berhasil;
* apakah depth berhasil;
* apakah storage mencukupi.

### 4. Safe capture

Jangan mengizinkan capture ketika:

* kamera disconnected;
* storage tidak tersedia;
* dataset belum dipilih;
* label belum dipilih;
* konfigurasi kamera invalid.

---

# 15. Non-Functional Requirements

### Offline

Frontend harus dapat berjalan tanpa internet.

Tidak boleh bergantung pada:

* cloud API;
* external authentication;
* remote CDN;
* online database;
* external analytics.

Semua asset frontend harus tersedia secara lokal setelah aplikasi di-install.

### Performance

Dashboard harus tetap responsive ketika stream kamera aktif.

UI tidak boleh melakukan processing depth/image yang berat di browser jika processing tersebut dapat dilakukan oleh backend.

### Reliability

Frontend harus dapat menangani:

* camera disconnect;
* backend restart;
* WebSocket disconnect;
* capture failure;
* storage failure.

### Responsive

Desktop-first.

Target utama:

```text
1920 × 1080
1600 × 900
1366 × 768
```

Mobile responsiveness bukan prioritas utama.

---

# 16. Out of Scope

Untuk versi frontend ini, jangan implementasikan:

* komunikasi langsung dengan RealSense;
* `pyrealsense2`;
* image processing;
* depth processing;
* penyimpanan PNG;
* penyimpanan NPY;
* filesystem operation;
* camera driver;
* Flask implementation;
* database;
* authentication;
* cloud synchronization;
* annotation tool.

Frontend hanya menyediakan UI dan komunikasi abstraction terhadap backend.

---

# 17. Definition of Done

Frontend dianggap selesai apabila:

* [ ] Dashboard utama tersedia.
* [ ] RGB preview tersedia.
* [ ] Depth preview tersedia.
* [ ] Camera status tersedia.
* [ ] Storage path UI tersedia.
* [ ] Dataset selector tersedia.
* [ ] Label selector tersedia.
* [ ] Capture button tersedia.
* [ ] Capture count tersedia.
* [ ] Capture mode tersedia.
* [ ] Capture interval tersedia.
* [ ] Capture progress tersedia.
* [ ] RGB-depth pairing status tersedia.
* [ ] Automatic filename information tersedia.
* [ ] Dataset counter tersedia.
* [ ] Delete/Retake tersedia.
* [ ] Camera settings tersedia.
* [ ] Depth information tersedia.
* [ ] Capture preview tersedia.
* [ ] Keyboard shortcuts tersedia.
* [ ] Storage monitoring tersedia.
* [ ] Error handling tersedia.
* [ ] Loading states tersedia.
* [ ] WebSocket abstraction tersedia.
* [ ] API service abstraction tersedia.
* [ ] Frontend dapat berjalan tanpa internet.
* [ ] Frontend tidak memiliki dependency terhadap backend implementation detail.

---

# 18. Important Implementation Principle

AI coding assistant **jangan mengimplementasikan backend atau mengakses RealSense secara langsung pada tahap ini**.

Gunakan mock API / mock WebSocket ketika backend belum tersedia.

Frontend harus dirancang seolah-olah backend menyediakan:

```text
Camera Stream
Camera Status
Camera Settings
Capture Command
Capture Progress
Capture Result
Dataset Statistics
Storage Information
Depth Information
```

Dengan demikian frontend dapat dikembangkan dan diuji terlebih dahulu.

Setelah frontend selesai, Flask backend dapat dibuat mengikuti API contract yang dibutuhkan frontend.

---

# 19. Final Product Flow

Expected user flow:

```text
Open Application
       │
       ▼
Connect RealSense
       │
       ▼
Camera Status = Connected
       │
       ▼
RGB + Depth Preview
       │
       ▼
Select Storage Path
       │
       ▼
Select Dataset
       │
       ▼
Select Label
       │
       ▼
Configure Capture
       │
       ├── Mode
       ├── Count
       └── Interval
       │
       ▼
Press CAPTURE
       │
       ▼
Capture Progress
       │
       ▼
RGB + Depth Pair
       │
       ▼
Capture Result
       │
       ├── Keep
       ├── Retake
       └── Delete
       │
       ▼
Dataset Counter Updated
       │
       ▼
Ready for next capture
```

**Prioritas utama produk:** pengguna harus dapat melakukan siklus **`lihat kamera → pilih label → klik capture → lihat hasil → capture lagi`** dengan sesedikit mungkin interaksi manual.
