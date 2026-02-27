from .decorators import is_game_master


def auth_flags(request):
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {"is_game_master": False}

    return {"is_game_master": is_game_master(user)}
