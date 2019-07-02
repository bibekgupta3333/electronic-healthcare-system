from celery import shared_task


@shared_task(bind=True)
def test_celery(self, x, y):
    return x + y
