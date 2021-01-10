from google.appengine.ext import ndb
from google.appengine.api import users
from myuser import MyUser
from directory import Directory
import logging
import re


# Get user from this page
def get_user():
    return users.get_current_user()


# get user from data
def get_my_user():
    user = get_user()
    if user:
        my_user_key = ndb.Key(MyUser, user.user_id())
        return my_user_key.get()


def is_user_logged_in():
    return True if get_user() else False


# returns true if for this user a myuser object already exists in the datastore
def user_exists():
    return True if get_my_user() else False


def add_new_user(user):
    my_user = MyUser(id=user.user_id())
    add_root_directory(my_user)

    # set current path on first login to root directory
    my_user.current_directory = ndb.Key(Directory, my_user.key.id() + '/')
    my_user.put()


def get_directories_in_current_path():
    return get_current_directory_object().directories



def get_path(name, parent_directory_object):
    if is_in_root_directory():
        return parent_directory_object.path + name
    else:
        return parent_directory_object.path + '/' + name


# returns true if current directory is root directory
def is_in_root_directory():
    current_directory = get_current_directory_object()
    return True if current_directory.parent_directory is None else False


def is_directory_empty(directory):
    return not directory.directories


# returns key of current directory
def get_current_directory_key():
    my_user = get_my_user()
    return my_user.current_directory


# returns key of current directory
def get_current_directory_object():
    return get_current_directory_key().get()


# returns key of parent directory
def get_parent_directory_key():
    current_directory = get_current_directory_key()
    return current_directory.get().parent_directory


def add_root_directory(my_user):
    directory_id = my_user.key.id() + '/'
    directory = Directory(id=directory_id)

    directory.parent_directory = None
    directory.name = 'root'
    directory.path = '/'
    directory.put()

    my_user.root_directory = directory.key
    my_user.put()


def add_directory(name, parent_directory_key):
    my_user = get_my_user()

    parent_directory_object = parent_directory_key.get()

    path = get_path(name, parent_directory_object)

    directory_id = my_user.key.id() + path
    directory = Directory(id=directory_id)

    # check if directory already exists in this path
    if exists(directory.key, parent_directory_object.directories):
        # check if parent directory name and directory name are not same
        if parent_directory_object.name != name:
            # Add key to parent directory
            parent_directory_object.directories.append(directory.key)
            parent_directory_object.put()

            # Set all attributes of the directory and save it to datastore
            directory.parent_directory = parent_directory_key
            directory.name = name
            directory.path = path
            directory.put()


def delete_directory(directory_name):
    my_user = get_my_user()

    # current directory is the parent directory of the one that will be deleted
    parent_directory_object = get_current_directory_object()

    directory_id = my_user.key.id() + get_path(directory_name, parent_directory_object)
    directory_key = ndb.Key(Directory, directory_id)
    directory_object = directory_key.get()

    if is_directory_empty(directory_object):

        # Delete reference to this object from parent_directory
        parent_directory_object.directories.remove(directory_key)
        parent_directory_object.put()

        # Delete directory object from datastore
        directory_key.delete()


# checks if a key is in a list of keys, if so returns true
def exists(key, key_list):
    return key not in key_list


# Remove all '/' and ';' from the directory name and leading whitespaces
def prepare_directory_name(directory_name):
    return re.sub(r'[/;]', '', directory_name).lstrip()



# extracts all the names from a list of directory keys
def get_names_from_list(elements):
    names = list()

    for element in elements:
        names.append(element.get().name)

    return names


def get_login_url(main_page):
    return users.create_login_url(main_page.request.uri)


def get_logout_url(main_page):
    return users.create_logout_url(main_page.request.uri)






def navigate_up():
    my_user = get_my_user()

    if not is_in_root_directory():
        parent_directory_key = get_parent_directory_key()
        my_user.current_directory = parent_directory_key
        my_user.put()


def navigate_home():
    my_user = get_my_user()

    my_user.current_directory = ndb.Key(Directory, my_user.key.id() + '/')
    my_user.put()


def navigate_to_directory(directory_name):
    my_user = get_my_user()

    parent_directory_object = get_current_directory_object()
    directory_id = my_user.key.id() + get_path(directory_name, parent_directory_object)
    directory_key = ndb.Key(Directory, directory_id)

    my_user.current_directory = directory_key
    my_user.put()
