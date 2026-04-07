from apps.users.models import CustomerProfile

class ProfileSelector:
    @staticmethod
    def get_user_profile(ruser):
        return CustomerProfile.objects.select_related('user').get(user=ruser)