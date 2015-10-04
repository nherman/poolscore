from poolscore.mod_common.utils import SecurityUtil

def _is_admin():
    return SecurityUtil.is_admin()

def datetime(value, format='%Y-%m-%d'):
    return value.strftime(format)    

globals = {
    'is_admin': _is_admin
}

filters = {
    'datetime': datetime
}
