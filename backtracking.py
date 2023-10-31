import copy
from shapely.geometry import LineString


def load_crossword_puzzle(filename):
    """
	Loads crossword puzzle into list.
	:param filename: name of text file containing crossword puzzle
	:return: list containing crossword puzzle
	"""

    crossword = []
    with open(filename, 'r') as cfile:
        puzzle = cfile.readlines()
    for line in puzzle:
        replaced = line.replace("\t", "")
        replaced = replaced.replace("\n", "")
        replaced = replaced.replace(" ", "")
        crossword.append(list(replaced))
    return crossword


def load_dictionary(filename):
    """
	Loads list of words to use in the crossword puzzle.
	:param filename: name of text file containing word dictionary
	:return: list of words to use in dictionary
	"""
    dictionary = []
    with open(filename, 'r') as dfile:
        wordslist = dfile.readlines()
    for word in wordslist:
        replaced = word.replace("\n", "")
        dictionary.append(replaced)
    return dictionary


def find_horizontal_words(crossword):
    """

    :param crossword:
    :return:
    """
    horizontal_words = []

    for row in range(len(crossword)):

        column = 0
        word = Word()
        finished = False
        prev = '#'

        while column <= len(crossword[row]) - 1:

            if crossword[row][column] == '0':

                if prev == '0':
                    word.length += 1
                    prev = '0'
                    if column == len(crossword[row]) - 1:
                        if not finished:
                            finished = True
                        word.end_coord = (row, column)
                        prev = '#'

                elif prev == "#":
                    if finished:
                        finished = False
                    word.start_coord = (row, column)
                    word.length += 1
                    prev = '0'

            elif crossword[row][column] == '#':

                if prev == '0':
                    if not finished:
                        finished = True
                    if word.length > 1:
                        word.end_coord = (row, column - 1)
                    else:
                        word = Word()
                    prev = '#'

            if word.length > 1 and finished:
                word.orientation = 0
                horizontal_words.append(word)
                word = Word()
                finished = False

            column += 1

    return horizontal_words


def find_vertical_words(crossword):
    """

    :param crossword:
    :return:
    """
    vertical_words = []
    word = Word()

    for column in range(0, len(crossword[0])):
        started = False
        for row in range(0, len(crossword) - 1):
            if crossword[row][column] == '0' and crossword[row + 1][column] == '0':
                if not started:
                    started = True
                    word.start_coord = (row, column)

                if row == len(crossword) - 2 and started:
                    word.end_coord = (row + 1, column)
                    word.length = word.end_coord[0] - word.start_coord[0] + 1
                    word.orientation = 1
                    vertical_words.append(word)
                    word = Word()
                    started = False
            else:
                if started:
                    word.end_coord = (row, column)
                    word.length = word.end_coord[0] - word.start_coord[0] + 1
                    word.orientation = 1
                    vertical_words.append(word)
                    word = Word()
                    started = False

    return vertical_words


def backtracking(assigned_variable_list, not_assigned_variable_list, dict):
    """

    :param assigned_variable_list:
    :param not_assigned_variable_list:
    :param dict:
    :return:
    """
    if len(not_assigned_variable_list) == 0:
        return assigned_variable_list

    var = not_assigned_variable_list[0]

    possible_val = get_possible_values(var, assigned_variable_list, dict)

    for val in possible_val:
        check_var = copy.deepcopy(var)
        check_var.value = val
        if check_constraint(check_var, assigned_variable_list):
            var.value = val
            result = backtracking(assigned_variable_list + [var], not_assigned_variable_list[1:], dict)
            if result != None:
                return result
            # we've reached here because the choice we made by putting some 'word' here was wrong
            # hence now leave the word cell unassigned to try another possibilities
            var.value = ''

    return None


# returns all possible values for the desired variable
def get_possible_values(var, assigned_variable_list, dict):
    """
	Function to return the possible values
	:param var:
	:param assigned_variable_list:
	:param dict:
	:return:
	"""
    possibles_values = []

    for val in dict:
        if len(val) == var.length:
            possibles_values.append(val)

    for item in assigned_variable_list:
        if item.value in possibles_values:
            possibles_values.remove(item.value)

    return possibles_values


# checks var against assigned variable list
def check_constraint(var, assigned_variable_list):
    """
	Function to validate constraints
	:param var:
	:param assigned_variable_list:
	:return:
	"""
    if assigned_variable_list is not None:
        for word in assigned_variable_list:
            # if orientation is equal they will never interesect!
            if var.orientation != word.orientation:
                intersection = check_intersections(var, word)
                if len(intersection) != 0:
                    if var.orientation == 0:  # horizontal
                        if var.value[int(intersection[0][1] - var.start_coord[1])] != word.value[
                            int(intersection[0][0] - word.start_coord[0])]:
                            return False
                    else:  # vertical
                        if var.value[int(intersection[0][0] - var.start_coord[0])] != word.value[
                            int(intersection[0][1] - word.start_coord[1])]:
                            return False
    return True


# treat words here like lines so we find the intersection point of horizontal and vertical words (the character
# position - intersection point is the constraints which the algorithm must apply to get a valid solution)
def check_intersections(w1, w2):
    """
	Check to see if words are intersecting.
	:param w1: word 1
	:param w2: word 2
	:return:
	"""
    line1 = LineString([w1.start_coord, w1.end_coord])
    line2 = LineString([w2.start_coord, w2.end_coord])

    intersection_point = line1.intersection(line2)

    if not intersection_point.is_empty:
        return [intersection_point.coords[0]]  # result(float)
    else:
        return []


def insert_word_to_puzzle(crossword, word, coord, orientation):
    """
	Add valid word to puzzle
	:param crossword:
	:param word:
	:param coord:
	:param orientation:
	:return:
	"""
    pos_count = 0
    for char in word:
        if orientation == 0:  # horizontal if orientation == 0
            crossword[coord[0]][coord[1] + pos_count] = char
        else:
            crossword[coord[0] + pos_count][coord[1]] = char
        pos_count += 1
    return crossword


def custom_heuristic():
    print('custom heuristic: ')


def execute_application():
    """
	Runs the application.
	:return:
	"""

    cw_puzzle = load_crossword_puzzle("crossword_1.txt")
    dictionary = load_dictionary("word_list.txt")
    horizontal_word = find_horizontal_words(cw_puzzle)
    vertical_word = find_vertical_words(cw_puzzle)
    total_words = horizontal_word + vertical_word
    assign_var_list = []
    suggested_solution = backtracking(assign_var_list, total_words, dictionary)

    print("---------- Crossword ---------")
    for line in cw_puzzle:
        print(line)
    print("------------------------------")
    print("---------- Solution ----------")

    if suggested_solution is None:
        print("No solution found")
    else:
        for word in suggested_solution:
            insert_word_to_puzzle(cw_puzzle, word.value, word.start_coord, word.orientation)

        for line in cw_puzzle:
            print(line)

    print("------------------------------")


class Word:
    # coordinates of the starting and ending point
    start_coord = ()
    end_coord = ()

    # horizontal word = 0, vertical word = 1
    orientation = 0

    # word length
    length = 0

    # value assigned to this word
    value = ''
