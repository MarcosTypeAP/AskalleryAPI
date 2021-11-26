"""Test utilities."""

# Models
from users.models import User, Profile

# Utils
from PIL import Image
import tempfile


def create_users(**data):
    """Creates 3 users for testing.

    Returns 3 'User' tuple and a dict with the users's password.

    Parameters passed will overwrite default_data.

    Parameter models: N = 1/2/3
        - uN_username
        - uN_email
        - uN_first_name
        - uN_last_name
        - uN_password
    """

    default_data = {
        'u1_username': 'user1username',
        'u1_email': 'user1email@test.com',
        'u1_first_name': 'user1firstname',
        'u1_last_name': 'user1lastname',
        'u1_password': 'user1password',

        'u2_username': 'user2username',
        'u2_email': 'user2email@test.com',
        'u2_first_name': 'user2firstname',
        'u2_last_name': 'user2lastname',
        'u2_password': 'user2password',

        'u3_username': 'user3username',
        'u3_email': 'user3email@test.com',
        'u3_first_name': 'user3firstname',
        'u3_last_name': 'user3lastname',
        'u3_password': 'user3password',
    }

    for new_data_key, new_data_value in data.items():
        if new_data_key in default_data:
            default_data[new_data_key] = new_data_value

    user_1_data = {
        k[3:]: v
        for k, v in default_data.items()
        if k.startswith('u1') and 'password' != k[3:]
    }
    user_2_data = {
        k[3:]: v
        for k, v in default_data.items()
        if k.startswith('u2') and 'password' != k[3:]
    }
    user_3_data = {
        k[3:]: v
        for k, v in default_data.items()
        if k.startswith('u3') and 'password' != k[3:]
    }

    user_1 = User.objects.create_user(**user_1_data)
    user_1.set_password(default_data['u1_password'])
    Profile.objects.create(user=user_1)
    user_1.save()

    user_2 = User.objects.create_user(**user_2_data)
    user_2.set_password(default_data['u2_password'])
    Profile.objects.create(user=user_2)
    user_2.save()

    user_3 = User.objects.create_user(**user_3_data)
    user_3.set_password(default_data['u3_password'])
    Profile.objects.create(user=user_3)
    user_3.save()

    return (user_1, user_2, user_3), {
        k: v
        for k, v in default_data.items() if k.endswith('password')
    }


def create_image():
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        image = Image.new('RGB', (200, 200), 'white')
        image.save(f, 'PNG')

    return open(f.name, mode='rb')


def create_data_list(k):
    """Returns a list of data, which can be used
    for post creation.

    data: (dict) -> {
        caption: (str) -> Caption for the post
        image: (tmp image) -> Image for the post
    }
    """
    data_list = [
        {
            'caption': 'Caption for testing {}.'.format(n),
            'image': create_image(),
        } for n in range(1, k + 1)
    ]
    return data_list
