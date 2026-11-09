# Laporan Video: Reels Ebook "Berhenti Menebak, Mulai Menghitung"

- File video: books/berhenti-menebak-mulai-menghitung/promo/reels-ebook-karbon-hutan.mp4 (repo metashape-scripts)
- Format: 1080x1920 (9:16), 30 fps, 20 detik, H.264 yuv420p bt709, tanpa audio, 11,5 MB
- Jenis: promo ebook, tanpa voice-over
- Audio: revisi 1 menghapus semua SFX. Video sengaja tanpa suara; musik dipilih dari pustaka musik Instagram saat upload
- Dibuat: 9 November 2026 · Naskah & storyboard: Alex · Video: Wahyu

## Isi video
| # | Waktu | Isi |
|---|---|---|
| 1 | 0–3 dtk | Hutan berkabut + drone: "Hutan ini simpan karbon berapa ton?" → "Masih jawab kira-kira?" |
| 2 | 3–7 dtk | Tim lapangan mengukur pohon: "Ngukur pohon satu per satu?" → "Ratusan hektare bisa makan waktu berminggu-minggu." |
| 3 | 7–12 dtk | Tajuk dengan lingkaran deteksi → peta karbon: "Drone menghitung pohonnya dari udara" → "Lalu jadi peta ton karbon per hektare" |
| 4 | 12–16,5 dtk | Sampul ebook masuk: "10 bab, dari terbang sampai laporan karbon" |
| 5 | 16,5–20 dtk | "Berhenti menebak. Mulai menghitung." + tombol "DM ya, aku kirim link ebooknya" |

## Aset yang dipakai
| File | Sumber |
|---|---|
| cover-art, cover, bab05, bab07, bab09 | Ilustrasi Kira (Nano Banana 2.1) dari ebook |
| Font Archivo, Newsreader | @fontsource, lisensi SIL OFL |
| sfx/pop, tick, impact, rise, chime | Dibikin Wahyu pakai kode (bebas lisensi) |
| sfx/whoosh, shutter-modern | Dibikin pakai kode juga (remotion.media diblokir jaringan sesi), bebas lisensi |

## Cek teknis
- Durasi 20,00 dtk, 1080x1920, yuv420p bt709, tanpa track audio (render --muted).
- SFX masih tersimpan di kode (`USE_SFX = false` di src/ReelsEbookKarbon.tsx); ubah ke true untuk memasang lagi.

## Cara revisi & render ulang
Project Remotion ada di folder scratchpad sesi (sementara). Teks ada di bagian atas `src/scenes/Scenes.tsx`, daftar SFX di `src/ReelsEbookKarbon.tsx`.
1. `npm run studio` untuk preview
2. `npm run render` untuk render ulang

---

# Versi Story Instagram

- File video: books/berhenti-menebak-mulai-menghitung/promo/story-ebook-karbon-hutan.mp4
- Format: 1080x1920 (9:16), 30 fps, 15 detik (satu potongan Story), H.264 yuv420p bt709, tanpa audio, 10 MB
- Komposisi Remotion: `StoryEbookKarbon` (src/scenes/Story.tsx), render: `npm run render:story`
- Zona aman Story: teks mulai y 290 (di bawah nama akun), elemen terbawah (panah) berhenti di y ±1510 (di atas kolom "Kirim pesan")

| # | Waktu | Isi |
|---|---|---|
| 1 | 0–3 dtk | Hutan berkabut + drone: "Hutan ini simpan karbon berapa ton?" → "Masih jawab kira-kira?" |
| 2 | 3–6 dtk | Tim lapangan mengukur pohon: "Ngukur pohon satu per satu?" |
| 3 | 6–10 dtk | Tajuk + lingkaran deteksi → peta karbon: "Drone menghitung pohonnya dari udara" → "Jadi peta ton karbon per hektare" |
| 4 | 10–12,5 dtk | Sampul ebook masuk |
| 5 | 12,5–15 dtk | "Berhenti menebak. Mulai menghitung." + "Balas story ini, aku kirim link-nya" + panah ke kolom pesan |
