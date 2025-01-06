
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User

class Command(BaseCommand):
    help = 'Delete users whose deletion date has passed'

    def handle(self, *args, **kwargs):
        print("Running delete_expired_users command")
        now = timezone.now()
        users_to_delete = User.objects.filter(deletion_date__lte=now)
        count = users_to_delete.count()
        users_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} users'))