# Pipeline & Progress Development "Tom & Jerry Maze Game"

Berikut adalah rangkuman pipeline dan progress dari awal pengembangan hingga saat ini:

## Fase 1: Setup & Inisialisasi Game Dasar
- [x] Inisialisasi proyek React dengan TypeScript dan Vite.
- [x] Konfigurasi Tailwind CSS untuk styling UI dan komponen board.
- [x] Pembuatan generator map prosedural (`generateRandomMaze`) yang menghasilkan grid berisi *wall*, *floor*, dan jalan keluar (*exit*).

## Fase 2: Mekanik Pemain (Jerry)
- [x] Implementasi sistem rendering map secara grid.
- [x] Pathfinding untuk pergerakan Jerry menggunakan representasi arah dan algoritma *Breadth-First Search* (BFS) agar Jerry dapat otomatis mencari rute menuju block yang diklik.
- [x] Penambahan sistem Movement Points (MP), di mana Jerry pada awalnya diset untuk base speed 2 MP.
- [x] Fitur pengambilan item (seperti keju) yang memberikan power-up atau bonus bergerak pada Jerry (menambah MP sementara).

## Fase 3: Mekanik AI Musuh (Tom)
- [x] Inisialisasi AI berkonsep *Finite State Machine (FSM)* untuk Tom dengan state: `patrol`, `search`, dan `chase`.
- [x] Penambahan algoritma *Minimax* saat Tom memasuki state `chase` untuk mengejar target yang terlihat.
- [x] Penambahan *Breadth-First Search* (BFS) untuk pencarian rute pada saat Tom sedang patroli.
- [x] Implementasi kecepatan gerakan awal Tom (yang lalu disesuaikan kembali agar sama dengan Jerry yaitu base speed 2 MP).

## Fase 4: Fitur *Fog of War* & Peningkatan Visual Map
- [x] Pembuatan logic *Line of Sight* untuk membuat fitur *Fog of War* (visibilitas tile tertentu berdasarkan posisi Jerry).
- [x] Penyesuaian lokasi *Exit* agar berada acak di pojokan map.
- [x] Peningkatan visual blok pada map untuk secara jelas membedakan letak tembok (*wall*) dan lantai pijakan (*floor*) dalam jarak pandang.
- [x] Implementasi tembok yang disembunyikan dalam *fog of war* di luar radius pandang Jerry agar bentuk asli maze tidak langsung terlihat.
- [x] Penyesuaian algoritma map generation untuk menambah jalan buntu/dead-ends (*loops control*).

## Fase 5: Peningkatan Kecerdasan Buatan (AI Tom)
- [x] **Hearing (Pendengaran):** Tom kini bisa mendeteksi suara pergerakan Jerry di sekitarnya dalam radius 7 blok, bahkan di balik tembok. Tom kemudian akan merespon dengan beralih ke state `search`.
- [x] **Global Scanning:** Tom memiliki cooldown scan (setiap 7 giliran sekali) di mana posisi aslimu (Jerry) akan terdeteksi di manapun kamu berada.
- [x] **Memory Tracking:** Ketika Tom melihat Jerry dan Jerry berhasil menghilang di balik *fog of war*, Tom tidak akan kebingungan dan akan bergerak lurus ke koordinat/lokasi terakhir kamu terlihat untuk menelusurinya `lastKnownJerryPos`.

## Fase 6: *Developer Mode* & UI Improvements (Progress Saat Ini)
- [x] Penambahan panel informasi sidebar/header untuk UI AI Intelligence & status pergerakan.
- [x] **Developer Mode:** Penambahan trigger/akses 'Dev Mode' menggunakan animasi toggle putar.
- [x] Mode developer menonaktifkan *Fog of War* secara full, sehingga isi seluruh peta dapat terlihat tanpa limitasi jarak pandang.
- [x] Mode developer memvisualisasikan garis proyeksi target/pathing algoritma AI yang sedang dipikirkan oleh Tom menuju Jerry.

---

### Rencana Selanjutnya Momen Berikutnya (Ide Refleksi ke Depan)
- Integrasi tingkatan level (semakin sulit / ukuran dari maze bertambah).
- Tom bisa jadi diperbanyak seiring bertambah susah nya level?
- Penambahan efek suara saat Tom menggunakan radar scanning atau tertangkap, dll.
