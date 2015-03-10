# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordmodel',
            name='content',
            field=picklefield.fields.PickledObjectField(editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recordmodel',
            name='document',
            field=models.ForeignKey(related_name='records', to='hub.DocumentModel'),
            preserve_default=True,
        ),
    ]
