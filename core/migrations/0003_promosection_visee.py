"""Startowa tresc sekcji "Nowość" – pióra wycieraczek VISEE (wczesniej wpisana na sztywno w szablonie)."""
from django.db import migrations


def create_visee(apps, schema_editor):
    PromoSection = apps.get_model('core', 'PromoSection')
    if PromoSection.objects.exists():
        return
    PromoSection.objects.create(
        is_published=True,
        label='Nowość · pióra wycieraczek',
        title='Pióra wycieraczek VISEE',
        text='Mamy w sprzedaży pióra polskiej firmy VISEE. Dobierzemy je do Twojego auta i od razu założymy, także przy okazji wymiany szyby.',
        bullets='Polska produkcja\nPióra dobrane do modelu auta\nZakładamy od razu, na miejscu',
        button_text='Zapytaj o pióra',
        button_link='',
        image_alt='Pióra wycieraczek VISEE',
        placeholder='VISEE',
    )


def remove_visee(apps, schema_editor):
    apps.get_model('core', 'PromoSection').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_promosection'),
    ]

    operations = [
        migrations.RunPython(create_visee, remove_visee),
    ]
