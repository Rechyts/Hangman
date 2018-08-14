import requests, string, random


token = '614927968:AAFs24jmYDlYzTSfWPFSRZB8kiucqdPwYVQ'
url = 'https://api.telegram.org/bot{}/'.format(token)


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=120):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)-1]

        return last_update


hangbot = BotHandler(token)
WORDLIST_FILENAME = "words.txt"

def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.

    Depending on the size of the word list, this function may
    take a while to finish.
    """
    # print("Loading word list from file...")
    # inFile: file
    inFile = open(WORDLIST_FILENAME, 'r')
    # line: string
    line = inFile.readline()
    # wordlist: list of strings
    wordlist = line.split()
    # print("  ", len(wordlist), "words loaded.")
    return wordlist


def choose_word(wordlist):
    """
    wordlist (list): list of words (strings)

    Returns a word from wordlist at random
    """
    return random.choice(wordlist)


def is_word_guessed(secret_word, letters_guessed):
    '''
    secret_word: string, the word the user is guessing; assumes all letters are
      lowercase
    letters_guessed: list (of letters), which letters have been guessed so far;
      assumes that all letters are lowercase
    returns: boolean, True if all the letters of secret_word are in letters_guessed;
      False otherwise
    '''
    list_answer = []
    for letter in letters_guessed:
        if letter in secret_word:
            list_answer.append(True)
        else:
            list_answer.append(False)
    return all(list_answer)


def get_guessed_word(secret_word, letters_guessed):
    '''
    secret_word: string, the word the user is guessing
    letters_guessed: list (of letters), which letters have been guessed so far
    returns: string, comprised of letters, underscores (_), and spaces that represents
      which letters in secret_word have been guessed so far.
    '''
    list_answer = []
    for letter in secret_word:
        if letter in letters_guessed:
            list_answer.append(letter)
        else:
            list_answer.append('_ ')
    return ''.join(list_answer)


def get_available_letters(letters_guessed):
    '''
    letters_guessed: list (of letters), which letters have been guessed so far
    returns: string (of letters), comprised of letters that represents which letters have not
      yet been guessed.
    '''
    list_available_letters = list(string.ascii_lowercase)
    for letter in letters_guessed:
        if letter in list_available_letters:
            list_available_letters.remove(letter)
    return ''.join(list_available_letters)

def match_with_gaps(my_word, other_word, available_letters):
    '''
    my_word: string with _ characters, current guess of secret word
    other_word: string, regular English word
    returns: boolean, True if all the actual letters of my_word match the
        corresponding letters of other_word, or the letter is the special symbol
        _ , and my_word and other_word are of the same length;
        False otherwise:
    '''
    my_clear_word = my_word.replace(' ', '')
    list_true = []
    if len(my_clear_word) == len(other_word):
        for num in range(len(other_word)):
            if my_clear_word[num] == '_' and other_word[num] not in available_letters:
                return False
            else:
                if my_clear_word[num] == other_word[num] or my_clear_word[num] == '_':
                    list_true.append(True)
                else:
                    list_true.append(False)
        return all(list_true)
    else:
        return False


def show_possible_matches(my_word, available_letters):
    '''
    my_word: string with _ characters, current guess of secret word
    returns: nothing, but should print out every word in wordlist that matches my_word
             Keep in mind that in hangman when a letter is guessed, all the positions
             at which that letter occurs in the secret word are revealed.
             Therefore, the hidden letter(_ ) cannot be one of the letters in the word
             that has already been revealed.

    '''
    list_posible_matches = []
    for word in load_words():
        if match_with_gaps(my_word, word, available_letters):
            list_posible_matches.append(word)
    if list_posible_matches:
        return(' '.join(list_posible_matches))
    else:
        return ('No matches found')


def main():
    new_offset = None
    while True:
        hangbot.get_updates(new_offset)
        last_update = hangbot.get_last_update()
        print(last_update)
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        if last_chat_text == '/start':
            hangbot.send_message(last_chat_id, 'Welcome to the game Hangman!\nfor starting game you need send /hangman\nYou have 6 guesses left and 3 warning left.\nFor the wrong vowel - a e i o subtracted 2 guesses, else - 1 guesses\nGood luck!')
        elif last_chat_text == '/hangman':
            secret_word = choose_word(wordlist=load_words())
            list_tempt = []
            true_list = []
            guess = 6
            warning = 3
            hangbot.send_message(last_chat_id, 'I am thinking of a word that is {} letters long.\nYou have {} warnings left.'.format(len(secret_word), warning))
            while guess > 0:
                hangbot.send_message(last_chat_id, 'You have {} guesses left.\nAvailable letters: {}\nPlease guess a letter:'.format(guess, get_available_letters(list_tempt)))
                new_offset = last_update_id + 1
                hangbot.get_updates(new_offset)
                last_update = hangbot.get_last_update()
                print(last_update)
                last_update_id = last_update['update_id']
                last_chat_text = last_update['message']['text']
                last_chat_id = last_update['message']['chat']['id']
                if last_chat_text.isalpha() and last_chat_text.lower() not in list_tempt:
                    list_tempt.append(last_chat_text.lower())
                    true_list.append(last_chat_text.lower())
                    if is_word_guessed(secret_word, true_list):
                        hangbot.send_message(last_chat_id, 'Good guess: {}'.format(get_guessed_word(secret_word, true_list)))
                    else:
                        if last_chat_text.lower() not in 'aioe':
                            guess -= 1
                        else:
                            guess -= 2
                        true_list.pop()
                        hangbot.send_message(last_chat_id, 'Oops! That letter is not in my word: \n{}'.format(get_guessed_word(secret_word, true_list)))
                    if get_guessed_word(secret_word, true_list) == secret_word:
                        hangbot.send_message(last_chat_id, 'Congratulations, you won!\nYour total score for this game is: {}'.format(guess*len(true_list)))
                        break
                elif last_chat_text.lower() == '*':
                    hangbot.send_message(last_chat_id, 'Possible word matches are:\n{}'.format(show_possible_matches(get_guessed_word(secret_word, true_list), get_available_letters(list_tempt))))
                else:
                    if warning > 0:
                        warning -= 1
                        if last_chat_text.lower() in list_tempt:
                            hangbot.send_message(last_chat_id, "Oops! You've already guessed that letter. You have {} warning left:\n{}".format(warning, get_guessed_word(secret_word, true_list)))
                        else:
                            hangbot.send_message(last_chat_id, 'Oops! That is not a valid letter. You have {} warning left: {}'.format(warning, get_guessed_word(secret_word, true_list)))
                    else:
                        guess -= 1
                        if last_chat_text.lower() in list_tempt:
                            hangbot.send_message(last_chat_id, "Oops! You've already guessed that letter. You have no warnings left so you lose one guess:\n{}".format(get_guessed_word(secret_word, true_list)))
                        else:
                            hangbot.send_message(last_chat_id, 'Oops! That is not a valid letter. You have no warnings left so you lose one guess:\n{}'.format(get_guessed_word(secret_word, true_list)))
                if guess <= 0:
                    hangbot.send_message(last_chat_id, 'Sorry, you ran out of guesses. The word was {}.'.format(secret_word))

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()