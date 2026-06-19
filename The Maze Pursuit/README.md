# 🐱🐭 Tom & Jerry: The AI Maze Chase

Sebuah game strategi *turn-based* berbasis grid di mana kamu bermain sebagai Jerry, berusaha melarikan diri dari sebuah labirin kompleks sambil menghindari kejaran Tom sang kucing cerdas. Game ini dibangun menggunakan React, TypeScript, dan Tailwind CSS, menonjolkan penerapan berbagai algoritma klasik untuk prosedural map dan kecerdasan buatan (AI) musuh.

---

## 🎮 Cara Bermain (Gameplay Overview)

- **Objektif:** Temukan dan capai pintu keluar (Exit, ubin hijau) sebelum Tom menangkapmu.
- **Kontrol:** Klik pada ubin lantai yang terlihat *(visible floor)* dalam radius pandangmu. Jerry akan secara otomatis mencari jalan (auto-routing) menuju ubin tersebut.
- **Fog of War:** Pandangan Jerry terbatas! Ubin di kejauhan atau yang terhalang tembok tidak akan terlihat. Kamu harus meraba-raba struktur labirin.
- **Power-ups:** Kumpulkan Keju (Cheese) yang tersebar di labirin untuk mendapat lonjakan kecepatan (Movement Points bertambah) selama beberapa turn.

---

## 🎨 Tampilan dan Antarmuka (UI/UX)

Aplikasi didesain dengan konsep **Neo-Dark Theme** menggunakan dominasi warna *indigo* pekat, dipadukan dengan aksen neon (cyan untuk Jerry, pink/merah muda untuk Tom). 

- **Dynamic Fog of War:** Lantai dan tembok di luar jarak pandang akan dikosongkan visualnya menyerupai kegelapan murni (`#05040a`), sehingga bentuk labirin benar-benar menjadi teka-teki.
- **Status Dashboard:** Sebuah *dashboard* atau *header* yang memberikan berbagai indikator secara *real-time*:
  - Giliran siapa yang sedang berjalan (Tom atau Jerry).
  - Status *State Machine* dari AI Tom (apakah sedang *Patrol*, *Search*, atau *Chase*).
  - Peringatan instan saat *Global Scan* dilakukan oleh Tom.
- **Developer Mode:** Terdapat tombol *Dev Mode* dengan ikon *refresh spin*. Saat diaktifkan:
  - *Fog of War* akan lenyap, menampilkan arsitektur penuh labirin beserta tembok dan rute buntu.
  - Visi Tom terungkap dengan visualisasi rute (garis/titik panduan warna pink) yang menunjukkan pergerakan algoritma pencarian jalan Tom menuju Jerry, posisiterakhir, atau target patrolinya.

---

## 🧠 Arsitektur Algoritma

Game ini sangat bergantung pada beberapa algoritma Computer Science untuk memastikan labirin yang dihasilkan tidak pernah sama, pergerakan yang mulus, dan musuh yang mengancam.

### 1. Algoritma Pembuatan Labirin (Maze Generation)
Dibuat menggunakan prosedur di `generateRandomMaze`:
- **Randomized Prim's Algorithm:** Algoritma ini pertama mengukir grid solid secara iteratif menggunakan daftar dinding potensial. Sebuah area mulai dari grid diinisialisasi terbuka, kemudian algoritma akan menandai dinding-dinding sekitarnya. Algoritma memilih secara acak salah satu dinding untuk dipecah yang akan mengarah ke area yang belum di-visit, sehingga menghasilkan labirin yang terhubung tanpa batas mati yang tidak dapat diakses (Perfect Maze). Algoritma ini secara natural membentuk jalur labirin pendek yang banyak bercabang (highly branching).
- **Loop / Dead-end Carving:** Labirin "sempurna" (tanpa putaran/loop) terkadang kurang menantang atau mudah membuat pemain terjebak. Script kemudian secara acak menghancurkan sebagian dinding `(width * height) / 30` untuk memunculkan jalan memutar (loops) dan beberapa jalan buntu yang dikontrol.
- **Placement Algoritma:** 
  - *Exit (Pintu Keluar):* Ditempatkan di ubin sudut/pinggir (Edge Tiles) terjauh dari posisi awal Jerry.
  - *Tom & Cheese:* Di-spawn pada titik-titik yang jarak relatifnya proporsional terhadap Jerry (menggunakan fungsi sortir jarak terbalik).

### 2. Algoritma Jerry (Pemain)
- **Grid Raycasting / Line of Sight (LoS):** Menghitung tile mana saja yang bisa dilihat oleh Jerry di sekelilingnya berdasarkan *radius (sight)*. Jika ada objek batu/wall di tengah, garis pandang akan terpotong sehingga ubin di belakang batu tidak terlihat.
- **Breadth-First Search (BFS):** Saat pemain mengklik sebuah tujuan, agen Jerry menggunakan algoritma BFS konvensional untuk mencari lintasan terpendek antar ubin pada array matriks, menghindari tembok, dan menghasilkan rute klik `jerryPath` langkah-demi-langkah.

### 3. Algoritma Tom (Kecerdasan Buatan Musuh yang Sangat Kompleks)
Sistem kecerdasan Tom mengkombinasikan perilaku kontekstual (*Finite State Machine*) dan taktik pathfinding berlapis:

**Finite State Machine (FSM) Tom:**
1. **Patrol:** Berjalan mengitari grid secara acak atau menuju titik patroli random menggunakan **BFS**.
2. **Search:** Apabila Tom kehilangan pandangan terhadap Jerry atau mendengar suara, dia berganti menjadi Search, berjalan (dengan **BFS**) menuju koordinat "jejak/suara terakhir" `lastKnownJerryPos`.
3. **Chase:** Mode aggro penuh di mana Tom melihat Jerry dan aktif memburunya dengan menggunakan skor matriks evaluasi **Minimax**.

**Intelijen Kognitif dan Perseptual Tom:**
- **Sight (Penglihatan):** Mirip dengan Jerry, jika rute penglihatan (Line of Sight) antara koordinat Tom dan Jerry terhubung tanpa terhalang dinding, Tom memicu transisi state ke `Chase` secara instan.
- **Super Hearing (Pendengaran Jarak Jauh):** Meskipun terpotong dinding, algoritma secara matematis mengecek selisih absolut jarak *Manhattan Distance*. Jika jarak <= 7 tile, Tom "mendengar" pergerakan lalu beralih ke state `Search` mengarah ke koordinat tersebut.
- **Persistent Memory:** Jika *Line of Sight* terputus saat mengejar (`Chase`), Tom tidak terkena "amnesia". Terprogram agar Tom menyimpan `jerry.pos` saat ini ke `lastKnownJerryPos` sehingga Tom menelusuri sudut tembok tempat kamu terakhir mengintip, lalu memastikannya sebelum kembali `Patrol`.
- **Global Scan (The Omni-Radar):** Agar pemain tidak bisa kemah (camping) selamanya. Memiliki *cooldown counter* setiap 7 giliran sekali (`turn % 7 === 0`), mendadak koordinat asli Jerry dioverwrite secara paksa ke memori Tom. Sistem UI akan merespon peringatan *"SCANNING!"*.

**Kecepatan Basis (Movement Points):** Keduanya dirancang memiliki *Base Speed 2 MP* yang mengartikan game ini *fair* dan bertumpu pada kelihaian manuver ruang serta pemanfaatan power-up *(Cheese)* yang akan me-nol/mereset MP lawan jika digunakan terampil.

---

## 🛠️ Stack Teknologi
- **Core:** React 18
- **Language:** TypeScript (Strict Mode)
- **Bundler:** Vite
- **Styling:** Tailwind CSS (beserta implementasi drop-shadows & inset-shadow glow / efek neon)
- **Icons:** Lucide-React

## 🚀 Instalasi & Menjalankan Lokal

```bash
# Instal dependensi
npm install

# Jalankan server pengembangan
npm run dev
```

Masuk ke `http://localhost:3000` (atau port setara) untuk mulai bermain. Gunakan kursor/tap untuk berinteraksi di dalam labirin. Semoga selamat dari kejaran Tom!
