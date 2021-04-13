from item import *
import re


is_int = re.compile(r'^([+-]?[1-9]\d*|0)$')


def print_menu():
    print('''
---- Menu ----
1. 아이템 추가
2. 아이템 목록
3. 아이템 세팅 구성
4. 종료
--------------
''')


def add_new_item():
    item_type = input('아이템 종류: ')
    while item_type not in Item.item_types:
        item_type = input(f'잘못된 종류입니다. 다음 중 하나를 골라주세요. ({Item.item_types}): ')

    print('추가할 옵션의 옵션 종류와 수치를 한 칸 띄어 입력해주세요. (예: `공속 3`, `회 -5`)\n(빈 내용으로 Enter하면 입력을 끝냅니다.)')
    options = []
    while True:
        opt_text = input('option) ')
        if opt_text == '':
            break

        opt_info = opt_text.split()
        if len(opt_info) != 2 or opt_info[0] not in Option.option_types or not re.match(is_int, opt_info[1]):
            print('잘못된 입력입니다. 다시 입력해주세요. ')
            continue

        opt = Option(opt_info[0], int(opt_info[1]))
        options.append(opt)

    item = Item(item_type, options)
    print('아이템 등록에 성공했습니다. ')
    print(item)
    return item


def show_items(item_manager):
    def print_item_list():
        print('     <아이템 목록>     ')
        for idx, item in enumerate(item_manager.item_list):
            print(f'#{idx} {item}')

    def print_sub_menu():
        print('''--------------
1. 아이템 옵션 수정
2. 아이템 삭제
3. 돌아가기
--------------
''')

    while True:
        print_item_list()
        print_sub_menu()
        cmd = input('>>> ')
        if cmd in ['1']:
            print('준비중입니다.')
        if cmd in ['2']:
            tgt_idx = None
            while True:
                if tgt_idx is None:
                    print_item_list()
                    tgt_idx = input('아이템 ID를 입력해주세요 (# 옆의 값): ')

                if not re.match(is_int, tgt_idx):
                    tgt_idx = input('ID는 정수로 입력해주세요: ')
                    continue
                tgt_idx = int(tgt_idx)
                if not (0 <= tgt_idx < len(item_manager.item_list)):
                    tgt_idx = input('범위를 벗어나는 ID값 입니다. 다시 입력해주세요: ')
                    continue

                tgt_item = item_manager.item_list[tgt_idx]
                print(f'선택한 아이템: #{tgt_idx} {tgt_item}')

                confirm = input('해당 아이템을 삭제하시겠습니까? (y/N): ')
                while confirm not in ['', 'y', 'Y', 'n', 'N']:
                    confirm = input('잘못된 입력입니다. 다시 입력해주세요: ')
                if confirm in ['y', 'Y']:
                    item_manager.pop_item(tgt_idx)
                    print('성공적으로 삭제되었습니다. ')
                else:
                    print('취소합니다.')

                cont = input('계속 아이템을 삭제하겠습니까? [Y/n]')
                while cont not in ['', 'y', 'Y', 'n', 'N']:
                    cont = input('잘못된 입력입니다. 다시 입력해주세요: ')
                if cont not in ['', 'y', 'Y']:
                    break
                tgt_idx = None

        if cmd in ['3']:
            return


def main():
    item_manager = ItemManager()

    print('=== Evil Hunter Calculator v0.0.1 ===')
    print('Made by nuxlear - GitHub: https://github.com/nuxlear\n')

    while True:
        print_menu()
        cmd = input('>>> ')
        if cmd in ['1']:
            while True:
                item = add_new_item()
                item_manager.add_item(item)

                cont = input('계속 아이템을 추가하겠습니까? [Y/n]')
                while cont not in ['', 'y', 'Y', 'n', 'N']:
                    cont = input('잘못된 입력입니다. 다시 입력해주세요: ')
                if cont not in ['', 'y', 'Y']:
                    break

        if cmd in ['2']:
            show_items(item_manager)

        if cmd in ['4']:
            break

    print('프로그램을 종료합니다. ')


if __name__ == '__main__':
    main()
