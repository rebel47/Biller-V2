from PIL import Image, UnidentifiedImageError
import pillow_heif
import io

# Enable HEIC support
pillow_heif.register_heif_opener()

class ImageProcessor:
    @staticmethod
    def convert_image_format(uploaded_file):
        try:
            image = Image.open(uploaded_file)
            buffer = io.BytesIO()
            image = image.convert("RGB")
            image.save(buffer, format="JPEG")
            buffer.seek(0)
            return buffer, "image/jpeg"
        except UnidentifiedImageError:
            raise ValueError("Unsupported image format. Please upload PNG, JPEG, or HEIC images.")

    @staticmethod
    def setup_input_image(uploaded_file):
        converted_file, mime_type = ImageProcessor.convert_image_format(uploaded_file)
        bytes_data = converted_file.getvalue()
        return bytes_data, mime_type