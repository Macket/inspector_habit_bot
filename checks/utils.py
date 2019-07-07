from enum import Enum


class CheckStatus(Enum):
    PENDING = 'PENDING'
    CHECKING = 'CHECKING'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'


status_icons = {
    'PENDING': '🔲',
    'CHECKING': '🔲',
    'SUCCESS': '✔',
    'FAIL': '️✖️',
}
