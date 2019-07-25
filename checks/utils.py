from enum import Enum


class CheckStatus(Enum):
    PENDING = 'PENDING'
    CHECKING = 'CHECKING'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'
    PAID = 'PAID'
    WORKED = 'WORKED'
    JUSTIFIED = 'JUSTIFIED'


status_icons = {
    'PENDING': '🔲',
    'CHECKING': '🔲',
    'SUCCESS': '✔',
    'FAIL': '️✖️',
    'PAID': '💰',
    'WORKED': '👥',
    'JUSTIFIED': '👨‍⚖️',
}
