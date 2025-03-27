import collections
from itertools import groupby

DIC_REAL_GAME = {
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
    }

def convert_dict_to_sorted_hand(main_dict):
    return sorted(
        [carte for carte, nb_cartes in main_dict.items() for _ in range(nb_cartes)]
    )


def convert_sorted_hand_to_dict(main_list):
    return dict(collections.Counter(main_list))

def show_super_pretty_hand(main):
    if not main:
        return ""
    return ".".join("".join(group) for _, group in groupby([DIC_REAL_GAME[el] for el in main]))

def pretty_actions_jouees(actions_jouees):
    if not actions_jouees:
        return ""
    dic_actions_jouees = mapping_actions_jouees()
    return ".".join("".join(group) for _, group in groupby([dic_actions_jouees[el] for el in actions_jouees]))

def mapping_actions_jouees() -> dict[str, str]:
    # Actions spéciales : Passe, Saut, Triche
    dic_actions_speciales = {el: el for el in ["P", "S", "T"]}
    dic_actions_speciales.update({str(el): val for el, val in DIC_REAL_GAME.items()})
    return dic_actions_speciales


def show_pretty_pose(pose):
    return "".join([DIC_REAL_GAME[el] for el in pose])


if __name__ == '__main__':
    print(show_super_pretty_hand(["A", "B", "B", "A"]))