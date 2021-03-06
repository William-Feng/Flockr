'''
Tests written to test user.py
'''
import os
import pytest
import urllib.request
from PIL import Image
from user import (
    user_profile, user_profile_setname, user_profile_uploadphoto,
    user_profile_setemail, user_profile_sethandle,
)
from other import clear
from auth import auth_register
from error import InputError, AccessError

# user_profile tests
def test_valid_user():
    '''
    Create a valid user
    Return the user detail associated with
    given token and u_id
    '''
    clear()
    # standard user
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    user_profile_sethandle(user['token'], 'Stevenson')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Steven"
    assert profile['user']['name_last'] == "Nguyen"
    assert profile['user']['u_id'] == user['u_id']
    assert profile['user']['email'] == 'stvnnguyen69@hotmail.com'
    assert profile['user']['handle_str'] == 'Stevenson'

    # another regular user
    user2 = auth_register(
        'madeulook100@gmail.com', 'madeulook',
        'Verylongfirstname', 'Verylonglastname'
    )
    user_profile_sethandle(user2['token'], 'LongHandleName')
    profile = user_profile(user2['token'], user2['u_id'])
    assert profile['user']['name_first'] == "Verylongfirstname"
    assert profile['user']['name_last'] == "Verylonglastname"
    assert profile['user']['u_id'] == user2['u_id']
    assert profile['user']['email'] == 'madeulook100@gmail.com'
    assert profile['user']['handle_str'] == 'LongHandleName'

def test_invalid_user():
    '''
    Raise exception when providing token and u_id that has not been created yet.
    Create valid users but call user detail with incorrrect u_id and token
    '''
    clear()
    user = auth_register('shortemail@gmail.com', '1234567', 'Michael', 'Jackson')
    # invalid token
    with pytest.raises(AccessError):
        user_profile('', user['u_id'])

    # retrieving information with correct token but wrong id
    user2 = auth_register('ilovescience10@hotmail.com', '7654321', 'Bill', 'Nye')
    user3 = auth_register('roariscool64@gmail.com', 'password123', 'Taylor', 'Series')
    with pytest.raises(InputError):
        user_profile(user['token'], 5)
    with pytest.raises(InputError):
        user_profile(user2['token'], 7)
    with pytest.raises(InputError):
        user_profile(user3['token'], 7)

    # retrieving information with wrong token but correct id
    with pytest.raises(AccessError):
        user_profile('@#*&$^', user['u_id'])
    with pytest.raises(AccessError):
        user_profile(')(!*#$', user2['u_id'])
    with pytest.raises(AccessError):
        user_profile('*%&^', user3['u_id'])

# user_profile_setname tests
def test_valid_setnames():
    '''
    Change name of the user with valid name and check that the id stays the same
    Use edge case to change into new name such as 1 character or exactly 50 characters
    '''
    clear()
    # original user
    user = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Apple"
    assert profile['user']['name_last'] == "Appleson"
    assert profile['user']['u_id'] == user['u_id']

    # same token, id but different username
    user_profile_setname(user['token'], 'Banana', 'Bananason')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Banana"
    assert profile['user']['name_last'] == "Bananason"
    assert profile['user']['u_id'] == user['u_id']

    # change name multiple times under the same token
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')
    profile = user_profile(user2['token'], user2['u_id'])
    assert profile['user']['name_first'] == "Orange"
    assert profile['user']['name_last'] == "Orangeson"
    assert profile['user']['u_id'] == user2['u_id']
    user_profile_setname(user2['token'], 'Strawberry', 'Strawberryson')
    profile = user_profile(user2['token'], user2['u_id'])
    assert profile['user']['name_first'] == "Strawberry"
    assert profile['user']['name_last'] == "Strawberryson"
    assert profile['user']['u_id'] == user2['u_id']
    user_profile_setname(user2['token'], 'Michael', 'Michaelson')
    profile = user_profile(user2['token'], user2['u_id'])
    assert profile['user']['name_first'] == "Michael"
    assert profile['user']['name_last'] == "Michaelson"
    assert profile['user']['u_id'] == user2['u_id']

    # changing name with 1 character
    user3 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    profile = user_profile(user3['token'], user3['u_id'])
    assert profile['user']['name_first'] == "John"
    assert profile['user']['name_last'] == "Johnson"
    user_profile_setname(user3['token'], "A", "B")
    profile = user_profile(user3['token'], user3['u_id'])
    assert profile['user']['name_first'] == "A"
    assert profile['user']['name_last'] == "B"

    # changing name with exactly 50 characters
    long_first = 'x' * 50
    long_last = 'y' * 50
    user4 = auth_register('austinnistau@hotmai.com', 'password', 'Austin', 'Austinson')
    profile = user_profile(user4['token'], user4['u_id'])
    assert profile['user']['name_first'] == "Austin"
    assert profile['user']['name_last'] == "Austinson"
    user_profile_setname(user4['token'], long_first, long_last)
    profile = user_profile(user4['token'], user4['u_id'])
    assert profile['user']['name_first'] == long_first
    assert profile['user']['name_last'] == long_last

def test_invalid_setnames():
    '''
    Raise exception when changing the name of user using invalid format
    such as names with more than 50 characers long, empty name and empty spaces
    '''
    clear()
    # changing name to more than 50 characters long
    long_first = 'a' * 51
    long_last = 'b' * 51
    user = auth_register('hardcoregamer02@hotmail.com', 'password', 'Raymond', 'Raymondson')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Raymond"
    assert profile['user']['name_last'] == "Raymondson"
    with pytest.raises(InputError):
        user_profile_setname(user['token'], long_first, long_last)

    # invalid token
    with pytest.raises(AccessError):
        user_profile_setname(user['token'] + 'paddddding', 'A', 'B')

    # changing name with empty space
    user2 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    profile = user_profile(user2['token'], user2['u_id'])
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '', '')
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '  ', '  ')

    # valid first, invalid last
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], 'Valid', '')
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], 'Valid', ' ')
    # invalid first, valid last
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '', 'Valid')
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], ' ', 'Valid')

# user_profile_setemail tests
def test_valid_email():
    '''
    Registers a user and sets their email to a valid email.
    '''
    clear()
    user = auth_register('hellothere44@gmail.com', 'ifajfiod1ad133', 'Matthew', 'Matthewson')
    profile = user_profile(user['token'], user['u_id'])

    # Check if email is still the same
    assert profile['user']['email'] == 'hellothere44@gmail.com'

    # Change user's email
    user_profile_setemail(user['token'], 'goodbye21@gmail.com')
    profile = user_profile(user['token'], user['u_id'])

    # Check if email has changed
    assert profile['user']['email'] == 'goodbye21@gmail.com'

def test_invalid_email():
    '''
    Registers valid users and attempts to change their email to strings
    that aren't emails.
    '''
    clear()
    user = auth_register('ilovescience10@hotmail.com', '7654321', 'Bill', 'Nye')
    # Invalid token
    with pytest.raises(AccessError):
        user_profile_setemail('', 'legit@gmail.com')

    # Alphanumeric string, no @ or domain
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'dkid12eid')

    # Alphanumeric string with @
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'ew9ijifewji90ejwiffjiifji1j2j@')

    # No string with @ and domain
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '@.com')

    # No string or @ with domain
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'gmail.cn')

    # No string with @
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '@')

def test_empty_email():
    '''
    Registers valid users and attempts to change their email to an empty email
    or one with whitespace only.
    '''
    clear()
    # Setting empty email
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '')

    # Setting email full of whitespaces
    user = auth_register('shortemail@gmail.com', '1234567', 'Michael', 'Jackson')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '          ')

def test_taken_email():
    '''
    Registers two valid users and tries to set both their emails to each other's
    emails.
    '''
    clear()
    user1 = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')

    # user1 tries to set email to user2's email
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'samsunggalaxy01@gmail.com')

    # user2 tries to set email to user1's email
    with pytest.raises(InputError):
        user_profile_setemail(user2['token'], 'blastfire97@gmail.com')

def test_same_email():
    '''
    Registers two users and tries to set their emails to their current emails.
    '''
    clear()
    user1 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'mmmonkey97@hotmail.com')

    user2 = auth_register('monkeymaster22@gmail.com', 'ilovebanaNas', 'Banana', 'Bananason')
    with pytest.raises(InputError):
        user_profile_setemail(user2['token'], 'monkeymaster22@gmail.com')

# user_profile_sethandle tests
def test_valid_handle():
    '''
    User registers and changes handle to normal handle
    '''
    clear()
    user = auth_register('therealbrucelee@gmail.com', 'gghgdshh', 'Bruce', 'Lee')
    profile = user_profile(user['token'], user['u_id'])
    # Invalid token
    with pytest.raises(AccessError):
        user_profile_sethandle('hi', 'Real Bruce Lee')

    user_profile_sethandle(user['token'], 'Real Bruce Lee')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['handle_str'] == 'Real Bruce Lee'

    user_profile_sethandle(user['token'], 'Actual Bruce Lee')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['handle_str'] == 'Actual Bruce Lee'

def test_handle_length():
    '''
    User registers and tries to change handle to 2 character and 27 character
    handles.
    '''
    clear()
    user = auth_register('peterpeterson222@hotmail.com', 'uaefhuasfnf', 'Peter', 'Peterson')
    profile = user_profile(user['token'], user['u_id'])

    # User tries to change to short handle
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'h')
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'hi')

    # Whitespace handle
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], '   ')

    # User tries to change to long handle
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'thisistwentyonechars!')

    # Make sure handle is still the same (default handle)
    user_profile_sethandle(user['token'], 'dog')
    profile = user_profile(user['token'], user['u_id'])
    assert len(profile['user']['handle_str']) == 3

def test_taken_handle():
    '''
    Two users register and try to change to the same valid handle.
    '''
    clear()
    user1 = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')

    # user1 changes handle to hello world
    user_profile_sethandle(user1['token'], 'hello world')
    user_profile(user1['token'], user1['u_id'])

    # user2 tries to also change to hello world
    with pytest.raises(InputError):
        user_profile_sethandle(user2['token'], 'hello world')

    # user1 changes handle again
    user_profile_sethandle(user2['token'], 'goodbye world')
    user_profile(user2['token'], user2['u_id'])

    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], 'goodbye world')

def test_user_profile_uploadphoto_invalid():
    '''
    Invalid test cases for user_profile_uploadphoto
    Correct crop size is tested in the HTTP test
    '''
    user = auth_register('admin@gmail.com', 'password', 'Admin', 'User')
    # Invalid img_url
    with pytest.raises(InputError):
        url = 'https://asldfkjh.asdfkj'
        user_profile_uploadphoto(user['token'], '', url, 0, 0, 1, 1)
    with pytest.raises(InputError):
        url = 'https://google.com'
        user_profile_uploadphoto(user['token'], '', url, 0, 0, 1, 1)
    # Invalid dimensions for a valid jpg
    img_url = 'https://wallpapercave.com/wp/OWmhWu0.jpg'
    urllib.request.urlretrieve(img_url, 'test.jpg')
    img = Image.open('test.jpg')
    width, height = img.size
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, 'a', 'a', 'a', 'a')
    
    # Invalid token
    with pytest.raises(AccessError):
        user_profile_uploadphoto(user['token'] + 'padding', '', img_url, 0, 0, 1, 1)
    # x coordinates not between 0 and width inclusive
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, -1, 0, width, height)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, 0, 0, width+1, height)

    # y coordinates not between 0 and height inclusive
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, 0, -1, width, height)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, 0, 0, width, height+1)

    # 0 pixels high / wide
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, 0, 0, 0, height)
    with pytest.raises(InputError):
        user_profile_uploadphoto(user['token'], '', img_url, 0, 0, width, 0)

    # Valid crop dimensions
    user_profile_uploadphoto(user['token'], '', img_url, 0, 0, width, height)

    # Delete test.jpg
    os.remove('test.jpg')
