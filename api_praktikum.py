# import requests

# url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
# headers = {'Authorization': f'OAuth {<ваш токен>}'}
# payload = {'from_date': <временная метка в формате Unix time>}.
# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
# homework_statuses = requests.get(url, headers=headers, params=payload)
# Печатаем ответ API в формате JSON
# print(homework_statuses.text)
# print(homework_statuses.json())
