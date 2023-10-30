import copy
from shapely.geometry import LineString


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


def load_crossword_puzzle(filename):
	"""

	:param filename:
	:return:
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

	:param filename:
	:return:
	"""
	dictionary = []
	with open(filename, 'r') as dfile:
		wordslist = dfile.readlines()
	for word in wordslist:
		replaced = word.replace("\n", "")
		dictionary.append(replaced)
	return dictionary


def find_horizontal_words(crossword):
	horizontal_words = []

	for row in range(len(crossword)):

		column = 0
		word = Word()
		finished = False
		prev = '#'  # prev mean the previous char in the word

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
	vertical_words = []
	word = Word()
	started = False

	for column in range(0, len(crossword[0])):
		started = False
		for row in range(0, len(crossword) - 1):
			if crossword[row][column] == '0' and crossword[row + 1][column] == '0':
				if started == False:
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
	# theres are no variables to assign a value so we are done
	if len(not_assigned_variable_list) == 0:
		return assigned_variable_list

	var = not_assigned_variable_list[0]

	possible_val = get_possible_values(var, assigned_variable_list, dict)

	for val in possible_val:
		# we create the variable check_var to do the checking and avoid assigning values which do not comply with the constraint
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
	possibles_values = []

	for val in dict:
		if len(val) == var.length:
			possibles_values.append(val)

	for item in assigned_variable_list:
		if item.value in possibles_values:
			possibles_values.remove(item.value)

	return possibles_values


#checks var against assigned variable list
def check_constraint(var, assigned_variable_list):
	if assigned_variable_list != None:
		for word in assigned_variable_list:
			#if orientation is equal they will never interesect!
			if var.orientation != word.orientation:
				intersection = check_intersections(var, word)
				if len(intersection) != 0:
					if var.orientation == 0: #horizontal
						if var.value[int(intersection[0][1]-var.start_coord[1])] != word.value[int(intersection[0][0]-word.start_coord[0])]:
							return False
					else: #vertical
						if var.value[int(intersection[0][0]-var.start_coord[0])] != word.value[int(intersection[0][1]-word.start_coord[1])]:
							return False
	return True


#treat words here like lines so we find the intersection point of horizontal and vertical words (the character position - intersection point is the constraints which the algorithm must apply to get a valid solution)
def check_intersections(w1, w2):
	line1 = LineString([w1.start_coord, w1.end_coord])
	line2 = LineString([w2.start_coord, w2.end_coord])

	intersection_point = line1.intersection(line2)

	if not intersection_point.is_empty:
		return [intersection_point.coords[0]] #result(float)
	else:
		return []


def insert_word_to_puzzle(crossword, word, coord, orientation):
	pos_count = 0
	for char in word:
		if orientation == 0: #horizontal if orientation == 0
			crossword[coord[0]][coord[1]+pos_count] = char
		else:
			crossword[coord[0]+pos_count][coord[1]] = char
		pos_count += 1
	return crossword


def execute_application():
	cw_puzzle = load_crossword_puzzle("crossword_3.txt")
	dict = load_dictionary("words.txt")
	horizontal_word = find_horizontal_words(cw_puzzle)
	vertical_word = find_vertical_words(cw_puzzle)
	total_words = horizontal_word + vertical_word
	assign_var_list = []
	suggested_solution = backtracking(assign_var_list, total_words, dict)

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

