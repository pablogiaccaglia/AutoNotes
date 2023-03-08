import cloudinary
from cloudinary.uploader import upload

class Cloudinary:

    def __init__(self,
                 cloud_name,
                 api_key,
                 api_secret,
                 secure = True):
        self.cdnry = cloudinary

        self.cdnry.config(
                cloud_name = cloud_name,
                api_key = api_key,
                api_secret = api_secret,
                secure = secure
        )

    def upload_file(self, file_name, folder_name, public_id, get_url = True):
        response = self.cdnry.uploader.upload(file = file_name, folder = folder_name, public_id = public_id)

        if get_url:
            return response['url']

    def get_url(self, folder_name, file_id, **kwargs):
        url, options = self.cdnry.utils.cloudinary_url(source = folder_name + "/" + file_id, **kwargs)
        return url
