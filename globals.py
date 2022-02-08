STAR_SYMBOLS = ['*', '.', ':', '+']
STARS_NUMBER = 200
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
SPACESHIP_SPEED = 1
TIC_TIMEOUT = 0.1
BORDER_INDENT = 1
coroutines = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957

EXPLOSION_FRAMES = [
    """\
           (_)
       (  (   (  (
      () (  (  )
        ( )  ()
    """,
    """\
           (_)
       (  (   (
         (  (  )
          )  (
    """,
    """\
            (
          (   (
         (     (
          )  (
    """,
    """\
            (
              (
            (
    """,
]
