USERTYPE_OWNER = 1
USERTYPE_MANAGER = 2
USERTYPE_EMPLOYEE = 3

USER_ROLE_CHOICES = (
    (USERTYPE_OWNER, 'owner'),
    (USERTYPE_MANAGER, 'manager'),
    (USERTYPE_EMPLOYEE, 'employee'),
)

STATUS_WAITING = 1
STATUS_SENT = 2

STATUS_CHOICES = (
        (STATUS_WAITING, 'Ожидание'),
        (STATUS_SENT, 'Отправлен'),
    )

STATUS_DRAFT = 1
STATUS_UNDER_REVIEW = 2
STATUS_READY = 3
STATUS_STOPPED = 4
STATUS_IN_PROGRESS = 5
STATUS_COMPLETED = 6
STATUS_DELETED = 7

NEWSLETTER_STATUS = (
    (STATUS_DRAFT, 'Черновик'),
    (STATUS_UNDER_REVIEW, 'На проверке'),
    (STATUS_READY, 'Готовы к запуску'),
    (STATUS_STOPPED, 'Остановлены'),
    (STATUS_IN_PROGRESS, 'Выполняются'),
    (STATUS_COMPLETED, 'Завершённые'),
    (STATUS_DELETED, 'Удалённые'),
)

PLAYED = 1
NOT_PLAYED = 2

RAFFLE_PRIZE_STATUS = (
    (PLAYED, 'Разыграно'),
    (NOT_PLAYED, 'Не разыграно'),
)


ISSUED = 1
NOT_ISSUED = 2

PRIZE_STATUS = (
    (ISSUED, 'Выдан'),
    (NOT_ISSUED, 'Не выдан'),
)

ACTIVE = 1
NOT_ACTIVE = 2
WAITING_PAIMENT = 3

BRANCH_STATUS = (
    (ACTIVE, 'Активен'),
    (NOT_ACTIVE, 'Не активен'),
    (WAITING_PAIMENT, 'Ожидается оплата'),
)