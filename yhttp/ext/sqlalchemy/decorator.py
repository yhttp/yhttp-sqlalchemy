import sys
import functools

import yhttp


def dbsession(func):

    @functools.wraps(func)
    def outter(req, *a, **kw):

        def wrapper(req, *a, **kw):
            app = req.application
            req.session = app.db.sessionfactory()
            try:
                with req.session as session, session.begin():
                    return func(req, *a, **kw)

            except AttributeError:
                print(
                    'Please intstall yhttp-sqlalchemy extention first.',
                    file=sys.stderr
                )
                raise

            except yhttp.HTTPStatus as ex:
                if ex.keepheaders:
                    return ex

                raise

        result = wrapper(req, *a, **kw)
        if isinstance(result, yhttp.HTTPStatus):
            raise result

        return result

    return outter
