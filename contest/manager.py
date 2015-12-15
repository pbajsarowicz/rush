from django.contrib.auth.models import BaseUserManager

from django.utils import timezone


class RushUserManager(BaseUserManager):

    def create_user(self, email, first_name,
        last_name, organization_name,
         organization_address, password):
        if not email:
            raise ValueError('Podaj poprawny adres email')

        email=self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name,
            organization_address=organization_address,
            date_joined=timezone.now()
        )
        user.is_active=False

        user.set_password('password')
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,
            password, '', '', '',''
        )

        user.is_admin=True
        user.is_staff=True
        user.is_superuser=True
        user.is_active=True
        user.save(using=self._db)
        
        return user
