# Outline: Berhenti Menebak, Mulai Menghitung
Stok Karbon Hutan dari Data Drone · Ramadhan Adi Pratama

Pembaca: pilot drone pemula dan orang kehutanan.
BEFORE: bisa terbang atau paham hutan, tapi bingung mengubah foto udara jadi angka karbon; mengira harus mengukur pohon satu per satu.
AFTER: bisa merencanakan terbang, membuat ortofoto/DSM/CHM, menghitung pohon, mengubahnya jadi biomassa, ton karbon, dan ton CO₂, lalu melaporkannya.
Gaya: santai, sapaan "kamu", penulis sebagai ahli perhitungan karbon berbasis tree counting + fotogrametri.
Aturan tiap bab: ada gambar ilustrasi yang jelas, ditutup bagian "Kesimpulan Bab".

Istilah baku (jaga konsisten):
- tree counting = penghitungan pohon
- ortofoto, DSM (model permukaan), DTM (model tanah), CHM (model tinggi tajuk)
- biomassa atas tanah (AGB), biomassa bawah tanah (BGB)
- fraksi karbon 0,47; konversi C ke CO₂ dikali 44/12
- plot lapangan / plot sampel

## Bab 1: Karbon Hutan Bisa Dihitung dari Udara
Ringkasan: kenapa karbon hutan penting, di mana karbon disimpan, dan bagaimana drone + tree counting memotong pekerjaan lapangan.
Tujuan: pembaca paham gambaran besar alur "foto, pohon, biomassa, karbon".
Gambar: alur besar dari drone sampai ton CO₂.

## Bab 2: Rumus Dasar dari Pohon ke Ton CO₂
Ringkasan: biomassa, persamaan alometrik, fraksi karbon, dan konversi ke CO₂, dengan contoh menghitung satu pohon.
Tujuan: pembaca bisa menghitung karbon satu pohon dengan tangan.
Gambar: tangga konversi pohon, biomassa, karbon, CO₂.

## Bab 3: Perlengkapan dan Software yang Kamu Butuhkan
Ringkasan: drone, GCP, alat lapangan, dan software pengolahan (Metashape, QGIS, alat tree counting).
Tujuan: pembaca bisa menyiapkan paket alat minimal dan tahu fungsi masing-masing.
Gambar: peta perlengkapan lapangan dan kantor.

## Bab 4: Merencanakan Terbang untuk Hutan
Ringkasan: GSD, ketinggian, overlap tinggi, waktu terbang, dan jebakan khas hutan (tajuk bergoyang, bayangan).
Tujuan: pembaca bisa membuat rencana terbang yang datanya layak untuk tree counting.
Gambar: perbandingan overlap dan GSD.

## Bab 5: Plot Lapangan, Kunci Kalibrasi
Ringkasan: kenapa drone tetap butuh plot lapangan, cara membuat plot, mengukur diameter, tinggi, jenis, dan berat jenis kayu.
Tujuan: pembaca bisa merancang dan mengambil data plot lapangan yang benar.
Gambar: tata letak plot dan cara mengukur diameter setinggi dada.

## Bab 6: Mengolah Foto Jadi Ortofoto, DSM, DTM, dan CHM
Ringkasan: alur fotogrametri di Metashape, cara mendapatkan model tanah di hutan rapat, dan membuat CHM.
Tujuan: pembaca bisa menghasilkan ortofoto dan CHM dari foto drone.
Gambar: potongan DSM, DTM, dan CHM.

## Bab 7: Tree Counting, Menghitung Pohon dari Udara
Ringkasan: metode puncak lokal pada CHM, segmentasi tajuk, dan deteksi berbasis AI, plus cara menguji akurasinya.
Tujuan: pembaca bisa menghitung pohon dan menilai akurasinya dengan angka.
Gambar: CHM dengan titik puncak pohon dan batas tajuk.

## Bab 8: Dari Tinggi dan Tajuk ke Biomassa
Ringkasan: menghubungkan data drone (tinggi, lebar tajuk) dengan data plot lewat regresi, lalu menghitung biomassa tiap pohon.
Tujuan: pembaca bisa membangun model sederhana dari data drone ke biomassa.
Gambar: grafik hubungan lebar tajuk dan diameter.

## Bab 9: Stok Karbon Seluruh Area dan Ketidakpastiannya
Ringkasan: menjumlahkan karbon semua pohon, menambahkan biomassa akar, menghitung per hektar, dan menyatakan rentang ketidakpastian.
Tujuan: pembaca bisa menyajikan total karbon area beserta tingkat keyakinannya.
Gambar: peta kepadatan karbon per hektar.

## Bab 10: Laporan Karbon yang Dipercaya dan Langkah Berikutnya
Ringkasan: isi laporan, peta, pemantauan berkala, batasan metode, dan peluang pekerjaan di bidang karbon.
Tujuan: pembaca bisa menyusun laporan karbon lengkap dan tahu cara mengembangkan layanannya.
Gambar: contoh tata letak halaman laporan.
