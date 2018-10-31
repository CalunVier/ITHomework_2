# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-31 11:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=50)),
                ('Visibility', models.IntegerField(choices=[(0, 'Public'), (1, 'Protected'), (2, 'Private')])),
                ('prossessor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.User')),
            ],
        ),
        migrations.CreateModel(
            name='ArticlesList',
            fields=[
                ('aid', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('article_name', models.CharField(max_length=60)),
                ('article_address', models.CharField(max_length=200)),
                ('issuing_time', models.TimeField(auto_now=True)),
                ('last_modified', models.TimeField(auto_now_add=True)),
                ('permissions', models.CharField(default='', max_length=1000, verbose_name='Permissions')),
                ('Visibility', models.IntegerField(choices=[(0, 'Public'), (1, 'Protected'), (2, 'Private')])),
                ('auther', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.User')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.ArticleGroups')),
            ],
        ),
        migrations.CreateModel(
            name='CommentList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(auto_now=True)),
                ('auther', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.User')),
                ('superior', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.CommentList')),
            ],
        ),
    ]
