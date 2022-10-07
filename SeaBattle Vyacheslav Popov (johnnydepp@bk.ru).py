from random import randint, choice


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Ошибка ввода: Координаты выходят за границы поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Ошибка ввода: Повторный ввод координат либо в этих координатах не может располагаться корабль"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow_xy, long, orient):
        self.bow_xy = bow_xy
        self.long = long
        self.orient = orient
        self.lives = long

    @property
    def dots(self):
        ship_dots = []
        for xy in range(self.long):
            ship_x = self.bow_xy.x
            ship_y = self.bow_xy.y

            if self.orient == 0:
                ship_x += xy

            elif self.orient == 1:
                ship_y += xy

            ship_dots.append(Dot(ship_x, ship_y))

        return ship_dots

    def shooting(self, shoot):
        return shoot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    def __str__(self):
        res = "  |"
        for sc in range(self.size):
            res += f" {size_column[sc]} |"
        amount = self.size * 4 + 3
        res += "\n" + "-" * amount
        for srt, row in enumerate(self.field):
            res += f"\n{srt + 1} | " + " | ".join(row) + " |"
        if self.hide:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shoot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Убил!")
                    return False
                else:
                    print("Ранил!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Промазал!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shoot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dx, dy = choice(find_ship_user)
        d = Dot(dx, dy)
        print(f"Координаты стрельбы Компьютера: {d.x+1} {size_column[d.y]}")
        find_ship_user.pop(find_ship_user.index((dx, dy)))
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Введите координаты стрельбы: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты через пробел! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.upper() in size_column):
                print(" Введите число и букву! ")
                continue

            x, y = int(x), int(size_column.index(y.upper()))

            return Dot(x - 1, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for hp in lens:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), hp, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("*"*105)
        print("Добро пожаловать, адмирал!")
        print('''Давайте сыграем в популярную настольную игру "Морской бой"''')
        print("*"*105)
        print("Напомню правила игры:")
        print("\t1. Перед началом игры на поле расставляются корабли в случайном порядке;")
        print("\t2. Игрок и Компьютер стреляют поочередно;")
        print("\t3. Чтобы выстрелить необходимо указать координаты в формате Строка Столбец;")
        print("\t\t\t(игра использует классическую доску, где вторая координата эта буква)")
        print("\t4. Если Игрок попадает в корабль (ранил), то ему предоставляется право стрелять еще раз;")
        print("\t5. Раненные и подбитые корабли отмечаются символом (X);")
        print("\t6. Если игрок промахивается, то ход переходит к противнику;")
        print("\t7. Места промахов отмечаются символом (Т);")
        print("\t8. Побеждает тот игрок, который первым потопит все корабли противника.")
        print("*"*105)
        print()
        print("Игра ведется на поле размером 6*6")
        print("У Игрока и Компьютера следующие корабли и их количество:")
        print("\t1. Трехпалубный (■■■) - 1 шт;")
        print("\t2. Двухпалубный (■■) - 2 шт;")
        print("\t3. Однопалубный (■) - 4 шт;")
        print()

    @staticmethod
    def merge_boards(first, second):
        first_lines = first.split("\n")
        second_lines = second.split("\n")

        result = ""
        for fl in range(len(first_lines)):
            result_line = f"     {first_lines[fl]}        ||        {second_lines[fl]} \n"
            result += result_line

        return result

    def loop(self):
        num = 0
        while True:
            print("*" * 78)
            user_board = "        Доска Игрока:      \n" + str(self.us.board)
            ai_board = "      Доска Компьютера:\n" + str(self.ai.board)
            print(Game.merge_boards(user_board, ai_board))

            if num % 2 == 0:
                print("*" * 78)
                print("Ход Игрока!")
                repeat = self.us.move()
            else:
                print("*" * 78)
                print("Ход Компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print(Game.merge_boards(user_board, ai_board))
                print("Поздравляю, адмирал, Вы выиграли!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print(Game.merge_boards(user_board, ai_board))
                print("Мне жаль, но победил Компьютер! Надеюсь в следующий раз повезет Вам")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


size_column = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "К"]
find_ship_user = []
for i in range(6):
    for j in range(6):
        find_ship_user.append((i, j))


g = Game()
g.start()
print("Автор: Вячеслав Попов (johnnydepp@bk.ru, группа PDEV-16).")
