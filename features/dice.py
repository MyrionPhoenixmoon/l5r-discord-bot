import random


def roll_and_keep(command):
    rolled, kept = command[0].split("k")
    rolled = int(rolled)
    kept = int(kept)
    message = ""
    modifier = 0
    target = 0
    unskilled = False
    emphasis = False
    explode_on = [10]
    show_dice = False

    for parameter in command:
        if parameter.startswith('+') or parameter.startswith('-'):
            modifier = int(parameter[1:])
            if parameter[0] == '-':
                modifier *= -1
        if parameter.startswith('TN'):
            target = int(parameter[2:])
        if not unskilled and (parameter == "unskilled" or parameter == "Unskilled"):
            unskilled = True
        if not emphasis and (parameter == "emphasis" or parameter == "Emphasis"):
            emphasis = True
        if parameter == "mastery" or parameter == "Mastery":
            explode_on = [9, 10]
        if parameter == "show_dice":
            show_dice = True

    dice = []
    if kept <= 0:
        return 0, "You must keep at least one die!"
    if rolled <= 0:
        return 0, "You must roll at least one die!"
    if kept > rolled:
        kept = rolled
    for i in range(rolled):
        die_roll = random.randint(1, 10)
        while die_roll == 1 and emphasis:
            die_roll = random.randint(1, 10)
        die_value = die_roll
        while die_roll in explode_on and not unskilled:
            die_roll = random.randint(1, 10)
            die_value += die_roll
        dice.append(die_value)
    dice.sort(reverse=True)
    dice_to_show = dice
    dice = dice[:kept]
    result = sum(dice) + modifier
    if result < 0:
        result = 0

    if target != 0:
        if result == target:
            message = "You hit the target exactly! \n"
        else:
            if result > target:
                message = "**Success** by " + str(result - target) + "! \n"
            if result < target:
                message = "**You failed** by " + str(target - result) + "! \n"
    if show_dice:
        message += "Your dice were " + str(dice_to_show) + " and I kept " + str(dice)

    return max(result, 0), message