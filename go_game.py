import random

# The number of spots per side of the board
# This code allows for an nxn board
BOARDSIZE = 5
# Value determining whether the player wants to quit or not
gameon = 1
# Lists of groups that have been removed from the board via capture,
# held in these varaibles in case, when all captures have been
# completed, the board resembles a previous game state and
# the move is invalid.  In that case, the groups are restored
# from these varaibles.
restore_o = []
restore_x = []

xoro = 'o'
notxoro = 'x'
game_state_current = []
game_state_future = []
o_groups = []
x_groups = []
non_groups = []
game_state_cache = ''
player1_pass = 0
player2_pass = 0
gameover = 0
o_points = 0
x_points = 0

# Generates blank game states
def initalize():
    global xoro
    global notxoro
    global game_state_current
    global gameover
    global game_state_future
    global o_groups
    global x_groups
    global non_groups
    global game_state_cache
    global player1_pass
    global player2_pass
    global o_points
    global x_points
    o_groups = []
    x_groups = []
    non_groups = []
    game_state_cache = ''
    player1_pass = 0
    player2_pass = 0
    gameover = 0
    o_points = 0
    x_points = 0
    xoro = 'o'
    notxoro = 'x'

    game_state_current = [
        ['-' for x in range(BOARDSIZE)] for y in range(BOARDSIZE)]
    game_state_future = [
        ['-' for x in range(BOARDSIZE)] for y in range(BOARDSIZE)]

# prints the supplied gamestate
def printboard(gs):
    for row in gs:
        rowprint = ''
        for element in row:
            rowprint += element
            rowprint += ' '
        print(rowprint)
## Returns a list of the board positions surrounding the passed group.
def gperm(group):
    permimeter = []
    hit = 0
    loss = 0
    # Adds permimeter spots below
    # Works by looking from top to bottom, left to right,
    # at each posisition on the board.  When a posistion
    # is hit that is in the given group, I set hit = 1.
    # Then, at the next position that is not in that group,
    # or if the end of the column is reached, I set loss = 1.
    # That point is the first point below a point in that group,
    # so it is part of the permieter of that group.
    for i in range(BOARDSIZE):
        hit = 0
        for j in range(BOARDSIZE):
            if [i, j] in group:
                hit = 1
            elif (hit == 1) & ([i, j] not in group):
                loss = 1
            if (hit == 1) & (loss == 1):
                permimeter.append([i, j])
                hit = 0
                loss = 0
    # Adds permimeter spots to the right
    for i in range(BOARDSIZE):
        hit = 0
        for j in range(BOARDSIZE):
            if [j, i] in group:
                hit = 1
            elif (hit == 1) & ([j, i] not in group):
                loss = 1
            if (hit == 1) & (loss == 1):
                permimeter.append([j, i])
                hit = 0
                loss = 0
    # Adds permimeter spots above
    for i in range(BOARDSIZE):
        hit = 0
        for j in range(BOARDSIZE-1, -1, -1):
            if [i, j] in group:
                hit = 1
            elif (hit == 1) & ([i, j] not in group):
                loss = 1
            if (hit == 1) & (loss == 1):
                permimeter.append([i, j])
                hit = 0
                loss = 0
    # Adds permimeter spots to the left
    for i in range(BOARDSIZE):
        j = BOARDSIZE - 1
        hit = 0
        for j in range(BOARDSIZE-1, -1, -1):
            if [j, i] in group:
                hit = 1
            elif (hit == 1) & ([j, i] not in group):
                loss = 1
            if (hit == 1) & (loss == 1):
                permimeter.append([j, i])
                hit = 0
                loss = 0
    return permimeter

# Returns a string that describes the game state
def readable(gs):
    readthis = ''
    readthis += '<<'
    for row in gs:
        for element in row:
            readthis += element
    readthis += '>>'
    return readthis

# Counts the territory captured by each player
def count():
    global non_groups
    global o_points
    global x_points

    # Creates a list of groups (non_groups) of empty positions.
    for i in range(BOARDSIZE):
        for j in range(BOARDSIZE):
            if game_state_current[j][i] == '-':
                new = 1
                for group in non_groups:
                    if [i, j] in gperm(group):
                        group.append([i, j])
                        new = 0
                if new == 1:
                    non_groups.append([[i, j]])
    concat('-')

    o_points = 0
    x_points = 0

    # Gives a point to the each player for every pebble they have
    # on the board.
    for group in o_groups:
        o_points += len(group)
    for group in x_groups:
        x_points += len(group)

    # The permimeter of these empty positions is here considered,
    # and if every position in the permimeter of a non_group is
    # one player or the other, that player gains a number of points
    # equal to the length of that group (the number of positions
    # that their pieces enclose).
    for group in non_groups:
        no = 0
        for element in gperm(group):
            if game_state_current[element[1]][element[0]] != 'o':
                no = 1
        if no == 0:
            o_points += len(group)

    for group in non_groups:
        no = 0
        for element in gperm(group):
            if game_state_current[element[1]][element[0]] != 'x':
                no = 1
        if no == 0:
            x_points += len(group)

# Checks for capture, and removes the captured pieces from the board
def capture(xoro):
    global game_state_future
    global restore_o
    global restore_x
    edited = 0
    if xoro == 'o':
        groups = x_groups
        otherplayer = 'o'
    else:
        groups = o_groups
        otherplayer = 'x'

    # Checks to see, for each group of a particular player,
    # whether any of the board positions in the
    # perimeter around that group are held by the other player.
    # If any position is not held by the other player,
    # the group is not captured, and is safe.  Otherwise,
    # the group is removed.  But we haven't tested this yet
    # to see if this would return the board to a previous
    # state, so we save the removed groups with the restore lists.
    for group in groups:
        safe = 0
        for element in gperm(group):
            if game_state_future[element[1]][element[0]] != otherplayer:
                safe = 1
        if safe != 1:
            edited = 1
            if xoro == 'o':
                restore_x.append(group)
            else:
                restore_o.append(group)
            groups.remove(group)

    # Sets game_state_future given the new captures
    game_state_future = [
        ['-' for x in range(BOARDSIZE)] for y in range(BOARDSIZE)]
    for group in o_groups:
        for point in group:
            game_state_future[point[1]][point[0]] = 'o'
    for group in x_groups:
        for point in group:
            game_state_future[point[1]][point[0]] = 'x'
    return edited

# Checks to see if the new game state, created by the most recent
# move, returns the board to a previous state.  If not, then
# game_state_current is set as this new state, and game_state_past is set as what
# game_state_current was, and
# the new game state is stored in game_state_cache.  The function returns 1
# if the move is valid, 0 otherwise.
def goodmove():
    global game_state_cache
    global game_state_current
    global game_state_future
    if readable(game_state_future) not in game_state_cache:
        game_state_past = []
        game_state_current = []
        for element in game_state_future:
            game_state_past.append(element)
            game_state_current.append(element)
        game_state_cache += readable(game_state_future)
        return 1
    else:
        return 0

# Checks if any groups contain the same point;
# if so, joins them into one group
def concat(xoro):
    global o_groups
    global x_groups
    global non_groups
    if xoro == 'o':
        groups = o_groups
    elif xoro == 'x':
        groups = x_groups
    else:
        groups = non_groups
    i = 0
    # currentgroups and previousgroups are used to compare the number
    # of groups before this nest of whiles to the number after.  If
    # The number is the same, then nothing needed to be concatinated,
    # and we can move on.  If the number is different, two groups
    # were concatinated, and we need to run through this nest again
    # to see if any other groups need to be joined together.
    currentgroups = len(groups)
    previousgroups = currentgroups + 1
    # Checks if the positions contained in any group are to be
    # found in any other group.  If so, all elements of the second are
    # added to the first, and the first is deleted.
    while previousgroups != currentgroups:
        while i < len(groups) - 1:
            reset = 0
            j = i + 1
            while j < len(groups):
                k = 0
                while k < len(groups[i]):
                    if groups[i][k] in groups[j]:
                        for element in groups[j]:
                            if element not in groups[i]:
                                groups[i].append(element)
                        groups.remove(groups[j])
                        reset = 1
                    if reset == 1:
                        break
                    k += 1
                j += 1
            if reset == 1:
                i = -1
            i += 1
        previousgroups = currentgroups
        currentgroups = len(groups)

# Adds point xy to a group if xy is in the
# perimeter of an existing group, or creates
# new group if xy is not a part of any existing group.
def addpoint(xy, xoro):
    global o_groups
    global x_groups
    if xoro == 'o':
        groups = o_groups
    else:
        groups = x_groups
    new = 1
    for group in groups:
        if xy in gperm(group):
            group.append(xy)
            new = 0
    if new == 1:
        groups.append([xy])

def simple_score():
    x_pieces = 0
    o_pieces = 0
    for row in range(BOARDSIZE):
        for col in range(BOARDSIZE):
            if(game_state_current[row][col] == 'x'):
                x_pieces += 1
            if(game_state_current[row][col] == 'o'):
                o_pieces += 1
    return x_pieces - o_pieces

# after a seccuesfull move return new board state, absolute score from players perspective, if the game is finished
def turn(xy, xoro):
    global game_state_future
    col = xy[0]
    row = xy[1]

    # Ensures that the input is on the board
    if(not(xoro == 'x' or xoro == 'o')):
            return -1
    elif (col >= BOARDSIZE) or (col < 0) or (row >= BOARDSIZE) or (row < 0):
        return -1
    elif game_state_current[row][col] != '-':
        return -1

    game_state_future[row][col] = xoro
    addpoint(xy, xoro)
    concat(xoro)
    minihold = 1
    # Edited is a value used to check
    # whether any capture is made.  capture()
    # is called as many times as until no pieces
    # are capture (until edited does not change
    # to 1)
    edited = 0
    while minihold == 1:
        restore_o = []
        restore_x = []
        if(capture(xoro) or capture(notxoro)):
            edited = 1
        if edited == 0:
            minihold = 0
            edited = 0
        else:
            edited = 0
        # Checks to see if the move, given all the
        # captures it causes, would return the board
        # to a previous game state.
    if goodmove() == 0:
        for group in restore_o:
            o_groups.append(group)
        for group in restore_x:
            x_groups.append(group)
    # update score
    if(xoro == "x"):
        score = simple_score()
    else:
        score = -simple_score()
    if(len(get_available_moves()) == 0 or score >= ((BOARDSIZE*BOARDSIZE)/2)):
        done = 1
    else:
        done = 0
    return game_state_current, score, done

def get_available_moves():
    available_moves = []
    for col in range(BOARDSIZE):
        for row in range(BOARDSIZE):
            if(game_state_current[row][col] == "-"):
                available_moves.append([col,row])#x = col y is row
    return available_moves

def random_move():
    available_moves = get_available_moves()
    return random.choice(available_moves)

def get_game_state_int():
    game_state_int = []
    for col in range(BOARDSIZE):
        for row in range(BOARDSIZE):
            if(game_state_current[row][col] == "-"):
                game_state_int.append(0)
            if(game_state_current[row][col] == "x"):
                game_state_int.append(1)
            if(game_state_current[row][col] == "o"):
                game_state_int.append(2)

# initalize()

# done = 0
# player = xoro
# test1 = []
# while not done:
#     _, _,done = turn(random_move(), player)
#     if(player == xoro):
#         player = notxoro
#     else:
#         player = xoro

# # turn([2,1], xoro)
# printboard(game_state_current)
# count()
# print(x_points)
# print(o_points)
# print("done")
