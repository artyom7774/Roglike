import typing
import random


class GenerateType:
    def __init__(self, width: typing.List[int], height: typing.List[int], count: int) -> None:
        self.width = width
        self.height = height

        self.count = count


class Cell:
    settings = {
        "null": {
            "image": "",
            "block": False
        },

        "floor": {
            "image": "",
            "block": True
        }
    }

    def __init__(self, name: str | int) -> None:
        self.name = "null" if name == 0 else name

        self.image = self.settings[name]["image"]
        self.empty = self.settings[name]["block"]

    def __repr__(self) -> str:
        return f"{list(self.settings.keys()).index(self.name)}"


class Map:
    def __init__(self, width: int, height: int, generators: GenerateType | typing.List[GenerateType]) -> None:
        self.width = width
        self.height = height

        self.generators = generators if isinstance(generators, list) else [generators]

        self.map = {}

    def place(self, x: int, y: int, width: int, height: int) -> bool:
        for i in range(x - 3, x + width + 7):
            for j in range(y - 3, y + height + 7):
                if f"{i}-{j}" not in self.map or self.map[f"{i}-{j}"] != 0:
                    return False

        return True

    def clear(self, ways: typing.Dict[str, int], x: int, y: int, path: typing.List[int]) -> None:
        while self.map[f"{x}-{y}"] == 0 and ways[f"{x + path[1]}-{y + path[0]}"] == 0 and ways[f"{x - path[1]}-{y - path[0]}"] == 0:
            ways[f"{x}-{y}"] = 0

            x += path[0]
            y += path[1]

    def way(self, ways: typing.Dict[str, int], x: int, y: int, path: typing.List) -> typing.List[int] | None:
        while f"{x + path[0]}-{y + path[1]}" in self.map and ways[f"{x + path[0]}-{y + path[1]}"] == 0 and self.map[f"{x + path[0]}-{y + path[1]}"] == 0:
            x += path[0]
            y += path[1]

            ways[f"{x}-{y}"] = 1

        if f"{x + path[0]}-{y + path[1]}" in self.map and ways[f"{x + path[0]}-{y + path[1]}"] == 1:
            return [x + path[0], y + path[1]]

        return None

    def generate(self) -> None:
        def get(x, y, width, height):
            return (1 if x == 0 else -1 if x == width - 1 else 0), (1 if y == 0 else -1 if y == height - 1 else 0)

        for i in range(self.width):
            for j in range(self.height):
                self.map[f"{i}-{j}"] = 0

        generator = random.choice(self.generators)

        graph = []

        for iteration in range(generator.count):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            width, height = random.randint(*generator.width), random.randint(*generator.height)

            iterations = 0

            while not self.place(x, y, width, height):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                width, height = random.randint(*generator.width), random.randint(*generator.height)

                iterations += 1

                if iterations > 100:
                    break

            else:
                for i in range(x - 3, x + width + 7):
                    for j in range(y - 3, y + height + 7):
                        self.map[f"{i}-{j}"] = 2

                for i in range(x, x + width + 1):
                    for j in range(y, y + height + 1):
                        self.map[f"{i}-{j}"] = 1

                graph.append({
                    "index": iteration,
                    "rect": [x, y, width, height],

                    "inputs": [],
                    "outputs": []
                })

        for i in range(self.width):
            for j in range(self.height):
                if self.map[f"{i}-{j}"] == 2:
                    self.map[f"{i}-{j}"] = 0

        ways = {}

        for i in range(self.width):
            for j in range(self.height):
                ways[f"{i}-{j}"] = 0

        for index, vertex in enumerate(graph):
            # UP
            x = vertex["rect"][0]
            y = random.randint(vertex["rect"][1] + 1, vertex["rect"][1] + vertex["rect"][3] - 1)

            self.way(ways, x, y, [-1, 0])

            # DOWN
            x = vertex["rect"][0] + vertex["rect"][2]
            y = random.randint(vertex["rect"][1] + 1, vertex["rect"][1] + vertex["rect"][3] - 1)

            self.way(ways, x, y, [1, 0])

            # LEFT
            x = random.randint(vertex["rect"][0] + 1, vertex["rect"][0] + vertex["rect"][2] - 1)
            y = vertex["rect"][1]

            self.way(ways, x, y, [0, -1])

            # RIGHT
            x = random.randint(vertex["rect"][0] + 1, vertex["rect"][0] + vertex["rect"][2] - 1)
            y = vertex["rect"][1] + vertex["rect"][3]

            self.way(ways, x, y, [0, 1])

        for i in range(self.width):
            for j in range(self.height):
                if (i == 0 or i == self.width - 1 or j == 0 or j == self.height - 1) and ways[f"{i}-{j}"] == 1:
                    self.clear(ways, i, j, get(i, j, self.width, self.height))

        for i in range(self.width):
            for j in range(self.height):
                self.map[f"{i}-{j}"] = max(self.map[f"{i}-{j}"], ways[f"{i}-{j}"])

    def get(self, x: int, y: int) -> Cell:
        if f"{x}-{y}" in self.map:
            return self.map[f"{x}-{y}"]

        return Cell(0)


if __name__ == "__main__":
    generateType = GenerateType([5, 17], [5, 17], 10)

    map = Map(100, 100, generateType)
    map.generate()

    # VISIABLE

    import matplotlib.pyplot as plt
    import numpy

    data = []

    for i in range(map.width):
        data.append([])

        for j in range(map.height):
            data[-1].append(1 - map.get(i, j))

    array = numpy.array(data)

    plt.imshow(array, cmap='gray', vmin=0, vmax=1)

    plt.show()
