PKG_NAMESPACE = yhttp.ext.sqlalchemy
PKG_NAME = yhttp-sqlalchemy
VENV_NAME = yhttp
PYDEPS_COMMON += \
	'coveralls >= 4.1.0' \
	'bddrest >= 6.2.3, < 7' \
	'bddcli >= 2.10.1, < 3' \
	'yhttp-dev >= 4.0.1, < 5'


# Assert the python-makelib version
PYTHON_MAKELIB_VERSION_REQUIRED = 2.5.2


# Ensure the python-makelib is installed
PYTHON_MAKELIB_PATH = /usr/local/lib/python-makelib
ifeq ("", "$(wildcard $(PYTHON_MAKELIB_PATH))")
  MAKELIB_URL = https://github.com/pylover/python-makelib
  $(error python-makelib is not installed. see "$(MAKELIB_URL)")
endif


# Include a proper bundle rule file.
include $(PYTHON_MAKELIB_PATH)/venv-lint-test-pypi.mk
