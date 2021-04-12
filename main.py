from random import randint


# Исключения
class BoardOutException(Exception):
    def __str__(self):
        return "Вы не можете выстрелить в клетку за пределами поля!"

class BoardException(Exception):
    pass

class BoardUsedException(Exception):
    def __str__(self):
        return "Не стреляйте в ту же клетку!"


# Класс точек в игре
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return self.x, self.y


# Класс кораблей
class Ship:
    def __init__(self, length, start_coord, direction):
        self.length = length
        self.start_coord = start_coord
        self.direction = direction
        self.health = length

    def get_data(self):
        data = {"length": self.length, "start_coord": self.start_coord,
                "direction": self.direction, "health": self.health}
        return data

    def dots(self):
        cords = []
        if self.direction == "horizontal":
            for i in range(self.length):
                arg = int(self.start_coord[0]), int(self.start_coord[1]) + i
                cords.append(arg)
        else:
            for i in range(self.length):
                arg = int(self.start_coord[0]) + i, int(self.start_coord[1])
                cords.append(arg)
        return cords

    @staticmethod
    def search_ship_by_cord(coord, ships, desc):
        ship_cords = []
        symbols = []
        for ship in ships:
            ship_cords = ship.dots()
            if coord in ship_cords:
                break
        for cord in ship_cords:
            y, x = cord[0] - 1, cord[1] - 1
            if desc[y][x] == "■":
                symbols.append(desc[y][x])
        length = len(ship_cords)
        health = len(symbols)
        (y1, x1), (y2, x2) = ship_cords[0], ship_cords[-1]
        if abs(y2 - y1) == 0:
            direction = "horizontal"
        else:
            direction = "vertical"
        ship = Ship(length, (y1, x1), direction)
        ship.__setattr__("health", health)
        return ship

# Класс игровое поле
class Board:
    def __init__(self, hid):
        self.desc = [[""] * 6 for _ in range(6)]
        self.ships = []
        self.unbroken_ships = []
        self.hid = hid

    def get_data(self):
        data = {"desc": self.desc, "ships": self.ships, "unbroken_ships": self.unbroken_ships, "hid": self.hid}
        return data

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def add_ship(self, length, start_coord, direction):
        try:
            x_c, y_c = start_coord
            if direction == "horizontal":
                if any([
                    int(x_c) < 1,
                    int(x_c) > 6,
                    int(y_c) < 1,
                    int(y_c) + length - 1 > 6
                ]):
                    raise BoardOutException()
            else:
                if any([
                    int(x_c) < 1,
                    int(x_c) + length - 1 > 6,
                    int(y_c) < 1,
                    int(y_c) > 6
                ]):
                    raise BoardOutException()

            ship = Ship(length, start_coord, direction)
            ship_cords = ship.dots()
            check_arr = self.check_border(ship_cords)

            if "×" in check_arr or "■" in check_arr:
                raise BoardException()
        except BoardOutException:
            return False
        except BoardException:
            return False
        else:
            for cord in ship_cords:
                x, y = cord
                self.desc[y - 1][x - 1] = "■"
            self.ships.append(ship)
            self.unbroken_ships.append(ship)
            return True

    def contour(self, ship):
        ship_cords = ship.dots()
        self.check_border(ship_cords, contour=True)

    def check_border(self, ship_cords, contour=False):
        check_arr, symbol = [], "•"
        near = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for cord in ship_cords:
            x, y = cord
            for dx, dy in near:
                cur = Dot(x + dx, y + dy)
                if not (self.out(cur)):
                    if self.desc[y + dy - 1][x + dx - 1] == "" and contour:
                        self.desc[cur.y - 1][cur.x - 1] = symbol
                    check_arr.append(self.desc[cur.y - 1][cur.x - 1])
        return check_arr

    @staticmethod
    def out(dot):
        x, y = dot.__repr__()
        if any([
            int(x) < 1,
            int(x) > 6,
            int(y) < 1,
            int(y) > 6
        ]):
            return True
        return False

    def shot(self, target_cords):
        try:
            x, y = target_cords
            if self.out(Dot(x, y)):
                raise BoardOutException()
            elif self.desc[y - 1][x - 1] == "•" or self.desc[y - 1][x - 1] == "X":
                raise BoardUsedException()
        except BoardUsedException as e:
            if self.get_data()["hid"]:
                print(e)
            return True
        except BoardOutException as e:
            print(e)
            return True
        else:
            if self.desc[y - 1][x - 1] == "■":
                self.desc[y - 1][x - 1] = "X"
                ship = Ship.search_ship_by_cord(target_cords, self.ships, self.desc)
                health = ship.get_data()["health"]
                if health == 0:
                    data = ship.get_data()["start_coord"]
                    unb_ships = self.get_data()["unbroken_ships"]
                    arr = []
                    for item in unb_ships:
                        cord = item.get_data()["start_coord"]
                        if not (Dot(*cord) == Dot(*data)):
                            arr.append(item)
                    self.__setattr__("unbroken_ships", arr)
                    return ship
                return "Hit"
            else:
                self.desc[y - 1][x - 1] = "•"
                return False


class Player:
    def __init__(self, own_desk, enemy_desc):
        self.own_desc = own_desk
        self.enemy_desc = enemy_desc

    def ask(self):
        return NotImplementedError()

    def move(self, board):
        x, y = self.ask()
        return board.shot((int(x), int(y)))


class User(Player):
    def ask(self):
        while True:
            string = None
            while not string:
                string = input("Ваш ход: ")

            cords = string.split()

            if len(cords) != 2:
                print("Введите 2 координаты!")
                continue
            x_c, y_c = cords
            if not (x_c.isdigit() and y_c.isdigit()):
                print("Нужны только числа!")
                continue
            elif not (0 < int(x_c) <= 6 and 0 < int(y_c) <= 6):
                print("Введите 2 точные координаты!")
                continue
            break
        return cords


class AI(Player):
    def ask(self):
        x, y = randint(1, 7), randint(1, 7)
        while not (0 < x <= 6 and 0 < y <= 6):
            x, y = randint(1, 7), randint(1, 7)
        return x, y

# Класс игры и генерации досок
class Game:
    def __init__(self, user, user_desc, AI, AI_desc):
        self.user = user
        self.user_desc = user_desc
        self.AI = AI
        self.AI_desc = AI_desc

    @staticmethod
    def greet():
        print("Приветствуем в игре «Морской бой»!\n\n"
              "Как играть?\n"
              "Задача игрока - уничтожить все вражеские корабли. Всего кораблей 7: 1 корабль на 3 клетки, 2 корабля на 2 клетки, 4 корабля на одну клетку.\n"
              "Для того, чтобы сделать ход, игрок вводит 2 координаты конечной клетки.\n")

    def print_boards(self):
        print("\nВаше поле:" + "\t" * 7 + "Поле соперника:")
        print(("\u250F" + ("\u2501" * 3 + "\u2533") * 6 + "\u2501" * 3 + "\u2513" + "\t" * 2) * 2)
        print("\u2503   ", end="")
        [print(f"\u2503 {i + 1} ", end="") for i in range(6)]
        print("\u2503" + "\t" * 2, end="")
        print("\u2503   ", end="")
        [print(f"\u2503 {i + 1} ", end="") for i in range(6)]
        print("\u2503")
        print(("\u2523" + ("\u2501" * 3 + "\u254B") * 6 + "\u2501" * 3 + "\u252B" + "\t" * 2) * 2)
        for row in range(6):
            print(f"\u2503 {row + 1} \u2503", end="")
            for column in range(6):
                if not self.user_desc.hid:
                    print(f" {self.user_desc.get_data()['desc'][row][column] or ' '} \u2503", end="")
                else:
                    if self.user_desc.get_data()["desc"][row][column] == "■":
                        print(f"   \u2503", end="")
                    else:
                        print(f" {self.user_desc.get_data()['desc'][row][column] or ' '} \u2503", end="")
            print("\t" * 2 + f"\u2503 {row + 1} \u2503", end="")
            for column in range(6):
                if not self.AI_desc.hid:
                    print(f" {self.AI_desc.get_data()['desc'][row][column] or ' '} \u2503", end="")
                else:
                    if self.AI_desc.get_data()["desc"][row][column] == "■":
                        print(f"   \u2503", end="")
                    else:
                        print(f" {self.AI_desc.get_data()['desc'][row][column] or ' '} \u2503", end="")
            print()
            if row == 5:
                print(("\u2517" + ("\u2501" * 3 + "\u253B") * 6 + "\u2501" * 3 + "\u251B" + "\t" * 2) * 2)
            else:
                print(("\u2523" + ("\u2501" * 3 + "\u254B") * 6 + "\u2501" * 3 + "\u252B" + "\t" * 2) * 2)
        print()

    @staticmethod
    def random_board(desc):
        count = 0
        s_len = 3
        s_count = 1
        ships = []
        while True:
            direct = Board(["horizontal", "vertical"])
            if direct == "horizontal":
                start_cords = randint(1, 7), randint(1, 7 - s_len)
            else:
                start_cords = randint(1, 7 - s_len), randint(1, 7)
            ship = desc.add_ship(s_len, start_cords, direct)
            if ship:
                ships.append(ship)
            if len(list(filter(lambda x: x == s_len,
                               list(map(lambda x: x.get_data()["length"],
                                        desc.get_data()["ships"]))))) == s_count:
                if s_len == 3:
                    s_len = s_count = 2
                elif s_len == 2:
                    s_len, s_count, ships = 1, 4, []
                else:
                    break
            count += 1
            if count >= 1000:
                arg = [[""] * 6 for _ in range(6)]
                desc.__setattr__("desc", arg)
                desc.__setattr__("ships", [])
                desc.__setattr__("unbroken_ships", [])
                count, s_len, s_count, ships = 0, 3, 1, []

    def loop(self):
        self.random_board(self.user_desc)
        self.random_board(self.AI_desc)
        while True:
            self.print_boards()

            reply = True
            while reply:
                reply = self.user.move(self.AI_desc)
                if reply == "Hit":
                    print("Попадание!")
                    print("Вы ходите еще раз!")
                    self.print_boards()
                elif isinstance(reply, Ship):
                    self.AI_desc.contour(reply)
                    if len(self.AI_desc.get_data()["unbroken_ships"]) == 0:
                        self.print_boards()
                        print("Вы победили!")
                        return
                    print("Корабль подбит!")
                    print("Вы ходите еще раз!")
                    self.print_boards()
                elif not reply:
                    print("Мимо!")
            reply = True
            while reply:
                reply = self.AI.move(self.user_desc)
                if isinstance(reply, Ship):
                    self.user_desc.contour(reply)
                    if len(self.user_desc.get_data()["unbroken_ships"]) == 0:
                        self.print_boards()
                        print("Вы проиграли!")
                        return
            print()

    def start(self):
        self.greet()
        self.loop()


u_desc = Board(False)
b_desc = Board(True)

AI = AI(b_desc.get_data()["desc"], u_desc.get_data()["desc"])
User = User(u_desc.get_data()["desc"], b_desc.get_data()["desc"])

game = Game(User, u_desc, AI, b_desc)
game.start()