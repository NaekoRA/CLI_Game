\scene start
Selamat datang di Sekolah Misteri!

\choice "Masuk ke dalam" goto hangman_challenge
\choice "Keliling halaman" goto explore_yard

\scene hangman_challenge
Kamu menemukan papan tulis dengan permainan Hangman.
Tebak kata untuk membuka pintu!

\hangman words("secret","mystery","puzzle") win=door_open lose=trapped

\scene door_open
\clear
🎉 Pintu terbuka! Kamu bisa melanjutkan.

\progress 1 "Melanjutkan..."

\scene explore_yard
yard