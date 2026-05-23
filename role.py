
def all_routes() :
    return  {
        "Home": "IndexHOME",
        "Login": "LoginHOME",
        "Signup": "SignupHOME",
        "Password Reset": "PasswordResetHOME",
    }

def routes_of_(role= 'viewer') :
    if role == 'viewer' :
        return all_routes()
    elif role == 'unverified_user' :
        return all_routes()|{'Verify Account':'VerifyHOME' }
    elif role == 'verified_user' :
        return all_routes()| {"My Account": "MyAccountHOME",}
    else :
        return all_routes()

def inner_access(role= 'viewer') :
    if role == 'viewer' :
        return {}
    elif role == 'unverified_user' :
        return  { "Logout" : "LogoutHOME",  "Password Reset": "PasswordResetHOME" }
    elif role == 'verified_user' :
        return  { "Logout" : "LogoutHOME",  "Password Reset": "PasswordResetHOME" }
    return all_routes()


def can_access_( route  , role= 'viewer'   ) :
    accessible_routes = routes_of_(role) | inner_access(role)
    return  not route in accessible_routes.values()

