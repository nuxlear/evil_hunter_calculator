from typing import List, Set, Dict, Union, Iterable
from pathlib import Path
import os
import json


class Option:
    main_option_types = ('공', '공속', '방', '체', '회', '치확', '치피', '흡', '영장', '보스', '뎀증', '뎀감')
    # sub_option_types = ('보스', '언데드', '악마', '동물', '뎀증', '뎀감', '대악마', '대천사')
    sub_option_types = ()
    option_types = main_option_types + sub_option_types

    def __init__(self, option_type: str, value: int):
        assert option_type in self.option_types, f'지원하지 않는 옵션입니다: `{option_type}`'
        self.option_type = option_type
        self.value = value
    
    def is_positive(self) -> bool:
        return self.value > 0

    def copy(self):
        return Option(self.option_type, self.value)

    def update_value(self, value: int):
        assert value != 0, 'Option의 value는 0이 될 수 없습니다.'
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Option) and self.option_type == other.option_type and self.value == other.value

    def __neg__(self):
        return Option(self.option_type, -self.value)

    def __add__(self, other):
        result = self.copy()
        if isinstance(other, Option):
            assert self.option_type == other.option_type, f'다른 옵션끼리 연산할 수 없습니다: {self.option_type}와 {other.option_type}'
            result.value += other.value
        if isinstance(other, int):
            result.value += other
        return result

    def __sub__(self, other):
        return self + (-other)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        sign = '+' if self.is_positive() else ''
        return f'{self.option_type} {sign}{self.value}'

    def to_dict(self):
        return {self.option_type: self.value}


class OptionSpec:
    @staticmethod
    def from_dict(d):
        options = [Option(k, v) for k, v in d.items()]
        return OptionSpec(options)

    @staticmethod
    def _pack_options(options: Iterable[Option]) -> Dict[str, Option]:
        packed = {}
        for opt in options:
            if opt.option_type not in packed:
                packed[opt.option_type] = opt
            else:
                packed[opt.option_type] += opt
        return packed

    def __init__(self, options=None):
        if isinstance(options, OptionSpec):
            self.options = options.options.copy()
            return
        options = options or list()
        self.options = self._pack_options(options) or dict()

    def get_option(self, option_type: str):
        if option_type not in self.options:
            return None
        return self.options[option_type]

    def add_option(self, option: Option) -> bool:
        assert isinstance(option, Option), f'invalid type: {type(option).__name__} instead of `Option`'
        if option.option_type in self.options:
            return False
        self.options[option.option_type] = option
        return True

    def update_option(self, option: Option) -> bool:
        if option.option_type not in self.options:
            return False
        self.options[option.option_type] = option

    def remove_option(self, option: Option) -> bool:
        assert isinstance(option, Option), f'invalid type: {type(option).__name__} instead of `Option`'
        if option.option_type not in self.options:
            return False
        self.options.pop(option.option_type)
        return True

    def __len__(self):
        return len(self.options)

    def __iter__(self):
        return iter(self.options.values())

    def __eq__(self, other):
        return isinstance(other, OptionSpec) and self.options == other.options

    def __add__(self, other):
        assert isinstance(other, OptionSpec), 'OptionSpec은 OptionSpec끼리만 연산이 가능합니다.'
        return OptionSpec(list(self.options.values()) + list(other.options.values()))

    def __sub__(self, other):
        assert isinstance(other, OptionSpec), 'OptionSpec은 OptionSpec끼리만 연산이 가능합니다.'
        return OptionSpec(list(self.options.values()) + [-x for x in other.options.values()])

    def __repr__(self):
        s = ' / '.join(map(str, self.options.values()))
        return f'{{{s}}}'

    def to_dict(self):
        result = {}
        for opt in self.options.values():
            result.update(opt.to_dict())
        return result


class Item:
    item_types = ('모자', '갑옷', '장갑', '신발', '벨트', '반지', '무기', '목걸이')

    @staticmethod
    def from_dict(d):
        item = Item(d['item_type'])
        item.pos_options = OptionSpec.from_dict(d['positive_options'])
        item.neg_options = OptionSpec.from_dict(d['negative_options'])
        return item

    def __init__(self, item_type: str, options: Union[OptionSpec, Iterable[Option]] = None):
        assert item_type in self.item_types, f'잘못된 아이템 타입입니다: `{item_type}`'
        self.item_type = item_type

        options = options or list()
        self.pos_options = OptionSpec([opt for opt in options if opt.is_positive()])
        self.neg_options = OptionSpec([opt for opt in options if not opt.is_positive()])

    def get_spec(self) -> OptionSpec:
        return self.pos_options + self.neg_options

    def add_option(self, option: Option):
        tgt = self.pos_options if option.is_positive() else self.neg_options
        return tgt.add_option(option)

    def update_option(self, option: Option):
        tgt = self.pos_options if option.is_positive() else self.neg_options
        return tgt.update_option(option)

    def remove_option(self, option: Option):
        tgt = self.pos_options if option.is_positive() else self.neg_options
        return tgt.remove_option(option)

    def __eq__(self, other):
        return isinstance(other, Item) and \
               self.item_type == other.item_type and \
               self.pos_options == other.pos_options and \
               self.neg_options == other.neg_options

    def __repr__(self):
        pos = ' / '.join(map(str, self.pos_options))
        neg = ' / '.join(map(str, self.neg_options))
        neg = f' / {{{neg}}}' if len(self.neg_options) > 0 else ''
        return f'Item[{self.item_type}] - {{{pos}}}{neg}'

    def to_dict(self):
        return {
            'item_type': self.item_type,
            'positive_options': self.pos_options.to_dict(),
            'negative_options': self.neg_options.to_dict()
        }


class ItemSet:
    def __init__(self, items=None):
        self.items = items or list()

        item_types = set()
        for item in self.items:
            if item.item_type in item_types:
                raise ValueError(f'같은 아이템 종류는 한 가지만 들어갈 수 있습니다: {item.item_type}(이)가 중복됨.')
            item_types.add(item.item_type)
        
    def get_spec(self) -> OptionSpec:
        result = OptionSpec()
        for item in self.items:
            result += item.get_spec()
        return result

    def __repr__(self):
        stat = list(self.get_spec())
        items = ''.join([f'\n - {x}' for x in self.items])
        return f'ItemSet: {stat}{items}'

    def to_dict(self):
        return {item.item_type: item.to_dict() for item in self.items}


class ItemManager:
    def __init__(self):
        self.data_dir = Path('data')
        self.file_name = 'item.json'
        self.file_path = self.data_dir / self.file_name
        os.makedirs(self.data_dir, exist_ok=True)

        self.item_list = list()
        self.load_item()

    def load_item(self):
        if self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
            self.item_list = [Item.from_dict(d) for d in items]

    def save_item(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in self.item_list], f, ensure_ascii=False)

    def add_item(self, item: Item, write_back=True):
        self.item_list.append(item)
        if write_back:
            self.save_item()

    def pop_item(self, idx: int) -> bool:
        if not (0 <= idx < len(self.item_list)):
            return False
        self.item_list.pop(idx)
        return True

    def remove_item(self, item: Item) -> bool:
        if item not in self.item_list:
            return False
        self.item_list.remove(item)
        return True


if __name__ == '__main__':
    ops = [Option('공', 3), Option('공속', 11), Option('흡', 5)]
    item = Item('장갑', ops)
    print(item)

    item_set = ItemSet([
        Item('모자', [Option('공', 4), Option('방', 10)]),
        Item('장갑', [Option('공속', -5), Option('방', 7), Option('체', 21)]),
        Item('신발', [Option('뎀증', 15), Option('체', 7)]),
    ])
    print(item_set)
