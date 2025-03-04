import collections
from itertools import groupby

def convert_dict_to_sorted_hand(main_dict):
    return sorted(
        [carte for carte, nb_cartes in main_dict.items() for _ in range(nb_cartes)]
    )


def convert_sorted_hand_to_dict(main_list):
    return dict(collections.Counter(main_list))

def show_super_pretty_hand(main):
    if not main:
        return ""
    return ".".join("".join(group) for _, group in groupby([mapping_card_real_game(el) for el in main]))

def mapping_card_real_game(el: int):
    return {
        0: "3",
        1: "4",
        2: "5",
        3: "6",
        4: "7",
        5: "8",
        6: "9",
        7: "10",
        8: "J",
        9: "Q",
        10: "K",
        11: "A",
        12: "2",
    }[el]


def show_pretty_pose(pose):
    return "".join([mapping_card_real_game(el) for el in pose])


if __name__ == '__main__':
    print(show_super_pretty_hand(["A", "B", "B", "A"]))