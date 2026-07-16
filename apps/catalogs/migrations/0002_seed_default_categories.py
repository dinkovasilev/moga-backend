from django.db import migrations

# Task creation UI is two-level (main category -> subcategory) and only submits
# a subcategory id, so every top-level entry needs at least one child to be usable.
TASK_CATEGORIES = {
    'Дом и бит': ['Почистване', 'Готвене', 'Гледане на деца/животни'],
    'Ремонт и поддръжка': ['Дребни ремонти', 'Електро', 'ВиК'],
    'Градинарство': ['Косене', 'Засаждане', 'Поддръжка'],
    'Транспорт': ['Превоз на хора', 'Превоз на товари'],
    'Образование': ['Уроци', 'Консултации'],
    'Компютри и технологии': ['Инсталация', 'Поддръжка'],
    'Здраве и грижи': ['Придружаване', 'Грижа за възрастни хора'],
    'Друго': ['Разни'],
}

ITEM_CATEGORIES = [
    'Дрехи и обувки',
    'Мебели',
    'Електроника',
    'Книги',
    'Домакински пособия',
    'Друго',
]


def seed_categories(apps, schema_editor):
    TCategory = apps.get_model('catalogs', 'TCategory')
    ICategory = apps.get_model('catalogs', 'ICategory')
    for parent_name, children in TASK_CATEGORIES.items():
        parent, _ = TCategory.objects.get_or_create(name=parent_name, parent=None)
        for child_name in children:
            TCategory.objects.get_or_create(name=child_name, parent=parent)
    for name in ITEM_CATEGORIES:
        ICategory.objects.get_or_create(name=name, parent=None)


def remove_categories(apps, schema_editor):
    TCategory = apps.get_model('catalogs', 'TCategory')
    ICategory = apps.get_model('catalogs', 'ICategory')
    TCategory.objects.filter(name__in=TASK_CATEGORIES.keys(), parent=None).delete()
    ICategory.objects.filter(name__in=ITEM_CATEGORIES, parent=None).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
