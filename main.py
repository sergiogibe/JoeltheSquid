


from game import Game


def main() -> None:
    '''This is the main function.'''

    '''INITIALIZE GAME INSTANCE'''
    game = Game()

    '''INITIALIZE LEVEL'''
    game.load_map(spritesheet="dungeon_tiles.png",
                  level="level1test.csv",
                  spritesheet_size=(5,5))

    while True:
        game.clock.tick(game.fps)
        game.handle_events()
        game.update()
        game.render()


if __name__ == '__main__':
    main()
