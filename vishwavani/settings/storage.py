# vishwavani/settings/storage.py

from storages.backends.s3boto3 import S3Boto3Storage
from urllib.parse import quote
from django.conf import settings


class R2Storage(S3Boto3Storage):
    """
    Custom storage class for Cloudflare R2
    Inherits from S3Boto3Storage to maintain compatibility with S3-like storage
    """

    def __init__(self, **kwargs):
        # Get options from settings, but allow override through kwargs
        options = settings.STORAGES['default'].get('OPTIONS', {})
        # Update with any passed kwargs
        options.update(kwargs)

        # Initialize the parent class with our options
        super().__init__(**options)

    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        Generate URL for the given file.
        Can be customized to handle custom domains, forced downloads, etc.
        """
        url = super().url(name, parameters=parameters, expire=expire)

        # Example of how to modify URLs based on configuration
        if hasattr(settings, 'S3_CUSTOM_DOMAIN') and settings.S3_CUSTOM_DOMAIN:
            base_url = f'{self.endpoint_url}/{self.bucket_name}'
            return url.replace(base_url, settings.S3_CUSTOM_DOMAIN)

        return url

    def get_download_url(self, name, original_filename=None):
        """
        Generate a URL that will force the browser to download the file
        rather than displaying it
        """
        parameters = {
            'ResponseContentDisposition': (
                f'attachment; filename="{quote(original_filename or name.split("/")[-1])}"'
            )
        }
        return self.url(name, parameters=parameters)

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system.
        Ensures we don't overwrite existing files.
        """
        if self.file_overwrite:
            return name

        return super().get_available_name(name, max_length)


class StaticR2Storage(R2Storage):
    """
    Storage for static files.
    Inherits from R2Storage but changes the location to 'static'
    """

    def __init__(self, **kwargs):
        kwargs['location'] = 'static'
        super().__init__(**kwargs)

