

def is_password_strong(password, old_password=None):
    """Return True if password valid"""
    from crack import VeryFascistCheck
    try:
        VeryFascistCheck(password, old=old_password)
    except Exception, e:
        return False
     
    return True
