import random

def main():
    # Faqat GET sorovlari yuboriladigan endpointlar:
    endpoints = [
        # List endpointlar (id parametr kerak emas)
        "GET http://localhost:8000/regions",
        "GET http://localhost:8000/districts",
        "GET http://localhost:8000/schools",
        "GET http://localhost:8000/librarians",
        "GET http://localhost:8000/formulars",
        "GET http://localhost:8000/booktransactions",
        # Detail endpointlar:
        ("GET http://localhost:8000/regions/{region_id}", lambda: random.randint(1, 12)),  # 12 ta region
        ("GET http://localhost:8000/districts/{district_id}", lambda: random.randint(1, 1500)),  # 1500 ta district
        ("GET http://localhost:8000/schools/{school_id}", lambda: random.randint(1, 15000)),  # 15000 ta school
        ("GET http://localhost:8000/librarians/{librarian_id}", lambda: random.randint(1, 15000)),  # 15000 ta librarian
        ("GET http://localhost:8000/formulars/{formular_id}", lambda: random.randint(1, 450000)),  # 450000 ta formular
        ("GET http://localhost:8000/booktransactions/{transaction_id}", lambda: random.randint(1, 4950000)),  # 4,950,000 ta transaction
        # Nested endpointlar:
        ("GET http://localhost:8000/regions/{region_id}/districts", lambda: random.randint(1, 12)),  # Har bir region uchun districtlar
        ("GET http://localhost:8000/districts/{district_id}/schools", lambda: random.randint(1, 1500)),  # Har bir district uchun maktablar
        ("GET http://localhost:8000/schools/{school_id}/librarians", lambda: random.randint(1, 15000)),  # Har bir maktab uchun kutubxonachilar
        ("GET http://localhost:8000/librarians/{librarian_id}/formulars", lambda: random.randint(1, 15000)),  # Har bir kutubxonachi uchun formularlar
        ("GET http://localhost:8000/schools/{school_id}/formulars", lambda: random.randint(1, 15000)),  # Har bir maktab uchun formularlar
        ("GET http://localhost:8000/formulars/{formular_id}/transactions", lambda: random.randint(1, 450000)),  # Har bir formular uchun transaksiyalar
    ]
    
    with open("urls.txt", "w") as f:
        for _ in range(100000):  # 100,000 ta URL yaratish
            ep = random.choice(endpoints)
            if isinstance(ep, tuple):
                template, value_func = ep
                value = value_func()
                # Aniqlash: qaysi placeholder ishlatilganini tekshiramiz
                if "{region_id}" in template:
                    full_url = template.format(region_id=value)
                elif "{district_id}" in template:
                    full_url = template.format(district_id=value)
                elif "{school_id}" in template:
                    full_url = template.format(school_id=value)
                elif "{librarian_id}" in template:
                    full_url = template.format(librarian_id=value)
                elif "{formular_id}" in template:
                    full_url = template.format(formular_id=value)
                elif "{transaction_id}" in template:
                    full_url = template.format(transaction_id=value)
                else:
                    full_url = template
            else:
                full_url = ep
            f.write(full_url + "\n")

if __name__ == "__main__":
    main()
