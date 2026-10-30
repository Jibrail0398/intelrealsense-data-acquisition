# RealSense Collector

Aplikasi lokal untuk mengambil dataset gambar RGB-D secara massal dengan kamera **Intel RealSense**
(D415, D435, D435i, D455, dan seri D400 lainnya). Dibuat untuk pengumpulan data deteksi stunting:
setiap gambar langsung diberi nama sesuai kelasnya, disimpan dalam format yang dipilih, dan diletakkan
di folder yang sudah ditentukan.

- **Capture**: buat atau pilih projek, lihat preview RGB dan depth secara langsung, pilih kelas, lalu ambil gambar
  (tombol atau `Space`). Ada timer dan mode burst (beberapa gambar sekali tekan).
- **History**: riwayat semua pengambilan (nama gambar, kelas, projek, waktu), dengan filter waktu, projek, dan kelas.
- **Settings**: konfigurasi kamera lewat pyrealsense2 (resolusi, fps, align, semua opsi sensor seperti exposure,
  gain, laser power, white balance, visual preset, dan filter post-processing depth), aturan pengambilan
  (jumlah gambar per take, timer), serta daftar shortcut.

| Bagian   | Teknologi |
| -------- | --------- |
| Frontend | Vue 3, TypeScript, Vite, Tailwind CSS 4, shadcn-vue (reka-ui), Pinia, Vue Router |
| Backend  | FastAPI, SQLAlchemy 2, SQLite, pyrealsense2, OpenCV, NumPy |
| Realtime | Preview MJPEG lewat HTTP; status kamera dan progres capture lewat WebSocket |

---

## 1. Kebutuhan

| Kebutuhan | Versi | Keterangan |
| --------- | ----- | ---------- |
| Python | **3.12** (didukung 3.10 – 3.14) | dikelola dengan **pyenv**; versi tercatat di `backend/.python-version` |
| Node.js | **24 LTS** (atau 22.18+) | dikelola dengan **nvm**; versi tercatat di `.nvmrc` |
| npm | 10+ | ikut terpasang bersama Node.js |
| Git | apa saja | |
| Kamera | Intel RealSense seri D400 | colok ke **port USB 3** dengan kabel USB 3 |
| OS | Linux (diuji di Fedora), Windows 10/11, macOS | lihat catatan per OS di bawah |

> Tanpa kamera pun aplikasi bisa dicoba dengan **mode simulasi** (`CAMERA_BACKEND=mock`, lihat bagian 5).

---

## 2. Memasang pyenv dan nvm (sekali saja per komputer)

pyenv dan nvm membuat versi Python dan Node.js mengikuti projek, bukan mengikuti sistem, sehingga siapa pun
yang meng-clone repo ini memakai versi yang sama.

### pyenv (Python)

**Linux / macOS**

```bash
curl -fsSL https://pyenv.run | bash
```

Tambahkan ke `~/.bashrc` (atau `~/.zshrc`), lalu buka terminal baru:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

pyenv meng-compile Python dari source, jadi pasang dulu paket build-nya:

```bash
# Ubuntu / Debian
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
# Fedora
sudo dnf install -y make gcc patch zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel \
  openssl-devel tk-devel libffi-devel xz-devel libuuid-devel gdbm-libs libnsl2
```

**Windows**: pakai [pyenv-win](https://github.com/pyenv-win/pyenv-win)
(`Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"` di PowerShell).

### nvm (Node.js)

**Linux / macOS**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# buka terminal baru, lalu cek:
nvm --version
```

**Windows**: pakai [nvm-windows](https://github.com/coreybutler/nvm-windows/releases) (unduh `nvm-setup.exe`).

---

## 3. Instalasi projek

### 3.1 Clone

```bash
git clone <url-repo-ini> intelrealsense-data-acquisition
cd intelrealsense-data-acquisition
```

### 3.2 Backend (FastAPI)

```bash
cd backend

pyenv install -s 3.12        # sekali saja; -s melewati jika sudah terpasang
python --version             # harus 3.12.x (dibaca dari backend/.python-version)

python -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements-dev.txt   # atau requirements.txt tanpa alat test

cp .env.example .env         # Windows: copy .env.example .env
cd ..
```

Database SQLite (`backend/data/app.db`) dan tabelnya dibuat otomatis saat backend pertama kali berjalan.
Tidak ada server database yang perlu dipasang.

### 3.3 Frontend (Vue)

```bash
cd frontend
nvm install          # membaca .nvmrc -> Node 24
nvm use
node --version       # v24.x
npm install
cd ..
```

### 3.4 Izin USB kamera (khusus Linux)

Agar pyrealsense2 bisa membuka kamera tanpa `sudo`, pasang udev rules dari Intel, lalu cabut dan colok
lagi kameranya:

```bash
sudo curl -fsSL https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules \
  -o /etc/udev/rules.d/99-realsense-libusb.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Windows tidak memerlukan langkah ini. Di macOS, pyrealsense2 dari pip belum tentu tersedia untuk chip Apple;
bila `pip install` gagal, jalankan dengan `CAMERA_BACKEND=mock` atau build librealsense dari source.

---

## 4. Menjalankan aplikasi

### Cara cepat: `start.sh`

> `start.sh` **hanya bisa dipakai setelah semua kebutuhan (bagian 1–2) terpasang dan instalasi (bagian 3)
> selesai**. Skrip ini tidak memasang apa pun; ia hanya menyalakan backend lalu frontend sekaligus.

```bash
./start.sh
```

Buka **http://127.0.0.1:5173**. Tekan `Ctrl+C` untuk menghentikan backend dan frontend bersamaan.
Di Windows, jalankan `start.sh` dari Git Bash, atau pakai dua terminal seperti di bawah.

### Cara manual (dua terminal)

```bash
# Terminal 1: backend, http://127.0.0.1:8000 (dokumentasi API: /docs)
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: frontend, http://127.0.0.1:5173
cd frontend
nvm use
npm run dev
```

Frontend meneruskan semua permintaan `/api` (REST, stream preview, dan WebSocket) ke backend di port 8000,
jadi cukup membuka satu alamat.

---

## 5. Konfigurasi backend (`backend/.env`)

| Variabel | Default | Arti |
| -------- | ------- | ---- |
| `CAMERA_BACKEND` | `auto` | `auto`/`realsense`: kamera RealSense di USB. `mock`: kamera simulasi, untuk mencoba tanpa perangkat. |
| `CAMERA_AUTO_CONNECT` | `true` | Langsung terhubung saat start dan otomatis tersambung saat kamera dicolok. |
| `DATABASE_URL` | `sqlite:///backend/data/app.db` | Lokasi database riwayat, projek, dan pengaturan. |
| `PREVIEW_FPS` | `15` | Frame rate preview di browser (tidak memengaruhi gambar yang disimpan). |
| `PREVIEW_JPEG_QUALITY` | `80` | Kualitas JPEG preview. |

Mode simulasi tidak pernah aktif dengan sendirinya, jadi dataset tidak mungkin tercampur gambar palsu.
Saat aktif, layar Capture menandainya dengan "(simulated)".

---

## 6. Cara pakai

1. **Buat projek**: di halaman Capture, klik **New project**, lalu isi:
   - nama projek;
   - kelas (mis. `stunting`, `tidak stunting`; tekan Enter setiap selesai mengetik satu kelas);
   - format output (checkbox, boleh lebih dari satu);
   - folder tujuan: **Choose folder** membuka dialog folder bawaan sistem operasi. Jika dialog itu tidak
     tersedia, muncul penjelajah folder di dalam aplikasi.
2. **Pilih kelas** yang sedang difoto di panel *Capturing class* (atau tekan `←` / `→`).
3. **Ambil gambar**: klik **Capture** atau tekan `Space`. Nama file berikutnya selalu terlihat di panel *Next shot*.
4. Ubah kelas, format, nama, atau folder kapan saja lewat **Project settings**. Mengganti nama kelas ikut
   mengganti nama folder dan file yang sudah ada di disk.
5. **Hapus projek** lewat ikon tempat sampah di daftar **Select project** (atau tombol *Delete project* di
   Project settings). Modal konfirmasi menanyakan **Yes / No**, dengan checkbox **Also delete its files and folders**:
   - tidak dicentang: projek dan riwayatnya dihapus dari aplikasi, file gambar tetap ada di disk;
   - dicentang: file gambar projek dan folder `{format}/{kelas}/` miliknya juga dihapus permanen. File lain di
     folder tujuan tidak disentuh, folder tujuan hanya ikut terhapus bila kosong, dan folder kelas yang juga dipakai
     projek lain tidak dihapus (hanya file milik projek ini).

### Struktur hasil

```
{folder tujuan}/
├── jpg/                     RGB JPG (8-bit)
│   ├── stunting/
│   │   ├── stunting-0001.jpg
│   │   └── stunting-0002.jpg
│   └── tidak stunting/
│       └── tidak stunting-0001.jpg
├── png/                     RGB PNG (8-bit, lossless)
├── tiff/                    Depth TIFF (16-bit, nilai depth mentah)
├── png16/                   Depth PNG 16-bit (nilai depth mentah)
└── npy/                     Depth NumPy uint16 (nilai depth mentah)
```

- RGB dan depth dalam satu nomor berasal dari **frameset yang sama** (tersinkron), sehingga
  `png/stunting/stunting-0007.png` berpasangan dengan `npy/stunting/stunting-0007.npy`.
- Secara default depth di-*align* ke RGB, jadi piksel (x, y) di kedua file adalah titik yang sama.
- Nilai depth disimpan mentah. Kalikan dengan *depth scale* (biasanya 0.001, artinya milimeter) untuk mendapat
  meter. Depth scale, intrinsik kamera, dan serial perangkat tiap gambar tercatat di database (tabel `captures`).
- Penomoran melanjutkan angka tertinggi yang sudah ada, baik di database maupun di disk, jadi file lama tidak
  pernah tertimpa.
- Semua format satu shot ditulis lengkap atau tidak sama sekali. Kalau satu format gagal, tidak ada file
  setengah jadi yang tertinggal.

### Shortcut (hanya aktif di halaman Capture)

| Tombol | Aksi |
| ------ | ---- |
| `Space` | Ambil gambar (memulai timer bila timer diaktifkan) |
| `→` atau `↓` | Kelas berikutnya |
| `←` atau `↑` | Kelas sebelumnya |
| `Esc` | Batalkan countdown timer |

Shortcut tidak berlaku saat mengetik di kolom input atau saat dialog terbuka. Kombinasi `Alt+panah` dan
`Ctrl+…` sengaja dihindari karena dipakai browser.

---

## 7. Struktur projek

```
intelrealsense-data-acquisition/
├── start.sh                      menjalankan backend + frontend sekaligus
├── .nvmrc                        versi Node.js
├── backend/
│   ├── .python-version           versi Python (pyenv)
│   ├── requirements.txt          dependensi runtime
│   ├── requirements-dev.txt      + pytest, httpx, ruff
│   ├── pyproject.toml            metadata, konfigurasi pytest & ruff
│   ├── .env.example
│   ├── app/
│   │   ├── main.py               entry point FastAPI, lifespan kamera
│   │   ├── api/
│   │   │   ├── deps.py           dependency injection (DB session, service)
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/    projects, camera, capture, history, settings, system, events (WebSocket)
│   │   ├── core/                 config (pydantic-settings), logging, exceptions
│   │   ├── db/                   Base, engine & session SQLite
│   │   ├── models/               Project, ProjectClass, CaptureRecord, AppSetting
│   │   ├── schemas/              skema Pydantic request/response
│   │   ├── repositories/         query database
│   │   ├── services/
│   │   │   ├── camera/           RealSenseDevice (pyrealsense2), MockDevice, CameraManager (thread pipeline)
│   │   │   ├── image_writer.py   registry format & penulisan file atomik
│   │   │   ├── project_service.py, capture_service.py, history_service.py,
│   │   │   ├── camera_service.py, settings_service.py, directory_service.py, event_hub.py
│   │   └── utils/                penamaan file, waktu
│   └── tests/                    unit & integration (pakai kamera simulasi)
└── frontend/
    ├── components.json           konfigurasi shadcn-vue
    ├── vite.config.ts            proxy /api -> backend
    └── src/
        ├── assets/styles/        tokens.css (warna, ukuran), main.css
        ├── components/
        │   ├── ui/               komponen shadcn-vue
        │   ├── layout/           AppSidebar, BrandMark
        │   ├── common/           PageHeader, SettingsRow, ConfirmDialog, Kbd, ...
        │   ├── capture/          CameraPreview, ClassPanel, CaptureControl, RecentStrip
        │   ├── project/          dialog buat/pilih/pengaturan projek, pemilih folder
        │   ├── history/          filter & tabel riwayat
        │   └── settings/         device, streams, opsi sensor, filter, preview
        ├── composables/          useCaptureShortcuts, useDepthProbe, useAutoSave
        ├── constants/            endpoint, shortcut, format, timer
        ├── layouts/              DefaultLayout (sidebar + konten)
        ├── router/
        ├── services/             axios API, WebSocket event
        ├── stores/               Pinia: camera, projects, capture, history
        ├── types/
        ├── utils/
        └── views/                CaptureView, HistoryView, settings/*
```

### API

Dokumentasi interaktif lengkap tersedia di **http://127.0.0.1:8000/docs** saat backend berjalan. Ringkasnya
(prefix `/api/v1`):

| Grup | Endpoint |
| ---- | -------- |
| Projek | `GET/POST /projects`, `GET/PATCH /projects/{id}`, `DELETE /projects/{id}?delete_files=true\|false`, `POST /projects/{id}/classes`, `PATCH/DELETE /projects/{id}/classes/{cid}`, `PUT /projects/{id}/classes/order`, `GET /formats` |
| Sesi | `GET/PUT /session` (projek & kelas aktif) |
| Kamera | `GET /camera/status`, `POST /camera/connect`, `POST /camera/disconnect`, `POST /camera/reset`, `GET /camera/capabilities`, `GET/PUT /camera/config`, `GET/PUT /camera/options`, `POST /camera/options/reset`, `GET /camera/depth?x=&y=`, `GET /camera/stream/{rgb\|depth}` (MJPEG) |
| Capture | `POST /capture`, `GET /capture/next-name` |
| Riwayat | `GET /history` (filter `project_id`, `class_name`, `date_from`, `date_to`, `q`), `GET /history/{id}/thumbnail`, `DELETE /history/{id}` |
| Pengaturan | `GET/PUT /settings/capture-rules` |
| Sistem | `GET /system/health`, `POST /system/pick-directory`, `GET/POST /system/directories` |
| Realtime | WebSocket `/events`: `camera.status`, `capture.started/progress/completed/failed`, `project.updated/deleted`, `capture.deleted`, `camera.config`, `settings.capture_rules` |

---

## 8. Pengujian

```bash
# Backend (memakai kamera simulasi dan database sementara)
cd backend && source .venv/bin/activate
pytest
ruff check app tests

# Frontend
cd frontend
npm run test:unit
npm run type-check
npm run test:e2e      # Playwright; backend harus berjalan
```

---

## 9. Pemecahan masalah

| Gejala | Solusi |
| ------ | ------ |
| "No RealSense camera detected on USB" | Cek kabel dan port USB 3. Di Linux pastikan udev rules sudah terpasang (3.4), lalu colok ulang. Tutup Intel RealSense Viewer, karena kamera hanya bisa dibuka satu aplikasi. |
| "Connected over USB 2" di Settings | Pindah ke port USB 3 (biasanya berwarna biru) dan gunakan kabel USB 3; USB 2 membatasi resolusi dan fps. |
| "Cannot reach the backend" | Backend belum berjalan atau port 8000 dipakai aplikasi lain. |
| `pip install pyrealsense2` gagal | Pastikan Python 3.10 – 3.14 (`python --version`) dan arsitektur x86_64 atau Windows. |
| Tombol *Choose folder* membuka penjelajah di aplikasi, bukan dialog sistem | Di Linux pasang `zenity` (`sudo apt install zenity` / `sudo dnf install zenity`). |
| Port 5173 sudah dipakai | Hentikan server Vite lain, atau jalankan `npm run dev -- --port 5174`. |
