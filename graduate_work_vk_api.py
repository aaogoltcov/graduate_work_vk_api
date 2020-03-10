import json
import time
import requests
from termcolor import colored
from tqdm import tqdm


class User:

    def __init__(self, access_token, user_id=None, user_ids=None, group_name=None, group_id=None, time_sleep=None,
                 friends_groups=None, person_groups=None, friends_groups_list=None):
        self.access_token = access_token
        self.user_id = user_id
        self.user_ids = user_ids
        self.group_id = group_id
        self.time_sleep = time_sleep
        self.person_groups = person_groups
        self.friends_groups = friends_groups
        self.group_name = group_name
        self.friends_groups_list = friends_groups_list

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
        URL = "https://api.vk.com/method/execute?"
        version = '5.61'
        get_friends_code = {
            "code": "return API.friends.get({'user_id': %d});" % self.user_id,
            'access_token': self.access_token,
            'v': version
        }
        friends_list = requests.post(url=URL, data=get_friends_code).json()
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

            # Получение списка друзей и количества групп для друзей
            print('1. Начинаем получать информацию о друзьях пользователя: ')
            friends_groups_count = list()
            source_code = "{'user_id': person, 'groups_count': API.users.get({'user_id': person, 'fields': 'counters'})@.counters@.groups[0]}"
            code_list = str()
            person_count = 0
            for person_code in tqdm(friends_list):
                person_code = source_code.__str__().replace("person", str(int(person_code)))
                code_list = person_code + ', ' + code_list
                person_count += 1
                if person_count == 25:
                    code = {'code': f'return [{code_list}];',
                            'access_token': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                            'oauth': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                            'v': '5.61'}
                    friends_groups_count_list = requests.post(url=URL, data=code).json()['response']
                    code_list = str()
                    person_count = 0
                    friends_groups_count.append(friends_groups_count_list)
            if person_count < 25 and person_count != 0:
                code = {'code': f'return [{code_list}];',
                        'access_token': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                        'oauth': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                        'v': '5.61'}
                friends_groups_count_list = requests.post(url=URL, data=code).json()['response']
                friends_groups_count.append(friends_groups_count_list)


            # Разделение списка друзей на списки с суммарным количеством групп не более 1000
            groups_count = 0
            group_list = list()
            self.friends_groups_list = list()
            for items in friends_groups_count:
                for item in items:
                    if item['groups_count'] == None:
                        pass
                    else:
                        groups_count = groups_count + item['groups_count']
                        if groups_count > 1000:
                            self.friends_groups_list.append(group_list)
                            group_list = list()
                            groups_count = item['groups_count']
                        group_list.append(item['user_id'])
            self.friends_groups_list.append(group_list)
        return print(colored('2. Доступ к пользователю получен, получена информация о группах друзей пользователя.', 'green')), \
               print(colored(f'3. Друзья разделены на {len(self.friends_groups_list)} кластеров, из расчета не более 1000 ответов в одном запросе, делаем запрос групп...', 'green')), \
               self.friends_groups_list

    def person_friends_groups_getting(self):
        try:
            # Получение списка групп друзей пользователя
            URL = "https://api.vk.com/method/execute?"
            version = '5.61'
            groups_source_code = "API.groups.get({'user_id': person}).items"
            friends_groups_getting = list()
            code_list = str()
            person_count = 0
            for person_code in self.friends_groups_list:
                person_code = groups_source_code.__str__().replace("person", person_code.__str__())
                code_list = person_code + ', ' + code_list
                person_count += 1
                if person_count == 25:
                    code = {'code': f'return [{code_list}];',
                            'access_token': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                            'oauth': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                            'v': '5.61'}
                    friends_groups_getting_list = requests.post(url=URL, data=code).json()
                    code_list = str()
                    person_count = 0
                    friends_groups_getting.append(friends_groups_getting_list['response'])

            if person_count < 25 and person_count != 0:
                code = {'code': f'return [{code_list}];',
                        'access_token': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                        'oauth': '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1',
                        'v': '5.61'}
                friends_groups_getting_list = requests.post(url=URL, data=code).json()
                friends_groups_getting.extend(friends_groups_getting_list['response'])

            # Очистка списка от групп пользователей, к которым нет доступа
            self.friends_groups = list()
            for items in friends_groups_getting:
                if items != None:
                    for item in items:
                        self.friends_groups.append(item)
            self.friends_groups = set(self.friends_groups)
            print(colored(f'4. Получено множество из {len(self.friends_groups)} групп друзей пользователя.', 'green'))

            # Получение групп пользователя
            get_friends_groups_code = {
                "code": "return API.groups.get({'user_id': %d, 'count': 1000}).items;" % self.user_id,
                'access_token': self.access_token,
                'oauth': self.access_token,
                'v': version
            }
            response = requests.post(url=URL, data=get_friends_groups_code).json()
            self.person_groups = set(response['response'])
            print(colored(f'5. Получено множество из {len(self.person_groups)} групп пользователя.', 'green'))
            return self.person_groups, self.friends_groups
        except TypeError:
            raise SystemExit('У пользователя нет групп!')

    def groups_get_info(self):
        # Получение информации о группе (имя, id, количество участников)
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
        person = str(input(colored('Введите ID пользователя (например, 171691064 или eshmargunov): ', 'blue')))
        # person = '171691064'

        # Вычисление user_id и проверка доступнуости пользователя
        try:
            if not person.isdigit():
                user_ids = str(person)
                person = User(access_token, user_ids=user_ids)
                person.get_user_id()
                user_id = int(person.user_id)
                print(f'Вычислили user_id: {user_id}')
                person = User(access_token=access_token, user_id=user_id)
                person.user_checking()
            else:
                user_id = int(person)
                person = User(access_token=access_token, user_id=user_id)
                person.user_checking()
        except KeyError:
            raise SystemExit('Пользователя не существует!')
        except IndexError:
            raise SystemExit('Вы ввели пустое значение!')

        # Получение групп пользователя и его друзей
        groups = User(access_token=access_token, user_id=user_id, friends_groups_list=person.friends_groups_list)
        groups.person_friends_groups_getting()
        person_groups = groups.person_groups
        friends_groups = groups.friends_groups
        final_set_of_absent_groups = person_groups.difference(friends_groups)
        final_set_of_together_groups = person_groups.intersection(friends_groups)
        print(colored('6. Вычислили пересечение групп для пользователя и его друзей:', 'green'))
        print(f'-> {len(final_set_of_absent_groups)} групп, в которых нет друзей пользователя')
        print(f'-> {len(final_set_of_together_groups)} групп, в которых есть друзья пользователя')

        data_for_file_absent = list()
        if len(final_set_of_absent_groups) > 0:
            print(colored('1-й файл - Записываем JSON файл с группами пользотвателя, в которых не состоят его друзья: ', 'blue'))
            time.sleep(0.03)
            with open('JSON_fiends_absent.json', 'w') as file_absent:
                for group_id in tqdm(final_set_of_absent_groups):
                    group_absent = User(access_token=access_token, group_id=group_id, time_sleep=0.01)
                    group_absent.groups_get_info()
                    data_for_file_absent.append(group_absent.group_name)
                file_absent.write(json.dumps(data_for_file_absent, ensure_ascii=False))
        else:
            print(colored('1-й файл - Нечего записывать, у пользователя нет групп, в которых не состоят его друзья!', 'red'))

        data_for_file_together = list()
        if len(final_set_of_together_groups) > 0:
            print(colored('2-й файл - Записываем JSON файл с группами пользотвателя, в которых состоят его друзья: ', 'blue'))
            time.sleep(0.03)
            with open('JSON_fiends_together.json', 'w') as file_together:
                for group_id in tqdm(final_set_of_together_groups):
                    group_together = User(access_token=access_token, group_id=group_id, time_sleep=0.01)
                    group_together.groups_get_info()
                    data_for_file_together.append(group_together.group_name)
                file_together.write(json.dumps(data_for_file_together, ensure_ascii=False))
        else:
            print(colored('2-й файл - Нечего записывать, у пользователя нет общих, с его друзьями, групп!', 'red'))

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        raise SystemExit('Отсутсует подключение к верверу...')

    print('Программа выполнена!')
    print('Время выполнения программы - %s секунд.' % round((time.time() - start_time), 2))


main()
