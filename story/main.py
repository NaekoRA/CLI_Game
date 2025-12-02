import random
from engine.utils import clear

class hangman:
    def __init__(self) :
        self.words = ('phasmophobia','megalophobia')
        self.hangman_art = {
            0:( '  +---+',
                '  |   |',
                '      |',
                '      |',
                '      |',
                '  ======'),
            
            1:( '  +---+',
                '  |   |',
                '  O   |',
                '      |',
                '      |',
                '  ======'),
            
            2:( '  +---+',
                '  |   |',
                '  O   |',
                '  |   |',
                '      |',
                '  ======'),
            
            3:( '  +---+',
                '  |   |',
                '  O   |',
                ' /|   |',
                '      |',
                '  ======'),
            
            4:( '  +---+',
                '  |   |',
                '  O   |',
                ' /|\  |',
                '      |',
                '  ======'),
            
            5:( '  +---+',
                '  |   |',
                '  O   |',
                ' /|\  |',
                ' /    |',
                '  ======'),
            
            6:( '  +---+',
                '  |   |',
                '  O   |',
                ' /|\  |',
                ' / \  |',
                '  ======'),
            
        }

        self.correct_answer = 0
        self.wrong_answer=0
        
    def main(self):
        clear()
        answer = random.choice(self.words)
        running = True
        template = ['_']*len(answer)
        while running:
            self.display_hangman()
            self.dispay_template(template)
            guess = input()
            if guess in template:
                print('sudah ada')
                clear()
                continue
            if guess in answer:
                self.correct_answer +=1
                for i ,char in enumerate(answer):
                    if char==guess:
                        template[i]=guess
            else:
                self.wrong_answer +=1
            if "_" not in template:
                print('you win')
                running=False
            elif self.wrong_answer >= len(self.hangman_art)-1:
                print('you lose')
                running= False
            clear()
        
    def display_hangman(self):
        for line in self.hangman_art[self.wrong_answer]:
            print(line)
    def dispay_template(self,template):
        print(" ".join(template))
    
if __name__=="__main__":
    game=hangman()
    game.main()