from random import choice
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

## Color Constants:
WINDOW_BG = (0.1451, 0.1451, 0.20784)
GRID_BG_COLOR = (0.08627, 0.08627, 0.11373)
GRID_BG_COLOR = (0, 0, 0)
GRID_LINE_COLOR = (1, 0.3, 1)
GRID_LINE_COLOR = (0.1451, 0.1451, 0.20784)
GRID_EMPTY_CELL = (0.03627, 0.08627, 0.031373)
GRID_EMPTY_CELL_ALT = (0.03627, 0.08627, 0.031373)

COLORS = [
    (1.0, 0.0, 0.0),  # red
    (0.0, 0.0, 1.0),  # blue
    (0.0, 1.0, 0.0),  # green
    (1.0, 1.0, 0.0),  # yellow
    (1.0, 0.0, 1.0),  # magenta
]

## grid width & height
GRID_SIZE = 30

WINDOW_WIDTH = GRID_SIZE * 10
WINDOW_HEIGHT = GRID_SIZE * 20

GRID_WIDTH = GRID_SIZE * 10
GRID_HEIGHT = GRID_SIZE * 20

GRID_ROW = GRID_HEIGHT // GRID_SIZE
GRID_COL = GRID_WIDTH // GRID_SIZE

GRID_OFFSET_X = WINDOW_WIDTH - GRID_WIDTH
GRID_OFFSET_Y = 0


SHAPES = {
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(0, 1), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 0), (1, 1), (2, 1)],
        [(0, 1), (1, 0), (1, 1), (1, 2)],
    ],
    "J": [
        [(2, 1), (1, 1), (0, 1), (0, 0)],
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 0)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(0, 1), (0, 2), (1, 0), (1, 1)],
    ],
    "S": [
        [(2, 0), (1, 0), (1, 1), (0, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "L": [
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 0)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (2, 1)],
    ],
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
}


class TetrisGame:
    def __init__(self):
        # using a matrix for whole window
        self.window = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
        # change whole window background color
        self.window[:, :, :] = np.array(WINDOW_BG) * 255

        # extracting grid portion from matrix
        self.grid = self.window[
            GRID_OFFSET_Y : GRID_OFFSET_Y + GRID_HEIGHT,
            GRID_OFFSET_X : GRID_OFFSET_X + GRID_WIDTH,
            :,
        ]

        # change grid background color
        self.grid[:, :, :] = np.array((0.8, 0.8, 8.0)) * 255

        # for - current shape
        self.shape_index = 0
        self.current_shape_type = choice(list(SHAPES.keys()))
        self.current_shape = SHAPES[self.current_shape_type][0]
        self.current_pos = (GRID_ROW - 1, GRID_COL // 2)
        self.current_color = choice(COLORS)
        self.ghost_color = choice(COLORS)

        # collision detection
        self.is_collided_bottom = True
        self.is_collided_left = False
        self.is_collided_right = False
        self.is_collided_left_wall = False
        self.is_collided_right_wall = False

        self.bool_grid = np.full((GRID_ROW, GRID_COL), False, dtype=bool)
        self.filled_grid = np.full(
            (GRID_ROW, GRID_COL, 3), GRID_EMPTY_CELL, dtype=np.float64
        )

        # Initial Game over is true, so game starts on pressing ` `(space)
        self.is_game_over = False
        self.score = 0

    def generate_new_shape(self):
        self.current_shape_type = choice(list(SHAPES.keys()))


        self.shape_index = 0
        self.current_shape = SHAPES[self.current_shape_type][self.shape_index]

        prev_color = self.current_color
        self.current_color = choice(COLORS)
        while self.current_color == prev_color:
            self.current_color = choice(COLORS)

        self.ghost_color = np.array(self.current_color) * 0.3

    def change_shape(self):
        self.shape_index = (self.shape_index + 1) % len(SHAPES[self.current_shape_type])
        tmp_shape = SHAPES[self.current_shape_type][self.shape_index]
        flag_collide = self.detect_rotation_collission(tmp_shape)

        for i in range(len(SHAPES[self.current_shape_type])):
            if flag_collide:
                self.shape_index = (self.shape_index + 1) % len(
                    SHAPES[self.current_shape_type]
                )
                tmp_shape = SHAPES[self.current_shape_type][self.shape_index]
                flag_collide = self.detect_rotation_collission(tmp_shape)
            else:
                break

        if not flag_collide:
            self.current_shape = SHAPES[self.current_shape_type][self.shape_index]
            self.update_current_shape()
        else:
            self.update_current_shape()

    def update_current_shape(self):
        if self.is_game_over:
            return
        # updates current shape in the grid
        self.change_grid_bg()
        self.fill_occupied_grid()
        self.update_ghost_shape()
        for x, y in self.current_shape:
            self.fill_grid(
                self.current_color,
                x + self.current_pos[0],
                y + self.current_pos[1],
            )

    def update_ghost_shape(self):
        ghost_shapes = self.get_ghost_shape()

        for x, y in ghost_shapes:
            self.fill_grid(
                self.ghost_color,
                x,
                y,
            )

    def fill_grid(self, color, x, y):
        x = x * GRID_SIZE
        y = y * GRID_SIZE
        xe = x + GRID_SIZE
        ye = y + GRID_SIZE
        self.grid[x:xe, y:ye, :] = np.array(color) * 255

    def fill_occupied_grid(self):

        for i in range(GRID_ROW):
            for j in range(GRID_COL):
                if self.bool_grid[i, j]:
                    self.fill_grid(self.filled_grid[i, j], i, j)

        if self.is_game_over:
            color = np.random.uniform(0.2, 0.3, 3)
            for i in range(GRID_ROW):
                for j in range(GRID_COL):
                    if not self.bool_grid[i, j]:
                        self.fill_grid(color, i, j)

    def change_grid_bg(self):
        self.grid[:, :, :] = np.array(GRID_BG_COLOR) * 255

    def detect_rotation_collission(self, new_shape):
        c1 = (
            new_shape[0][0] + self.current_pos[0],
            new_shape[0][1] + self.current_pos[1],
        )
        c2 = (
            new_shape[1][0] + self.current_pos[0],
            new_shape[1][1] + self.current_pos[1],
        )
        c3 = (
            new_shape[2][0] + self.current_pos[0],
            new_shape[2][1] + self.current_pos[1],
        )
        c4 = (
            new_shape[3][0] + self.current_pos[0],
            new_shape[3][1] + self.current_pos[1],
        )

        flag_collide = False

        # collision with bottom
        if c1[0] <= 0 or c2[0] <= 0 or c3[0] <= 0 or c4[0] <= 0:
            return True

        # collision with left wall
        if c1[1] < 0 or c2[1] < 0 or c3[1] < 0 or c4[1] < 0:
            return True

        if (
            c1[1] >= GRID_COL
            or c2[1] >= GRID_COL
            or c3[1] >= GRID_COL
            or c4[1] >= GRID_COL
        ):
            return True

        h, w = self.bool_grid.shape
        h, w = h - 1, w - 1
        for c in [c1, c2, c3, c4]:
            y, x = c
            if y > h:
                continue
            if self.bool_grid[c]:
                return True

        return False

    def get_ghost_shape(self):
        flag_collide = False
        i = 1
        while not flag_collide:
            x, y = self.current_pos
            x_down = x - i

            c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
            c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
            c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
            c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

            c1_down = (
                min(GRID_ROW - 1, self.current_shape[0][0] + x_down),
                self.current_shape[0][1] + y,
            )
            c2_down = (
                min(GRID_ROW - 1, self.current_shape[1][0] + x_down),
                self.current_shape[1][1] + y,
            )
            c3_down = (
                min(GRID_ROW - 1, self.current_shape[2][0] + x_down),
                self.current_shape[2][1] + y,
            )
            c4_down = (
                min(GRID_ROW - 1, self.current_shape[3][0] + x_down),
                self.current_shape[3][1] + y,
            )

            # collision with left wall
            if c1[1] < 0 or c2[1] < 0 or c3[1] < 0 or c4[1] < 0:
                flag_collide = True

            if (
                c1[1] >= GRID_COL
                or c2[1] >= GRID_COL
                or c3[1] >= GRID_COL
                or c4[1] >= GRID_COL
            ):
                flag_collide = True

            # check if coliision with bottom
            flag_collide = False
            if c1_down[0] == 0 or c2_down[0] == 0 or c3_down[0] == 0 or c4_down[0] == 0:
                flag_collide = True

            h, w = self.bool_grid.shape
            h, w = h - 1, w - 1
            for c in [c1_down, c2_down, c3_down, c4_down]:
                y, x = c
                y -= 1
                if y >= h or y < (h * -1):
                    continue
                if self.bool_grid[y, x]:
                    flag_collide = True

            if flag_collide:
                return c1_down, c2_down, c3_down, c4_down

            i += 1

    def detect_bottom_collision(self):
        x, y = self.current_pos
        x_down = x - 1

        c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
        c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
        c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
        c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

        c1_down = (
            min(GRID_ROW - 1, self.current_shape[0][0] + x_down),
            self.current_shape[0][1] + y,
        )
        c2_down = (
            min(GRID_ROW - 1, self.current_shape[1][0] + x_down),
            self.current_shape[1][1] + y,
        )
        c3_down = (
            min(GRID_ROW - 1, self.current_shape[2][0] + x_down),
            self.current_shape[2][1] + y,
        )
        c4_down = (
            min(GRID_ROW - 1, self.current_shape[3][0] + x_down),
            self.current_shape[3][1] + y,
        )

        flag_collide = False
        if c1[0] == 0 or c2[0] == 0 or c3[0] == 0 or c4[0] == 0:
            flag_collide = True

        if (
            self.bool_grid[c1_down]
            or self.bool_grid[c2_down]
            or self.bool_grid[c3_down]
            or self.bool_grid[c4_down]
        ):
            flag_collide = True

        if flag_collide:
            self.is_collided_bottom = True
            self.update_filled_grid(c1, c2, c3, c4)

    def detect_left_collision(self):
        x, y = self.current_pos
        y_left = y - 1

        c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
        c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
        c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
        c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

        c1_left = (
            min(self.current_shape[0][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[0][1] + y_left),
        )
        c2_left = (
            min(self.current_shape[1][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[1][1] + y_left),
        )
        c3_left = (
            min(self.current_shape[2][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[2][1] + y_left),
        )
        c4_left = (
            min(self.current_shape[3][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[3][1] + y_left),
        )

        flag_collide = False
        #
        if c1[1] == 0 or c2[1] == 0 or c3[1] == 0 or c4[1] == 0:
            flag_collide = True

        if (
            self.bool_grid[c1_left]
            or self.bool_grid[c2_left]
            or self.bool_grid[c3_left]
            or self.bool_grid[c4_left]
        ):
            flag_collide = True

        if flag_collide:
            self.is_collided_left = True

    def detect_right_collision(self):
        x, y = self.current_pos
        y_right = y + 1

        c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
        c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
        c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
        c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

        c1_right = (
            min(self.current_shape[0][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[0][1] + y_right),
        )
        c2_right = (
            min(self.current_shape[1][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[1][1] + y_right),
        )
        c3_right = (
            min(self.current_shape[2][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[2][1] + y_right),
        )
        c4_right = (
            min(self.current_shape[3][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[3][1] + y_right),
        )

        flag_collide = False
        if (
            c1[1] == GRID_COL - 1
            or c2[1] == GRID_COL - 1
            or c3[1] == GRID_COL - 1
            or c4[1] == GRID_COL - 1
        ):
            flag_collide = True

        if (
            self.bool_grid[c1_right]
            or self.bool_grid[c2_right]
            or self.bool_grid[c3_right]
            or self.bool_grid[c4_right]
        ):
            flag_collide = True

        if flag_collide:
            self.is_collided_right = True

    def game_restart(self):
        self.bool_grid = np.full((GRID_ROW, GRID_COL), False, dtype=bool)
        self.filled_grid = np.full(
            (GRID_ROW, GRID_COL, 3), GRID_EMPTY_CELL, dtype=np.float64
        )
        self.is_game_over = False
        self.score = 0

    def detect_game_over(self, cell_one, cell_two, cell_three, cell_four):
        if self.is_game_over:
            print(" GAME OVER ")
            return

        if (
            cell_one[0] >= GRID_ROW - 1
            or cell_two[0] >= GRID_ROW - 1
            or cell_three[0] >= GRID_ROW - 1
            or cell_four[0] >= GRID_ROW - 1
        ):
            self.is_game_over = True
            for cell in [cell_one, cell_two, cell_three, cell_four]:
                if cell[0] <= GRID_ROW - 1:
                    self.filled_grid[cell[0], cell[1]] = self.current_color
                    self.bool_grid[cell] = True

            print(" GAME OVER ")
            print("Your Final score:", self.score)
            return

    def update_score(self):

        if self.is_game_over:
            return

        i = 0
        while i < GRID_ROW:
            if all(self.bool_grid[i]):
                self.score += GRID_COL
                self.bool_grid[i] = False

                # down down
                for j in range(i + 1, GRID_ROW):
                    self.bool_grid[j - 1] = self.bool_grid[j]
                    self.filled_grid[j - 1] = self.filled_grid[j]

                # unset top row
                self.bool_grid[GRID_ROW - 1] = False

                # decrease i by 1 to check again if buttom row is also full
                i -= 1

            i += 1

        print("Updated Score:", self.score)

    def update_filled_grid(self, c1, c2, c3, c4):
        self.detect_game_over(c1, c2, c3, c4)
        if self.is_game_over:
            return

        self.filled_grid[c1] = self.current_color
        self.filled_grid[c2] = self.current_color
        self.filled_grid[c3] = self.current_color
        self.filled_grid[c4] = self.current_color

        self.bool_grid[c1] = True
        self.bool_grid[c2] = True
        self.bool_grid[c3] = True
        self.bool_grid[c4] = True

        self.update_score()
        self.update_current_shape()

    def place_on_grid(self):
        self.generate_new_shape()
        self.is_collided_bottom = False
        self.current_pos = (GRID_ROW, GRID_COL // 2)

        self.update_current_shape()

    def move_auto_down(self):
        if self.is_game_over:
            return

        self.detect_bottom_collision()

        if self.is_collided_bottom:
            self.place_on_grid()
            return

        self.current_pos = (
            self.current_pos[0] - 1,
            self.current_pos[1],
        )

        self.update_current_shape()

    def move_left(self):
        # need tweek
        self.detect_left_collision()
        if self.is_collided_left:
            self.update_current_shape()  # ??
            self.is_collided_left = False
            return

        self.current_pos = (
            self.current_pos[0],
            self.current_pos[1] - 1,
        )

        self.update_current_shape()

    def move_right(self):
        self.detect_right_collision()

        if self.is_collided_right:
            self.update_current_shape()  # ??
            self.is_collided_right = False
            return

        self.current_pos = (
            self.current_pos[0],
            self.current_pos[1] + 1,
        )
        self.update_current_shape()

    def move_bottom(self):
        for i in range(GRID_ROW + 4):
            self.detect_bottom_collision()

            if self.is_collided_bottom:
                self.place_on_grid()
                return

            self.current_pos = (
                self.current_pos[0] - 1,
                self.current_pos[1],
            )
            self.update_current_shape()


def keyboard(key, _x, _y):
    _, _ = _x, _y

    avoid_redisplay = False
    if key.decode("utf-8") in "qhlj ":
        # update grid background color as shape will be moved
        game.change_grid_bg()
        game.fill_occupied_grid()

    if game.is_game_over and key != b" ":
        print("Enter (space) for restart")

    # map action to key
    if key == b"q":
        print("Bye Bye")
        print("Your Latest Score", game.score)
        glutDestroyWindow(glutGetWindow())
        avoid_redisplay = True
    elif key == b"a":
        game.move_left()
    elif key == b"d":
        game.move_right()
    elif key == b"s":
        game.move_bottom()
    elif key == b"w":
        if game.is_game_over:
            game.game_restart()
        else:
            game.change_shape()

    if not avoid_redisplay:
        glutPostRedisplay()


# def draw_grid_lines():
#     # draw vertical lines in grid
#     for i in range(0, WINDOW_HEIGHT):
#         for j in range(WINDOW_WIDTH - GRID_WIDTH, WINDOW_WIDTH, GRID_SIZE):
#             game.window[i, j] = np.array(GRID_LINE_COLOR) * 255

#     # draw horizontal lines in grid
#     for i in range(0, WINDOW_HEIGHT, GRID_SIZE):
#         for j in range(WINDOW_WIDTH - GRID_WIDTH, WINDOW_WIDTH):
#             game.window[i, j] = np.array(GRID_LINE_COLOR) * 255


def draw_grid_lines():
    # draw vertical lines in grid
    glColor3f(*GRID_LINE_COLOR)
    glBegin(GL_LINES)
    for i in range(GRID_OFFSET_X, WINDOW_WIDTH, GRID_SIZE):
        glVertex2f(i, 0)
        glVertex2f(i, WINDOW_HEIGHT)
    glEnd()

    # draw horizontal lines in grid
    glBegin(GL_LINES)
    for i in range(GRID_OFFSET_Y, WINDOW_HEIGHT, GRID_SIZE):
        glVertex2f(GRID_OFFSET_X, i)
        glVertex2f(WINDOW_WIDTH, i)
    glEnd()


# def draw_score():
#     glColor3f(1.0, 1.0, 1.0)  # Set color to white
#     glMatrixMode(GL_PROJECTION)  # Switch to projection mode
#     glPushMatrix()  # Push the current matrix
#     glLoadIdentity()  # Load the identity matrix
#     gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)  # Set orthographic projection
#     glMatrixMode(GL_MODELVIEW)  # Switch back to modelview mode
#     glPushMatrix()  # Push the current matrix
#     glLoadIdentity()  # Load the identity matrix
    
#     # Position and draw the score using OpenGL primitives
#     glRasterPos2i(10, WINDOW_HEIGHT - 30)  # Set position for the score
#     # if game is over
#     if game.is_game_over:
#         score_string = f"Game Over. Your Final score: {game.score}"
#     else:
#         score_string = f"Score: {game.score}"  # Construct score string
        
#     for character in score_string:
#         glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))  # Draw each character of the score string

#     glPopMatrix()  # Restore the modelview matrix
#     glMatrixMode(GL_PROJECTION)  # Switch back to projection mode
#     glPopMatrix()  # Restore the projection matrix
#     glMatrixMode(GL_MODELVIEW)  # Switch back to modelview mode

def draw_score():
    glColor3f(1.0, 1.0, 1.0)  # Set color to white
    glPushMatrix()  # Push the current matrix
    glLoadIdentity()  # Load the identity matrix
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)  # Set orthographic projection
    
    # Position and draw the score using OpenGL points
    glRasterPos2i(10, WINDOW_HEIGHT - 30)  # Set position for the score
    if game.is_game_over:
        score_string = f"Game Over. Your Final score: {game.score}"
    else:
        score_string = f"Score: {game.score}"  # Construct score string
        
    for character in score_string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))  # Draw each character of the score string

    glPopMatrix()  # Restore the modelview matrix


def fill_buffer():
    # Takes game.window matrix and draws in one step
    # Only this function applies changes to the screen, the rest of the methods only manipulate game.window matrix

    glClear(GL_COLOR_BUFFER_BIT)
    glRasterPos2f(-1, -1)
    glDrawPixels(WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, game.window)
    draw_score()  # Draw the score on the screen
    glutSwapBuffers()


# def fill_buffer():
#     # takes game.window matrix and draw in one step
#     # only this function apply changes in the screen, rest of the method only
#     # manuplate game.window matrix

#     glClear(GL_COLOR_BUFFER_BIT)
#     glRasterPos2f(-1, -1)
#     glDrawPixels(WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, game.window)
#     glutSwapBuffers()


def display():
    # display all the components

    # draw grids in right side
    draw_grid_lines()

    # update the matrix into display
    fill_buffer()


def update(value):
    game.change_grid_bg()
    game.fill_occupied_grid()
    game.move_auto_down()

    glutTimerFunc(1000, update, 0)
    glutPostRedisplay()


def reshape(width, height):
    # ?? what this does
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)


def main():
    # ctrl+c && ctrl+v
    glutInit(sys.argv)
    # ctrl+c && ctrl+v
    glutInitDisplayMode(GLUT_RGB)
    # ctrl+c && ctrl+v
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)

    # this set window position (0,0) means strt from top-left
    # then oftet determine the exact position of start from top-left
    glutInitWindowPosition(100, 100)

    # (`opengl` is important for xmonad to ingnore tiling)
    wind = glutCreateWindow(b"opengl")
    # wind = glutCreateWindow(b"Tetris")

    # window background color (does not matter really)
    # glClearColor(1.0, 0, 0, 1.0)w
    # glClearColor(*WINDOW_BG, 1.0)

    # display maybe, god knows
    glutDisplayFunc(display)

    # what this does?
    # glutReshapeFunc(reshape)

    # to handle keyboard control
    glutKeyboardFunc(keyboard)

    # timer function
    glutTimerFunc(0, update, 0)

    # game.generate_new_shape()
    glutMainLoop()


if __name__ == "__main__":
    game = TetrisGame()
    main()
