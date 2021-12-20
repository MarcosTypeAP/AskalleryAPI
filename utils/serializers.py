"""Serializer utilities."""

# Django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Utils
import jwt
from datetime import timedelta
from io import BytesIO
from PIL import Image
import os


def is_asuka_picture(image=None, user=None, image_url=None):
    """Validates that the image is a asuka picture."""

    google_search_url = 'https://www.google.com/searchbyimage'
    extra_query_params = '&encoded_image=&image_content=&filename=&hl=en-AR'
    import pdb; pdb.set_trace()

    if image_url is not None:
        search_by_image_url = '{}?image_url={}{}'.format(
            google_search_url, image_url, extra_query_params
        )
    else:
        filename = 'tmp-img-{}-{}'.format(user.pk, image.name)

        with open(f'/app/tmp_images/{filename}', 'wb+') as tmp_img:
            for chunck in image.chunks():
                tmp_img.write(chunck)

        tmp_images_url = 'api/tmpimage/'
        search_by_image_url = '{}?image_url=https://{}{}{}{}'.format(
            google_search_url, settings.APP_URL, tmp_images_url,
            filename, extra_query_params
        )

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("-disable-gpu")
    options.add_argument("-no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    service = Service(os.environ.get("CHROMEDRIVER_PATH"))

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    driver.get(search_by_image_url)
    result = driver.find_element('name', 'q').get_attribute('value').upper()

    wrong_words = ('WWE', 'LUCHADORA', 'WRESTLER')
    if 'ASUKA' not in result or any([x in result for x in wrong_words]):
        return False
    return True


def gen_verification_token(user):
    """Create a JWT token that the user
    can use to verify its account.
    """
    exp_date = timezone.now() + timedelta(days=2)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def send_confirmation_email(user):
    """Send account verification link to given user."""
    verification_token = gen_verification_token(user)
    subject = 'Welcome @{}! Verify your account to start using Askallery'.format(
        user.username
    )
    from_email = 'Askallery <noreply@askallery.com>'
    content = render_to_string(
        'emails/account_verification.html', {
            'token': verification_token,
            'app_url': settings.APP_URL,
            'http_protocol': settings.HTTP_PROTOCOL,
            'user': user,
        }
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


def compress_image(image):
    """Compress the given image."""
    img = Image.open(image)
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    return InMemoryUploadedFile(
        file=img_io,
        field_name=image.field_name,
        name=image.name,
        content_type=image.content_type,
        size=image.size,
        charset=image.charset,
        content_type_extra=image.content_type_extra,
    )
