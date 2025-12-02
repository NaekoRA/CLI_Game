import random
import os
from engine.utils import console, slow_print, input_no_empty

class HangmanManager:
    # Words database (fallback jika tidak ada words yang diberikan)
    WORD_CATEGORIES = {
        "horror": ["phasmophobia", "megalophobia", "arachnophobia", "nyctophobia", 
                  "claustrophobia", "spectrophobia", "demophobia", "thanatophobia"],
        "school": ["classroom", "laboratory", "library", "principal", "detention"],
        "mystery": ["conspiracy", "investigation", "suspicious", "enigma", "puzzle"]
    }
    
    @staticmethod
    def start_hangman(config=None):
        """Start hangman game with configuration"""
        if config is None:
            config = {}
        
        # Check if custom words provided
        custom_words = config.get("words", [])
        
        if custom_words:
            # Use custom words from user
            words = custom_words
        else:
            # Use default category
            category = config.get("category", "horror")
            words = HangmanManager.WORD_CATEGORIES.get(category, HangmanManager.WORD_CATEGORIES["horror"])
        
        # Validate words
        if not words:
            console.print("[red]Error: Tidak ada kata untuk permainan Hangman![/red]")
            return "LOSE"
        
        # Create game instance
        game = HangmanGame(words)
        return game.main()

class HangmanGame:
    def __init__(self, words_list):
        self.words = words_list
        self.hangman_art = {
            0: ('  +---+',
                '  |   |',
                '      |',
                '      |',
                '      |',
                '  ======'),
            
            1: ('  +---+',
                '  |   |',
                '  O   |',
                '      |',
                '      |',
                '  ======'),
            
            2: ('  +---+',
                '  |   |',
                '  O   |',
                '  |   |',
                '      |',
                '  ======'),
            
            3: ('  +---+',
                '  |   |',
                '  O   |',
                ' /|   |',
                '      |',
                '  ======'),
            
            4: ('  +---+',
                '  |   |',
                '  O   |',
                ' /|\  |',
                '      |',
                '  ======'),
            
            5: ('  +---+',
                '  |   |',
                '  O   |',
                ' /|\  |',
                ' /    |',
                '  ======'),
            
            6: ('  +---+',
                '  |   |',
                '  O   |',
                ' /|\  |',
                ' / \  |',
                '  ======'),
        }
        self.correct_guesses = 0
        self.wrong_guesses = 0
        self.guessed_letters = set()
        
    def clear_screen(self):
        """Clear screen compatible with game"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_hangman(self):
        """Display hangman art"""
        for line in self.hangman_art[self.wrong_guesses]:
            console.print(line, style="white")
    
    def display_template(self, template):
        """Display word template"""
        display = " ".join(template)
        console.print(f"\n[bold cyan]{display}[/bold cyan]", justify="center")
    
    def display_status(self):
        """Display game status"""
        console.print(f"\n[dim]Tebakan salah: {self.wrong_guesses}/6[/dim]")
        console.print(f"[dim]Huruf sudah ditebak: {', '.join(sorted(self.guessed_letters)) if self.guessed_letters else '-'}[/dim]")
    
    def main(self):
        """Main game loop"""
        # Select random word
        answer = random.choice(self.words).lower()
        template = ['_'] * len(answer)
        
        self.clear_screen()
        
        # Game introduction
        console.print("\n" + "🎯" * 30, style="bold magenta")
        console.print("           GAME HANGMAN", style="bold magenta")
        console.print("🎯" * 30, style="bold magenta")
        console.print(f"\n[dim]Kata terdiri dari {len(answer)} huruf[/dim]")
        console.print("[dim]Tebak kata dengan menebak satu huruf per percobaan![/dim]")
        console.print("[yellow]Tekan Enter untuk memulai...[/yellow]")
        input()
        
        running = True
        
        while running:
            self.clear_screen()
            
            # Display game state
            console.print("\n" + "─" * 40, style="dim")
            self.display_hangman()
            self.display_template(template)
            self.display_status()
            console.print("─" * 40, style="dim")
            
            # Get player input
            try:
                guess = input_no_empty("\n[bold]Tebak huruf:[/bold] ").strip().lower()
                
                # Validate input
                if len(guess) != 1:
                    console.print("[red]Masukkan hanya 1 huruf![/red]")
                    continue
                    
                if not guess.isalpha():
                    console.print("[red]Masukkan huruf saja![/red]")
                    continue
                
                # Check if already guessed
                if guess in self.guessed_letters:
                    console.print("[yellow]Huruf ini sudah ditebak![/yellow]")
                    continue
                
                # Add to guessed letters
                self.guessed_letters.add(guess)
                
                # Check if guess is correct
                if guess in answer:
                    console.print(f"[green]Benar! Huruf '{guess}' ada dalam kata.[/green]")
                    
                    # Update template
                    for i, char in enumerate(answer):
                        if char == guess:
                            template[i] = guess
                    
                    # Check if all letters guessed
                    if "_" not in template:
                        self.clear_screen()
                        self.display_hangman()
                        self.display_template(template)
                        console.print("\n" + "🎉" * 30, style="bold green")
                        console.print("        SELAMAT! KAMU MENANG!", style="bold green")
                        console.print("🎉" * 30, style="bold green")
                        console.print(f"\n[bold]Kata yang benar:[/bold] {answer.upper()}")
                        console.print(f"[dim]Sisa nyawa: {6 - self.wrong_guesses}[/dim]")
                        return "WIN"
                        
                else:
                    console.print(f"[red]Salah! Huruf '{guess}' tidak ada dalam kata.[/red]")
                    self.wrong_guesses += 1
                    
                    # Check if game over
                    if self.wrong_guesses >= len(self.hangman_art) - 1:
                        self.clear_screen()
                        self.display_hangman()
                        console.print("\n" + "💀" * 30, style="bold red")
                        console.print("           GAME OVER!", style="bold red")
                        console.print("💀" * 30, style="bold red")
                        console.print(f"\n[bold]Kata yang benar:[/bold] {answer.upper()}")
                        console.print(f"[bold]Kata yang kamu tebak:[/bold] {' '.join(template)}")
                        return "LOSE"
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Permainan dihentikan...[/yellow]")
                return "LOSE"
        
        return "LOSE"