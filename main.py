import random

# определяем константы, избегаем грамматических ошибок
game_state = 'game_state'
battlefield = 'opponent_state'
available_cells = 'available_cells'
coordinates_dict = 'coordinates_dict'
health_points = 'health_points'
ship_coordinates = 'ship_coordinates'
ships_count = 'ships_count'
end_of_game_status = 'end_of_game_status'
required_ships = 'required_ships'
selected_coordinates = 'selected_coordinates'
attack_cells = 'attack_cells'
letters = 'letters'
player1 = 'player1'
player2 = 'player2'
game = 'game'
ships = 'ships'
is_AI = 'is_AI'

# состояние приложения
state = {
    # <неизменяемые параметры>
    letters: list('АБВГДЕЖЗИК'),
    # список кораблей для расстановки
    required_ships: [4, 3, 3, 2, 2, 2, 1, 1, 1, 1],

    # <параметры, значения которых в течение игры будут изменяться>
    player1: {
        # собственная карта с расставленными кораблями
        game_state: None,
        # карта с состоянием атак совершенных противником
        battlefield: [],
        # список кораблей.
        # корабль - словарь, который включает в себя здоровье и координаты определенного корабля
        ships: [],
        # количество оставшихся(не потопленных) кораблей
        ships_count: 10,
        # доступные ячейки для расстановки
        available_cells: [],
        # является ли игрок компьютером, если хотите играть с компьютером измените значение на True
        # доступно только для одного из игроков! либо player1 либо player2
        is_AI: True,
    },
    player2: {
        game_state: None,
        battlefield: [],
        ships: [],
        ships_count: 10,
        available_cells: [],
        is_AI: False,
    },
    game: {
        # словарь, где ключ – координата (например, 1А), а значение – кортеж
        # из индексов списка списков, соответствующий этой координате.
        coordinates_dict: {},
        # ячейки которые AI уже посещал
        selected_coordinates: [],
        # параметр для AI ячейки, которые следуют атаковать
        attack_cells: [],
    },
}


# функция возвращает внутренний объект для хранения состояния поля каждого игрока
# вида: список списков размером 10*10 нулей.
def create_player_game_state():
    initial_state = []
    for i in range(10):
        row = []
        for j in range(10):
            row.append(0)
        initial_state.append(row)

    return initial_state


# функция возвращает словарь, где ключ – координата (например, 1А), а значение – кортеж
# из индексов списка списков, соответствующий этой координате.
def create_coordinates_dict():
    dictionary = {}
    for i in range(10):
        for j in range(10):
            coordinate = str(i + 1) + state[letters][j]
            dictionary[coordinate] = (i, j)

    return dictionary


# Функция, выбирающая случайную ячейку на поле – ячейка,
# с которой начинается попытка разместить корабль.
def select_cell(player):
    return random.choice(state[player][available_cells])


# Функция, случайно выбирающая направление, в котором
# будем пытаться поставить корабль, для данной ячейки.
# 1 – вверх, 2 – вправо, 3- вниз, 4 - влево
# параметр available_directions указывает на доступные направления
# для каждого случая находим пересечение с доступными направлениями, например {2, 3} & directions
def choose_direction(cell, available_directions):
    directions = set(available_directions)
    if cell == (0, 0):
        return random.choice(list({2, 3} & directions))
    elif cell == (0, 9):
        return random.choice(list({3, 4} & directions))
    elif cell == (9, 0):
        return random.choice(list({1, 2} & directions))
    elif cell == (9, 9):
        return random.choice(list({1, 4} & directions))
    else:
        return random.choice(list({1, 2, 3, 4} & directions))


# Функция рассчитывает соседние ячейки для ячейки cell
# и возвращает список этих ячеек.
def calculate_adjacent_cells(cell):
    x = cell[1]
    y = cell[0]

    return [(y - 1, x - 1), (y, x - 1), (y + 1, x - 1),
            (y - 1, x), (y + 1, x),
            (y - 1, x + 1), (y, x + 1), (y + 1, x + 1)]


# Функция, реализующая случайную расстановку корабля на поле
def build_ship(ship_len, player):
    forbidden_cells_ships = []
    forbidden_cells = []
    selected_cell = select_cell(player)
    forbidden_cells_ships.append(selected_cell)
    forbidden_cells = forbidden_cells + calculate_adjacent_cells(selected_cell)
    # доступные направления для расстановки
    available_directions = [1, 2, 3, 4]
    # количество расставленных частей корабля
    counter = 1
    # флаг выхода из while
    ship_is_not_built = True

    # повторять пока текущий корабль не установлен на карту
    while ship_is_not_built:
        # пробуем все 4 направления,
        # ограничения на направления накладывает фунцкия choose_direction()
        for i in range(4):
            direction = choose_direction(selected_cell, available_directions)
            # если корабль расставлен не полностью
            if counter != ship_len:
                # для выбранного направления пытаемся расставить все части корабля
                for j in range(ship_len - 1):
                    x = selected_cell[1]
                    y = selected_cell[0]

                    if direction == 1:
                        next_cell = (y - 1, x)
                    elif direction == 2:
                        next_cell = (y, x + 1)
                    elif direction == 3:
                        next_cell = (y + 1, x)
                    else:
                        next_cell = (y, x - 1)

                    if next_cell in state[player][available_cells]:
                        # следующая точка нашлась
                        forbidden_cells_ships.append(next_cell)
                        forbidden_cells = forbidden_cells + calculate_adjacent_cells(next_cell)
                        selected_cell = next_cell
                        counter += 1
                        if counter == ship_len:
                            # если расставлены все части корабля
                            for cell in forbidden_cells_ships:
                                state[player][game_state][cell[0]][cell[1]] = ship_len
                            # вычитаем занятые ячейки из списка доступных с помощью действий
                            # над множествами
                            state[player][available_cells] = list(
                                set(state[player][available_cells]) - set(forbidden_cells) - set(forbidden_cells_ships))
                            # переключаем флаг выхода из бесконечного цикла
                            ship_is_not_built = False
                            # добавляем корабль в состояние игрока
                            state[player][ships].append({
                                # очки прочности корабля
                                health_points: ship_len,
                                # координаты корабля
                                ship_coordinates: forbidden_cells_ships
                            })
                            break
                    else:
                        # попробовали все 4 направления и не нашли нужное
                        # => нужно генерировать новую точку
                        if i == 3:
                            forbidden_cells_ships = []
                            forbidden_cells = []
                            selected_cell = select_cell(player)
                            forbidden_cells_ships.append(selected_cell)
                            forbidden_cells = forbidden_cells + calculate_adjacent_cells(selected_cell)
                            available_directions = [1, 2, 3, 4]
                            counter = 1
                        else:
                            # одно из направлений не подошло
                            # зануляем переменные и выбираем новое направление
                            forbidden_cells_ships = [selected_cell]
                            forbidden_cells = forbidden_cells + calculate_adjacent_cells(selected_cell)
                            counter = 1
                            # удаляем направление из списка доступных
                            available_directions.remove(direction)
                            break
            else:
                # случай для однопалубных кораблей
                for cell in forbidden_cells_ships:
                    state[player][game_state][cell[0]][cell[1]] = ship_len
                state[player][available_cells] = list(
                    set(state[player][available_cells]) - set(forbidden_cells) - set(forbidden_cells_ships))
                ship_is_not_built = False
                state[player][ships].append({
                    health_points: ship_len,
                    ship_coordinates: forbidden_cells_ships
                })
                break


#  функция генерирует и возвращает список доступных ячеек в начале игры
def generate_available_cells():
    cells = []
    for i in range(10):
        for j in range(10):
            cells.append((i, j))

    return cells


# функция генерирует подозрительные ячейки и возвращает их список
def calculate_attack_cells(cell):
    x = cell[0]
    y = cell[1]
    target_cells = []

    _x = x - 1
    x_ = x + 1
    _y = y - 1
    y_ = y + 1

    if 9 >= _x >= 0:
        target_cells.append((_x, y))
    if 9 >= x_ >= 0:
        target_cells.append((x_, y))
    if 9 >= _y >= 0:
        target_cells.append((x, _y))
    if 9 >= y_ >= 0:
        target_cells.append((x, y_))

    return target_cells


# Функция, реализующая изменение состояния ячейки после хода.
def move(player):
    print('$$$$$ Ход игрока ' + player + '! $$$$$')

    # запоминаем кто ходит изначально
    initial_player = player
    if player == player1:
        player = player2
    else:
        player = player1

    print('$$$$$ Карта для бомбардировки противника $$$$$')
    render_game_state(player)

    # логика для человека
    if not state[initial_player][is_AI]:
        msg = 'Введите координаты для удара: '
        while True:
            # принимает ответ и переводим в верхний регистр на случай, если будет введено например 1а
            player_answer = input(msg).upper()

            # для не аварийного завершения игры игрок должен вместо координат ввести команду "стоп"
            if player_answer == 'СТОП':
                return end_of_game_status

            try:
                cell = state[game][coordinates_dict][player_answer]
                if state[initial_player][battlefield][cell[0]][cell[1]] not in ['.', '*', 'X']:
                    # в случае успеха выходим из цикла
                    break
                else:
                    # пользователь ввел координаты повторно
                    msg = 'Вы уже выбирали эти координаты! Попробуйте снова: '
                    continue
            except:
                # пользователь ввел некорректный ключ
                msg = 'Вы точно ввели координаты правильно? Попробуйте снова: '
                continue

        # проверяем находится ли в ячейке корабль или часть корабля
        if state[player][game_state][cell[0]][cell[1]] > 0:
            # в случае успеха ищем корабль соперника с такими координатами
            for ship in state[player][ships]:
                for coord in ship[ship_coordinates]:
                    # в случае успеха отнимаем очки жизни у корабля
                    if coord == cell:
                        ship[health_points] -= 1
                        if ship[health_points] > 0:
                            # очки жизни еще остались, значит корабль подбит
                            state[initial_player][battlefield][cell[0]][cell[1]] = '*'
                            render_game_state(player)
                            print('Корабль ранен!')

                            # передача хода самому себе (повтор)
                            return initial_player
                        else:
                            # если корабль уничтожен по всем координатам ставим "X"
                            for _coord in ship[ship_coordinates]:
                                state[initial_player][battlefield][_coord[0]][_coord[1]] = 'X'
                            render_game_state(player)

                            # уменьшаем количество кораблей соперника
                            state[player][ships_count] -= 1
                            print('Корабль убит!')

                            # если у противника не осталось кораблей
                            if state[player][ships_count] == 0:
                                print('Выиграл ' + initial_player + '!')
                                return end_of_game_status

                            # передача хода самому себе (повтор)
                            return initial_player
        else:
            # если в ячейке было пусто
            state[initial_player][battlefield][cell[0]][cell[1]] = '.'
            render_game_state(player)
            print('Промах!')

            # передача хода сопернику
            return player
    else:
        # логика для компьютера

        # если у нас нет в очереди подозрительных для атаки точек, выбираем новую
        if len(state[game][attack_cells]) == 0:
            while True:
                random_key = random.choice(list(state[game][coordinates_dict].keys()))
                cell = state[game][coordinates_dict][random_key]

                if cell in state[game][selected_coordinates]:
                    continue
                else:
                    state[game][selected_coordinates].append(cell)
                    print('Введите координаты для удара: ' + random_key)
                    break
        else:
            # иначе берем следующую подозрительную точку и стреляем по ней
            cell = state[game][attack_cells].pop()
            state[game][selected_coordinates].append(cell)
            for k, v in state[game][coordinates_dict].items():
                if v == cell:
                    print('Введите координаты для удара: ' + k)
                    break

        # проверяем находится ли в ячейке корабль или часть корабля
        if state[player][game_state][cell[0]][cell[1]] > 0:
            # в случае успеха ищем корабль соперника с такими координатами
            for ship in state[player][ships]:
                for coord in ship[ship_coordinates]:
                    # в случае успеха отнимаем очки жизни у корабля
                    if coord == cell:
                        ship[health_points] -= 1
                        if ship[health_points] > 0:
                            # очки жизни еще остались, значит корабль подбит
                            state[initial_player][battlefield][cell[0]][cell[1]] = '*'
                            render_game_state(player)
                            print('Корабль ранен!')
                            # теперь нужно добавить подозрительные точки в очередь
                            state[game][attack_cells] = list(
                                set.union(set(state[game][attack_cells]), set(calculate_attack_cells(cell)))
                                - set(state[game][selected_coordinates]))
                            # передача хода самому себе (повтор)
                            return initial_player
                        else:
                            # если корабль уничтожен по всем координатам ставим "X"
                            for _coord in ship[ship_coordinates]:
                                state[initial_player][battlefield][_coord[0]][_coord[1]] = 'X'
                            render_game_state(player)

                            # уменьшаем количество кораблей соперника
                            state[player][ships_count] -= 1
                            print('opp ships count ' + str(state[player][ships_count]))

                            print('Корабль убит!')
                            state[game][attack_cells] = []
                            # если у противника не осталось кораблей
                            if state[player][ships_count] == 0:
                                print('Выиграл ' + initial_player + '!')
                                return end_of_game_status

                            # передача хода самому себе (повтор)
                            return initial_player
        else:
            # если в ячейке было пусто
            state[initial_player][battlefield][cell[0]][cell[1]] = '.'
            render_game_state(player)
            print('Промах!')

            # передача хода сопернику
            return player


# Функция, реализующая отрисовку поля в текущем состоянии для
# каждого игрока.
def render_game_state(player):
    # если рендерим для игрока player1, то рисуем поле боя игрока player2 и наоборот
    if player == player1:
        player = player2
    else:
        player = player1

    row = '|    | ' + ' | '.join(state[letters]) + ' |'
    print(row)
    for i in range(10):
        s = '| ' + str(i + 1) + ' |'
        if i != 9:
            s = '|  ' + str(i + 1) + ' |'

        for j in range(10):
            s += ' ' + str(state[player][battlefield][i][j]) + ' |'

        print(s)


# наполняем наш state начальными данными для дальнейшей модификации
def initialize_state():
    # игрок 1
    state[player1][game_state] = create_player_game_state()
    state[player1][battlefield] = create_player_game_state()
    state[player1][available_cells] = generate_available_cells()

    # игрок 2
    state[player2][game_state] = create_player_game_state()
    state[player2][battlefield] = create_player_game_state()
    state[player2][available_cells] = generate_available_cells()

    # игра
    state[game][coordinates_dict] = create_coordinates_dict()


# Функция, реализующая случайную расстановку всех кораблей на
# поле. Для каждого корабля, перечисленного в списке кораблей, вызываем
# функцию, реализующую случайную постановку корабля на поле.
def build_all_ships(player):
    for i in range(len(state[required_ships])):
        build_ship(state[required_ships][i], player)

    print('$$$$$ Поле игрока <' + player + '> готово! $$$$$')


# Функция, собственно реализующая игру.
def run_game():
    # инициализируем state
    initialize_state()
    # расставляем корабли для каждого игерока
    build_all_ships(player1)
    build_all_ships(player2)
    print('$$$$$ Игра проинициализирована, можно начинать! $$$$$')
    # кто будет первым ходить?
    current_player = random.choice([player1, player2])
    while True:
        current_player = move(current_player)
        if current_player == end_of_game_status:
            break

    return input('Начать игру заново? Введите 1, если согласны и любую клавишу для выхода: ')


if __name__ == '__main__':
    while True:
        ans = run_game()
        if ans == '1':
            # обновляем значения перед следующей игрой
            state[player1][ships] = []
            state[player1][ships_count] = 10

            state[player2][ships] = []
            state[player2][ships_count] = 10

            state[game][selected_coordinates] = []
            state[game][attack_cells] = []
            continue
        else:
            break
