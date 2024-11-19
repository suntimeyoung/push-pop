from game.game import Game

# Start Game
if __name__ == '__main__':
    game = Game()
    game.board_init_rand()
    print("GAMING")
    print("press ENTER to START")
    input()
    game.console_show()
    while True:
        game.game_step(input("Your movement: "))
        game.game_level()
        game.console_show()
        if True:
            game.game_reset(rand=False)
            continue
        if game.game_status() == 'over':
            print("GAME OVER")
            print("press ENTER to RESTART")
            input()
            game.game_reset()
            game.console_show()
