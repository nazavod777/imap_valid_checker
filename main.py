from multiprocessing.dummy import Pool
from sys import stderr

from imap_tools import MailBox
from imap_tools.errors import MailboxLoginError
from loguru import logger

import config

logger.remove()
logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')


def percent_difference(value1: float | int,
                       value2: float | int) -> float | int:
    if value1 == value2:
        return 100

    if value1 == 0:
        return 0

    percent = (value1 / value2) * 100

    return int(percent)


def check(credentials: str) -> str | None:
    email, password = credentials.split(':')[:2]

    try:
        with MailBox(config.IMAP_HOST).login(email, password):
            pass

    except MailboxLoginError as error:
        logger.error(f'{credentials} | {error}')
        return

    except Exception as error:
        logger.error(f'{credentials} | {error}')
        return

    else:
        logger.success(f'{credentials}')
        return f'{email}:{password}'


if __name__ == '__main__':
    emails_folder: str = input('Drop .txt with emails: ')

    with open(file=emails_folder,
              mode='r',
              encoding='utf-8-sig') as file:
        emails_list: list[str] = [row.strip().replace(';', ':').replace(' ', '')
                                  for row in file]

    logger.success(f'Успешно загружено {len(emails_list)} emails')
    threads: int = int(input('Threads: '))
    print()

    with Pool(processes=threads) as executor:
        result: list[None | str] = executor.map(check, emails_list)

    valid_result: list[str] = [row for row in result if row]

    with open(file='valid.txt',
              mode='a',
              encoding='utf-8-sig') as file:
        file.write('\n'.join(valid_result) + '\n')

    valid_percent: int = percent_difference(value1=len(valid_result),
                                            value2=len(emails_list))
    logger.success(f'Работа успешно завершена, Valid Percent: {valid_percent}')
    input('\nPress Enter to Exit..')
