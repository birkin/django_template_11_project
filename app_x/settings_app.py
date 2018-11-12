# -*- coding: utf-8 -*-

import json, os


README_URL = os.environ['DJANGO_TEMPLATE__README_URL']

## auth
# SUPER_USERS = json.loads( os.environ['DJANGO_TEMPLATE__UPER_USERS_JSON'] )
# STAFF_USERS = json.loads( os.environ['DJANGO_TEMPLATE__STAFF_USERS_JSON'] )  # users permitted access to admin
# STAFF_GROUP = os.environ['DJANGO_TEMPLATE__STAFF_GROUP']  # not grouper-group; rather, name of django-admin group for permissions
# TEST_META_DCT = json.loads( os.environ['DJANGO_TEMPLATE__TEST_META_DCT_JSON'] )
# POST_LOGIN_ADMIN_REVERSE_URL = os.environ['DJANGO_TEMPLATE__POST_LOGIN_ADMIN_REVERSE_URL']  # tricky; for a direct-view of a model, the string would be in the form of: `admin:APP-NAME_MODEL-NAME_changelist`
