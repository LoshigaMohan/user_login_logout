import jinja2
import os
import helper

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def render_login(self, url):
    template_values = {
        'url': url
    }

    template = JINJA_ENVIRONMENT.get_template('/login.html')
    self.response.write(template.render(template_values))


<<<<<<< HEAD
def render_main(self, url, directories, files, current_path, is_in_root, upload_url,error,duplicates):
=======
def render_main(self, url, directories, files, current_path, is_in_root, upload_url,error):
>>>>>>> 5c6f47db68a3793896e47a6b5e96ab938ebc09a0
    template_values = {
        'url': url,
        'user': helper.get_user(),
        'directories': directories,
        'files': files,
        'current_path': current_path,
        'is_not_in_root': not is_in_root,
        'upload_url': upload_url,
<<<<<<< HEAD
        'error' : error,
        'duplicates' : duplicates
=======
        'error' : error
>>>>>>> 5c6f47db68a3793896e47a6b5e96ab938ebc09a0
    }

    template = JINJA_ENVIRONMENT.get_template('/main.html')
    self.response.write(template.render(template_values))
