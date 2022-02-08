import asyncio
import curses
import globals


def get_frame_size(text):
    '''Calculate size of multiline text fragment,
    return pair — number of rows and colums.
    '''

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw_frame(canvas, start_row, start_column, text, negative=False):
    '''Draw multiline text fragment on canvas, erase text instead of
    drawing if negative=True is specified.
    '''

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def fire(canvas, start_row, start_column, rows_speed=-0.3,
               columns_speed=0):
    '''Display animation of gun shot, direction and speed can be specified.'''

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in globals.obstacles:
            if obstacle.has_collision(row, column):
                globals.obstacles_in_last_collisions.append(obstacle)
                globals.coroutines.append(explode(canvas, row, column))
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def explode(canvas, center_row, center_column):
    rows, columns = get_frame_size(globals.EXPLOSION_FRAMES[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    for frame in globals.EXPLOSION_FRAMES:

        draw_frame(canvas, corner_row, corner_column, frame)

        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await asyncio.sleep(0)
