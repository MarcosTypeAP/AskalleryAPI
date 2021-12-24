"""Serializer utilities."""

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.files.uploadedfile import (
    InMemoryUploadedFile, TemporaryUploadedFile
)
from django.core.files import temp as tempfile

# Utils
import jwt
import time
import os
import requests
from datetime import timedelta
from io import BytesIO
from PIL import Image
from datetime import datetime
from bs4 import BeautifulSoup


def is_asuka_picture(image=None, image_url=None):
    """Validates that the image is a asuka picture."""

    google_search_url = 'https://www.google.com/searchbyimage'
    extra_query_params = '&encoded_image=&image_content=&filename=&hl=en'

    if image_url:
        search_by_image_url = '{}?image_url={}{}'.format(
            google_search_url, image_url, extra_query_params
        )
    else:
        filename = image.name
        with open(f'{str(settings.MEDIA_ROOT)}/{filename}', 'wb+') as tmp_img:
            for chunck in image.chunks():
                tmp_img.write(chunck)

        import os
        os.system('ls -la /app/media')

        search_by_image_url = '{}?image_url=https://{}{}{}{}'.format(
            google_search_url, settings.APP_URL, settings.MEDIA_URL, filename,
            extra_query_params
        )

    headers = {
        'User-Agent':
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept':
            'text/html',
    }

    for x in range(3):
        response = requests.get(search_by_image_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        target = soup.find('input', {'aria-label': 'Search', 'name': 'q'})
        result = target.get('value').upper()
        if result:
            break
        time.sleep(5)

    print(result)
    WRONG_WORDS = ('WWE', 'LUCHADORA', 'WRESTLER', 'AYANAMI', 'REI')
    MANDATORY_WORDS = ('ASUKA', 'アスカ')

    check_1 = any([x in result for x in MANDATORY_WORDS])
    check_2 = any([x in result for x in WRONG_WORDS])

    if not check_1 or check_2:
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


class CustomTemporaryUploadedFile(TemporaryUploadedFile):
    """Overrides __init__ to make `delete` false."""
    def __init__(
        self, name, content_type, size, charset, content_type_extra=None
    ):
        _, ext = os.path.splitext(name)
        file = tempfile.NamedTemporaryFile(
            suffix='.upload' + ext,
            dir=settings.FILE_UPLOAD_TEMP_DIR,
            delete=False
        )
        super(TemporaryUploadedFile, self).__init__(
            file, name, content_type, size, charset, content_type_extra
        )


def size_reduction(image, quality=70, height=720, width=1280):
    """Compress and resize the given image."""
    img = Image.open(image)
    img = img.convert('RGB')
    img.thumbnail(
        (height, width) if img.width < img.height else (width, height)
    )
    filename = '{}.jpeg'.format(int(datetime.now().timestamp()))

    if isinstance(image, InMemoryUploadedFile):
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=quality)
        new_image = InMemoryUploadedFile(
            file=img_io,
            field_name=image.field_name,
            name=filename,
            content_type='image/jpeg',
            size=img_io.tell(),
            charset=None,
        )
        new_image.seek(0)
        image.seek(0)
        return new_image

    elif isinstance(image, TemporaryUploadedFile):
        new_image = CustomTemporaryUploadedFile(
            name=filename, content_type='image/jpeg', size=0, charset=None
        )
        img.save(new_image, 'JPEG', quality=quality)
        new_image.seek(0)
        new_image.size = len(new_image.read())
        new_image.seek(0)
        image.seek(0)
        return new_image
