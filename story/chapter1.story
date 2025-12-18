\scene start
$bold SELAMAT DATANG DI SEKOLAH MISTERI
\divider ~
🎹 NOT MUSIK: C-D-E-F-G-A-B
\divider =
Kamu berdiri di depan Sekolah Menengah Atas "Matahari Terbenam".
Sekolah ini telah ditinggalkan selama 10 tahun setelah insiden misterius.
Kini, karena tantangan dari teman-temanmu, kamu memutuskan untuk menjelajahinya.

\pause

\choice "Masuk melalui gerbang utama" goto main_gate
\choice "Cari pintu belakang" goto back_entrance
\choice "Lihat papan pengumuman" goto notice_board

\scene main_gate
\clear
GERBANG UTAMA terkunci. Tapi ada kertas tergantung di pagar.

\divider -
$red TULISAN BERDARAH: "Hanya yang berani yang akan selamat"

\choice "Coba buka kunci" goto lock_puzzle
\choice "Cari alternatif lain" goto window_search

\scene lock_puzzle
\clear
Kamu menemukan gembok dengan kombinasi angka.
Tapi ada permainan hangman di sampingnya...

\hangman words("combination","password","security") win=lock_open lose=lock_failed

\scene lock_open
🎉 Kombinasi terbuka! Kamu mendapatkan: KUNCI GERBANG

\progress 2 "Membuka gerbang..."
Gerbang berderit terbuka. Kamu memasuki halaman sekolah.

\goto courtyard

\scene lock_failed
\clear
💀 Gembok tidak terbuka! Tiba-tiba alarm berbunyi!

\loading 3 "Lari menghindari penjaga..."
Kamu bersembunyi di semak-semak dan menemukan jalan alternatif.


\scene courtyard
\clear
Halaman sekolah penuh dengan rumput liar dan pohon-pohon besar.
Di tengah ada patung kepala sekolah yang sudah rusak.

\pause

$yellow SUARA GEMERISIK: "Siapa di sana?"

\choice "Mendekati patung" goto statue_inspect
\choice "Masuk gedung utama" goto main_building
\choice "Jelajari taman" goto garden_maze

\scene garden_maze
\clear
Taman belakang ternyata adalah labirin tanaman yang sangat rumit!

\maze map_name="forest" description="Cari jalan keluar dari labirin taman!" win=maze_escape lose=maze_lost

\scene maze_escape
\clear
🎉 Kamu berhasil keluar dari labirin!
Di ujung labirim kamu menemukan gazebo tua dengan peti.

\progress 2 "Membuka peti..."
Kamu mendapatkan: SENTER TUA

\choice "Nyalakan senter" goto with_flashlight
\choice "Kembali ke halaman" goto courtyard

\scene maze_lost
\clear
💀 Kamu tersesat di labirin! Suara aneh semakin dekat...

\loading 2 "Mencari jalan keluar..."
Tiba-tiba kamu melihat cahaya dari sebuah gubuk kecil.


\scene main_building
\clear
LORONG UTAMA gelap dan berdebu. 
Jendela-jendela pecah membuat cahaya bulan masuk dengan samar.

\divider ~
$cyan BISIKAN: "Jangan sendirian... jangan..."

\choice "Pergi ke perpustakaan" goto library
\choice "Cek ruang kelas" goto classroom
\choice "Naik ke lantai 2" goto second_floor

\scene library
\clear
PERPUSTAKAAN penuh dengan buku-buku berserakan.
Di meja utama ada buku terbuka dengan tulisan aneh.

\hangman words("ancient","forbidden","knowledge") win=book_decoded lose=book_reject

\scene book_decoded
\clear
📖 Kamu berhasil memecahkan kode! Buku itu berisi ritual kuno.

\progress 2 "Membaca buku..."
Kamu belajar: Mantra Perlindungan Tingkat 1

Kamu mendapatkan: BUKU MANTRA

\choice "Cari buku lainnya" goto more_books
\choice "Keluar perpustakaan" goto main_building

\scene book_reject
\clear
📚 Buku itu menolakmu! Tiba-tiba rak buku bergerak...

\loading 2 "Menghindari rak buku yang bergerak..."
Kamu terjebak di sudut perpustakaan!

\battle enemy="Living Books" hp=50 strength=8 win=escape_books lose=trapped_in_library

\scene second_floor
\clear
LORONG LANTAI 2 lebih gelap. 
Ada beberapa pintu dengan tulisan aneh.

$red PERINGATAN: Kamu mendengar langkah kaki dari ujung koridor!

\choice "Masuk Laboratorium" goto lab_challenge
\choice "Masuk Ruang Musik" goto music_room
\choice "Lari ke bawah" goto main_building

\scene lab_challenge
\clear
LABORATORIUM penuh dengan peralatan sains rusak.
Di papan tulis ada persamaan kimia yang harus dipecahkan.

\hangman words("experiment","chemical","formula") win=lab_success lose=lab_explosion

\scene lab_success
\clear
🧪 Kamu memecahkan persamaan! Sebuah lemari terbuka...

\progress 1 "Mengambil isi lemari..."
Kamu mendapatkan: JAKET LAB + BATERAI

\choice "Gabungkan dengan senter" goto upgrade_flashlight
\choice "Lanjut eksplorasi" goto lab_continue

\scene lab_explosion
\clear
💥 Eksperimen meledak! Asap tebal memenuhi ruangan.

\loading 3 "Mencari jalan keluar..."
Kamu berlari keluar tapi terjatuh di tangga...



\scene music_room
\clear
RUANG MUSIK penuh dengan alat musik berdebu.
Piano tua tiba-tiba berbunyi sendiri!

\divider ~
🎹 NOT MUSIK: C-D-E-F-G-A-B

\choice "Coba mainkan" goto piano_puzzle
\choice "Keluar dengan cepat" goto second_floor

\scene piano_puzzle
\clear
Kamu harus memainkan melodi yang benar...

\hangman words("melody","harmony","rhythm") win=piano_solved lose=ghost_angry

\scene piano_solved
\clear
🎶 Piano memainkan melodi indah! Sebuah lantai rahasia terbuka.

\progress 2 "Turun ke ruang bawah tanah..."
\goto basement_secret

\scene ghost_angry
\clear
👻 Hantu pemain piano marah! Dia menyerangmu!

\battle enemy="Ghost Pianist" hp=70 strength=12 win=defeat_pianist lose=piano_death

\scene basement_secret
\clear
RUANG BAWAH TANAH rahasia! Ini adalah ruang ritual.
Di tengah ada altar dengan simbol aneh.

\divider =
$bold yellow FINAL CHALLENGE: Hadapi Penjaga Sekolah


\scene final_confrontation
\clear
🎊 Kamu berhasil mencapai ruang inti!
Di hadapanmu berdiri PENJAGA SEKOLAH yang legendaris.

\progress 3 "Persiapan pertarungan terakhir..."
$bold red PERTARUNGAN AKHIR DIMULAI

\battle enemy="The School Keeper" hp=100 strength=20 win=true_ending lose=bad_ending draw=neutral_ending surrender=escape_ending

\scene true_ending
\clear
🌟 KAMU MENANG! 🌟

\divider =
Setelah mengalahkan Penjaga Sekolah, kutukan terangkat.
Sekolah kembali normal dan semua rahasia terungkap.

\progress 5 "Epilog..."
Kamu menjadi legenda di kotamu dan mendapatkan:

1. 🏆 TROFI PENJELAJAH
2. 📜 SERTIFIKAT KEBERANIAN
3. 💰 HADIAH UANG TUAI

\goto credits

\scene bad_ending
\clear
💀 GAME OVER

\divider =
Kamu dikalahkan oleh Penjaga Sekolah.
Kini jiwamu menjadi bagian dari sekolah selamanya...

\pause

\choice "Coba lagi dari checkpoint" goto checkpoint_reload
\choice "Keluar game" goto exit_game

\scene neutral_ending
\clear
🤝 HASIL SERI

Kamu dan Penjaga Sekolah sepakat berdamai.
Dia mengizinkanmu pergi dengan syarat tidak kembali.

Kamu mendapatkan: PERJANJIAN DAMAI

\goto credits

\scene escape_ending
\clear
🏃 KABUR!

Kamu memilih untuk menyerah dan kabur dari sekolah.
Tapi setidaknya kamu selamat...

\progress 2 "Lari keluar sekolah..."
Kamu mendapatkan: PELAJARAN HIDUP

\goto credits

\scene credits
\clear
$bold CREDITS

\divider =
Game Created By: [Nama Kamu]
Story & Programming: AI Assistant
Testing: Player

\progress 3 "Menghitung statistik..."

STATISTIK PERMAINAN:
- Maze diselesaikan: [count]
- Hangman dimenangkan: [count]  
- Pertarungan dimenangkan: [count]
- Item dikumpulkan: [count]

\pause

TERIMA KASIH TELAH BERMAIN!