import json
import time

import requests
from termcolor import colored
from tqdm import tqdm


class User:

    def __init__(self, access_token, user_id=None, user_ids=None, group_name=None, group_id=None, time_sleep=None,
                 friends_groups=None, person_groups=None):
        self.access_token = access_token
        self.user_id = user_id
        self.user_ids = user_ids
        self.group_id = group_id
        self.time_sleep = time_sleep
        self.person_groups = person_groups
        self.friends_groups = friends_groups
        self.group_name = group_name

    def code_params(self):
        return dict(
            access_token=self.access_token,
            v='5.61',
            user_id=self.user_id,
            user_ids=self.user_ids
        )

    def get_user_id(self):
        code_params = self.code_params()
        response = requests.get(
            'https://api.vk.com/method/users.get',
            code_params
        )
        self.user_id = response.json()['response'][0]['id']
        return self.user_id

    def user_checking(self):
        URL = "https://api.vk.com/method/execute?"
        version = '5.61'
        get_friends_code = {
            "code": "return API.friends.get({'user_id': %d});" % self.user_id,
            'access_token': self.access_token,
            'v': version
        }
        response = requests.post(url=URL, data=get_friends_code).json()
        if response.keys() == {'error'}:
            if response['error']['error_code'] == 18:
                raise SystemExit('-> Пользователь удален или заблокирован!')
            if response['error']['error_code'] == 15:
                raise SystemExit('-> Ничего не поделаешь, пользователь заблокировал доступ!')
            else:
                print(response['error']['error_code'], response['error']['error_msg'])
                raise SystemExit('-> Описание ошибки смотри выше!')
        else:
            response = response['response']['items']
            return print(colored('Доступ к пользователю получен!', 'green'))

    def person_friends_groups_getting(self):
        try:
            URL = "https://api.vk.com/method/execute?"
            version = '5.61'
            get_friends_groups_code = {
                "code": "var person_groups = API.groups.get({'user_id': %d, 'count': 1000}).items;"
                        # "var person_groups_name = API.groups.getById({'group_ids': person_groups});"
                        # "var person_groups_members_count = API.groups.getMembers({'group_id': person_groups});"
                        "var friends = API.friends.get({'user_id': %d, 'count': 1000}).items;"
                        "var friends_groups = API.groups.get({'user_id': friends@.response, 'count': 1000, 'offset': 0}).items;"
                        "return {'person_groups': person_groups,"
                        "'friends_groups': friends_groups};" % (self.user_id, self.user_id),
                'access_token': self.access_token,
                'oauth': self.access_token,
                'v': version
            }
            response = requests.post(url=URL, data=get_friends_groups_code).json()
            # print(response)
            self.person_groups = set(response['response']['person_groups'])
            self.friends_groups = set(response['response']['friends_groups'])
            return self.person_groups, self.friends_groups
        except TypeError:
            raise SystemExit('У пользователя нет групп!')

    def groups_get_info(self):
        URL = "https://api.vk.com/method/execute?"
        version = '5.61'
        get_group_name_code = {
            "code": "var group = %d;"
                    "return {'name': API.groups.getById({'group_id': group})@.name[0], "
                    "'gid': API.groups.getById({'group_id': group})@.id[0], "
                    "'members_count': API.groups.getMembers({'group_id': group}).count};" % self.group_id,
            'access_token': self.access_token,
            'oauth': self.access_token,
            'v': version
        }
        response = requests.post(url=URL, data=get_group_name_code).json()  # ['response']#['items'])
        if response.keys() == {'error'}:
            if response['error']['error_code'] == 6:
                # print(colored('-> Слишком много запросов в секунду, подбираю подходящий time.sleep и делаю запрос снова...', 'red'))
                while response.keys() == {'error'} and response['error']['error_code'] == 6:
                    self.time_sleep += 0.4
                    time.sleep(self.time_sleep)
                    response = requests.post(url=URL, data=get_group_name_code).json()
                response = response['response']
                pass
            else:
                print('Новая ошибка ' + response['error']['error_code'], response['error']['error_msg'])
                pass
            pass
        else:
            response = response['response']
        self.group_name = response
        return self.group_name


def main():
    start_time = time.time()
    try:
        access_token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
        person = input(colored('Введите ID пользователя (например, 171691064 или eshmargunov): ', 'blue'))
        # person = '171691064'

        # Вычисление user_id и проверка доступнуости пользователя
        try:
            if not person.isdigit():
                user_ids = str(person)
                person = User(access_token, user_ids=user_ids)
                person.get_user_id()
                user_id = int(person.user_id)
                print(f'Вычислили user_id: {user_id}')
            else:
                user_id = int(person)
                person = User(access_token=access_token, user_id=user_id)
                person.user_checking()
        except KeyError:
            raise SystemExit('Пользователя не существует!')
        except IndexError:
            raise SystemExit('Вы ввели пустое значение!')

        # Получение групп пользователя и его друзей
        groups = User(access_token=access_token, user_id=user_id)
        groups.person_friends_groups_getting()
        person_groups = groups.person_groups
        friends_groups = groups.friends_groups
        final_set_of_absent_groups = person_groups.difference(friends_groups)
        final_set_of_together_groups = person_groups.intersection(friends_groups)
        data_for_file = list()
        print(colored('Загрузили даные о пользователе, его друзьях и группах!', 'green'))

        if len(final_set_of_absent_groups) > 0:
            print(colored('1-й файл - Записываем JSON файл с группами пользотвателя, в которых не состоят его друзья: ', 'blue'))
            with open('JSON_fiends_absent.json', 'w') as file:
                for group_id in tqdm(final_set_of_absent_groups):
                    group = User(access_token=access_token, group_id=group_id, time_sleep=0.01)
                    group.groups_get_info()
                    data_for_file.append(group.group_name)
                # print(data_for_file)
                file.write(json.dumps(data_for_file, ensure_ascii=False))
        else:
            print(colored('1-й файл - Нечего записывать, у пользователя нет групп, в которых не состоят его друзья!', 'red'))

        if len(final_set_of_together_groups) > 0:
            print(colored('2-й файл - Записываем JSON файл с группами пользотвателя, в которых состоят его друзья: ', 'blue'))
            with open('JSON_fiends_together.json', 'w') as file:
                for group_id in tqdm(final_set_of_together_groups):
                    group = User(access_token=access_token, group_id=group_id, time_sleep=0.01)
                    group.groups_get_info()
                    data_for_file.append(group.group_name)
                # print(data_for_file)
                file.write(json.dumps(data_for_file, ensure_ascii=False))
        else:
            print(colored('2-й файл - Нечего записывать, у пользователя нет общих, с его друзьями, групп!', 'red'))

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        raise SystemExit('Отсутсует подключение к верверу...')

    print('Программа выполнена!')
    print('Время выполнения программы - %s секунд.' % round((time.time() - start_time), 2))


main()
