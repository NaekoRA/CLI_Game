\scene start
\clear
$yellow ===============================
$yellow         BOSS BATTLE
$yellow ===============================

Kamu bertemu dengan Hantu Guru yang menyeramkan!
Dia ingin mengujimu dengan pertarungan.

\battle player_hp=120 enemy_hp=150 player_name="Kamu" enemy_name="Hantu Guru"

Setelah pertarungan sengit...
\pause

$green Kamu berhasil melewati ujian tersebut!
Hantu Guru memberikan kunci rahasia.

\goto next_scene

\scene hard_battle
\clear
$red ===============================
$red        BATTLE FINAL
$red ===============================

Ini adalah pertarungan terakhirmu!
Lawan sangat kuat, hati-hati!

\battle player_hp=150 enemy_hp=200 player_name="Pahlawan" enemy_name="Bayangan Gelap"