from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Settings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("server", models.URLField(default="https://www.cookiesregtech.com")),
                ("domain_id", models.CharField(blank=True, default="", max_length=40)),
                ("secret", models.CharField(blank=True, default="", max_length=64)),
                ("pending_token", models.CharField(blank=True, default="", max_length=64)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("banner_enabled", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "CookiesRegTech settings",
                "verbose_name_plural": "CookiesRegTech settings",
            },
        ),
    ]
