from poolscore.mod_common.utils import SecurityUtil

def _is_admin():
    return SecurityUtil.is_admin()

globals = {
    'is_admin': _is_admin
}
