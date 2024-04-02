from django.conf import settings


def pytest_configure():
    try:
        settings.configure()
        installed_apps = settings.INSTALLED_APPS.append('hydrology')
        settings.configure(INSTALLED_APPS=installed_apps)
    except RuntimeError:
        print('running tests as part of a django-project, not a standalone app')
