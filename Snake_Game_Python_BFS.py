import pygame
import random

pygame.init()

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

HEIGHT = 30          
WIDTH = 40
FIELD_SIZE = HEIGHT * WIDTH

HEAD = 0
FOOD = 0
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)
SNAKE = 2 * UNDEFINED

LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH

ERR = -2333
MOV = [LEFT, RIGHT, UP, DOWN]

SNAKE_BLOCK = 20
SNAKE_SPEED = 5000

FONT_STYLE = pygame.font.SysFont("bahnschrift", 12)
SCORE_FONT = pygame.font.SysFont("comicsansms", 33)

# The initial State of the game

def initial_game():
    global board, snake, snake_size, tmpboard, tmpsnake, tmpsnake_size, food, best_move
    board = [0] * FIELD_SIZE  # [0,0,0,……]
    snake = [0] * (FIELD_SIZE + 1)
    snake[HEAD] = 1 * WIDTH + 1
    snake_size = 1

    tmpboard = [0] * FIELD_SIZE
    tmpsnake = [0] * (FIELD_SIZE + 1)
    tmpsnake[HEAD] = 1 * WIDTH + 1
    tmpsnake_size = 1

    food = 4 * WIDTH + 7
    best_move = ERR


# Set up the game window
display_Board = pygame.display.set_mode((SNAKE_BLOCK * WIDTH, SNAKE_BLOCK * HEIGHT))


clock = pygame.time.Clock()


def Your_score(score):
    value = SCORE_FONT.render("Your Score: " + str(score), True, red)
    display_Board.blit(value, [300, 0])


def new_food():
    global food, snake_size, display_Board
    cell_free = False
    while not cell_free:
        w = random.randint(0, WIDTH - 1)
        h = random.randint(0, HEIGHT - 1)
        food = WIDTH * h + w
        cell_free = is_cell_free(food, snake_size, snake)


def draw():
    global SNAKE_BLOCK, snake, snake_size, food
    for Current_Index in snake[:snake_size]:
        pygame.draw.rect(display_Board, black,
                         [SNAKE_BLOCK * (Current_Index % WIDTH), SNAKE_BLOCK * (Current_Index // WIDTH), SNAKE_BLOCK, SNAKE_BLOCK])
        
    pygame.draw.rect(display_Board, green,
                     [SNAKE_BLOCK * (food % WIDTH), SNAKE_BLOCK * (food // WIDTH), SNAKE_BLOCK, SNAKE_BLOCK])

 # Function to display messages

def message(msg, color):
    mesg = FONT_STYLE.render(msg, True, color)
    display_Board.blit(mesg, [WIDTH * SNAKE_BLOCK / 6, HEIGHT * SNAKE_BLOCK / 3])

# Function to Check if a move is Possible
def is_move_possible(Current_Index, move):

    flag = False

    if move == LEFT:
        flag = True if Current_Index % WIDTH > 0 else False

    elif move == RIGHT:
                flag = True if Current_Index % WIDTH < (WIDTH - 1) else False
    elif move == UP:
          flag = True if Current_Index > (WIDTH - 1) else False
    elif move == DOWN:
         flag = True if Current_Index < (FIELD_SIZE - WIDTH) else False
    return flag


def is_cell_free(Current_Index, ssize, Indices_Of_snake_Body):
    return not (Current_Index in Indices_Of_snake_Body[:ssize])


def BFS(Ifood, Indices_Of_snake_Body, GameBoard):
    queue = []
    queue.append(Ifood)
    inqueue = [0] * FIELD_SIZE
    found = False
    """
    BFS Thinking :
    1* Remove first node and then cheack is gool ? yes --> done : No --> add children
    2* Remove
    3* Checke is goal or not ?
    4* Is goal Return solution
    5* Is not the goal add children
    6* .....
    """
    while len(queue) != 0:
        # Removing First Element
        Current_Index = int(queue.pop(0))
        # Cheacking
        if inqueue[Current_Index] == 1:
            continue
        inqueue[Current_Index] = 1
        # Iterating Over The Neighbors (four possible directions)
        for i in range(4):
            if is_move_possible(Current_Index, MOV[i]):
                
                # If the neighbor corresponds to the head of the snake -- Done
                if Current_Index + MOV[i] == Indices_Of_snake_Body[HEAD]:
                    found = True

                    # If the neighbor is an empty space
                if GameBoard[Current_Index + MOV[i]] < SNAKE:
                    if GameBoard[Current_Index + MOV[i]] > GameBoard[Current_Index] + 1:
                        GameBoard[Current_Index + MOV[i]] = GameBoard[Current_Index] + 1
                    if inqueue[Current_Index + MOV[i]] == 0:
                        queue.append(Current_Index + MOV[i])
    return found

# Check Whether the Tail of the Snake is Reachable or Not
def is_tail_reachable():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size - 1]] = FOOD
    tmpboard[food] = SNAKE
    result = BFS(tmpsnake[tmpsnake_size - 1], tmpsnake, tmpboard)
    for i in range(4):
        if is_move_possible(tmpsnake[HEAD], MOV[i]) and tmpsnake[HEAD] + MOV[i] == tmpsnake[
            tmpsnake_size - 1] and tmpsnake_size > 3:
            result = False
    return result

#  Moves the snake in the specified direction
def make_move(move):
    global snake, board, snake_size, score
    shift_array(snake, snake_size)
    snake[HEAD] += move
    p = snake[HEAD]
    # Updates the game board
    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE
        snake_size += 1
        if snake_size < FIELD_SIZE: new_food()
    else:
        board[snake[HEAD]] = SNAKE
        board[snake[snake_size]] = UNDEFINED

#  Resets the game Board by placing food 
def board_reset(Indices_Of_snake_Body, ssize, GameBoard):
    for i in range(FIELD_SIZE):
        if i == food:
            GameBoard[i] = FOOD
        #  Resetting all cells that are not part of the snake body in Undefined Form
        elif is_cell_free(i, ssize, Indices_Of_snake_Body):
            GameBoard[i] = UNDEFINED
        else:
            GameBoard[i] = SNAKE

# Finds the shortest safe move for the snake By using BFS
def find_safe_way():
    global snake, board
    safe_move = ERR
    virtual_shortest_move()
    if is_tail_reachable():
        return choose_shortest_safe_move(snake, board)
    safe_move = follow_tail()
    return safe_move

# Shifts an array by one position to the right
def shift_array(arr, size):
    for i in range(size, 0, -1):
        arr[i] = arr[i - 1]

# Find the best possible move for the snake if there are no safe moves available
def any_possible_move():
    global food, snake, snake_size, board
    best_move = ERR
# Using BFS to find the minimum distance to the food for each possible move
    board_reset(snake, snake_size, board)
    BFS(food, snake, board)
    min = SNAKE
# Chooses The Best Move with The Shortest Distance
    for i in range(4):
        if is_move_possible(snake[HEAD], MOV[i]) and board[snake[HEAD] + MOV[i]] < min:
            min = board[snake[HEAD] + MOV[i]]
            best_move = MOV[i]
    return best_move

# Finds the longest safe move for the snake to follow its Tail without hit himself
def follow_tail():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard)
    tmpboard[tmpsnake[tmpsnake_size - 1]] = FOOD
    tmpboard[food] = SNAKE
    BFS(tmpsnake[tmpsnake_size - 1], tmpsnake, tmpboard)
    tmpboard[tmpsnake[tmpsnake_size - 1]] = SNAKE
    return choose_longest_safe_move(tmpsnake, tmpboard)

# Determines The Shortest Path to The Food and Then Updates the tmpsnake and tmpboard arrays
def virtual_shortest_move():
    global snake, board, snake_size, tmpsnake, tmpboard, tmpsnake_size, food
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    tmpboard = board[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard)

    food_eated = False
    while not food_eated:
        BFS(food, tmpsnake, tmpboard)
        move = choose_shortest_safe_move(tmpsnake, tmpboard)
        shift_array(tmpsnake, tmpsnake_size)
        tmpsnake[HEAD] += move
        if tmpsnake[HEAD] == food:
            tmpsnake_size += 1
            board_reset(tmpsnake, tmpsnake_size, tmpboard)
            tmpboard[food] = SNAKE
            food_eated = True
        else:
            tmpboard[tmpsnake[HEAD]] = SNAKE
            tmpboard[tmpsnake[tmpsnake_size]] = UNDEFINED

# Chooses the shortest safe move from the current position
def choose_shortest_safe_move(psnake, pboard):
    best_move = ERR
    min = SNAKE
    for i in range(4):
        if is_move_possible(psnake[HEAD], MOV[i]) and pboard[psnake[HEAD] + MOV[i]] < min:
            min = pboard[psnake[HEAD] + MOV[i]]
            best_move = MOV[i]
    return best_move

# Chooses the longest safe move from the current position
def choose_longest_safe_move(psnake, pboard):
    best_move = ERR
    max = -1
    for i in range(4):
        if is_move_possible(psnake[HEAD], MOV[i]) and pboard[psnake[HEAD] + MOV[i]] < UNDEFINED and pboard[
            psnake[HEAD] + MOV[i]] > max:
            max = pboard[psnake[HEAD] + MOV[i]]
            best_move = MOV[i]
    return best_move

# Updates the game State and Checks any Events and Finnaly displays the Game Board
def gameLoop():
    game_over = False
    game_close = False

    initial_game()

    while not game_over:

        while game_close == True:
            display_Board.fill(blue)
            message("You Lost! Press C-Play Again or Q-Quit", red)
            Your_score(snake_size - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True

        board_reset(snake, snake_size, board)

        if BFS(food, snake, board):
            best_move = find_safe_way()
        else:
            best_move = follow_tail()
        if best_move == ERR:
            best_move = any_possible_move()

        if best_move != ERR:
            make_move(best_move)
        else:
            game_close = True

        display_Board.fill(blue)

        draw()
        Your_score(snake_size - 1)

        pygame.display.update()

        clock.tick(SNAKE_SPEED)

    pygame.quit()
    quit()


gameLoop()