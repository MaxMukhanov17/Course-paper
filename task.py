import requests

from pprint import pprint

import os

import json

import yadisk

with open('token_vk.txt', 'r') as file_object:
    token = file_object.read().strip()

class VKUser:
    URL = "https://api.vk.com/method/"
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
            }

    def get_largest(self, size_dict):
        if size_dict['width'] >= size_dict['height']:
            return size_dict['width']
        else:
            return size_dict['height']

    def download_photo(self, photos):
        # for root, dirs, files in os.walk("images"):  
        #     for file in files:
            
        for photo in photos:
            likes = photo['likes']['count']
            sizes = photo['sizes']
            url_max_size = max(sizes, key=self.get_largest)['url']
            max_size = max(sizes, key=self.get_largest)['type']
            response = requests.get(url_max_size)
            path = 'images/'
            filename = path + str(likes) + '.jpg'
            out = open(filename, 'wb')
            out.write(response.content)
            out.close()
    
    def photos_get(self):
        URL = "https://api.vk.com/method/photos.get"
        params_photos_get = {'owner_id': '388635325',
                'album_id': 'profile', 
                'photo_sizes': '1',
                'extended': '1',
                }
        response = requests.get(url=URL, params={**self.params, **params_photos_get})
        photos = response.json()['response']['items']
        self.download_photo(photos)
        

if __name__ == '__main__': 
    vk_client = VKUser(token, '5.131')
    vk_client.photos_get()


class YaUploader:
    def __init__(self, token: str):
        self.token = token
    
    def upload(self):
        y = yadisk.YaDisk(token=token)
        for root, dirs, files in os.walk("images"):  
            for photo_disk in files:
                photo = 'images/' + photo_disk
                path = '/Курсовая. VK photos/' + photo_disk
                y.upload(photo, path)

if __name__ == '__main__':
    token = ''
    uploader = YaUploader(token)
    uploader.upload()


