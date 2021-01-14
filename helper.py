from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from myuser import MyUser
from directory import Directory
from errorhandler import Errorhandler
from file import File
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
    return not directory.files and not directory.directories


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
    else:
        put_error("Directory Not Empty")

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






def get_files_in_current_path():
    return get_current_directory_object().files


def get_file_object(file_name):
    my_user = get_my_user()

    parent_directory_object = get_current_directory_object()
    file_path = get_path(file_name, parent_directory_object)
    file_id = my_user.key.id() + file_path
    file_key = ndb.Key(File, file_id)
    return file_key.get()

def add_file(upload, file_name):
    my_user = get_my_user()
    current_directory_object = get_current_directory_object()
    file_id = my_user.key.id() + get_path(file_name, current_directory_object)
    file_key = ndb.Key(File, file_id)

    
    file_object = File(id=file_id)
    file_object.name = file_name
    file_object.blob = upload.key()
    file_object.put()

    current_directory_object.files.append(file_key)
    current_directory_object.put()



def delete_file(file_name):
    my_user = get_my_user()

    parent_directory_object = get_current_directory_object()
    file_path = get_path(file_name, parent_directory_object)
    file_id = my_user.key.id() + file_path
    file_key = ndb.Key(File, file_id)

    # Delete file key from directory
    parent_directory_object.files.remove(file_key)
    parent_directory_object.put()

    # Delete actual file from blobstore
    blobstore.delete(file_key.get().blob)

    # Delete file object
    file_key.delete()

def put_error(msg):
    my_user = get_my_user()

    error_id = my_user.key.id()+"Error"
    errorhandler = Errorhandler(id=error_id)
    errorhandler.error = msg
    errorhandler.put()


def get_error():
    my_user = get_my_user()

    error_id = my_user.key.id()+"Error"
    error_key = ndb.Key(Errorhandler, error_id)
    return error_key.get()

def get_duplicate_names_from_list(elements):
    dupes = list()
    duplicates = list()
    
    for i in range(len(elements)): 
        if (elements.count(elements[i]) > 1 ): 
            dupes.append(elements[i]) 
            duplicates = set(dupes)

    return duplicates

def get_duplicate_names_from_dropbox():
    my_user = get_my_user()
    dupes = list()
    paths = list()
    current_path = '/'
    directoryId = my_user.key.id() + current_path
    my_user.current = ndb.Key(Directory, directoryId)
    my_user.put()
    sortedFiles = sorted(get_my_user().current.get().files, key=lambda element: element.
                                 get().name.lower())
    files_in_current_path = [element.get().name for element in sortedFiles]

    
    for i in range(len(files_in_current_path)): 
        if (files_in_current_path.count(files_in_current_path[i]) > 1 ): 
            dupes.append(files_in_current_path[i]) 
            paths.append(current_path)
            


    sortedDir = sorted(get_my_user().current.get().directories,
                               key=lambda element: element.get().name.lower())
    directories_in_current_path = [element.get().name for element in sortedDir]
    
    for directoryName in directories_in_current_path: 
        current_path =  get_path(directoryName, get_my_user().current.get())
        directoryId = my_user.key.id() + current_path
        my_user.current = ndb.Key(Directory, directoryId)
        my_user.put()
        sortedFiles = sorted(get_my_user().current.get().files, key=lambda element: element.
                                 get().name.lower())
        files_in_current_path = [element.get().name for element in sortedFiles]

        
        for i in range(len(files_in_current_path)): 
            if (files_in_current_path.count(files_in_current_path[i]) > 1 ): 
                dupes.append(files_in_current_path[i]) 
                paths.append(current_path)

    return (dupes,paths)
    
    