# Generated by Django 2.2.19 on 2022-10-14 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='post',
        ),
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Comment'),
        ),
    ]
