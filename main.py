


from game import Game
import json


def main() -> None:
    '''This is the main function.'''

    '''OPEN CONFIGURATION'''
    with open("settings.json") as json_file:
        game_config = json.load(json_file)

    '''INITIALIZE GAME INSTANCE'''
    game = Game(config=game_config)

    '''INITIALIZE LEVEL'''
    game.load_map(level=game_config['level2'])

    while True:
        game.clock.tick(game.fps)
        game.handle_events()
        game.update()
        game.render()


if __name__ == '__main__':
    main()

