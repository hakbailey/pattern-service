from django.conf import settings

from dispatcherd.publish import task


@task(queue=settings.DISPATCHERD_DEFAULT_CHANNEL, decorate=False)
def print_hello():
    print('hello world!!')
