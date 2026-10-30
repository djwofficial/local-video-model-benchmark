# Dua Model Layak Menantang LTX-2.5 di Mac

Dari daftar perbandingan, hanya dua model yang layak dibuktikan berikutnya di Mac mini M5 Pro 24 GB. Yang pertama adalah **Kandinsky 6.0 Lite distill** (3B, MIT, rilis 6 Oktober 2026) lewat Diffusers di PyTorch MPS. Yang kedua adalah **HunyuanVideo 1.5 480p T2V dengan LoRA 4-step LightX2V** lewat ComfyUI-GGUF. Keduanya belum pernah diukur di Mac mana pun. Semua angka kecepatan dan memori untuk keduanya adalah estimasi yang diturunkan dari run GPU NVIDIA dan benchmark buatan developer sendiri. Peringkat ketiga adalah uji ulang murah Wan 2.2 TI2V-5B. Skor 1/3-nya di proyek ini diukur dengan protokol ronde 1 (512×320, prompt dengan kata "slowly"), dan dengan protokol itu LTX-2.3 juga hanya mendapat 1/3. MiniMax H3 adalah satu-satunya kandidat yang punya run terukur di Mac 24 GB, tetapi butuh ~23 menit per klip 5,17 detik, dan lisensinya mewajibkan izin tertulis bila pendapatan di atas US$20 juta. Karena itu H3 hanya pantas menjadi patokan kualitas, bukan pengganti. Lisensi sangat menentukan di sini: **LTX-2.5 sendiri hanya gratis untuk entitas dengan pendapatan tahunan di bawah US$10 juta (afiliasi ikut dihitung)**. Artinya model berlisensi MIT atau Apache-2.0 adalah satu-satunya jalan ke produksi tanpa perjanjian vendor. FastH3 Omni, Pika H3 Flex, Kandinsky Pro, Cosmos 3, LongCat-Video dan Helios sebaiknya dilewati karena terlalu besar untuk disk 42 GiB atau hanya punya jalur CUDA. Satu catatan metodologi juga penting: dua prompt sederhana sudah jenuh (LTX-2.5 6/6), jadi kandidat paling banter hanya bisa menyamai. Untuk membuktikan "upgrade", tes perlu ditambah klip ~5 detik dan prompt yang lebih sulit.

## Lima kandidat lolos saringan, tetapi dua teratas belum pernah jalan di Mac

Laporan ini memakai tiga label angka:

| Label | Arti |
|---|---|
| **T (Terukur)** | Ada run nyata dan perangkat kerasnya disebut. |
| **K (Klaim)** | Pernyataan vendor atau developer, atau benchmark yang dijalankan developer sendiri. |
| **E (Estimasi)** | Turunan saya dari angka T dan K, biasanya dengan menskalakan jumlah token atau langkah sampling. Rentangnya sengaja lebar. |

Bukti yang ada sangat tipis. Dari semua model di daftar, **satu-satunya run terukur di Mac 24 GB adalah MiniMax H3 di MacBook Pro M4 Pro 24 GB**, lewat rute streaming MLX dari Argus ([Argus](https://github.com/Argus-AiTeam/minimax-h3-mac)). Untuk **M5 Pro 24 GB**, tidak ada run terukur sama sekali untuk kandidat mana pun. Satu-satunya data dari mesin itu adalah laporan bug mlx-video. Dalam laporan itu, pemuatan T5 gagal karena timeout GPU. Setelah di-patch, run Wan 2.1 1.3B kecil (480×480, 17 frame) selesai dalam 165 dtk, dan 78% waktunya habis untuk encoding T5 ([mlx-video #54](https://github.com/Blaizzy/mlx-video/issues/54)). Semua angka in-house proyek ini berasal dari MacBook Pro M4 Pro.

| # | Model dan rute | Unduhan | Muat di 15 GiB / 42 GiB? | Puncak memori proses | Waktu per klip | Lisensi untuk telco besar | Bukti di Mac |
|---|---|---|---|---|---|---|---|
| 1 | **Kandinsky 6.0 Lite distill** (3B). Diffusers di PyTorch MPS, dua fase (encode Qwen → bebaskan memori → DiT+VAE), `sample_audio=False` | 24,5 GB tanpa audio (26,7 GB penuh) | Tidak / Ya | E: ~16 GiB di fase encoder, ~8–12 GiB di fase DiT | E: ~4–9 mnt per klip 2 dtk 768×512. K: 173,7 dtk per klip 5 dtk 480×864 di RTX 5060 Ti | **MIT, tanpa ambang** | Tidak ada |
| 2 | **HunyuanVideo 1.5 480p T2V** + LoRA 4-step LightX2V. ComfyUI + ComfyUI-GGUF di MPS | ~14,1 GB (encoder GGUF) / ~18,8 GB (encoder fp8) | Ya, tipis (GGUF) / Ya | E: ~10–13 GiB | E: ~5–10 mnt | Tencent Community: Taiwan boleh, ambang 100 juta MAU, output tidak boleh dipakai melatih model lain | K: maintainer menyatakan macOS bisa; tidak ada angka |
| 3 | **Wan 2.2 TI2V-5B, uji ulang adil**. Workflow ComfyUI FP16 lama dengan setelan ronde 2 | 18,15 GB (file lama sudah dihapus permanen saat ronde 1, jadi perlu unduh ulang) | Tidak / Ya | T: 14,94 GiB di 512×320. E: ~15–17 GiB di 768×512 | T: 274 dtk di 512×320. E: ~11–14 mnt di 768×512 | **Apache-2.0** | T: in-house, 1/3 dengan protokol lama |
| 4 | **MiniMax H3 base** (t2va). ComfyUI GGUF Q3_K_M + Qwen3-VL-32B Q4_K_M | ~29–31 GB | Tidak / Ya | E: ~15–16 GiB di fase encoder, ~11–13 GiB di fase DiT | E: ~3–8 mnt per klip 2,3 dtk 352×608. T: 1378 dtk per klip 5,17 dtk 768×448 (Argus, M4 Pro 24 GB) | Butuh izin tertulis di atas US$20 juta; hanya untuk evaluasi | T: 24 GB lewat Argus; rute GGUF belum diuji di 24 GB |
| 5 | **Wan 2.2 A14B Q4** + Lightning, mlx-video | ~31 GB | Tidak / Ya | T: 16,37 GiB RSS di mesin 128 GB. E: kemungkinan >17,8 GiB di 24 GB | T: 10:25 (512×320×81) di M5 Max. E: ~8–12 mnt | Apache-2.0 | T: hanya M5 Max 128 GB; ada bug terbuka |

Sumber angka tabel dibahas per model di bagian berikut.

Urutan peringkat ditimbang dari tiga hal:

1. Apakah lisensinya bisa dipakai untuk produksi oleh perusahaan sebesar Taiwan Mobile.
2. Seberapa kuat bukti prompt-following-nya.
3. Berapa biaya pembuktiannya dengan disk 42 GiB.

Lisensi diberi bobot tinggi karena **baseline-nya sendiri tidak gratis**. LTX-2.x Community License hanya gratis untuk penggunaan komersial di bawah US$10 juta pendapatan tahunan. Pendapatan dihitung untuk seluruh entitas, termasuk anak perusahaan dan afiliasi. Di atas ambang itu dibutuhkan Paid Commercial Use Agreement ([Lightricks/LTX-2.5](https://huggingface.co/Lightricks/LTX-2.5)). Estimasi waktu di tabel diturunkan dengan menskalakan jumlah token dan langkah dari run CUDA atau run in-house. Angka itu cukup untuk merencanakan jadwal, tetapi tidak cukup untuk memutuskan apa pun tanpa run nyata.

## Kandinsky 6.0 Lite: DiT 3B berlisensi MIT, tetapi encoder 16,6 GB yang menentukan nasibnya

Kandinsky 6.0 Video adalah keluarga model text-to-audio-video. Model ini dibuka 6 Oktober 2026, dan dukungan Diffusers serta ComfyUI diumumkan di hari yang sama ([GitHub kandinsky-6](https://github.com/kandinskylab/kandinsky-6)). Varian **Lite berukuran 3B**: stream video 2B, stream audio 0,6B, dan cross-attention 0,4B. Lite memakai VAE HunyuanVideo, dengan Qwen2.5-VL-7B dan CLIP ViT-L/14 sebagai encoder teks ([arXiv 2610.05608](https://arxiv.org/html/2610.05608)). Checkpoint **Lite distill** melakukan sampling dalam **10 langkah PiFlow dengan guidance 1,0**. Opsi `sample_audio=False` menghasilkan video saja ([HF card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)). Kandinsky 6.0 tidak punya varian 10 detik; checkpoint 10 detik adalah milik Kandinsky 5.0.

Sinyal kualitasnya nyata, tetapi semuanya berasal dari developer:

| Metrik VABench (paper Kandinsky) | Kandinsky 6.0 Lite | LTX 2.5 |
|---|---|---|
| tv_align | **0,227** | 0,185 |
| visual_qa | 0,691 | 0,617 |
| "alignment" | 4,351 | **4,527** |

Sumber: ([arXiv](https://arxiv.org/html/2610.05608)).

Belum ada evaluasi side-by-side oleh manusia untuk Lite. Dalam uji manusia milik developer sendiri, MiniMax H3 lebih disukai daripada Kandinsky Pro di sebagian besar kriteria, termasuk prompt following ([arXiv v1](https://arxiv.org/html/2610.05608v1)). Tidak ada sumber yang menguji arah gerak. Jadi Lite tidak menempati peringkat 1 karena terbukti lebih patuh prompt. Lite ada di peringkat 1 karena hanya dia model baru yang sekaligus kecil, sudah di-distill, dan berlisensi MIT tanpa ambang pendapatan.

Hambatan utamanya ada di encoder, bukan di DiT. Repo Lite distill berukuran **26,68 GB**. Transformer-nya hanya 6,38 GB, tetapi **text encoder Qwen2.5-VL mencapai 16,60 GB** ([HF tree API](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers/tree/main?recursive=true)). Encoder itu saja (~15,5 GiB) sudah mendekati batas working set ~17,8 GiB. Resep yang masuk akal memakai dua proses terpisah:

1. Proses pertama memuat Qwen, mengenkode prompt, menyimpan embedding ke disk, lalu keluar.
2. Proses kedua memuat transformer, VAE dan CLIP untuk denoise dan decode.

`enable_model_cpu_offload()` yang dipakai di contoh resmi tidak menghemat apa pun di unified memory, karena salinan "CPU" tetap tinggal di kolam RAM yang sama (E).

Kelayakan di MPS adalah pertanyaan terbuka:

- **Pipeline resmi:** Kandinsky mensyaratkan GPU NVIDIA ([quick_start](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/quickstart/quick_start.md)).
- **Diffusers:** transformer versi Diffusers memakai `dispatch_attention_fn` dengan backend native dan RoPE fp32. Saya tidak menemukan operasi float64, complex, triton atau CUDA di dalamnya ([sumber diffusers](https://github.com/huggingface/diffusers/blob/main/src/diffusers/models/transformers/transformer_kandinsky6.py)).
- **Pipeline SR:** hanya pipeline SR yang wajib memakai flex attention ([Diffusers docs](https://github.com/huggingface/diffusers/blob/main/docs/source/en/api/pipelines/kandinsky6.md)), jadi SR harus dilewati.
- **ComfyUI:** node native masih berupa PR #16825 yang belum di-merge ([PR](https://github.com/Comfy-Org/ComfyUI/pull/16825)).
- **GGUF/MLX:** tidak ada GGUF atau port MLX untuk Lite.

Semua patokan memori dan waktu berasal dari CUDA:

| Run | Waktu | Memori |
|---|---|---|
| Developer, RTX 5060 Ti 16 GB, klip 5 dtk 480×864 (Qwen NF4, SageAttention, torch.compile) | **173,7 dtk**, dengan 36,2% waktu habis di VAE decoder ([rtx-5060-ti.md](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/performance/rtx-5060-ti.md)) | — |
| Pihak ketiga, RTX 3090, BF16 asli | **184,6 dtk** | **16,13 GiB** teralokasi ([WaveCut](https://huggingface.co/WaveCut/Kandinsky-6.0-Lite-distill-5s-OrbitQuant-W4A4)) |
| Paper, preset 16 GB, SD | — | puncak 7,9 GiB ([arXiv](https://arxiv.org/html/2610.05608)) |

Klip uji 2 dtk 768×512 (49 frame) kira-kira setara 20 ribu token, dibandingkan ~50 ribu token untuk default 121 frame (E). Perkiraan saya untuk M5 Pro adalah **~4–9 menit per klip**, lebih lambat dari LTX-2.5 (175 dtk). Puncak memorinya ~16 GiB di fase encoder, hampir sama dengan 15,5 GiB milik LTX-2.5, dan ~8–12 GiB di fase DiT (E).

Ada tiga risiko yang bisa menggagalkan uji:

- **Memori attention:** jika SDPA di MPS mematerialisasi matriks attention penuh untuk 20 ribu token, memorinya bisa jauh lebih besar daripada kernel CUDA.
- **VAE decode:** VAE HunyuanVideo berat dan perlu tiling.
- **Jumlah frame:** model card hanya menunjukkan 121 frame, jadi dukungan 49 frame belum terkonfirmasi.

Resep uji yang membatasi kerugian berjalan dalam dua langkah:

1. Unduh dulu transformer, VAE, CLIP, tokenizer dan scheduler (~7,9 GB). Jalankan smoke test DiT+VAE di MPS dengan embedding dummy pada 512×320.
2. Jika lolos, baru tambahkan Qwen 16,6 GB.

Total unduhan untuk uji penuh tanpa audio ~24,5 GB, jadi Trash harus dikosongkan dulu. Jika 6.0 Lite gagal di MPS, Kandinsky 5.0 T2V Lite (MIT, termasuk varian "distilled16steps") bisa menjadi cadangan dari keluarga yang sama ([HF kandinskylab](https://huggingface.co/api/models?search=kandinskylab&sort=downloads)).

## HunyuanVideo 1.5 membawa bukti prompt-following terkuat dan muat di disk hari ini

HunyuanVideo 1.5 (Tencent, November 2025) memakai DiT 8,3B, VAE kausal 3D dengan kompresi 16× spasial dan 4× temporal, serta encoder Qwen2.5-VL-7B ([HF card](https://huggingface.co/tencent/HunyuanVideo-1.5); [tech report](https://arxiv.org/html/2511.18870v2)). Ada dua alasan model ini menempati peringkat 2.

Alasan pertama: buktinya paling kuat di antara model kelas menengah.

| Evaluasi | HunyuanVideo 1.5 | Wan 2.2 | Catatan |
|---|---|---|---|
| Instruction following T2V, evaluasi Tencent (300 prompt, >100 penilai) | **61,57** | 44,07 | Veo3 73,77; GSB bersih +17,12% atas Wan 2.2 ([tech report](https://arxiv.org/html/2511.18870v2)) |
| LMArena T2V, lewat agregator | 1169 | 1132 (A14B) | Interval kepercayaan tidak tumpang tindih ([gradually.ai](https://www.gradually.ai/en/ai-video-model-comparison/wan-2-2-a14b-vs-hunyuan-video-1-5/)) |

Kelemahannya, angka-angka itu untuk model 720p penuh, bukan 480p dengan LoRA 4-step. Selain itu tidak ada benchmark yang membandingkannya langsung dengan LTX-2.5.

Alasan kedua: jalurnya paling murah.

- ComfyUI punya dukungan native ([Comfy blog](https://blog.comfy.org/p/hunyuanvideo-15-native-support)).
- GGUF kecil tersedia: Q4_K_M 5,09 GB dan Q5_K_M 6,12 GB ([jayn7](https://huggingface.co/jayn7/HunyuanVideo-1.5_T2V_480p-GGUF)).
- Seorang engineer Tencent menyatakan **macOS didukung, hanya tanpa fitur lanjutan seperti sparse attention** ([issue #18](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/issues/18)). Pernyataan ini tanpa angka waktu.

Jumlah langkah adalah kuncinya. Model cfg-distilled 480p "harus memakai 50 langkah" ([HF card](https://huggingface.co/tencent/HunyuanVideo-1.5)). Itu jauh terlalu lambat untuk menyaingi LTX-2.5 distilled di Mac. Satu-satunya jalur T2V yang cepat adalah distill 4-step LightX2V. Distill ini tersedia sebagai LoRA rank-32 berukuran 0,34 GB untuk ComfyUI ([Comfy-Org](https://huggingface.co/Comfy-Org/Hunyuan-Video-1.5)), dengan setelan 4 langkah dan guidance 1 ([lightx2v](https://huggingface.co/lightx2v/Hy1.5-Distill-Models)). Belum ada evaluasi kualitas independen untuk distill ini. Jadi uji lokal menilai paket "HunyuanVideo + LoRA", bukan HunyuanVideo murni.

Encoder bisa diambil dalam dua versi:

| Pilihan encoder | Total unduhan | Muat di disk sekarang? | Risiko |
|---|---|---|---|
| Qwen2.5-VL-7B GGUF Q4_K_M, 4,68 GB ([unsloth](https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF)) | ~14,1 GB (DiT Q5_K_M 6,12 + encoder 4,68 + ByT5 0,44 + VAE 2,52 + LoRA 0,34) | **Ya**, dari 15 GiB yang kosong, dengan sisa tipis | Belum ada yang membuktikan node HunyuanVideo menerima encoder GGUF |
| `qwen_2.5_vl_7b_fp8_scaled`, 9,38 GB ([Comfy-Org](https://huggingface.co/Comfy-Org/Hunyuan-Video-1.5)) | ~18,8 GB | Tidak; Trash harus dikosongkan dulu | Lebih aman: proyek ini sudah pernah menjalankan `umt5_xxl_fp8_e4m3fn_scaled` lewat ComfyUI di Mac yang sama untuk uji Wan ([retired-candidate-cache.json lokal](/Users/dyn/AI/video-model-comparison-2026-10-29/retired-candidate-cache.json)) |

ComfyUI-GGUF di MPS sudah terbukti untuk model lain, yaitu MiniMax H3 di M5 Pro 48 GB dan M1 Air 16 GB ([Bambushu](https://github.com/Bambushu/minimax-h3-mac)). Perkiraan saya: puncak ~10–13 GiB dan **~5–10 menit per klip 2 dtk** pada ~480p (E). Dequantisasi GGUF di MPS menjadi salah satu sumber perlambatan. Resolusi uji sebaiknya 768×512, yang luas pikselnya setara bucket 480p (E).

Ada alternatif Apple-native: `PocketAiHub/HunyuanVideo-1.5-Distilled-MLX` (21,08 GB, dengan runtime sendiri bernama `pocketai_video`). Repo ini dibatasi gate wilayah, dan README serta file benchmark-nya tidak bisa dibaca tanpa login ([HF API](https://huggingface.co/api/models/PocketAiHub/HunyuanVideo-1.5-Distilled-MLX)).

Ketentuan lisensi Tencent Hunyuan Community ([LICENSE](https://huggingface.co/tencent/HunyuanVideo-1.5/blob/main/LICENSE)):

- Lisensi tidak berlaku di EU, UK dan Korea Selatan. **Taiwan tidak termasuk wilayah yang dikecualikan.**
- Ambangnya **100 juta MAU**, bukan pendapatan.
- Output tidak boleh dipakai untuk memperbaiki model AI lain.

Bagi telco besar, ambang berbasis MAU ini justru lebih ramah daripada ambang pendapatan di LTX-2.5 dan H3. Syaratnya, produk terkait harus di bawah 100 juta MAU, dan tidak ada staf, region cloud atau pengguna di wilayah yang dikecualikan. Hal ini perlu dikonfirmasi tim legal.

## Wan 2.2 belum gagal secara adil; H3 hanya pantas sebagai patokan kualitas

### Uji ulang Wan 2.2 TI2V-5B murah dan lisensinya bersih

Skor 1/3 Wan 2.2 TI2V-5B di proyek ini tidak bisa dibandingkan dengan 6/6 LTX. Skor itu diukur di ronde 1: 512×320, prompt asli yang memuat kata "slowly", 30 langkah, CFG 5, ComfyUI FP16. Hasilnya **274 dtk per klip dan 14,94 GiB**. Pada kondisi yang sama, **LTX-2.3 juga hanya mendapat 1/3**. LTX-2.3 baru mencapai 3/3 setelah ronde 2 menaikkan resolusi ke 768×512 dan menghapus "slowly" dari prompt ([RESULTS.md lokal](/Users/dyn/AI/video-model-comparison-2026-10-29/RESULTS.md)). Wan tidak pernah diuji ulang dengan setelan ronde 2.

Uji ulang yang adil memakai workflow yang sama dengan tiga file yang sudah dipensiunkan: DiT FP16 10,0 GB, UMT5 fp8 6,74 GB dan VAE 1,41 GB, total **18,15 GB** ([retired-candidate-cache.json lokal](/Users/dyn/AI/video-model-comparison-2026-10-29/retired-candidate-cache.json)). File-file itu sudah dihapus permanen setelah ronde 1 (tidak ada di Trash), jadi perlu diunduh ulang. Pada 768×512 jumlah token naik ~2,4×, jadi saya memperkirakan ~11–14 menit per klip dengan puncak ~15–17 GiB (E).

Harapan hasilnya rendah, karena evaluasi Tencent menempatkan Wan 2.2 paling bawah untuk instruction following (44,07). Namun biayanya kecil dan lisensinya Apache-2.0 ([Wan2.2 GitHub](https://github.com/Wan-Video/Wan2.2)). Jika Wan lolos, versi cepatnya sudah tersedia: FastWan2.2-TI2V-5B MLX q8 (18,8 GB, distill 3 langkah). Di M2 Max 32 GB, versi ini terukur **43 dtk untuk klip 1 dtk 832×480, dengan puncak 17,0 GB**. Catatannya, T5 4-bit "merusak prompt", jadi T5 harus tetap 8-bit ([jboone100](https://huggingface.co/jboone100/FastWan2.2-TI2V-5B-MLX-q8)).

Wan 2.2 A14B Q4 lewat mlx-video hanya layak dicoba bila semua kandidat lain sudah selesai. Satu-satunya run terukur ada di M5 Max 128 GB, mesin yang tidak mengalami tekanan memori: **10:25 untuk 512×320×81 frame dengan 16,37 GiB RSS**, dan 36:53 di 768×512 ([PocketAI](https://huggingface.co/PocketAiHub/Wan2.2-T2V-A14B-MLX)). Di 24 GB ada empat hambatan:

- Dua expert Q4 saja sudah ~15,6 GiB.
- Mode relay (hanya satu expert dimuat) masih berupa PR yang belum di-merge ([PR #41](https://github.com/Blaizzy/mlx-video/pull/41)).
- Kombinasi kuantisasi + CFG + 81 frame menghasilkan video hitam ([#40](https://github.com/Blaizzy/mlx-video/issues/40)).
- Di M5 Pro 24 GB, pemuatan T5 memicu timeout GPU karena T5 di-upcast ke fp32 (~22,7 GB) ([#54](https://github.com/Blaizzy/mlx-video/issues/54)).

Dengan LoRA Lightning (4 langkah, CFG 1) dan klip 49 frame, saya memperkirakan ~8–12 menit per klip dengan risiko swap yang tinggi (E).

### MiniMax H3 bisa jalan di 24 GB, tetapi lambat dan lisensinya terkunci

MiniMax H3 jelas pemimpin kualitas di antara model open-weight. Di leaderboard T2V open-weights Artificial Analysis, Elo-nya **1161, dibanding 947 untuk LTX-2.5 Fast** ([AA](https://artificialanalysis.ai/video/leaderboard/text-to-video/open-weights)). H3 juga satu-satunya kandidat dengan run terukur di Mac 24 GB. Di M4 Pro 24 GB, rute Argus (DiT INT8 terkalibrasi, encoder 4-bit, Turbo) menghasilkan **klip 768×448, 124 frame (5,17 dtk) dalam 1378 dtk, dengan max RSS ~12,0 GB**. Run BF16 di 1344×768 memakan 2879 dtk dengan footprint puncak ~15,8 GB ([Argus](https://github.com/Argus-AiTeam/minimax-h3-mac)). Dihitung per detik video, H3 ~3× lebih lambat dari LTX-2.5, padahal resolusinya lebih kecil (E). Rute Argus juga butuh ~115 GB disk ([ModelFit](https://modelfit.io/video/minimax-h3/)), jauh di atas 42 GiB. Rute MLX lain lebih berat lagi:

- **PipeNetwork:** hanya diuji di M3 Ultra 550 GB ([PipeNetwork](https://github.com/PipeNetwork/minimax-h3-mlx)).
- **mlx-h3:** anggaran memori default 70 GiB ([PyPI](https://pypi.org/project/mlx-h3/)).
- **Paket mlx-serve:** puncak 66,7–76,6 GB ([ModelFit](https://modelfit.io/video/minimax-h3/)).

Rute yang muat di disk adalah workflow ComfyUI GGUF dari Bambushu ([Bambushu](https://github.com/Bambushu/minimax-h3-mac)):

| File | Ukuran |
|---|---|
| DiT `MiniMax-H3-FL2VA-Pruned-Q3_K_M` | 8,8 GB |
| Qwen3-VL-32B Q4_K_M | 14,6 GB |
| VAE video | 5,2 GB |
| VAE audio | 0,6 GB |
| LoRA Turbo | 1,38–2,1 GB |
| **Total** | **~29–31 GB** |

Untuk Mac di bawah 32 GB, rute ini memakai flag `--reserve-vram 1`. Hasil terukurnya 6 mnt 54 dtk untuk 352×608×124 frame di M5 Pro 48 GB. Di M1 Air 16 GB, run gagal kehabisan memori GPU mulai 56 frame. **Rute ini belum pernah diuji di 24 GB.** Perkiraan saya ~3–8 menit per klip 56 frame (2,3 dtk) di 352×608, dengan puncak ~15–16 GiB di fase encoder (E).

Kualitas H3 lokal kemungkinan berada di bawah yang ditunjukkan leaderboard:

- **Kuantisasi:** Q3_K_M lebih agresif daripada konfigurasi mana pun yang pernah dicek kualitasnya. Bahkan kuantisasi 4-bit di PipeNetwork hanya mencapai 22,0 dB PSNR ([PipeNetwork](https://github.com/PipeNetwork/minimax-h3-mlx)).
- **Context-IR:** versi lokal tidak menyertakan H3-Context-IR, yang ada di versi hosted ([HF card](https://huggingface.co/MiniMaxAI/MiniMax-H3)).
- **Motion physics:** review pihak ketiga yang dekat dengan reseller memberi skor 6,2/10 ([Atlas Cloud](https://www.atlascloud.ai/zh-TW/blog/tips/choose-ai-video-model-wan-3.0-seedance-2.5-minimax-h3)).

Draw Things juga mendukung H3 sejak 11 September 2026, termasuk varian SpinQuant 4-bit untuk RAM rendah, tetapi tanpa angka waktu yang dipublikasikan ([Draw Things](https://drawthings.ai/downloads/)).

Lisensinya membuat H3 hanya bisa menjadi patokan ([LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)):

- Taiwan tidak termasuk wilayah yang dikecualikan (EU, UK, Korea Selatan, AS).
- Produk atau layanan dengan pendapatan di atas **US$20 juta per tahun butuh izin tertulis dari MiniMax**.
- UI komersial wajib menampilkan "MiniMax H3".
- Output tidak boleh dipakai untuk memperbaiki model AI lain.

Uji H3 menjawab satu pertanyaan: apakah versi lokal terkuantisasi dari model terbaik ini mengalahkan LTX-2.5 di prompt yang lebih sulit? Jika tidak, hampir pasti tidak ada model lain di daftar yang bisa.

## Tujuh model dilewati karena ukuran, CUDA, atau mode input yang tidak cocok

| Model | Alasan dilewati | Sumber |
|---|---|---|
| **Kandinsky 6.0 Pro / Pro Distill** (29B) | Transformer Pro distill 60,34 GB BF16. Kuantisasi terkecil (W4A8, 17,13 GB) bergantung pada kernel CUDA, dan GGUF untuk versi distill masih "Coming". Paper menyebut Pro butuh ~58 GiB RSS host, bahkan dengan preset 16 GB. | [realrebelai](https://huggingface.co/realrebelai/Kandinsky-6.0-Pro-5s_GGUFs); [arXiv](https://arxiv.org/html/2610.05608) |
| **FastH3 Omni** | Distill 8 langkah **khusus reference-to-video** yang mewajibkan minimal satu gambar atau video, jadi tidak bisa menjalankan prompt T2V murni. Format cepatnya FP8/NVFP4, dan profil lokalnya hanya RTX 5090 dan DGX Spark. | [FastVideo card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1) |
| **Pika H3 Flex** | LoRA rank-128 di atas basis H3 penuh (komponen ~210 GB), divalidasi di H100 80 GB. Secara teori LoRA versi Comfy bisa dipasang di basis GGUF, tetapi belum ada yang mencoba, dan Bambushu memperingatkan bahwa LoRA di MPS kehabisan memori pada 16 GB. | [Pika card](https://huggingface.co/Pika-Labs/Pika-H3-Flex) |
| **Cosmos 3** | Tidak ada varian kecil. Nano 16B sudah 34,99 GB dalam BF16 dan hanya diuji di Linux/NVIDIA BF16. Satu-satunya GGUF adalah cabang reasoning, bukan generator video. | [Cosmos3-Nano](https://huggingface.co/nvidia/Cosmos3-Nano); [Hob-forge](https://huggingface.co/Hob-forge/Cosmos3-Nano-GGUF) |
| **LongCat-Video** (13,6B, MIT) | Repo 83,31 GB, tanpa port MLX atau GGUF untuk T2V. | [HF API](https://huggingface.co/api/models/meituan-longcat/LongCat-Video/tree/main?recursive=true) |
| **Helios** (14B, Apache-2.0) | Repo 137,75 GB dengan kuantisasi yang hanya untuk CUDA. Angka "~6 GB VRAM" bergantung pada offload ke RAM host CUDA, yang tidak menghemat apa pun di unified memory. | [Helios](https://github.com/PKU-YuanGroup/Helios) |
| **Lance-3B-Video MLX** (Apache-2.0, 15,64 GB; daftar tunggu) | Native Mac dan muat di 16 GB, tetapi batas pakainya 768×768×25 frame, dan hasil 49 frame "degraded". Tidak cocok dengan protokol 49 frame. | [mlx-community](https://huggingface.co/mlx-community/Lance-3B-Video-bf16) |

Dua celah lain di pasar juga tertutup. Tidak ada "LTX-2.5 Lite", karena checkpoint distilled tetap berukuran 22B ([Lightricks](https://huggingface.co/Lightricks/LTX-2.5)). Open weights Wan juga berhenti di versi 2.2 ([HowAIWorks](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)). LongCat, Helios dan Cosmos 3 layak ditinjau ulang begitu port MLX atau GGUF T2V muncul. Ketiganya berlisensi permisif tanpa ambang pendapatan, termasuk OpenMDW-1.1 untuk Cosmos ([OpenMDW](https://openmdw.ai/license/1-1/)).

## Dua prompt sederhana sudah jenuh, jadi tes pembeda butuh klip 5 detik

LTX-2.5 sudah 6/6 di kedua prompt, jadi kandidat mana pun paling banter hanya bisa menyamai. Untuk menemukan "upgrade", tes perlu menyasar area di mana LTX lemah. Data proyek ini sendiri menunjukkan area itu. Di ladder ronde 4, LTX-2.3 dengan keyframe gagal pada klip panjang 768×512: **97 frame 0/2, 121 frame 1/2, 145 frame 1/2**. Bolanya berbalik arah atau keluar frame setelah ~2 dtk ([STATUS.md lokal](/Users/dyn/AI/video-model-comparison-2026-10-29/STATUS.md)). LTX-2.5 text-only pada 5 dtk belum pernah diukur. Sebaliknya, Kandinsky, HunyuanVideo dan H3 justru dilatih untuk klip ~5 dtk (121–124 frame). Catatan riset H3 juga sudah memperingatkan bahwa klip 2 dtk berada di bawah rentang yang dimaksud.

Setiap kandidat sebaiknya diuji pada tiga sel:

1. Dua prompt lama pada 2 dtk, untuk paritas.
2. Dua prompt yang sama pada ~5 dtk.
3. Satu prompt yang lebih sulit, misalnya dua objek yang bergerak berlawanan arah.

LTX-2.5 ikut dijalankan di sel kedua dan ketiga sebagai baseline. Aturan yang sudah berlaku tetap dipakai: seed 42–44, pengukur memori yang sama (`claude_memprobe.py`, phys_footprint), dan run serial. Semua angka in-house berasal dari MacBook Pro M4 Pro, jadi jalankan LTX-2.5 sekali di Mac mini M5 Pro sebagai baseline baru sebelum membandingkan waktu.

Urutan kerja yang realistis untuk disk:

1. File Wan 2.2 lama sudah dihapus permanen saat ronde 1 (tidak ada di Trash), jadi uji ulang Wan perlu unduh ulang 18,15 GB.
2. Jalankan HunyuanVideo. Uji ini bisa dimulai bahkan sebelum Trash dikosongkan, asalkan encoder GGUF diterima.
3. Jalankan Kandinsky (~24,5 GB), lalu pensiunkan file-nya.
4. Jalankan uji ulang Wan.
5. Jalankan H3 terakhir, karena paling besar dan paling lama.

Kandinsky dan HunyuanVideo sama-sama memakai Qwen2.5-VL-7B, tetapi dalam format berbeda (shard Diffusers versus file tunggal ComfyUI). Jadi kemungkinan besar file encoder itu tidak bisa dipakai bersama (E). Skrip "encode → simpan embedding → keluar" yang dibuat untuk Kandinsky bisa dipakai ulang untuk kandidat mana pun, karena di Mac 24 GB fase encoder teks yang menentukan puncak memori. Hal yang sama terlihat di LTX-2.5: puncak 15,45 GiB-nya terjadi saat Gemma-4 dimuat, sedangkan selama generasi video memorinya hanya 5,6–7,7 GiB ([STATUS.md lokal](/Users/dyn/AI/video-model-comparison-2026-10-29/STATUS.md)).

## Kesimpulan

Untuk perusahaan sebesar Taiwan Mobile, kemenangan yang paling mungkin dari eksperimen ini adalah di sisi lisensi, bukan kualitas. Kandidat dengan lisensi paling bersih (Kandinsky MIT, Wan Apache-2.0) justru paling sedikit punya bukti di Mac. Jadi eksperimen berikutnya pada dasarnya membeli informasi kelayakan. Model MIT yang menyamai 6/6, meskipun dua kali lebih lambat, sudah merupakan upgrade bisnis, karena menghapus kebutuhan Paid Commercial Use Agreement dengan Lightricks. Sebaliknya, model dengan bukti kualitas terkuat (H3) terkunci oleh lisensi dan kecepatan, sehingga nilainya hanya sebagai penanda batas atas.

Pelajaran teknisnya: di Mac 24 GB, jumlah parameter DiT adalah petunjuk yang menyesatkan. DiT 3B Kandinsky diperkirakan tetap lebih lambat dari LTX-2.5 22B. Penyebabnya, VAE 8× menghasilkan ~20 ribu token untuk klip 2 dtk, dan encoder 7B-nya sendiri sudah memenuhi hampir seluruh working set. Yang menentukan muat atau tidaknya sebuah model adalah ukuran encoder teks dan disiplin memuat secara bertahap. Yang menentukan kecepatannya adalah jumlah token dan jumlah langkah. Karena itu, distill 4–10 langkah dan skrip dua fase lebih penting daripada memilih model "kecil".
