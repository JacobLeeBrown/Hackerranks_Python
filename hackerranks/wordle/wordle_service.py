
import csv
from datetime import datetime, timedelta
import file_service as fs
import word_analysis_service as was


def get_all_used_words():
    used_words_ = []
    today = datetime.today()
    with open('all_wordle_words.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        word_count = 0
        for row in csv_reader:
            if word_count == 0:  # Header row
                word_count += 1
            else:
                row_date = datetime.strptime(row['date'], '%b %d %Y')
                if row_date >= (today + timedelta(days=7)):  # Offset for removed words
                    break
                else:
                    word = row['word'].strip()
                    if len(word) != 5:
                        pass  # Skip removed words
                    else:
                        used_words_.append(word)
                        word_count += 1
        print(f'Processed {word_count-1} used Wordle words.')
    return used_words_


def solver(words, ignored_words_, correct_, close_, wrong_):
    if _solver_check_empty(correct_, close_, wrong_):
        return words
    possible_words = []
    for word in words:
        if word in ignored_words_:
            continue
        word_matches = True
        close_dict = _init_close_dict(close_)
        for i, letter in enumerate(word):
            # Conditions for word not being a match
            if letter in wrong_:
                word_matches = False
                break
            if letter in close_[i]:
                word_matches = False
                break
            elif letter in close_dict:  # Found a close letter not in the known wrong position
                close_dict[letter] = True
            if len(correct_[i]) != 0 and letter not in correct_[i]:
                word_matches = False
                break

        # Once all letters are processed, check we covered all close letters
        if word_matches:
            for val in close_dict.values():
                if not val:
                    word_matches = False
                    break

        # If word still matches, then it's a candidate
        if word_matches:
            possible_words.append(word)

    return possible_words


def _solver_check_empty(correct_, close_, wrong_):
    if (correct_ is not None) and (len(correct_) != 0) and (correct_ != [[]]*len(correct_)):
        return False
    if (close_ is not None) and (len(close_) != 0) and (close_ != [[]]*len(close_)):
        return False
    if (wrong_ is not None) and (len(wrong_) != 0):
        return False
    return True


def _init_close_dict(close_):
    d = {}
    for letters in close_:
        for letter in letters:
            d[letter] = False
    return d


if __name__ == '__main__':
    print('Begin wordle_service')
    # wordle_words = get_all_used_words()
    # was.analyze_most_used_letters(wordle_words)
    # fs.get_words_of_length(input_file='scrabble_dict.txt', n=5, alpha_only=True, save=True, output_file='possible_wordle_words.txt')

    used_words = get_all_used_words()
    fs.add_to_file(set(used_words), 'ignored_words.txt')
    ignored_words = fs.load_words('ignored_words.txt')
    possible_wordle_words = fs.load_words('possible_wordle_words_simple.txt')
    analysis = was.analyze_most_used_letters(used_words, should_print=True)

    # Example usage
    # correct = [[], [], [], [], []]
    # close = [[], [], ['A'], ['C'], []]
    # wrong = 'STLEBRIKDOUGH'

    # No Hints
    correct = [[], [], [], [], []]
    close = [[], [], [], [], []]
    wrong = []

    potential_solutions = solver(possible_wordle_words, ignored_words, correct, close, wrong)
    was.find_best_words(potential_solutions, analysis[0], analysis[1], n=20, should_print=True)

    print('End wordle_service')
