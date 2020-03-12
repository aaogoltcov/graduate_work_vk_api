import json
import time
import requests
from termcolor import colored
from tqdm import tqdm


class User:

    def __init__(self, access_token, user_id=None, user_ids=None, group_name=None, group_id=None, time_sleep=None,
                 friends_groups=None, person_groups=None, friends_groups_list=None, treated_groups_list=None,
                 source_code=None, items_list=None, response_total=None, URL=None):
        self.access_token = access_token
        self.user_id = user_id
        self.user_ids = user_ids
        self.group_id = group_id
        self.time_sleep = time_sleep
        self.person_groups = person_groups
        self.friends_groups = friends_groups
        self.group_name = group_name
        self.friends_groups_list = friends_groups_list
        self.treated_groups_list = treated_groups_list
        self.source_code = source_code
        self.items_list = items_list
        self.response_total = response_total
        self.URL = URL

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
        self.user_id = response.json()
        self.user_id = self.user_id['response'][0]['id']
        return self.user_id

    def user_checking(self):
        get_friends_code = {
            "code": "return API.friends.get({'user_id': %d});" % self.user_id,
            'access_token': self.access_token,
            'v': '5.61'
        }
        friends_list = requests.post(url=self.URL, data=get_friends_code).json()

        # Проверка доступности пользователя
        if friends_list.keys() == {'error'}:
            if friends_list['error']['error_code'] == 18:
                raise SystemExit('-> Пользователь удален или заблокирован!')
            if friends_list['error']['error_code'] == 15:
                raise SystemExit('-> Ничего не поделаешь, пользователь заблокировал доступ!')
            else:
                print(friends_list['error']['error_code'], friends_list['error']['error_msg'])
                raise SystemExit('-> Описание ошибки смотри выше!')
        else:
            friends_list = friends_list['response']['items']
            self.friends_groups_list = friends_list
        return print(colored('1. Доступ к пользователю получен, начинаем получать информацию по группам:', 'green')), self.friends_groups_list

    def person_friends_groups_getting(self):
        try:
            # Получение списка групп друзей пользователя
            self.source_code = "API.groups.get({'user_id': person}).items"
            self.items_list = self.friends_groups_list
            friends_groups_getting = self.code_request()

            # Очистка списка от групп пользователей, к которым нет доступа
            self.friends_groups = list()
            for items in friends_groups_getting:
                if items != None:
                    for item in items:
                        self.friends_groups.append(item)
            self.friends_groups = set(self.friends_groups)
            print(colored(f'2. Получено множество из {len(self.friends_groups)} групп друзей пользователя.', 'green'))

            # Получение групп пользователя
            time.sleep(0.5)
            get_friends_groups_code = {
                "code": "return API.groups.get({'user_id': %d, 'count': 1000}).items;" % self.user_id,
                'access_token': self.access_token,
                'oauth': self.access_token,
                'v': '5.61'
            }
            response = requests.post(url=self.URL, data=get_friends_groups_code).json()
            self.person_groups = set(response['response'])
            print(colored(f'3. Получено множество из {len(self.person_groups)} групп пользователя.', 'green'))
            return self.person_groups, self.friends_groups
        except TypeError:
            raise SystemExit('У пользователя нет групп!')

    def groups_get_info(self):
        # Получение информации о группе (имя, id, количество участников)
        self.source_code = "API.groups.getById({'group_ids': person, 'fields': 'members_count'})"
        self.items_list = self.treated_groups_list
        groups_info = self.code_request()

        # Приведение полученной информации к списку со словарем
        group_info_list = list()
        for response in groups_info:
            response = {'gid': response[0]['id'], 'name': response[0]['name'], 'members_count': response[0]['members_count']}
            group_info_list.append(response)
        self.group_name = group_info_list
        return self.group_name

    def code_request(self):
        self.response_total = list()
        code_list = str()
        code_count = 0
        for full_code in tqdm(self.items_list):
            full_code = self.source_code.__str__().replace("person", full_code.__str__())
            code_list = full_code + ', ' + code_list
            code_count += 1
            if code_count == 25:
                code = {'code': f'return [{code_list}];',
                        'access_token': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                        # 'oauth': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                        'v': '5.61'}
                response = requests.post(url=self.URL, data=code).json()
                if response.keys() == {'error'}:
                    if response['error']['error_code'] == 6:
                        # print(colored('-> Слишком много запросов в секунду, подбираю подходящий time.sleep и делаю
                        # запрос снова...', 'red'))
                        pass
                        while response.keys() == {'error'} and response['error'][
                            'error_code'] == 6:
                            self.time_sleep += 0.4
                            time.sleep(self.time_sleep)
                            response = requests.post(url=self.URL, data=code).json()
                        response = response['response']
                        pass
                    else:
                        print('Новая ошибка:')
                        print(response['error']['error_code'])
                        print(response['error']['error_msg'])
                        pass
                    pass
                else:
                    response = response['response']
                code_list = str()
                code_count = 0
                self.response_total.extend(response)
        if code_count < 25 and code_count != 0:
            code = {'code': f'return [{code_list}];',
                    'access_token': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                    'oauth': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                    'v': '5.61'}
            response = requests.post(url=self.URL, data=code).json()
            if response.keys() == {'error'}:
                if response['error']['error_code'] == 6:
                    # print(colored('-> Слишком много запросов в секунду, подбираю подходящий time.sleep и делаю
                    # запрос снова...', 'red'))
                    while response.keys() == {'error'} and response['error'][
                        'error_code'] == 6:
                        self.time_sleep += 0.4
                        time.sleep(self.time_sleep)
                        response = requests.post(url=self.URL, data=code).json()
                    response = response['response']
                    pass
                else:
                    print('Новая ошибка:')
                    print(response['error']['error_code'])
                    print(response['error']['error_msg'])
                    pass
                pass
            else:
                response = response['response']
            self.response_total.extend(response)
            return self.response_total


def main():
    URL = "https://api.vk.com/method/execute?"
    try:
        access_token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
        person = str(input(colored('Введите ID пользователя (например, 171691064 или eshmargunov): ', 'blue')))
        # person = '171691064'
        start_time = time.time()
        # Вычисление user_id и проверка доступнуости пользователя
        try:
            if not person.isdigit():
                user_ids = str(person)
                person = User(access_token, user_ids=user_ids, time_sleep=0.01, URL=URL)
                person.get_user_id()
                user_id = int(person.user_id)
                print(f'Вычислили user_id: {user_id}')
                person = User(access_token=access_token, user_id=user_id, time_sleep=0.01, URL=URL)
                person.user_checking()
            else:
                user_id = int(person)
                person = User(access_token=access_token, user_id=user_id, time_sleep=0.01, URL=URL)
                person.user_checking()
        except KeyError:
            raise SystemExit('Пользователя не существует!')
        except IndexError:
            raise SystemExit('Вы ввели пустое значение!')

        # Получение групп пользователя и его друзей
        groups = User(access_token=access_token, user_id=user_id, friends_groups_list=person.friends_groups_list,
                      time_sleep=0.01, URL=URL)
        groups.person_friends_groups_getting()
        person_groups = groups.person_groups
        friends_groups = groups.friends_groups
        final_set_of_absent_groups = person_groups.difference(friends_groups)
        final_set_of_together_groups = person_groups.intersection(friends_groups)
        print(colored('4. Вычислили пересечение групп для пользователя и его друзей:', 'green'))
        print(f'-> {len(final_set_of_absent_groups)} групп, в которых нет друзей пользователя')
        print(f'-> {len(final_set_of_together_groups)} групп, в которых есть друзья пользователя')
        print('Время выполнения до записи файлов - %s секунд(ы).' % round((time.time() - start_time), 2))

        if len(final_set_of_absent_groups) > 0:
            print(colored('1-й файл - Записываем JSON файл с группами пользотвателя, в которых не состоят его друзья: ',
                          'blue'))
            time.sleep(0.01)
            with open('JSON_fiends_absent.json', 'w') as file_absent:
                data_for_file_absent = User(access_token=access_token, treated_groups_list=final_set_of_absent_groups,
                                            time_sleep=0.01, URL=URL)
                file_absent.write(json.dumps(data_for_file_absent.groups_get_info(), ensure_ascii=False))
        else:
            print(colored('1-й файл - Нечего записывать, у пользователя нет групп, в которых не состоят его друзья!',
                          'red'))

        if len(final_set_of_together_groups) > 0:
            print(colored('2-й файл - Записываем JSON файл с группами пользотвателя, в которых состоят его друзья: ',
                          'blue'))
            time.sleep(0.01)
            with open('JSON_fiends_together.json', 'w') as file_together:
                data_for_file_together = User(access_token=access_token,
                                              treated_groups_list=final_set_of_together_groups, time_sleep=0.01,
                                              URL=URL)
                file_together.write(json.dumps(data_for_file_together.groups_get_info(), ensure_ascii=False))
        else:
            print(colored('2-й файл - Нечего записывать, у пользователя нет общих, с его друзьями, групп!', 'red'))

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        raise SystemExit('Отсутсует подключение к верверу...')

    print('Программа выполнена!')
    print('Время выполнения программы - %s секунд(ы).' % round((time.time() - start_time), 2))


main()
