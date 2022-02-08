import curses
import asyncio
from random import randint, choice
from itertools import cycle
import time
from obstacles import Obstacle
from physics import update_speed
from animation import draw_frame, fire, get_frame_size
import globals


with open('frames/spaceship_frame1', 'r') as fr:
    spaceship_picture_1 = fr.read()
with open('frames/spaceship_frame2', 'r') as fr:
    spaceship_picture_2 = fr.read()
with open('frames/trash_large', 'r') as fr:
    trash_large_picture = fr.read()
with open('frames/trash_small', 'r') as fr:
    trash_small_picture = fr.read()
with open('frames/trash_xl', 'r') as fr:
    trash_xl_picture = fr.read()
with open('frames/gameover', 'r') as fr:
    gameover_picture = fr.read()


async def blink(canvas, row, column, symbol='*'):
    '''Animate stars'''
    await sleep(randint(0, 20))
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(5)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(2)

        canvas.addstr(row, column, symbol)
        await sleep(1)


async def change_year():
    while True:
        await sleep(20)
        globals.year += 1


async def show_year(year_canvas):
    '''Show current year at window bottom'''
    while True:
        year = str(globals.year)
        draw_frame(year_canvas, 1, 1, year)
        year_canvas.refresh()
        await sleep(10)
        draw_frame(year_canvas, 1, 1, year, True)


async def sleep(ticks):
    for i in range(ticks):
        await asyncio.sleep(0)


async def gameover(canvas, max_height, max_length):
    '''Animate gameover'''
    while True:
        draw_frame(canvas, max_height/3, max_length/7, gameover_picture)
        await asyncio.sleep(0)


async def animate_spaceship(canvas, max_win_height, max_win_length,
                            spaceship_frame_1, spaceship_frame_2):
    '''Animate spaceship frame'''

    start_row = int(max_win_height / 3)
    start_column = int(max_win_length / 2)

    spaceship_frame_lines_list = spaceship_frame_1.split('\n')
    spaceship_height = len(spaceship_frame_lines_list)
    spaceship_length = len(max(spaceship_frame_lines_list))

    row_speed = column_speed = 0

    for frame in cycle((spaceship_frame_1, spaceship_frame_2)):
        for obstacle in globals.obstacles:
            if obstacle.has_collision(start_row, start_column):
                globals.coroutines.append(gameover(canvas, max_win_height,
                                                   max_win_length))
                return

        row_directions, column_directions, space_pressed = \
            read_controls(canvas)

        row_speed, column_speed = update_speed(
                                    row_speed,
                                    column_speed,
                                    row_directions,
                                    column_directions,
                                    )

        start_row += row_speed
        if start_row > max_win_height - spaceship_height:
            start_row = (max_win_height - spaceship_height -
                         globals.BORDER_INDENT)
        elif start_row < 1:
            start_row = 1

        start_column += column_speed
        if start_column > (max_win_length - spaceship_length):
            start_column = (max_win_length - spaceship_length -
                            globals.BORDER_INDENT)
        elif start_column < 1:
            start_column = 1

        if globals.year >= 2020:
            if space_pressed:
                fire_column = start_column + spaceship_length / 2
                globals.coroutines.append(fire(canvas, start_row, fire_column))

        await animate_frame(canvas, start_row, start_column, frame)


async def animate_frame(canvas, row, column, frame):
    '''Animate frame got in parameters'''
    draw_frame(canvas, row, column, frame)
    await asyncio.sleep(0)
    draw_frame(canvas, row, column, frame, True)


def read_controls(canvas):
    '''Read keys pressed and returns tuple witl controls state.'''

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == globals.UP_KEY_CODE:
            rows_direction = -globals.SPACESHIP_SPEED

        if pressed_key_code == globals.DOWN_KEY_CODE:
            rows_direction = globals.SPACESHIP_SPEED

        if pressed_key_code == globals.RIGHT_KEY_CODE:
            columns_direction = globals.SPACESHIP_SPEED

        if pressed_key_code == globals.LEFT_KEY_CODE:
            columns_direction = -globals.SPACESHIP_SPEED

        if pressed_key_code == globals.SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start.
    """

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    frame_rows, frame_columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, frame_rows, frame_columns)
    globals.obstacles.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in globals.obstacles_in_last_collisions:
                globals.obstacles_in_last_collisions.remove(obstacle)
                return
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = row
    finally:
        globals.obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas, max_win_length):
    '''Add fly_garbage coroutines in global event-loop'''

    while True:
        garbage_frame = choice((trash_large_picture, trash_small_picture,
                                trash_xl_picture))
        garbage_frame_lines_list = garbage_frame.split('\n')
        garbage_length = len(max(garbage_frame_lines_list))
        column = randint(1, max_win_length-garbage_length)

        if globals.year >= 1960:
            globals.coroutines.append(fly_garbage(canvas, column,
                                                  garbage_frame))
        delay = get_delay_of_year(globals.year)
        await sleep(delay)


def get_delay_of_year(year):
    delay = 2000 - year
    if year < 2020:
        delay = max(delay, 15)
    else:
        delay = max(delay, 7)
    return delay


def main(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_window_height, max_window_length = canvas.getmaxyx()
    year_canvas = canvas.derwin(max_window_height - 3, 3)

    globals.coroutines.append(change_year())
    globals.coroutines.append(show_year(year_canvas))
    for i in range(globals.STARS_NUMBER):
        globals.coroutines.append(blink(
                    canvas,
                    randint(globals.BORDER_INDENT,
                            max_window_height-globals.BORDER_INDENT),
                    randint(globals.BORDER_INDENT,
                            max_window_length-globals.BORDER_INDENT),
                    choice(globals.STAR_SYMBOLS)
                    ))
    globals.coroutines.append(animate_spaceship(
                canvas,
                max_window_height,
                max_window_length,
                spaceship_picture_1,
                spaceship_picture_2
                ))
    globals.coroutines.append(fill_orbit_with_garbage(canvas,
                                                      max_window_length))

    while True:
        for coroutine in globals.coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                globals.coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(globals.TIC_TIMEOUT)
        if not globals.coroutines:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
