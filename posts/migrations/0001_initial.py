# Generated by Django 3.2.6 on 2021-11-09 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Stores the datetime when the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Stores the datetime when the object was last modified', verbose_name='modified at')),
                ('caption', models.TextField(help_text='It can be short description of the picture and extra info.', max_length=400, verbose_name='caption')),
                ('image', models.ImageField(help_text='Its the main content of the post.', upload_to='posts/pictures/', verbose_name='picture')),
                ('likes_quantity', models.IntegerField(default=0, help_text=('Quantity of likes of this post.Stores the value to perform less queries.Increase 1 when another user give a like to this post.',), verbose_name='quantity of likes')),
                ('comments_quantity', models.IntegerField(default=0, help_text=('Quantity of comments of this post.Stores the value to perform less queries.Increase 1 when another user leaves a comment on this post.',), verbose_name='quantity of comments')),
                ('is_active', models.BooleanField(default=True, help_text='It will be False when the post is removed.', verbose_name='active')),
                ('likes', models.ManyToManyField(related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created', '-modified'),
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Stores the datetime when the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Stores the datetime when the object was last modified', verbose_name='modified at')),
                ('content', models.TextField(help_text='It is text given by a user.', max_length=500, verbose_name='content')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.post')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created', '-modified'),
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]