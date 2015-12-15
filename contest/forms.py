from django.contrib.auth.forms import UserCreationForm

from contest.models import RushUser


class RegistrationForm(UserCreationForm):

	class Meta:
		model=RushUser
		fields=('email', 'first_name', 'last_name', 'organization_name',
			'organization_address', 'password1', 'password2'
			)
