import os
BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', BROKER_URL)
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200}
CELERY_IMPORTS = ('tasks', )
CELERY_ACCEPT_CONTENT = ['json','pickle']
# uncomment to enable debugging:
CELERYD_POOL = 'celery.concurrency.threads:TaskPool'