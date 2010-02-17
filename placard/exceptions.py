"Placard exceptions"

class PlacardException(Exception):
    "Base Class"
    pass

class DoesNotExistException(PlacardException):
    "LDAP object does not exist"
    pass

class MultipleResultsException(PlacardException):
    "Returned multiple results when expecting one"
    pass

class RequiredAttributeNotGiven(PlacardException):
    "Required attribute not given when adding object"
    pass
