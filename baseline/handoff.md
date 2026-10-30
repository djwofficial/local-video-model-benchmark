# Handoff Codex — Instalasi dan benchmark AI video lokal

Tanggal konteks: 29 Oktober 2026.
Bahasa komunikasi: Indonesia, langsung dan mudah dimengerti.

## Permintaan untuk Codex

Bantu saya memasang dan menguji model video generation secara lokal di Mac saya. Mulai dari pemeriksaan perangkat dan instalasi yang sudah ada, lalu selesaikan satu pipeline sampai menghasilkan animasi/video dan mencatat hasil benchmark. Jangan hanya memberi tutorial jika terminal lokal tersedia dan pekerjaan bisa dijalankan langsung.

Target pertama: **ComfyUI + LTX-Video 2B v0.9.5**, memakai workflow resmi yang ditautkan di bawah. Setelah pipeline pertama berfungsi, gunakan hasilnya sebagai baseline untuk pengujian model berikutnya.

Periksa dulu bahwa terminal benar-benar berjalan di Mac saya. Sesi ChatGPT sebelumnya hanya memiliki terminal Linux di cloud dan **belum memasang atau mengunduh apa pun di Mac saya**. Status instalasi lokal saat ini belum diketahui. Jangan menganggap ComfyUI, Homebrew, Python, Git, atau model sudah terpasang.

## Perangkat dan tujuan

- Perangkat utama: **MacBook Pro, Apple M4 Pro, unified memory 24GB**.
- Versi macOS, GPU core count, ruang disk kosong, dan software lokal: perlu diperiksa.
- Perangkat pembanding teman: **NVIDIA GeForce RTX 3050**; laptop/desktop, VRAM, RAM, dan OS belum diketahui.
- Gambar benchmark yang sebelumnya dibahas memakai **M3 Max 36GB**, bukan Mac saya. Jangan memakai angka hasil gambar itu sebagai hasil pengukuran Mac saya.
- Tujuan: mencari model gratis untuk dijalankan lokal, membandingkan waktu, penggunaan memori, kestabilan, dan kualitas gerakan.
- Tidak memakai layanan generate berbayar, API pihak ketiga, atau Comfy Cloud untuk tes ini.
- Internet boleh diperlukan untuk instalasi dan download model. Setelah dependency/model lengkap, verifikasi bahwa generasi bisa berjalan tanpa layanan cloud.
- Lisensi bobot berbeda antarcheckpoint; gratis untuk download/generate lokal tidak otomatis berarti penggunaan komersial tanpa syarat.

## Cara bekerja

1. Periksa OS, arsitektur, memori, ruang disk, dan instalasi yang sudah ada secara read-only.
2. Pakai instalasi yang sehat bila sudah tersedia. Jangan menimpa instalasi, model, atau workflow lama.
3. Utamakan Comfy Desktop untuk jalur GUI; instalasi manual dalam virtual environment boleh digunakan jika lebih sesuai dengan akses lokal Codex. Hindari modifikasi Python sistem.
4. Pilih build Apple Silicon/MPS. CUDA bukan backend untuk Mac ini. Pastikan log menunjukkan backend yang benar.
5. Jelaskan kebutuhan download dan lokasi file dengan singkat. Download hanya komponen pipeline pertama dahulu.
6. Kerjakan instalasi yang diizinkan oleh permintaan ini, ikuti aturan lingkungan Codex dan izin OS yang berlaku. Jika ada dialog OS yang hanya bisa diklik pengguna, minta satu tindakan spesifik.
7. Jangan mengubah batas keamanan memori MPS untuk memaksakan model masuk RAM.
8. Jangan mengklaim sukses hanya karena aplikasi terbuka. Harus ada file animasi/video yang bisa dibuka, workflow tersimpan, dan log hasil aktual.
9. Simpan catatan versi, konfigurasi, prompt, log, hasil, dan kendala agar tes dapat diulang.

## Pipeline pertama yang sudah ditelusuri

### Sumber resmi

- Download Comfy Desktop: https://www.comfy.org/download
- Panduan macOS: https://docs.comfy.org/installation/desktop/macos
- Penggunaan Desktop: https://docs.comfy.org/installation/desktop/usage/overview
- Pengelolaan instance: https://docs.comfy.org/installation/desktop/usage/instance-management
- Folder model/output: https://docs.comfy.org/installation/desktop/usage/settings
- Contoh LTX: https://comfyanonymous.github.io/ComfyUI_examples/ltxv/
- Workflow JSON: https://comfyanonymous.github.io/ComfyUI_examples/ltxv/ltxv_text_to_video_0.9.5.json
- Repository LTX-Video: https://github.com/Lightricks/LTX-Video

Tautan dan UI dapat berubah. Verifikasi sumber dan isi workflow saat pelaksanaan; jangan menebak nama file atau node jika berubah.

### File model

| File | Lokasi relatif terhadap direktori model aktif |
| --- | --- |
| `ltx-video-2b-v0.9.5.safetensors` | `checkpoints/` |
| `t5xxl_fp16.safetensors` | `text_encoders/` |

Halaman download checkpoint (sekitar 6.34GB menurut halaman yang diperiksa):
https://huggingface.co/Lightricks/LTX-Video/blob/main/ltx-video-2b-v0.9.5.safetensors

Halaman text encoder yang ditautkan oleh contoh resmi LTX:
https://huggingface.co/Comfy-Org/Mochi-Preview/blob/main/split_files/text_encoders/t5xxl_fp16.safetensors

Direct download checkpoint:
https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors

Encoder berada di repo bernama Mochi tetapi dipakai oleh workflow LTX ini. Tidak perlu mengunduh model Mochi. Workflow ini mengambil VAE dari checkpoint; tidak memerlukan file VAE terpisah pada konfigurasi contoh tersebut.

Comfy Desktop versi baru dapat memakai shared model directories. Gunakan lokasi yang benar-benar terdaftar di Settings/Storage; jangan menebak folder lama atau membuat `models/models`.

Periksa ukuran file dan integritas download bila ada checksum sumber. Jangan menganggap halaman HTML/error sebagai file model yang valid.

### Node penting pada workflow yang diperiksa

- `CheckpointLoaderSimple`: checkpoint LTX di atas.
- `CLIPLoader`: encoder T5 di atas, type `ltxv`, device awal `default`.
- `EmptyLTXVLatentVideo`: width, height, length, batch_size.
- `CLIPTextEncode`: positive dan negative prompt.
- `LTXVConditioning`: frame_rate.
- `LTXVScheduler`, `KSamplerSelect`, `SamplerCustom`.
- `VAEDecode`.
- `SaveAnimatedWEBP`: output aktif pada contoh.
- `SaveWEBM`: ada dalam contoh, tetapi mode awalnya bypass/tidak aktif. Aktifkan bila memerlukan WebM; samakan FPS.

Biarkan konfigurasi sampling bawaan workflow untuk baseline v0.9.5. Jangan menyalin steps/guidance distilled ke model biasa. Jangan mengganti checkpoint biasa ke distilled tanpa workflow yang sesuai.

## Uji awal sampai berhasil

Gunakan satu job pada satu waktu:

| Pengaturan | Nilai awal |
| --- | --- |
| Mode | Text-to-video |
| Width × height | 512 × 320 |
| Frames / length | 25 |
| Batch size | 1 |
| Seed | 41, fixed |
| Conditioning frame rate | 25 |
| Playback/output FPS | 25 |
| Steps, guidance, sampler | Bawaan workflow v0.9.5; catat nilai aktual |
| Upscale / interpolation | Tidak digunakan |

Ini hanya smoke test sekitar satu detik, bukan pengukuran final kualitas video atau bukti kemampuan durasi panjang. Kalau gagal karena memori, kurangi konfigurasi dan catat; jangan menjanjikan pasti muat di 24GB.

Prompt pertama:

```text
A single bright red ball rolls slowly from the left side to the right side of a wooden table. The ball remains round and keeps the same size and color throughout the shot. A plain beige wall is visible in the background. Soft daylight enters from a window on the left. The camera stays completely still, showing the entire table surface in one continuous shot.
```

Gunakan negative prompt bawaan workflow dan simpan teks aktualnya.

Konfirmasi output memiliki lebih dari satu frame, dapat dibuka, dan gerakannya terlihat. Animated WebP boleh untuk tes pertama; simpan WebM/MP4 bila pipeline mendukungnya. Jangan menyebut WebP sebagai MP4. Konversi tambahan harus dicatat dan waktu konversi dipisahkan bila tidak termasuk cakupan benchmark.

## Benchmark setelah pipeline berhasil

1. Charger terpasang, Low Power Mode off; hindari aplikasi berat dan job paralel.
2. Naikkan length ke **49 frame**, tetap 512×320 dan 25 FPS (durasi playback sekitar 1.96 detik).
3. Jalankan warm-up pada konfigurasi ini dengan seed 41.
4. Ukur tiga run dengan seed **42, 43, 44**. Gunakan daftar seed sama pada perangkat pembanding.
5. Perubahan seed mencegah hasil sampler sebelumnya dipakai ulang. Pastikan proses sampling benar-benar berjalan; pertahankan kebijakan cache dan residency model yang konsisten.
6. Pisahkan download/setup dari generation. Bedakan cold run/loading awal dan warm execution. Catat apakah encoding prompt, decoding VAE, dan penulisan output termasuk waktu yang dilaporkan.
7. Catat tiga nilai dan rata-ratanya. Jangan mengambil angka GPU lain sebagai perkiraan hasil terukur.

Tabel catatan yang perlu dibuat saat menjalankan tes:

| Model/checkpoint | Runtime + versi | Precision | Resolusi | Frame | FPS | Steps | Guidance | Seed | Waktu aktual (s) | Status/error | Memori/metode | Swap sebelum/sesudah | Catatan kualitas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LTX-Video 2B v0.9.5 | TBD | TBD | 512×320 | 49 | 25 | TBD | TBD | 42 | Belum diukur | Belum dijalankan | Belum diukur | Belum diukur | Belum dinilai |

Untuk penilaian visual, beri skor 1–5 dan penjelasan singkat: mengikuti prompt, konsistensi bentuk/warna, kewajaran gerakan, flicker/distorsi. Tambah prompt lain setelah baseline berhasil; satu prompt saja bukan evaluasi kualitas menyeluruh.

### Catatan metrik memori dan kecepatan

- Unified memory Mac bukan VRAM NVIDIA yang terpisah dari RAM sistem.
- Activity Monitor/process RSS/Memory Pressure bukan peak GPU memory yang sama persis dengan allocator MPS/MLX.
- Nyatakan alat, metode sampling, dan cakupan pengukuran. Jika peak tidak diukur, tulis tidak diukur.
- Catat swap awal dan akhir; swap akhir saja tidak membuktikan semuanya disebabkan satu run.
- Generated frames per second = jumlah frame output dibagi waktu generate; berbeda dari playback FPS.
- Untuk pembandingan Mac vs RTX 3050, samakan checkpoint/precision/workflow/config sejauh memungkinkan. Dokumentasikan perbedaan backend dan optimasi, jangan menjanjikan hasil bit-identik.

## Penanganan masalah

| Gejala | Langkah awal |
| --- | --- |
| Model tidak ditemukan | Periksa nama, ukuran file, folder aktif, restart/rescan |
| Missing node | Periksa kompatibilitas versi ComfyUI sebelum menambah plugin |
| MPS out of memory | Batch 1, kurangi frame/resolusi, tutup proses berat |
| Memori encoder terlalu besar | Pertimbangkan CLIPLoader device CPU; tetap berbagi RAM 24GB dan catat perubahan |
| Output hitam/rusak | Periksa model/encoder/workflow, dtype, log; jangan ubah banyak hal sekaligus |
| Run selesai seketika | Pastikan tidak hanya mengambil output cache |
| Swap besar / Mac tidak responsif | Hentikan job, evaluasi memori, turunkan konfigurasi |

## Model berikutnya — kandidat, bukan jaminan kompatibel

| Prioritas praktik | Kandidat | Jalur |
| --- | --- | --- |
| 1 | LTX-Video 2B v0.9.5 | Baseline ComfyUI sesuai panduan ini |
| 2 | LTX-Video 2B distilled | Workflow dan checkpoint distilled yang cocok; verifikasi dahulu |
| 3 | Wan 2.1 T2V 1.3B | ComfyUI untuk pembandingan lintas perangkat; opsi MLX untuk eksperimen Mac terpisah |
| 4 | LTX-2.3 distilled MLX 4-bit | Runtime komunitas MLX terpisah; memori aktual perlu diuji |
| 5 | Wan 2.2 TI2V 5B | Tes lanjutan setelah pipeline kecil stabil |

Referensi lanjutan:

- Wan 2.1 ComfyUI: https://comfyanonymous.github.io/ComfyUI_examples/wan/
- Wan 2.1 upstream: https://github.com/Wan-Video/Wan2.1
- Wan 2.2 upstream: https://github.com/Wan-Video/Wan2.2
- MLX-Video komunitas: https://github.com/Blaizzy/mlx-video
- LTX-2 MLX komunitas: https://github.com/dgrauet/ltx-2-mlx

Jangan download semuanya sekaligus. Model 13B/14B dan HunyuanVideo belum menjadi target awal untuk Mac 24GB ini. Kebutuhan VRAM CUDA yang dipublikasikan tidak boleh dianggap identik dengan unified memory Mac.

## Kriteria selesai tahap pertama

- [ ] Terminal terbukti lokal di Mac dan spek diverifikasi.
- [ ] ComfyUI lokal berjalan dengan backend Apple Silicon/MPS yang benar.
- [ ] Dua file model tersedia dan terbaca.
- [ ] Workflow dapat dimuat tanpa missing node/model.
- [ ] Smoke test menghasilkan animasi yang dapat dibuka.
- [ ] Workflow dan konfigurasi aktual tersimpan.
- [ ] Warm-up dan tiga run benchmark selesai, atau kegagalan didokumentasikan jelas.
- [ ] File hasil, log, serta catatan benchmark tersimpan di lokasi yang diinformasikan kepada pengguna.
- [ ] Ringkasan akhir membedakan hasil terukur, klaim sumber, dan hal yang belum diuji.

## Instruksi singkat untuk memulai

"Baca file ini dan lanjutkan instalasi serta pengujian langsung di Mac saya. Mulai dengan memeriksa perangkat dan software yang sudah ada. Selesaikan pipeline pertama sampai menghasilkan video/animasi dan mencatat benchmark. Beri pembaruan singkat dalam bahasa Indonesia, dan minta tindakan saya hanya jika diperlukan oleh dialog atau izin lokal."
