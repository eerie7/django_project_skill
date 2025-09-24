from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group, User
from News_portal.models import Author


@receiver(m2m_changed, sender=Group.user_set.through)
def user_groups_changed(sender, instance, action, pk_set, **kwargs):
    """
    Автоматически создает/удаляет профиль Author при изменении групп пользователя
    """
    if action in ['post_add', 'post_remove']:
        authors_group = Group.objects.filter(name='authors').first()

        if authors_group and authors_group.id in pk_set:
            if action == 'post_add':
                # Создаем автора с именем пользователя
                Author.objects.get_or_create(
                    user=instance,
                    defaults={'author_name': instance.username}
                )
                print(f"Создан автор: {instance.username}")
            elif action == 'post_remove':
                Author.objects.filter(user=instance).delete()
                print(f"Удален автор: {instance.username}")

def get_user_author(self):
    """Возвращает автора, связанного с пользователем, если существует"""
    try:
        return self.author
    except Author.DoesNotExist:
        return None

# Добавляем метод к модели User
User.add_to_class('get_author', get_user_author)