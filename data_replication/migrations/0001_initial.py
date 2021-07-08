# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Replication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('state', models.IntegerField(choices=[(-1, 'Locked'), (0, 'Not Replicated'), (1, 'In Storage'), (2, 'Removed')])),
                ('last_updated', models.DateTimeField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'permissions': (('view_replication', 'View Replication'),),
            },
        ),
        migrations.CreateModel(
            name='ReplicationTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('replication_type', models.IntegerField(choices=[(1, 'Mongo'), (2, 'Splunk')])),
                ('state', models.SmallIntegerField(choices=[(1, 'Ready'), (2, 'In-Process')])),
                ('last_updated', models.DateTimeField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='replication',
            name='tracker',
            field=models.ForeignKey(to='data_replication.ReplicationTracker', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='replication',
            unique_together=set([('content_type', 'object_id', 'tracker')]),
        ),
    ]
