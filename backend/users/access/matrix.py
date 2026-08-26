# main code
# Single source of truth for field-level permissions (6.2). Data only, no logic.
#
# Shape:
#   '<Department.code>': {
#       '<app_label>.<Model>': frozenset({'<field>', ...}),
#   }
#
# It is a whitelist: whatever is not declared here is not visible. A department with
# no entry sees no field at all, and a new model field stays invisible to everyone
# until it is added here on purpose. HR_ADMIN never appears: it is resolved earlier,
# with full access.
#
# PENDING (14, #5): the real matrix is defined with Human Resources. Filling this in
# with guesses would silently expose employee data, so it stays empty until then.
FIELD_ACCESS_MATRIX = {}
