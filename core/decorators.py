from django.contrib.auth.decorators import user_passes_test

def is_game_master(user):
    return user.is_active and (
        user.is_superuser or user.groups.filter(name='Game Master').exists()
    )

def game_master_required(view_func):
    """
    Decorator for views that checks that the user is a superuser or in the Game Master group.
    """
    decorated_view_func = user_passes_test(
        is_game_master,
        login_url='/admin/login/'  # Redirect to admin login if unauthorized
    )(view_func)
    return decorated_view_func
