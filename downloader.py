from google.appengine.ext.webapp import blobstore_handlers
import helper


class Downloader(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        filename = self.request.get('file_name')

        file_object = helper.get_file_object(filename)

        self.send_blob(file_object.blob)
