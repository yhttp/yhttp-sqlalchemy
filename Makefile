PKG_NAMESPACE = yhttp.ext.sqlalchemy
PKG_NAME = yhttp-sqlalchemy
PYDEPS_COMMON += \
	'bddrest >= 4, < 5' \
	'bddcli >= 2.5.1, < 3' \
	'yhttp-dev >= 3.1.2'


include make/common.mk
include make/install.mk
include make/lint.mk
include make/dist.mk
include make/pypi.mk
include make/test.mk
include make/venv.mk
