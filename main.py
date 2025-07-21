from app.GameFactory import GameFactory

def main():
   game = GameFactory().create()
   game.run()
    
if __name__ == "__main__":
    main()
