import numpy as np
import multiprocessing
import time
import copy
import random
import signal


class Intersection:
    def __init__(self, coord, index, intersectedID):
        self.coord = coord
        self.index = index
        self.intersectedID = intersectedID


class Word:
    def __init__(self, pos, horizontal, length, remainingValues, idN):
        self.pos = pos
        self.horizontal = horizontal
        self.length = length
        self.remainingValues = remainingValues
        self.letters = [0] * length
        self.id = idN
        self.intersections = []
        self.intersectionsNumber = 0


def load_crossword(crossword):
    """
    Loads text file containing crossword puzzle into numpy matrix.
    :param crossword: File name
    :return: numpy matrix containing crossword puzzle
    """
    table = []

    with open(crossword, 'r') as file:
        for line in file:
            line = line.strip()
            row = [int(cell) if cell != '#' else 35 for cell in line]
            table.append(row)

    np_matrix = np.array(table, dtype=np.uint8)
    return np_matrix


def vert_id_by_coord(coord, vertical_words):
    """
    Gets the ID of vertical word from given coordinates
    :param coord: coordinates
    :param vertical_words: vertical words
    :return: Id of vertical word or -1 if word is not found
    """
    for word in vertical_words:
        if word.pos[1] == coord[1]:
            if word.pos[0] <= coord[0] <= word.pos[0] + word.length:
                return word.id
    return -1


def hor_id_by_coord(coord, horizontal_words):
    """
    Gets the ID of horizontal word from given coordinates
    :param coord: coordinates
    :param horizontal_words: horizontal words
    :return: ID of a horizontal word or -1 if word is not found
    """
    for word in horizontal_words:
        if word.pos[0] == coord[0]:
            if word.pos[1] <= coord[1] <= word.pos[1] + word.length:
                return word.id
    return -1


def search_hor_vars(np_matrix, id_n):
    """
    Searches for horizontal words to fill crossword
    :param np_matrix: numpy matrix
    :param id_n: ID
    :return: list of horizontal words
    """
    words = []

    for x in range(0, np_matrix.shape[0]):
        length = 0
        for y in range(1, np_matrix.shape[1]):
            if length == 0:
                if np_matrix[x][y - 1] != 35 and np_matrix[x][y] != 35:
                    length = 2
                    continue
            if length > 1:
                if np_matrix[x][y] != 35:
                    length += 1
                    continue
                else:
                    pos = (x, y - length)
                    words.append(Word(pos, 1, length, length, id_n))
                    id_n += 1
                    length = 0

        if length > 1:
            pos = (x, np_matrix.shape[1] - length)
            word = Word(pos, 1, length, length, id_n)
            id_n += 1
            words.append(word)
    return words


def search_vert_words(np_matrix, id_n):
    """
    Searches for vertical words to fill crossword
    :param np_matrix: numpy matrix
    :param id_n: ID
    :return: vertical words
    """
    words = []
    for y in range(0, np_matrix.shape[1]):
        length = 0
        for x in range(1, np_matrix.shape[0]):
            if length == 0:
                if np_matrix[x - 1][y] != 35 and np_matrix[x][y] != 35:
                    length = 2
                    continue

            if length > 1:
                if np_matrix[x][y] != 35:
                    length += 1
                    continue
                else:
                    pos = (x - length, y)
                    words.append(Word(pos, 0, length, length, id_n))
                    id_n += 1
                    length = 0
        if length > 1:
            pos = (np_matrix.shape[0] - length, y)
            word = Word(pos, 0, length, length, id_n)
            id_n += 1
            words.append(word)
    return words


def intersections(words, horizontal_words, vert_words, crossword):
    """
    Finds the intersections and stores them in an attribute for its corresponding word
    :param words: given words
    :param horizontal_words: horizontal words
    :param vert_words: vertical words
    :param crossword: crossword puzzle
    :return: list of intersected words
    """
    for w in words:
        if w.horizontal == 1:
            y_start = w.pos[1]
            y_end = y_start + w.length - 1
            for y in range(y_start, y_end + 1):
                if w.pos[0] > 0:
                    if crossword[w.pos[0] - 1][y] == 0:
                        index = y - w.pos[1]
                        intersected_id = vert_id_by_coord((w.pos[0], y), vert_words)
                        w.intersections.append(Intersection((w.pos[0], y), index, intersected_id))
                        continue
                if w.pos[0] < crossword.shape[0] - 1:
                    if crossword[w.pos[0] + 1][y] == 0:
                        index = y - w.pos[1]
                        intersected_id = vert_id_by_coord((w.pos[0], y), vert_words)
                        w.intersections.append(Intersection((w.pos[0], y), index, intersected_id))
        else:
            x_start = w.pos[0]
            x_end = x_start + w.length - 1
            for x in range(x_start, x_end + 1):
                if w.pos[1] > 0:
                    if crossword[x][w.pos[1] - 1] == 0:
                        index = x - w.pos[0]
                        intersected_id = hor_id_by_coord((x, w.pos[1]), horizontal_words)
                        w.intersections.append(Intersection((x, w.pos[1]), index, intersected_id))
                        continue
                if w.pos[1] < crossword.shape[1] - 1:
                    if crossword[x][w.pos[1] + 1] == 0:
                        index = x - w.pos[0]
                        intersected_id = hor_id_by_coord((x, w.pos[1]), horizontal_words)
                        w.intersections.append(Intersection((x, w.pos[1]), index, intersected_id))
        w.intersectionsNumber = len(w.intersections)

    return words


def fill_dict(dict_path):
    """
    Gets words from the dictionary path
    :param dict_path: path to dictionary text file
    :return:
    """

    dictionary = {}

    for line in open(dict_path, encoding="Windows-1252"):
        word = line[:-1]
        size = len(word)
        byte_arr = bytearray(word, 'Windows-1252')
        ascii_word = list(byte_arr)

        if size in dictionary:
            dictionary[size].append(ascii_word)
        else:
            dictionary[size] = [ascii_word]

    # Transforming list into numpy array
    for k, v in dictionary.items():
        random.shuffle(v)
        numpy_arr = np.array(v, dtype=np.uint8)
        dictionary[k] = numpy_arr

    return dictionary


def domain(var, d):
    """
    Gets the domain of a variable
    :param var: variable
    :param d: domain
    :return: domain of given variable
    """
    return d[var.id]


def store_to_crossword(lva, crossword):
    """
    Write LVA values to crossword
    :param lva: LVA
    :param crossword: crossword
    :return: crossword
    """
    for word in lva.values():
        index = 0
        if word.horizontal == 1:
            x = word.pos[0]
            for y in range(word.pos[1], word.pos[1] + word.length):
                crossword[x][y] = word.letters[index]
                index += 1
        else:
            y = word.pos[1]
            for x in range(word.pos[0], word.pos[0] + word.length):
                crossword[x][y] = word.letters[index]
                index += 1
    return crossword


def store_word_to_crossword(word, crossword):
    """
    Writes a word to the crossword
    :param word: word to write
    :param crossword: base crossword puzzle
    :return: updated crossword puzzle
    """
    index = 0
    if word.horizontal == 1:
        x = word.pos[0]
        for y in range(word.pos[1], word.pos[1] + word.length):
            crossword[x][y] = word.letters[index]
            index += 1
    else:
        y = word.pos[1]
        for x in range(word.pos[0], word.pos[0] + word.length):
            crossword[x][y] = word.letters[index]
            index += 1
    return crossword


def print_crossword(crossword):
    """
    Formats and prints crossword
    :param crossword: crossword
    :return: None
    """
    print('\n'.join([''.join(['{:4}'.format(chr(item))
                              for item in row]) for row in crossword]))


def pass_restrictions(var, word, lva, r):
    """
    Validates restrictions from other variables
    :param var: variable
    :param word: words
    :param lva: LVA
    :param r:
    :return: Boolean
    """
    intersections_1 = var.intersections

    for i in intersections_1:
        if i.intersectedID not in lva:
            continue

        intersected_word = lva[i.intersectedID]
        candidate_value = word[i.index]

        if intersected_word.horizontal == 1:
            intersection_index = i.coord[1] - intersected_word.pos[1]
            intersected_value = intersected_word.letters[intersection_index]
        else:
            intersection_index = i.coord[0] - intersected_word.pos[0]
            intersected_value = intersected_word.letters[intersection_index]

        if intersected_value != candidate_value:
            return False

    return True


def insert_lva(lva, var, crossword):
    """
    Writes LVA list to new variable
    :param lva: LVA list
    :param var: variable
    :param crossword: crossword
    :return: LVA list
    """
    var.letters = crossword.tolist()
    lva[var.id] = var
    return lva


def backtracking(lva, lvna, d, r, crossword):
    """
    Implements backtracking algorithm
    :param lva: LVA values
    :param lvna:
    :param d: domain
    :param r: r
    :param crossword: crossword
    :return:
    """

    if not lvna:
        return lva, 1

    var = lvna[0]

    domain_values = domain(var, d)
    for cWord in domain_values:

        if pass_restrictions(var, cWord, lva, 0):

            lva = insert_lva(lva, var, cWord)
            lva, r = backtracking(lva, lvna[1:], d, r, crossword)
            if r == 1:
                return lva, r

    if r == 0 and var.id in lva:
        lva.pop(var.id)

    return lva, 0


def update_domains(var, lvna, cr, d):
    """
    Updates all domains for variables
    :param var:
    :param lvna:
    :param cr:
    :param d:
    :return:
    """
    validate_domain = True
    temp = copy.copy(d)

    dictionary_id = {}
    for i, vna in enumerate(lvna):
        dictionary_id[vna.id] = i

    for inter in var.intersections:
        if inter.intersectedID not in dictionary_id:
            continue

        intersected_word_index = dictionary_id[inter.intersectedID]

        word_intersected = lvna[intersected_word_index]
        temp_domain = temp[word_intersected.id]

        x = inter.coord[0]
        y = inter.coord[1]

        index_inter = 0
        for intersected in word_intersected.intersections:
            if intersected.intersectedID == var.id:
                index_inter = intersected.index

        existing_value = cr[x][y]
        if existing_value > 64:  # is a letter
            sub_index = np.where(temp_domain[:, index_inter] == existing_value)
            temp_domain = temp_domain[sub_index]
            if temp_domain.shape[0] == 0:
                validate_domain = False
                break

        temp[word_intersected.id] = temp_domain
        lvna[intersected_word_index].remainingValues = temp_domain.shape[0]

    if not validate_domain:
        return None
    else:
        return temp


def backtracking_forward_checking(lva, lvna, d, r, crossword_restrictions):
    """
    Implements backtracking algorithm with forward checking
    :param lva:
    :param lvna:
    :param d:
    :param r:
    :param crossword_restrictions:
    :return:
    """
    if not lvna:
        print_crossword(crossword_restrictions)
        return lva, 1

    lvna.sort(key=lambda x: x.remainingValues)

    var = lvna[0]

    domain_values = domain(var, d)

    for cWord in domain_values:
        if not pass_restrictions(var, cWord, lva, 0):
            continue

        var.letters = cWord.tolist()
        crossword_restrictions_backup = copy.copy(crossword_restrictions)
        crossword_restrictions = store_word_to_crossword(var, crossword_restrictions)

        update_domains_result = update_domains(var, lvna, crossword_restrictions, d)

        if update_domains_result is None:
            var.letters = [0] * var.length
            crossword_restrictions = crossword_restrictions_backup
            continue

        lva = insert_lva(lva, var, cWord)
        lva, r = backtracking_forward_checking(lva, lvna[1:], update_domains_result, r, crossword_restrictions)
        if r == 1:
            return lva, r

    if r == 0 and var.id in lva:
        lva.pop(var.id)

    return lva, 0


def create_domains(dict, words):
    """
    Creates domains for each variable
    :param dict:
    :param words:
    :return:
    """
    domains = {}
    for w in words:
        domains[w.id] = dict[w.length]
        w.remainingValues = dict[w.length].shape[0]

    return domains, words


def shuffle_domains(d):
    """
    Shuffles domains
    :param d:
    :return:
    """
    for k, v in d.items():
        np.random.shuffle(v)
        d[k] = v
    return d


def handler(signum, frame):
    """
    Exception handler
    :param signum:
    :param frame:
    :return:
    """
    raise Exception("end of time")


def long_crossword_signal(words, domains, crossword):
    """
    Handling function using SIGALRM
    :param words:
    :param domains:
    :param crossword:
    :return:
    """
    # only works on UNIX

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        backtracking_forward_checking({}, copy.deepcopy(words), copy.deepcopy(domains), 0, copy.deepcopy(crossword))
    except Exception as exc:
        print(exc)
        long_crossword_signal(words, domains, crossword)


# Handling function timeout using Process.join()
def long_crossword_join(words, domains, crossword):
    """
    Handling function
    :param words:
    :param domains:
    :param crossword:
    :return:
    """
    # Using processes and not threads because formers don't share variables.

    p = multiprocessing.Process(target=backtracking_forward_checking, args=({}, words, domains, 0, crossword))
    p.start()

    p.join(1)

    if p.is_alive():
        p.kill()
        p.join()
        domains = shuffle_domains(domains)
        long_crossword_join(words, domains, crossword)


def execute_forward_checking(crossword_name, dictionary_name, forward_checking_version):
    """
    Executes forward checking algorithm
    :param crossword_name: Name of crossword text file
    :param dictionary_name: Name of dictionary text file
    :param forward_checking_version: Boolean for forward checking
    :return: None
    """
    start_time = time.time()

    crossword = load_crossword(crossword_name)

    horizontal_words = search_hor_vars(crossword, 0)
    vertical_words = search_vert_words(crossword, len(horizontal_words))
    words = horizontal_words + vertical_words
    words = intersections(words, horizontal_words, vertical_words, crossword)

    dict = fill_dict(dictionary_name)
    domains, words = create_domains(dict, words)

    if not forward_checking_version:
        bt_start = time.time()

        lva, r = backtracking({}, words, domains, 0, crossword)
        crossword = store_to_crossword(lva, crossword)
        print_crossword(crossword)

        bt_end = time.time()
        bt_elapsed_time = bt_end - bt_start
        print("\nBacktracking: ", bt_elapsed_time, "seconds")

    else:
        fc_start = time.time()
        if crossword_name == "crossword_2.txt":
            long_crossword_join(words, domains, crossword)
        else:

            lva, r = backtracking_forward_checking({}, words, domains, 0, crossword)
        fc_end = time.time()
        fc_elapsed_time = fc_end - fc_start
        print("\nForward Checking: ", fc_elapsed_time, "seconds")

    end_time = time.time()
    total_elapsed_time = end_time - start_time

    print("Total elapsed time: ", total_elapsed_time, "seconds\n\n")


def print_outputs():
    """
    Prints outputs to terminal
    :return:
    """
    print("CROSSWORD CB Backtracking\n")
    execute_forward_checking("crossword_1.txt", "word_list.txt", False)

    print("CROSSWORD CB Forward Checking\n")
    execute_forward_checking("crossword_1.txt", "word_list.txt", True)

    print("CROSSWORD A Forward Checking\n")
    execute_forward_checking("crossword_2.txt", "words.txt", True)

    print("CROSSWORD A Forward Checking\n")
    execute_forward_checking("crossword_3.txt", "words.txt", True)
