\scene start    
\clear
$green ===============================
$green          TUTORIAL MAZE
$green ===============================

Sebelum melanjutkan, kamu harus belajar navigasi!
Ini adalah maze sederhana untuk latihan.

\maze map_name="tutorial" description="Learn basic movement in this simple maze"

Setelah menyelesaikan maze, kamu merasa lebih percaya diri!
\goto forest_escape

\scene forest_escape
\clear
$yellow ===============================
$yellow          ESCAPE THE FOREST
$yellow ===============================

Kamu terjebak di hutan berhantu!
Cari jalan keluar sebelum ditangkap hantu penjaga!

\maze map_name="forest" description="Escape the haunted forest maze!"

\battle_branch win=selamat_dari_hutan lose=tertangkap_di_hutan

\scene school_escape  
\clear
$red ===============================
$red          SCHOOL LOCKDOWN
$red ===============================

Sekolah dikunci! Kamu harus mencari jalan keluar
dari koridor sekolah yang gelap.

Hati-hati dengan satpam yang berpatroli!

\maze map_name="school" description="Escape the school corridors!"

\battle_branch win=keluar_sekolah lose=tertangkap_satpam