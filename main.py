import json
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any


# Свои исключения
class ShelterError(Exception):
    pass


class BadAgeError(ShelterError):
    pass


class NotFoundError(ShelterError):
    pass


# 11 классов предметной области
class Clinic:
    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address

    def to_dict(self) -> dict:
        return {"name": self.name, "address": self.address}


class Vaccination:
    def __init__(self, name: str, date: str) -> None:
        self.name = name
        self.date = date

    def to_dict(self) -> dict:
        return {"name": self.name, "date": self.date}


class VetRecord:
    def __init__(self, diagnosis: str, date: str, clinic: Clinic) -> None:
        self.diagnosis = diagnosis
        self.date = date
        self.clinic = clinic

    def to_dict(self) -> dict:
        return {
            "diagnosis": self.diagnosis,
            "date": self.date,
            "clinic": self.clinic.to_dict()
        }


class Food:
    def __init__(self, brand: str, kind: str, weight: float) -> None:
        self.brand = brand
        self.kind = kind
        self.weight = weight

    def to_dict(self) -> dict:
        return {"brand": self.brand, "kind": self.kind, "weight": self.weight}


class Toy:
    def __init__(self, title: str, material: str) -> None:
        self.title = title
        self.material = material

    def to_dict(self) -> dict:
        return {"title": self.title, "material": self.material}


class Owner:
    def __init__(self, fio: str, phone: str, address: str) -> None:
        self.fio = fio
        self.phone = phone
        self.address = address

    def to_dict(self) -> dict:
        return {"fio": self.fio, "phone": self.phone, "address": self.address}


class Animal:
    def __init__(self, name: str, age: int, breed: str) -> None:
        if age < 0:
            raise BadAgeError("Возраст не может быть отрицательным!")
        self.name = name
        self.age = age
        self.breed = breed
        self.toys: List[Toy] = []
        self.records: List[VetRecord] = []
        self.owner: Optional[Owner] = None

    def add_toy(self, toy: Toy) -> None:
        self.toys.append(toy)

    def set_owner(self, owner: Owner) -> None:
        self.owner = owner

    def to_dict(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "name": self.name,
            "age": self.age,
            "breed": self.breed,
            "toys": [t.to_dict() for t in self.toys],
            "owner": self.owner.to_dict() if self.owner else None
        }


class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str, guard: bool) -> None:
        super().__init__(name, age, breed)
        self.guard = guard

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["guard"] = self.guard
        return d


class Cat(Animal):
    def __init__(self, name: str, age: int, breed: str, mouser: bool) -> None:
        super().__init__(name, age, breed)
        self.mouser = mouser

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["mouser"] = self.mouser
        return d


class Bird(Animal):
    def __init__(self, name: str, age: int, breed: str, singing: bool) -> None:
        super().__init__(name, age, breed)
        self.singing = singing

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["singing"] = self.singing
        return d


class Shelter:
    def __init__(self, title: str) -> None:
        self.title = title
        self.animals: List[Animal] = []

    # CRUD
    def add(self, animal: Animal) -> None:
        self.animals.append(animal)

    def get_all(self) -> List[Animal]:
        return self.animals

    def find(self, name: str) -> Animal:
        for a in self.animals:
            if a.name.lower() == name.lower():
                return a
        raise NotFoundError(f"Питомец '{name}' не найден")

    def update_age(self, name: str, new_age: int) -> None:
        if new_age < 0:
            raise BadAgeError("Возраст не может быть меньше 0")
        item = self.find(name)
        item.age = new_age

    def remove(self, name: str) -> None:
        item = self.find(name)
        self.animals.remove(item)

    # JSON сохранение/загрузка
    def save_json(self, filename: str) -> None:
        data = {
            "title": self.title,
            "animals": [a.to_dict() for a in self.animals]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_json(self, filename: str) -> None:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.title = data.get("title", "Приют")
            self.animals = []
            for item in data.get("animals", []):
                cls = item.get("class")
                name = item.get("name")
                age = item.get("age")
                breed = item.get("breed")

                if cls == "Dog":
                    obj = Dog(name, age, breed, item.get("guard", False))
                elif cls == "Cat":
                    obj = Cat(name, age, breed, item.get("mouser", True))
                elif cls == "Bird":
                    obj = Bird(name, age, breed, item.get("singing", True))
                else:
                    obj = Animal(name, age, breed)

                o_data = item.get("owner")
                if o_data:
                    obj.set_owner(Owner(o_data["fio"], o_data["phone"], o_data["address"]))

                self.animals.append(obj)

    # XML сохранение/загрузка
    def save_xml(self, filename: str) -> None:
        root = ET.Element("Shelter", title=self.title)
        animals_node = ET.SubElement(root, "Animals")
        for a in self.animals:
            node = ET.SubElement(animals_node, "Animal", type=a.__class__.__name__)
            ET.SubElement(node, "Name").text = a.name
            ET.SubElement(node, "Age").text = str(a.age)
            ET.SubElement(node, "Breed").text = a.breed
            if isinstance(a, Dog):
                ET.SubElement(node, "Guard").text = str(a.guard)
            elif isinstance(a, Cat):
                ET.SubElement(node, "Mouser").text = str(a.mouser)
            elif isinstance(a, Bird):
                ET.SubElement(node, "Singing").text = str(a.singing)

        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    def load_xml(self, filename: str) -> None:
        tree = ET.parse(filename)
        root = tree.getroot()
        self.title = root.get("title", "Приют")
        self.animals = []

        animals_node = root.find("Animals")
        if animals_node is not None:
            for node in animals_node.findall("Animal"):
                t = node.get("type")
                name = node.find("Name").text
                age = int(node.find("Age").text)
                breed = node.find("Breed").text

                if t == "Dog":
                    obj = Dog(name, age, breed, node.find("Guard").text == "True")
                elif t == "Cat":
                    obj = Cat(name, age, breed, node.find("Mouser").text == "True")
                elif t == "Bird":
                    obj = Bird(name, age, breed, node.find("Singing").text == "True")
                else:
                    obj = Animal(name, age, breed)
                self.animals.append(obj)


# Проверка работы
if __name__ == "__main__":
    s = Shelter("Уютный дом")

    # тестовые данные
    d = Dog("Шарик", 3, "Овчарка", True)
    c = Cat("Барсик", 2, "Британская", True)
    b = Bird("Чика", 1, "Канарейка", True)

    s.add(d)
    s.add(c)
    s.add(b)

    print("Список животных:")
    for animal in s.get_all():
        print(f"- {animal.name}, возраст: {animal.age}")

    # проверка ошибок
    try:
        s.find("Бобби")
    except NotFoundError as e:
        print("Ошибка поймана:", e)

    try:
        s.update_age("Шарик", -2)
    except BadAgeError as e:
        print("Ошибка поймана:", e)

    # сохраняем в файлы
    s.save_json("out.json")
    s.save_xml("out.xml")
    print("Всё сохранилось!")