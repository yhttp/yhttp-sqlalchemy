PKG_NAMESPACE = yhttp.ext.sqlalchemy
PKG_NAME = yhttp-sqlalchemy
PYDEPS_COMMON += \
	'coveralls' \
	'bddrest >= 4, < 5' \
	'bddcli >= 2.5.1, < 3' \
	'yhttp-dev >= 3.1.2'


# Assert the python-makelib version
PYTHON_MAKELIB_VERSION_REQUIRED = 1.4.1


# Ensure the python-makelib is installed
PYTHON_MAKELIB_PATH = /usr/local/lib/python-makelib
ifeq ("", "$(wildcard $(PYTHON_MAKELIB_PATH))")
  MAKELIB_URL = https://github.com/pylover/python-makelib
  $(error python-makelib is not installed. see "$(MAKELIB_URL)")
endif


# Include a proper bundle rule file.
include $(PYTHON_MAKELIB_PATH)/venv-lint-test-pypi.mk
