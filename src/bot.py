''' Import required modules '''
import random
from threading import Timer
from datetime import datetime
from english_words import english_words_set
from data import (data, User, Message, current_time, user_with_token,
                  user_with_id, user_with_handle, channel_with_id)
from channel import channel_kick
from error import InputError, AccessError

bot_status = {
    'active': False,
    'bot_user': None,
}

def bot_message_parser(token, channel_id, message):
    '''
    Parses a message sent to find valid command
    '''
    if message == '/help':
        bot_help(channel_id)
    elif message == '/time':
        bot_time(channel_id)
    elif message == '/flip':
        bot_flip(channel_id)
    elif message == '/hangman start':
        bot_hangman_start(channel_id)
    elif message.startswith('/kick'):
        bot_kick(token, channel_id, message)
    elif message.startswith('/prune'):
        bot_message_prune(token, channel_id, message)
    elif message.startswith('/guess'):
        bot_hangman_guess(token, channel_id, message)
    elif message.startswith('/choose'):
        bot_choose(channel_id, message)
    elif message.startswith('/dice'):
        bot_dice(channel_id, message)


def bot_init():
    '''
    Creates a bot user if not already started
    '''
    global bot_status
    # Bot not technically registered
    if bot_status['active']:
        return bot_status['bot_user']
    else:
        # Create new bot
        bot_user = User('flockbot@gmail.com', 'c0mpLicAt3d', 'Flockr', 'Bot')
        img_url = 'https://nuvro.com/wp-content/uploads/2018/11/Flock-Logo-1.png'
        bot_user.set_profile_img_url(img_url)
        data['users'].append(bot_user)
        # Change status
        bot_status = {
            'active': True,
            'bot_user': bot_user,
        }
        return bot_user


def bot_send_message(channel, message, temporary):
    '''
    Sends a message to a provided channel through the bot
    The message can be temporary
    '''
    bot_user = bot_init()
    # Bot sends message to channel
    msg = Message(sender=bot_user, message=message, time_created=current_time())
    channel.get_messages().append(msg)
    # Temporary message (automatically removes after 10 seconds)
    if temporary:
        t = Timer(5, channel.get_messages().remove, args=[msg])
        t.start()


######################
## General commands ##
######################
def bot_help(channel_id):
    ''' Displays help message '''
    bot_msg = '''
    Available commands:
    === General ===
    - /help
      displays this message
    - /time
      displays the current time
    - /standup X
      starts a standup for X seconds
    - /prune X
      removes the last X messages - requires admin permissions
    - /kick user_handle
      kicks a specified user from this channel - requires admin permissions
    === Hangman ===
    - /hangman start
      starts a hangman game
    - /guess X
      guess a character or word for an active hangman game
    === Fun Utilities ===
    - /choose A B C.
      bot randomly chooses from the space-separated arguments
    - /flip
      flips a coin - heads or tails?
    - /dice (X)
      rolls a X-sided dice, or a six-sided dice by default
    '''
    bot_send_message(channel_with_id(channel_id), bot_msg, temporary=False)


def bot_time(channel_id):
    '''
    Displays the current time
    '''
    bot_init()
    channel = channel_with_id(channel_id)
    bot_msg = f'The current time is {datetime.now().strftime(r"%A %-d %B %Y, %-I:%M %p")}.'
    bot_send_message(channel, bot_msg, temporary=False)


def bot_kick(token, channel_id, message):
    '''
    Wrapper command for kicking a user from a channel
    '''
    user = user_with_token(token)
    channel = channel_with_id(channel_id)
    try:
        handle = message[6:]
        kick_user = user_with_handle(handle)
        if kick_user is None:
            raise InputError('Please provide a valid user handle!')
        channel_kick(token, channel_id, kick_user.get_u_id())
        bot_msg = f'⚽️ {kick_user.get_handle()} has been kicked by {user.get_handle()}!'
        bot_send_message(channel, bot_msg, temporary=False)
    except Exception as e:
        bot_msg = f'Failed to kick: {e}'
        bot_send_message(channel, bot_msg, temporary=False)


def bot_message_prune(token, channel_id, message):
    '''
    Wrapper command for pruning messages
    '''
    bot_init()
    channel = channel_with_id(channel_id)
    try:
        auth_user = user_with_token(token)
        num_messages = int(message[6:])
        message_prune(token, channel_id, num_messages)
        bot_msg = f'{num_messages} messages have been successfully pruned by {auth_user.get_handle()}'
        bot_send_message(channel, bot_msg, temporary=True)
    except Exception as e:
        bot_msg = f'Failed to prune: {e}'
        bot_send_message(channel, bot_msg, temporary=False)


def message_prune(token, channel_id, num_messages):
    '''
    Prunes the last num_messages messages from a channel
    NOTE: this function cannot be placed in message.py
          due to circular imports
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)
    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel')
    elif auth_user not in channel.get_all_members():
        raise AccessError('Invalid permission')
    elif auth_user not in channel.get_owner_members() and auth_user.get_permission_id() != 1:
        raise AccessError('Invalid permission for pruning messages')
    total_messages = len(channel.get_messages())
    if num_messages > total_messages:
        raise InputError(f'Attempted to prune more messages than there are messages in the channel')
    # Prune last num_messages messages
    del channel.get_messages()[-num_messages:]

    return {
    }


######################
## Hangman commands ##
######################
TOTAL_HANGMAN_GUESSES = 10
hangman_status = {
    'active': False,
    'word': '',
    'word_set': set(),
    'guessed_letters': set(),
    'guesses_remaining': TOTAL_HANGMAN_GUESSES,
}

def bot_hangman_word_display(channel):
    '''
    Displays the current hangman game status
    '''
    global hangman_status
    correct_word = hangman_status['word']
    show_word = ' '.join([c if c in hangman_status['guessed_letters'] else '_' for c in correct_word])
    # Format message
    bot_msg = f"{show_word} - You have {hangman_status['guesses_remaining']} guesses remaining!"
    bot_send_message(channel, bot_msg, temporary=False)

def bot_hangman_start(channel_id):
    '''
    Starts a new hangman game
    '''
    channel = channel_with_id(channel_id)
    global hangman_status
    if hangman_status['active']:
        # Already active
        bot_msg = 'Hangman game already in progress!'
        bot_send_message(channel, bot_msg, temporary=False)
        bot_hangman_word_display(channel)
        return
    word = random.choice(list(english_words_set)).upper()
    hangman_status = {
        'active': True,
        'word': word,
        'word_set': set(word),
        'guessed_letters': set(),
        'guesses_remaining': TOTAL_HANGMAN_GUESSES,
    }
    bot_hangman_word_display(channel)

def bot_hangman_reset():
    '''
    Resets a hangman game
    '''
    global hangman_status
    hangman_status = {
        'active': False,
        'word': '',
        'word_set': set(),
        'guessed_letters': set(),
        'guesses_remaining': TOTAL_HANGMAN_GUESSES,
    }

def bot_hangman_guess(token, channel_id, message):
    '''
    Registers a guess for an active hangman game
    '''
    channel = channel_with_id(channel_id)
    try:
        global hangman_status
        if not hangman_status['active']:
            raise InputError('No active hangman games.. please type /hangman start to start one!')
        # Extract character or word
        game_win = False
        if len(message) < 8:
            raise InputError("Invalid guess format. Please ensure it's /guess C")
        elif len(message) == 8:
            # Character guessed
            character = message[7].upper()
            hangman_status['guessed_letters'].add(character)
            hangman_status['guesses_remaining'] -= 1
            # Win condition (all letters in word have been guessed, as a subset)
            if hangman_status['word_set'].issubset(hangman_status['guessed_letters']):
                game_win = True
        else:
            # Word guessed
            hangman_status['guesses_remaining'] -= 1
            # Check win condition
            if hangman_status['word'] == message[7:].upper():
                game_win = True

        # Process end condition
        if game_win:
            # Win condition (word guessed)
            user = user_with_token(token)
            bot_msg = f"Congratulations {user.get_handle()} on guessing the word {hangman_status['word']}!"
            bot_send_message(channel, bot_msg, temporary=False)
            bot_hangman_reset()
        elif hangman_status['guesses_remaining'] == 0:
            # Loss condition
            bot_msg = f"Unlucky, the word was {hangman_status['word']}!"
            bot_send_message(channel, bot_msg, temporary=False)
            bot_hangman_reset()
        else:
            # Continue condition
            bot_hangman_word_display(channel)

    except Exception as e:
        bot_msg = f'Failed to register guess: {e}'
        bot_send_message(channel, bot_msg, temporary=False)


###################
## Fun Utilities ##
###################
def bot_choose(channel_id, message):
    '''
    Bot randomly chooses one of the options listed in the /choose command
    '''
    options = message.split(' ')[1:]
    bot_msg = f'Hmm.. tough choice.. but I choose {random.choice(options)}'
    bot_send_message(channel_with_id(channel_id), bot_msg, temporary=False)

def bot_flip(channel_id):
    '''
    Bot flips a coin and returns heads or tails
    '''
    bot_msg = f"It appears to be {random.choice(['heads', 'tails'])}!"
    bot_send_message(channel_with_id(channel_id), bot_msg, temporary=False)

def bot_dice(channel_id, message):
    '''
    Bot rolls a dice (6 if no number of sides specified), returning a random side
    '''
    sides = 6
    # Not default
    try:
        if len(message) > 5:
            sides = int(message[6:])
        choice = 1 + random.choice(range(sides))
        bot_msg = f'Rolling a {sides}-sided dice.. and got {choice}'
        bot_send_message(channel_with_id(channel_id), bot_msg, temporary=False)
    except Exception:
        bot_msg = 'Please provide a valid number for /dice X, or just /dice for a six-sided dice!'
        bot_send_message(channel_with_id(channel_id), bot_msg, temporary=False)
