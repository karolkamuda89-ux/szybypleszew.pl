"""Startowa tresc sekcji "Nowość" – pióra wycieraczek VISEE (wczesniej wpisana na sztywno w szablonie)."""
from django.db import migrations


def create_visee(apps, schema_editor):
    PromoSection = apps.get_model('core', 'PromoSection')
    if PromoSection.objects.exists():
        return
    PromoSection.objects.create(
        is_published=True,
        label='Nowość · pióra wycieraczek',
        title='Pióra wycieraczek VISEE z montażem od ręki',
        text='Nawiązaliśmy współpracę z VISEE – polskim producentem piór wycieraczek. '
             'Dobierzemy pióra do Twojego auta i od razu je zamontujemy, także przy okazji wymiany szyby.',
        bullets='Polska produkcja\n'
                'Dobór do konkretnego modelu auta\n'
                'Montaż na miejscu – odjeżdżasz z nowymi wycieraczkami',
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
