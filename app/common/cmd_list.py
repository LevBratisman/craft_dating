from cities import cities

with open("bot/app/common/city_list.txt", "w") as f:
    for city in cities:
        print(city['name'])
        f.write(f"{city['name']}\n")