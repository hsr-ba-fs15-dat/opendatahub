# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'hub_documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('document', models.ForeignKey(to='hub.DocumentModel')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'hub_records',
            },
            bases=(models.Model,),
        ),
    ]
