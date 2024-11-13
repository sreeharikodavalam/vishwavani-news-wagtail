from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


class Command(BaseCommand):
    help = 'Test R2 storage configuration with detailed checks'

    def test_storage(self):
        """Test storage operations"""
        self.stdout.write("\nTesting storage operations...")
        try:
            # Upload test
            content = ContentFile(b'test content')
            path = default_storage.save('test_r2.txt', content)
            url = default_storage.url(path)
            self.stdout.write(self.style.SUCCESS(f"✓ File uploaded: {path}"))
            self.stdout.write(self.style.SUCCESS(f"✓ Public URL: {url}"))

            # Read test
            retrieved_content = default_storage.open(path).read()
            if retrieved_content == b'test content':
                self.stdout.write(self.style.SUCCESS("✓ Content verification successful"))

            # Delete test
            default_storage.delete(path)
            self.stdout.write(self.style.SUCCESS("✓ File deleted successfully"))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Storage test failed: {str(e)}"))
            return False

    def test_file_overwrite(self):
        """Test file overwrite protection"""
        self.stdout.write("\nTesting file overwrite protection...")
        try:
            # Upload first file
            path = default_storage.save('test_overwrite.txt', ContentFile(b'content1'))
            self.stdout.write(self.style.SUCCESS(f"✓ First file uploaded: {path}"))

            # Try to upload second file with same name
            path2 = default_storage.save('test_overwrite.txt', ContentFile(b'content2'))

            if path != path2:
                self.stdout.write(self.style.SUCCESS("✓ Overwrite protection working"))

            # Cleanup
            default_storage.delete(path)
            default_storage.delete(path2)
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Overwrite test failed: {str(e)}"))
            return False

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\nR2 Storage Configuration Test"))
        self.stdout.write("=" * 50)

        # Print configuration
        options = settings.STORAGES['default']['OPTIONS']
        self.stdout.write("\nStorage Configuration:")
        self.stdout.write(f"Storage Backend: {default_storage.__class__.__name__}")
        self.stdout.write(f"Bucket: {options['bucket_name']}")
        self.stdout.write(f"Endpoint: {options['endpoint_url']}")
        self.stdout.write("=" * 50)

        # Run tests
        tests = {
            "Storage Operations Test": self.test_storage,
            "File Overwrite Test": self.test_file_overwrite
        }

        success_count = 0
        for test_name, test_func in tests.items():
            self.stdout.write(f"\nRunning {test_name}...")
            try:
                if test_func():
                    success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Test failed with unexpected error: {str(e)}"))

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nTest Summary: {success_count}/{len(tests)} tests passed"
        ))