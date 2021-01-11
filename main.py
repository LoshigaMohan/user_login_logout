import webapp2
import logging
import renderhtml
import helper

from uploader import Uploader
from downloader import Downloader
from google.appengine.ext import blobstore
from errorhandler import Errorhandler

class MainPage(webapp2.RequestHandler):
    
    helper.put_error('')
    def get(self):
        logging.debug('GET')
        self.response.headers['Content-Type'] = 'text/html'
        # check whether user is logged in
        if helper.is_user_logged_in():

            # if myuser object is None --> No user with key found --> new user --> make new user in datastore
            if not helper.user_exists():
                helper.add_new_user(helper.get_user())

            self.navigate()
            # get all directoriesin the current path
            directories_in_current_path = helper.get_directories_in_current_path()
            files_in_current_path = helper.get_files_in_current_path()
            # extract directory names from the key list for showing only the names to display
            directories_in_current_path = helper.get_names_from_list(directories_in_current_path)
            files_in_current_path = helper.get_names_from_list(files_in_current_path)

            duplicate_files_in_current_path = helper.get_duplicate_names_from_list(files_in_current_path)

            error_message = helper.get_error().error
            renderhtml.render_main(self,
                                    helper.get_logout_url(self),
                                    directories_in_current_path,
                                    files_in_current_path,
                                    helper.get_current_directory_object().path,
                                    helper.is_in_root_directory(),
                                    blobstore.create_upload_url('/upload'),
                                    error_message,
                                    duplicate_files_in_current_path)

        # no login
        else:
            renderhtml.render_login(self, helper.get_login_url(self))

    # POST-request
    def post(self):
        logging.debug('POST')
        self.response.headers['Content-Type'] = 'text/html'

        button_value = self.request.get('button')

        if button_value == 'Add':
            self.add()
            self.redirect('/')

        elif button_value == 'Delete':
            self.delete()
            self.redirect('/')

        elif button_value == 'Up':
            helper.navigate_up()
            self.redirect('/')

        elif button_value == 'Home':
            helper.navigate_home()
            self.redirect('/')

    def add(self):
        directory_name = self.request.get('value')
        directory_name = helper.prepare_directory_name(directory_name)
        if not (directory_name is None or directory_name == ''):
            helper.add_directory(directory_name, helper.get_current_directory_key())

    def delete(self):
        name = self.request.get('name')
        kind = self.request.get('kind')

        if kind == 'file':
            helper.delete_file(name)
        elif kind == 'directory':
            helper.delete_directory(name)

    def navigate(self):
        directory_name = self.request.get('directory_name')

        # Navigate to a directory sent in the url via get request
        if directory_name != '':
            helper.navigate_to_directory(directory_name)
            self.redirect('/')



# starts the web application and specifies the routing table
app = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/upload', Uploader),
        ('/download', Downloader)
    ], debug=True)
