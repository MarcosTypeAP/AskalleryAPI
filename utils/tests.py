"""Test utilities."""

# Models
from users.models import User, Profile 


def create_users(**data):
    """Creates 3 users for testing.

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
        'u1_password': 'user1password',

        'u2_username': 'user2username',
        'u2_email': 'user2email@test.com',
        'u2_first_name': 'user2firstname',
        'u2_last_name': 'user2lastname',
        'u2_password': 'user2password',
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

    user_1_data = { k[3:]: v for k, v in default_data.items() if k.startswith('u1') and 'password' != k[3:] }
    user_2_data = { k[3:]: v for k, v in default_data.items() if k.startswith('u2') and 'password' != k[3:] }
    user_3_data = { k[3:]: v for k, v in default_data.items() if k.startswith('u3') and 'password' != k[3:] }

    user_1 = User.objects.create_user(**user_1_data)
    user_1.set_password(default_data['u1_password'])
    Profile.objects.create(user=user_1)
    
    user_2 = User.objects.create_user(**user_2_data)
    user_2.set_password(default_data['u2_password'])
    Profile.objects.create(user=user_2)

    user_3 = User.objects.create_user(**user_3_data)
    user_3.set_password(default_data['u3_password'])
    Profile.objects.create(user=user_3)

    return user_1, user_2, user_3
