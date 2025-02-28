import enum


class ItemClassification(enum.Flag):
    unknown = 0
    trap = 1
    filler = 2
    useful = 4
    progression = 8
    mcguffin = 16
