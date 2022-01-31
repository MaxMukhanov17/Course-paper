import requests
import json
import time
from progress.bar import IncrementalBar

with open('token_vk.txt', 'r') as file_object:
    token = file_object.read().strip()


class VKUser:
    URL = "https://api.vk.com/method/"

    def __init__(self, token, version):
        self.params = {'access_token': token, 'v': version}
        self.dict_url_filename = {}

    def get_largest(self, size_dict):
        if size_dict['width'] >= size_dict['height']:
            return size_dict['width']
        else:
            return size_dict['height']

    def download_photo(self, photos):
        list_like = []
        data_list = []
        for photo in photos:
            sizes = photo['sizes']
            url_max_size = max(sizes, key=self.get_largest)['url']
            max_size = max(sizes, key=self.get_largest)['type']
            date = photo['date']
            like = photo['likes']['count']
            if like in list_like:
                file_name_date = str(date) + '.jpg'
                self.dict_url_filename[file_name_date] = url_max_size
                data_dict = {'file_name': file_name_date,
                             'size': max_size
                             }
                data_list.append(data_dict)
            else:
                file_name_like = str(like) + '.jpg'
                self.dict_url_filename[file_name_like] = url_max_size
                list_like.append(like)
                data_dict = {
                    'file_name': file_name_like,
                    'size': max_size
                    }
                data_list.append(data_dict)
        with open('data_file.json', 'w') as write_file:
            json.dump(data_list, write_file)

    def photos_get(self, user_name_id):
        URL = "https://api.vk.com/method/photos.get"
        params_photos_get = {'owner_id': user_name_id,
                             'album_id': 'profile',
                             'photo_sizes': '1',
                             'extended': '1',
                             }
        response = requests.get(
            url=URL,
            params={
                **self.params,
                **params_photos_get
                }
        )
        photos = response.json()['response']['items']
        self.download_photo(photos)

    def user_search(self):
        type_command = int(input(
            'Введите команду:\n1 - если хотите ввести имя пользователя.'
            '\n2 - если хотите ввести id пользователя.'
            '\n3 - если хотите ввести username(короткое имя профиля)\n')
        )
        if type_command == 1:
            url = "https://api.vk.com/method/users.search"
            user_name = input('Введите имя и фамилию пользователя: ')
            user_birth_day = int(input('Введите день рождения пользователя: '))
            user_birth_month = int(input(
                'Введите месяц рождения пользователя: ')
            )
            user_birth_year = int(input('Введите год рождения пользователя: '))
            user_city = input(
                'Введите город в котором проживает пользователь: '
            )
            params_user_search = {'q': user_name,
                                  'count': '10',
                                  'fields': 'city, screen_name',
                                  'has_photo': '1',
                                  'birth_day': user_birth_day,
                                  'birth_month': user_birth_month,
                                  'birth_year': user_birth_year
                                  }
            response = requests.get(
                url=url,
                params={
                    **self.params,
                    **params_user_search
                    }
            )
            users_info = response.json()['response']['items']
            for user_info in users_info:
                if (user_info['city']['title'] == user_city and
                   'city' in user_info):
                    user_name_id = user_info['id']
                    break
                else:
                    user_id = int(input('Введите id пользователя: '))
                    self.photos_get(user_id)
            self.photos_get(user_name_id)
        elif type_command == 2:
            user_id = input('Введите id пользователя: ')
            self.photos_get(user_id)
        elif type_command == 3:
            url_username = "https://api.vk.com/method/users.get"
            username = input('Введите username(короткое имя профиля): ')
            params_user_search = {'user_ids': username,
                                  'fields': 'id',
                                  }
            response = requests.get(
                url=url_username,
                params={
                    **self.params,
                    **params_user_search
                    }
            )
            user_info = response.json()['response']
            for info in user_info:
                user_id_username = info['id']
                self.photos_get(user_id_username)


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self):
        create_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params_get = {'path': '/'}
        response = requests.get(
            url=create_url,
            headers=headers,
            params=params_get
        )
        info_folders = response.json()['_embedded']['items']
        for info_folder in info_folders:
            name_folder = info_folder['name']
            if name_folder == 'VK Photos':
                continue
            else:
                params = {'path': '/VK Photos'}
                requests.put(url=create_url, params=params, headers=headers)

    def get_upload_link(self, destination_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": destination_path, "overwrite": "true"}
        response = requests.get(url=upload_url, headers=headers, params=params)
        return response.json()

    def upload(self, file_path, destination_path):
        href = self.get_upload_link(
            destination_path=destination_path
        ).get("href", "")
        response = requests.put(href, data=requests.get(file_path))
        response.raise_for_status()


if __name__ == '__main__':
    vk_client = VKUser(token, '5.131')
    vk_client.user_search()
    token = ''
    uploader = YaUploader(token)
    bar = IncrementalBar(
        'ChargingBar',
        max=len(vk_client.dict_url_filename.keys())
    )
    for key, value in vk_client.dict_url_filename.items():
        bar.next()
        uploader.create_folder()
        uploader.upload(f'{value}', f'VK Photos/{key}')
        time.sleep(1)
    bar.finish()
