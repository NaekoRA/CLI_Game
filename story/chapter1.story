\scene start
$yellow ================================
$yellow         CHAPTER 1: AWAL MISTERI
$yellow ================================

Hari sudah larut. Kamu adalah siswa yang tertinggal di sekolah untuk mengerjakan tugas kelompok.
$red Tiba-tiba listrik padam! 
Semua menjadi gelap gulita.

\choice "Cari senter di ruang guru" goto cari_senter
\choice "Tinggal di kelas dan tidur" goto tidur_kelas  
\choice "Coba cari jalan keluar" goto cari_keluar

\scene cari_senter
Kamu berjalan pelan menuju ruang guru.
$green Di mekar guru, kamu menemukan senter!
Tapi baterainya hampir habis.

\choice "Ambil senter dan explore" goto explore_dengan_senter
\choice "Tinggalkan senter, lanjut tanpa cahaya" goto tanpa_senter
\choice "Kembali ke kelas" goto kembali_kelas

\scene tidur_kelas
Kamu memutuskan untuk tidur di kelas.
$red Dalam mimpi, kamu mendengar suara tangisan...
\bold "BANGUN! BANGUN!"

\choice "Bangun dan periksa" goto bangun_periksa
\choice "Terus tidur" goto terus_tidur
\choice "Berteriak minta tolong" goto berteriak

\scene cari_keluar
Kamu mencoba mencari jalan keluar dalam gelap.
$yellow Kamu tersandung sesuatu yang lembut...
\bold "AAAAAKKKK!"

\choice "Lari sekencangnya" goto lari_ketakutan
\choice "Periksa apa yang tersandung" goto periksa_tersandung
\choice "Diam dan dengarkan" goto diam_dengarkan

\scene explore_dengan_senter
Dengan senter, kamu menjelajahi koridor.
$green Kamu menemukan peta sekolah!
Tapi senter semakin redup.

\choice "Lihat peta dan cari exit" goto lihat_peta
\choice "Cari baterai di gudang" goto cari_baterai
\choice "Kembali ke tempat aman" goto tempat_aman

\scene tanpa_senter
Kamu memutuskan menjelajah tanpa cahaya.
$red Dalam gelap, kamu mendengar langkah kaki...
Seseorang atau sesuatu mendekat!

\choice "Bersembunyi di locker" goto sembunyi_locker
\choice "Hadapi dan tanya siapa itu" goto hadapi_datang
\choice "Lari ke arah suara" goto lari_ke_suara

\scene kembali_kelas
Kamu kembali ke kelas.
$yellow Tapi sekarang pintunya terkunci!
Kamu terjebak di luar.

\choice "Pecahkan jendela" goto pecahkan_jendela
\choice "Cari kunci" goto cari_kunci_kelas
\choice "Tinggal di koridor" goto tinggal_koridor

\scene bangun_periksa
Kamu bangun dan melihat sekeliling.
$red Ada bayangan di pintu kelas!
Bayangan itu perlahan mendekat.

\choice "Sembunyi di bawah meja" goto sembunyi_meja
\choice "Tanya 'Siapa di sana?'" goto tanya_siapa
\choice "Lempar buku ke bayangan" goto lempar_buku

\scene terus_tidur
Kamu memutuskan terus tidur.
$green Pagi datang, kamu selamat!
Tapi ada coretan darah di whiteboard...

\goto ending_selamat_tapi_aneh

\scene berteriak
Kamu berteriak sekencangnya.
$red Suara itu berhenti... lalu tertawa!
\bold "TERIAK LEBIH KERAS LAGI!"

\choice "Terus berteriak" goto terus_berteriak
\choice "Diam dan sembunyi" goto diam_sembunyi
\choice "Lari keluar kelas" goto lari_keluar_kelas

\scene lari_ketakutan
Kamu lari tanpa arah dalam gelap.
$yellow Tiba-tiba kamu menabrak sesuatu yang dingin...
\bold "KENAPA LARI? AKU HANYA INGIN BERTEMAN"

\choice "Minta maaf" goto minta_maaf
\choice "Terus lari" goto terus_lari
\choice "Tawarkan pertolongan" goto tawarkan_tolong

\scene periksa_tersandung
Kamu menyalakan ponsel untuk melihat...
$red Itu adalah boneka yang rusak dan berdarah!
Matanya seolah menatapmu.

\choice "Ambil boneka" goto ambil_boneka
\choice "Langkahi dan lanjut" goto langkahi_boneka
\choice "Buang boneka" goto buang_boneka

\scene diam_dengarkan
Kamu diam dan mendengarkan.
$green Kamu mendengar suara air menetes...
Dan ada bisikan: "Tolong... aku terjebak..."

\choice "Ikuti suara bisikan" goto ikuti_bisikan
\choice "Cari sumber air" goto cari_sumber_air
\choice "Abaikan dan cari exit" goto cari_exit

\scene lihat_peta
Dengan peta, kamu menemukan ada exit di belakang sekolah.
$yellow Tapi harus melewati laboratorium yang gelap.

\choice "Lewati laboratorium" goto lewati_lab
\choice "Cari jalan lain" goto cari_jalan_lain
\choice "Tinggal sampai pagi" goto tunggu_pagi

\scene cari_baterai
Kamu menuju gudang untuk mencari baterai.
$red Gudang penuh dengan barang-barang aneh...
Dan bau anyir.

\choice "Cari baterai cepat" goto cari_cepat
\choice "Periksa sumber bau" goto periksa_bau
\choice "Keluar dari gudang" goto keluar_gudang

\scene tempat_aman
Kamu kembali ke aula.
$green Di sana kamu menemukan telepon darurat!
Tapi tidak ada sinyal.

\choice "Coba telepon tetap" goto coba_telepon
\choice "Tinggal di aula" goto tinggal_aula
\choice "Tulis pesan darurat" goto tulis_pesan

\scene sembunyi_locker
Kamu bersembunyi di locker.
$red Locker itu terkunci dari luar!
Kamu terjebak!

\choice "Teriak minta tolong" goto teriak_dalam_locker
\choice "Coba buka paksa" goto buka_paksa_locker
\choice "Tunggu sampai pagi" goto tunggu_pagi_locker

\scene hadapi_datang
Kamu menghadapi sosok yang mendekat.
$yellow Itu adalah satpam sekolah!
Tapi matanya... kosong.

\choice "Tanya kenapa matanya kosong" goto tanya_mata_kosong
\choice "Minta tolong keluar" goto minta_tolong_satpam
\choice "Lari dari satpam" goto lari_dari_satpam

\scene lari_ke_suara
Kamu lari ke arah suara.
$green Kamu menemukan siswa lain yang juga terjebak!
Namanya Andi.

\choice "Ajak kerjasama" goto ajak_kerjasama
\choice "Tanya apakah dia nyata" goto tanya_nyata
\choice "Tinggalkan Andi" goto tinggalkan_andi

\scene pecahkan_jendela
Kamu memecahkan jendela kelas.
$red Alarm berbunyi! Tapi tidak ada yang datang...
Yang datang adalah... sesuatu yang hitam.

\choice "Masuk kelas lewat jendela" goto masuk_jendela
\choice "Lari dari sesuatu yang hitam" goto lari_dari_hitam
\choice "Bersembunyi" goto bersembunyi_darurat

\scene cari_kunci_kelas
Kamu mencari kunci di sekitar koridor.
$yellow Kamu menemukan kunci di bawah karpet!
Tapi ada tulisan: "JANGAN BUKA"

\choice "Gunakan kunci" goto gunakan_kunci
\choice "Buang kunci" goto buang_kunci
\choice "Bawa kunci tapi tidak digunakan" goto bawa_kunci

\scene tinggal_koridor
Kamu memutuskan tinggal di koridor.
$green Kamu menemaku kursi dan memutuskan untuk menunggu.
Tapi semakin larut, semakin dingin...

\choice "Tetap di kursi" goto tetap_kursi
\choice "Cari selimut" goto cari_selimut
\choice "Lakukan peregangan" goto lakukan_peregangan

\scene sembunyi_meja
Kamu bersembunyi di bawah meja.
$red Bayangan itu berlutut dan melihatmu!
\bold "AKU TAHU KAU DI SANA..."

\choice "Keluar dan hadapi" goto keluar_hadapi
\choice "Tetap diam" goto tetap_diam
\choice "Serang bayangan" goto serang_bayangan

\scene tanya_siapa
Kamu bertanya "Siapa di sana?"
$yellow Suara itu menjawab: "GURU BARU..."
Tapi kamu tahu tidak ada guru baru.

\choice "Tanya mata pelajaran" goto tanya_mapel
\choice "Minta tolong" goto minta_tolong_guru
\choice "Lari melalui jendela" goto lari_jendela

\scene lempar_buku
Kamu melempar buku ke bayangan.
$red Buku itu melewati bayangan!
Itu bukan benda fisik...

\choice "Coba sentuh" goto coba_sentuh
\choice "Bacakan doa" goto bacakan_doa
\choice "Terima nasib" goto terima_nasib

\scene ending_selamat_tapi_aneh
$cyan ================================
$cyan           ENDING 1: SELAMAT
$cyan ================================
Kamu selamat sampai pagi.
Tapi coretan darah di whiteboard berbunyi:
"KAMU BERHUTANG NYAWAMU PADAKU"
$red Besok malam, aku akan kembali...

\goto game_over

\scene terus_berteriak
Kamu terus berteriak.
$red Suara itu semakin dekat...
Dan sekarang kamu bisa melihatnya!
Wajahnya... tanpa mata dan mulut.

\choice "Pingsan" goto pingsan
\choice "Lawan dengan kursi" goto lawan_kursi
\choice "Terus teriak sampai kehilangan suara" goto kehilangan_suara

\scene minta_maaf
Kamu minta maaf telah menabrak.
$yellow Sosok itu tertawa: "JANGAN KHAWATIR... 
AKU SUDAH TERBIAASA DITABRAK"

\choice "Tanya siapa dia" goto tanya_siapa_dia
\choice "Tawarkan bantuan" goto tawarkan_bantuan
\choice "Pelan-pelan mundur" goto mundur_pelan

\scene ambil_boneka
Kamu mengambil boneka berdarah.
$red Boneka itu berbisik: "TERIMA KASIH...
SEKARANG KITA BISA BERMAIN SELAMANYA"

\choice "Buang boneka" goto buang_boneka_teriak
\choice "Simpan boneka" goto simpan_boneka
\choice "Tanya boneka cara keluar" goto tanya_boneka

\scene ikuti_bisikan
Kamu mengikuti suara bisikan.
$green Kamu menemukan siswa terjebak di toilet!
Dia ketakutan sekali.

\choice "Bantu keluar dari toilet" goto bantu_toilet
\choice "Tanya apa yang terjadi" goto tanya_kejadian
\choice "Curiga dan pergi" goto curiga_pergi

\scene lewati_lab
Kamu melewati laboratorium.
$red Di sana ada eksperimen yang masih berjalan...
Dan ada sesuatu yang bergerak dalam gelas.

\choice "Periksa eksperimen" goto periksa_eksperimen
\choice "Langsung lewati" goto lewati_cepat
\choice "Ambil senjata dari lab" goto ambil_senjata_lab

\scene cari_cepat
Kamu mencari baterai dengan cepat.
$yellow Kamu menemakan baterai!
Tapi juga menemukan album foto guru-guru...
Dengan mata yang dicoret.

\choice "Ambil baterai saja" goto ambil_baterai
\choice "Lihat album foto" goto lihat_album
\choice "Lapor ke polisi besok" goto lapor_polisi

\scene coba_telepon
Kamu mencoba telepon darurat.
$green Ada suara di telepon: "TEKAN 0 UNTUK BANTUAN"
Tapi ketika kamu tekan 0... tertawa.

\choice "Tekan angka lain" goto tekan_angka_lain
\choice "Bicara ke telepon" goto bicara_telepon
\choice "Hancurkan telepon" goto hancurkan_telepon

\scene game_over
$red ================================
$red            GAME OVER
$red ================================
$yellow Cerita ini akan berlanjut...
Jika kamu berani bermain lagi.

\bold "TERIMA KASIH TELAH BERMAIN!"