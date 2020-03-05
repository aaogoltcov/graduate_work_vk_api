import json
import time
from tqdm import tqdm
import requests
from termcolor import colored


class User:

    def __init__(self, access_token, user_id=None, user_ids=None, user_name=None, user_last_name=None, friends=None,
                 groups=None,
                 info=None,
                 mistake=None, mistake_code=None, group_id=None, group_name=None, group_count=None, time_sleep=None):
        self.access_token = access_token
        self.user_name = user_name
        self.user_last_name = user_last_name
        self.friends = friends
        self.user_id = user_id
        self.info = info
        self.mistake = mistake
        self.mistake_code = mistake_code
        self.groups = groups
        self.group_id = group_id
        self.group_name = group_name
        self.group_count = group_count
        self.time_sleep = time_sleep
        self.user_ids = user_ids

    def __str__(self):
        return f'https://vk.com/id{self.user_id}'

    def get_params(self):
        return dict(
            access_token=self.access_token,
            v='5.52',
            user_id=self.user_id,
            user_ids=self.user_ids
        )

    def checking_groups_access(self):
        params = self.get_params()
        response = requests.get(
            'https://api.vk.com/method/groups.get',
            params
        )
        self.info = response.json().keys()
        if self.info == {'error'}:
            self.mistake = 'error'
            self.mistake = response.json()[self.mistake]['error_msg']
            if self.mistake == 'User authorization failed: invalid access_token (4).':
                self.mistake = 'Не верный Access Token...'
                raise SystemExit(self.mistake)
            elif self.mistake == 'Access denied: this profile is private':
                self.mistake = colored('-> Закрыт доступ к группам, пропускаем.', 'red')
                self.mistake_code = 13
                pass
            elif self.mistake == 'Permission to perform this action is denied':
                self.mistake = colored('-> Закрыт доступ к группам, пропускаем.', 'red')
                self.mistake_code = 13
                pass
            elif self.mistake == 'User was deleted or banned':
                self.mistake = colored(
                    '-> Закрыт доступ к группам, т.к. пользователь заблокирован или удален, пропускаем.', 'red')
                self.mistake_code = 13
                pass
            elif self.mistake == 'Too many requests per second':
                self.mistake = 'Слишком много запросов в секунду, попробуйте увеличить интервал.'
                raise SystemExit(self.mistake)
            else:
                self.mistake = 'Пустой Access Token или что-то пошло не так...'
                mistake_text = response.json()
                print(mistake_text)
                raise SystemExit(self.mistake)
        elif self.info == {'response'}:
            self.mistake = 'response'
            self.mistake = response.json()[self.mistake]  # [0]#['deactivated']

            try:
                if not self.mistake:
                    self.mistake = f'Пользователь не существует: {self.user_id}'
                    raise SystemExit(self.mistake)
                elif not self.mistake[0]['deactivated']:
                    self.mistake = colored(f'Доступ к группам {self.user_id} получен.', 'green')
                else:
                    self.mistake = f'Пользователь удален или отключен: {self.user_id}'
                    raise SystemExit(self.mistake)
            except KeyError:
                self.mistake = colored(f'Доступ к группам {self.user_id} получен.', 'green')

        return self.mistake, self.mistake_code

    def checking_user(self):
        params = self.get_params()
        response = requests.get(
            'https://api.vk.com/method/users.get',
            params
        )
        self.info = response.json().keys()
        if self.info == {'error'}:
            self.mistake = 'error'
            self.mistake = response.json()[self.mistake]['error_msg']
            if self.mistake == 'User authorization failed: invalid access_token (4).':
                self.mistake = 'Введен не верный Access Token...'
                raise SystemExit(self.mistake)
            elif self.mistake == 'Access denied: this profile is private':
                self.mistake = colored('-> Закрыт доступ к пользователю, пропускаем.', 'red')
                self.mistake_code = 13
                pass
            elif self.mistake == 'Too many requests per second':
                self.mistake = 'Слишком много запросов в секунду, попробуйте увеличить интервал.'
                raise SystemExit(self.mistake)
            else:
                self.mistake = 'Пустой Access Token или что-то пошло не так...'
                mistake_text = response.json()
                print(mistake_text)
                raise SystemExit(self.mistake)
        elif self.info == {'response'}:
            self.mistake = 'response'
            self.mistake = response.json()[self.mistake]  # [0]#['deactivated']

            try:
                if not self.mistake:
                    self.mistake = colored(f'-> Пользователь не существует: {self.user_id}', 'red')
                    self.mistake_code = 13
                    pass
                elif not self.mistake[0]['deactivated']:
                    self.mistake = colored(f'Доступ к {self.user_id} получен.', 'green')
                else:
                    self.mistake = colored(f'-> Пользователь удален или отключен: {self.user_id}', 'red')
                    self.mistake_code = 13
                    pass
            except KeyError:
                self.mistake = colored(f'Доступ к {self.user_id} получен.', 'green')

        return self.mistake, self.mistake_code

    def get_info(self):
        params = self.get_params()
        response = requests.get(
            'https://api.vk.com/method/users.get',
            params
        )
        self.user_name = response.json()['response'][0]['first_name']
        self.user_last_name = response.json()['response'][0]['last_name']
        self.user_id = response.json()['response'][0]['id']
        return self.user_id, self.user_name, self.user_last_name

    def get_friends(self):
        params = self.get_params()
        response = requests.get(
            'https://api.vk.com/method/friends.get',
            params
        )
        self.friends = response.json()['response']['items']
        return response.json()

    def get_friends_execute(self):
        url = "https://api.vk.com/method/execute?"
        v = '5.52'
        get_friends_code = {
            "code": "var a = API.friends.get({'user_id': %d});"
                    "return a;" % self.user_id
        }
        header = {
            'oauth': self.access_token
        }
        params = dict(access_token=self.access_token, v=v, user_id=self.user_id)
        self.friends = set(
            requests.post(url=url, data=get_friends_code, headers=header, params=params).json()['response']['items'])
        return self.friends

    def get_groups_execute(self):
        url = "https://api.vk.com/method/execute?"
        v = '5.52'
        get_groups_code = {
            "code": "var b = API.groups.get({'user_id': %d});"
                    "return b;" % self.user_id,
            "oauth": self.access_token
        }
        header = {
            'oauth': self.access_token
        }
        params = dict(access_token=self.access_token, v=v, user_id=self.user_id)
        self.groups = set(
            requests.post(url=url, data=get_groups_code, headers=header, params=params).json()['response']['items'])
        return self.groups

    def get_groups_info_execute(self):
        url = "https://api.vk.com/method/execute?"
        v = '5.52'
        get_group_name_code = {
            "code": "var c = API.groups.getById({'group_id': %d});"
                    "return c;" % self.group_id
        }
        get_group_members_count_code = {
            "code": "var e = API.groups.getMembers({'group_id': %d});"
                    "return e;" % self.group_id
        }
        header = {
            'oauth': self.access_token
        }
        params = dict(access_token=self.access_token, v=v, user_id=self.user_id)
        self.group_name = requests.post(url=url, data=get_group_name_code, params=params).json()['response'][0][
            'name']
        time.sleep(self.time_sleep)
        self.group_count = \
            requests.post(url=url, data=get_group_members_count_code, params=params).json()['response']['count']
        return self.group_name, self.group_count


def check_token_user(access_token, user_id):
    # print(f'Проверяем доступность пользователя: {user_id}')
    user = User(access_token, user_id)
    user.checking_user()
    # print(user.mistake)
    return user.mistake_code


def check_groups_access(access_token, user_id):
    # print(f'Проверяем доступность групп пользователя: {user_id}')
    user = User(access_token, user_id)
    user.checking_groups_access()
    # print(user.mistake)
    return user.mistake_code


def main():
    try:
        access_token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
        time_sleep = 1.1
        users = input(colored('Введите ID пользователя (например, 171691064 или eshmargunov): ', 'blue'))
        try:
            if not users.isdigit():
                users = str(users)
                users = User(access_token, user_ids=users)
                users.get_info()
                users = users.user_id
                print(f'Вычислили user_id: {users}')
            else:
                users = int(users)
        except KeyError:
            raise SystemExit('Пользователя не существует...')
        except IndexError:
            raise SystemExit('Вы ввели пустое значение...')

        # Проверяем введенного пользователя
        mistake_user_code = check_token_user(access_token, user_id=users)
        if mistake_user_code == 13:
            raise SystemExit('Пользователь не существует, отулючен или удален...')
        else:
            pass
        print(colored(f'Смотрим друзей пользователя {users}, с проверкой доступности к профилю и группам:\n', 'blue'))
        friends = User(access_token, user_id=users)
        friends.get_friends_execute()
        get_friends = friends.friends
        time.sleep(time_sleep)

        # Загружаем группы друзей пользователя
        set_of_groups = set()
        user_access_error = int()
        group_access_error = int()
        for friend in tqdm(get_friends):
            # time.sleep(0.05)
            # print('\r')

            # Проверка друзей и их групп
            mistake_user_code = check_token_user(access_token, user_id=friend)
            time.sleep(time_sleep)
            mistake_groups_code = check_groups_access(access_token, user_id=friend)
            time.sleep(time_sleep)
            if mistake_user_code == 13:
                user_access_error += 1
                pass
            elif mistake_groups_code == 13:
                group_access_error += 1
                pass
            else:
                groups = User(access_token, user_id=friend)
                groups.get_groups_execute()
                get_groups = groups.groups
                set_of_groups = set.union(set_of_groups, get_groups)
                time.sleep(time_sleep)

        print(colored(f'Недоступных пользователей -  {user_access_error} шт.', 'red'))
        print(colored(f'Недоступных групп пользователей -  {group_access_error} шт.\n', 'red'))

        print(f'Получаем список групп нашего пользователя {users} в которых нет его друзей, и в которых они вместе...')
        groups = User(access_token, user_id=users)
        groups.get_groups_execute()
        get_groups = groups.groups
        final_set_of_absent_groups = set.difference(get_groups, set_of_groups)
        final_set_of_together_groups = set.intersection(get_groups, set_of_groups)
        print(colored('Получили!', 'green'))
        print(colored(
            f'\nИ так, всего {len(final_set_of_absent_groups)} групп(ы) в которых состоит наш пользователь, но не '
            f'состоят его друзья, а также {len(final_set_of_together_groups)} групп(ы) в которых состоит наш '
            f'пользователь и его друзья.\n', 'blue'))
        time.sleep(2)

        # Сбор информации по группа друзей пользователя, запись в файл
        list_groups_for_file = dict()
        data_for_file = list()
        print(
            'Начинаем собирать информацию по группам, где есть только наш пользователь, и записываем в 1-й JSON файл:')
        time.sleep(0.1)
        with open('JSON_fiends_absent.json', 'w') as file:
            for group in tqdm(final_set_of_absent_groups):
                group_name = User(access_token, group_id=group, time_sleep=time_sleep)
                group_name.get_groups_info_execute()
                list_groups_for_file.update(
                    {"name": group_name.group_name, "gid": group, "members_count": group_name.group_count})
                group_info_total = dict()
                for key, value in list_groups_for_file.items():
                    group_info = {key: value}
                    group_info_total.update(group_info)
                data_for_file.append(group_info_total)
            file.write(json.dumps(data_for_file, ensure_ascii=False))

        list_groups_for_file = dict()
        data_for_file = list()
        print('\nНачинаем собирать информацию по группам, где пользователь с друзьями, и записываем во 2-й JSON файл:')
        time.sleep(0.1)
        cycle = int()
        N = 1000
        with open('JSON_fiends_together.json', 'w') as file:
            for group in tqdm(final_set_of_together_groups):
                if cycle <= N:
                    group_name = User(access_token, group_id=group, time_sleep=time_sleep)
                    group_name.get_groups_info_execute()
                    list_groups_for_file.update(
                        {"name": group_name.group_name, "gid": group, "members_count": group_name.group_count})
                    group_info_total = dict()
                    for key, value in list_groups_for_file.items():
                        group_info = {key: value}
                        group_info_total.update(group_info)
                    data_for_file.append(group_info_total)
                    cycle += 1
                else:
                    pass
            file.write(json.dumps(data_for_file, ensure_ascii=False))

        # Чтение из записанного файла
        with open('JSON_fiends_absent.json', encoding='utf-8') as file:
            print('\nJSON_fiends_absent.json файл записан!\n')
            # print(file.read())

        with open('JSON_fiends_together.json', encoding='utf-8') as file:
            print('\nJSON_fiends_together.json файл записан!\n')
            # print(file.read())

        print(colored('\nПрограмма завершена, файлы записаны.', 'green'))

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        raise SystemExit('Отсутсует подключение к верверу...')


main()

# access_token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
# user = 'aaogoltcov'
# user = User(access_token, user_ids=user)
# user.get_info()
# print(user.user_name)
