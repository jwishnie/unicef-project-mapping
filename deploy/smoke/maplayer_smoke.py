# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from twill.commands import *

go("http://mapping.mepemepe.com/")
code(200)
title("UNICEF Maps")
title("Home")
go("http://mapping.mepemepe.com/projects/id/1/")
code(200)
title("School for all")

# Login as admin
follow("Login")
code(200)
title("UNICEF Maps")
fv("1", "username", "admin")
fv("1", "password", "admin")
submit()

# Redirect to page before login with logged in state
title("School for all")
assert([link.url for link in showlinks()].count('/accounts/logout/') == 1)
assert([link.url for link in showlinks()].count('/projects_for_review/') == 1)
