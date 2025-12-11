from django.db import migrations, models


def copy_category_to_categories(apps, schema_editor):
    Book = apps.get_model('users', 'Book')
    for book in Book.objects.exclude(category__isnull=True):
        if book.category_id:
            book.categories.add(book.category_id)


def reverse_noop(apps, schema_editor):
    # No reverse migration; removing category field
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_book_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='books', to='users.category'),
        ),
        migrations.RunPython(copy_category_to_categories, reverse_noop),
        migrations.RemoveField(
            model_name='book',
            name='category',
        ),
    ]
