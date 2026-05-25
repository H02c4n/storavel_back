from django.utils.text import slugify


def unique_slug_generator(instance, slug_field='slug', source_field='title'):
    slug = slugify(getattr(instance, source_field))
    klass = instance.__class__

    unique_slug = slug
    num = 1

    while klass.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{num}"
        num += 1

    return unique_slug