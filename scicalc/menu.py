"""Old numbered menu (menu_main)

Module 24 of 47.  Taken from lines 7380-7937 of the original single-file calculator.py.
Every name used here is imported explicitly from the module that defines it.
"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "menu"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import CalcError
from .engine import Calculator

# ======================================================================================
#  PART 8 : THE OLD NUMBERED MENU (geometry, BMI, converters, tables ...)  -  type 'menu'
# ======================================================================================
# THE MENU PROGRAM READS EVERY NUMBER THROUGH THE CALCULATOR ENGINE, SO YOU CAN TYPE THINGS
# LIKE  3/4,  2*pi,  sin(30)  OR  2^10  WHEREVER IT ASKS FOR A (MIXED) NUMBER.
_INPUT_CALC = Calculator()      # separate from the main calculator so Ans / history stay clean


def ask(prompt, kind=3):
    """ASK FOR A NUMBER UNTIL A VALID ONE IS TYPED. kind: 1=INTEGER, 2=FLOAT, 3=MIXED (any expression)."""
    while True:
        text = input(prompt)
        try:
            if kind == 1:
                return int(text)
            if kind == 2:
                value = float(text)
                if not math.isfinite(value):
                    raise ValueError("not a finite number")
                return value
            value = _INPUT_CALC.evaluate(text).value
            return value if isinstance(value, int) else float(value)
        except (ValueError, OverflowError, CalcError):
            print("Invalid number. Please try again.")


def dim(prompt):
    """ASK FOR A LENGTH / DIMENSION (MUST BE GREATER THAN ZERO)."""
    while True:
        value = ask(prompt)
        if value > 0:
            return value
        print("Value must be greater than zero. Please try again.")


def ask_count(prompt):
    """ASK FOR HOW MANY ENTRIES (1 OR MORE)."""
    while True:
        n = ask(prompt, 1)
        if n >= 1:
            return n
        print("Please enter 1 or more. Please try again.")


def choose(prompt, valid):
    """ASK UNTIL THE ANSWER IS ONE OF THE VALID CHOICES. RETURNS IT IN LOWER CASE."""
    valid = [v.lower() for v in valid]
    while True:
        answer = input(prompt).strip().lower()
        if answer in valid:
            return answer
        print("Your input choice is invalid.\nPlease try again.")


def pick_type():
    print("1.INTEGER\n2.FLOAT\n3.MIXED")
    return int(choose("Enter your choice [1,2,3]:", ["1", "2", "3"]))


def zero(value):
    """TURN TINY FLOATING POINT NOISE (LIKE 6.1e-17) INTO EXACT 0."""
    return 0.0 if abs(value) < 1e-12 else value


def clean(value):
    """ROUND TO 12 SIGNIFICANT DIGITS SO 0.9999999999999998 SHOWS AS 1.0."""
    return float(f"{value:.12g}") + 0.0


# ====================================================================================
#  SECTION 2 : BASIC ARITHMETIC
# ====================================================================================

# THIS FUNCTION KEY WILL DO THE OPERATIONS REGARDING ADDITION.
def menu_add():
    kind = pick_type()
    n = ask_count("enter total numbers to be added:")
    total = 0
    for _ in range(n):  # pyright: ignore[reportArgumentType]
        total += ask("Enter number:", kind)
    print("Addition result=", total)


# THIS FUNCTION KEY WILL DO THE OPERATIONS REGARDING SUBTRACTION. (1ST NUMBER - 2ND NUMBER)
def menu_subtract():
    kind = pick_type()
    a = ask("Enter 1st number:", kind)
    b = ask("Enter 2nd number:", kind)
    print("Subtraction result=", a - b)


# THIS FUNCTION KEY WILL DO THE OPERATIONS REGARDING MULTIPLICATIONS.
def menu_multiply():
    kind = pick_type()
    a = ask("Enter 1st number:", kind)
    b = ask("Enter 2nd number:", kind)
    print("Multiplication result=", a * b)


# THIS FUNCTION KEY WILL DO THE OPERATIONS REGARDING DIVISION.
def menu_divide():
    kind = pick_type()
    a = ask("Enter 1st number:", kind)
    b = ask("Enter 2nd number:", kind)
    if b == 0:
        print("Division by zero is not possible.")
    else:
        print("Division result=", a / b)


# THIS FUNCTION KEY WILL DO THE OPERATIONS RELATED TO FINDING AVERAGE OF NUMBERS.
def menu_average():
    kind = pick_type()
    n = ask_count("Enter the no.of entries you want to calculate:")
    total = sum(ask("Enter the number:", kind) for _ in range(n))  # pyright: ignore[reportArgumentType]
    print("Average result=", total / n)


# THIS FUNCTION KEY WILL DO THE OPERATIONS RELATED TO FINDING PERCENTAGE OF THE GIVEN ENTRIES
# (FOR EXAMPLE MARKS OBTAINED IN DIFFERENT SUBJECTS OUT OF A TOTAL).
def menu_percentage():
    n = ask_count("Enter the no.of entries:")
    obtained = sum(ask("Enter the number:") for _ in range(n))  # pyright: ignore[reportArgumentType]
    total = ask("Enter total entity:")
    if total == 0:
        print("Total cannot be zero.")
    else:
        print("Percentage result=", (obtained / total) * 100, "%")


# THIS FUNCTION KEY WILL DO THE OPERATIONS RELATED TO FINDING FACTORIAL OF A NUMBER.
def menu_factorial():
    num = ask("Enter number to be factorialised:", 1)
    if num < 0:
        print("Factorial is not defined for negative numbers.")
    elif num > 1500:
        print("Number is too large. Please enter 1500 or less.")
    else:
        print("Factorial of", num, "is", math.factorial(num))  # pyright: ignore[reportArgumentType]


# ====================================================================================
#  SECTION 3 : GEOMETRY  (2-D SHAPES)
# ====================================================================================

def ask_triangle():
    """ASK FOR 3 SIDES AND MAKE SURE THEY CAN REALLY FORM A TRIANGLE."""
    while True:
        a = dim("Enter side1 length:")
        b = dim("Enter side2 length:")
        c = dim("Enter side3 length:")
        if a + b > c and b + c > a and a + c > b:
            return a, b, c
        print("These sides cannot form a triangle. Please enter them again.")


def heron(a, b, c):
    s = (a + b + c) / 2
    return math.sqrt(max(0.0, s * (s - a) * (s - b) * (s - c)))


SHAPES_2D = "1.SQUARE\n2.RECTANGLE\n3.CIRCLE\n4.TRIANGLE\n5.PARALLELOGRAM\n6.RHOMBUS\n7.TRAPEZIUM\n8.ELLIPSE"


# THIS FUNCTION WILL DO THE OPERATIONS RELATED TO FINDING AREA OF DIFFERENT SHAPES.
def menu_area():
    print(SHAPES_2D)
    ch = choose("Enter choice[1,2,..,8]:", list("12345678"))

    if ch == "1":
        side = dim("Enter side length:")
        name, result = "SQUARE", side * side
    elif ch == "2":
        length = dim("Enter length of rectangle:")
        width = dim("Enter width of rectangle:")
        name, result = "RECTANGLE", length * width
    elif ch == "3":
        radius = dim("Enter diameter length:") / 2
        name, result = "CIRCLE", math.pi * radius * radius
    elif ch == "4":
        base = dim("Enter base length:")
        height = dim("Enter height length:")
        name, result = "TRIANGLE", base * height / 2
    elif ch == "5":
        base = dim("Enter base length:")
        height = dim("Enter height length:")
        name, result = "PARALLELOGRAM", base * height
    elif ch == "6":
        d1 = dim("Enter 1st diagonal length:")
        d2 = dim("Enter 2nd diagonal length:")
        name, result = "RHOMBUS", d1 * d2 / 2
    elif ch == "7":
        a = dim("Enter side1 length (parallel):")
        b = dim("Enter side2 length (parallel):")
        height = dim("Enter height length:")
        name, result = "TRAPEZIUM", (a + b) * height / 2
    else:
        a = dim("Enter length of semi major axis:")
        b = dim("Enter length of semi minor axis:")
        name, result = "ELLIPSE", math.pi * a * b

    print(name, "Area result=", result, "sq.units")


# THIS FUNCTION WILL DO THE OPERATIONS RELATED TO FINDING PERIMETER OF DIFFERENT SHAPES.
def menu_perimeter():
    print(SHAPES_2D)
    ch = choose("Enter choice[1,2,..,8]:", list("12345678"))

    if ch == "1":
        name, result = "SQUARE", 4 * dim("Enter side length:")
    elif ch == "2":
        length = dim("Enter length of rectangle:")
        width = dim("Enter width of rectangle:")
        name, result = "RECTANGLE", 2 * (length + width)
    elif ch == "3":
        radius = dim("Enter diameter length:") / 2
        name, result = "CIRCLE", 2 * math.pi * radius
    elif ch == "4":
        a, b, c = ask_triangle()
        name, result = "TRIANGLE", a + b + c
    elif ch == "5":
        a = dim("Enter opposite side1 length:")
        b = dim("Enter opposite side2 length:")
        name, result = "PARALLELOGRAM", 2 * (a + b)
    elif ch == "6":
        name, result = "RHOMBUS", 4 * dim("Enter side of rhombus length:")
    elif ch == "7":
        sides = [dim(f"Enter side{i} length:") for i in range(1, 5)]
        name, result = "TRAPEZIUM", sum(sides)
    else:
        a = dim("Enter length of semi major axis:")
        b = dim("Enter length of semi minor axis:")
        # RAMANUJAN'S APPROXIMATION (VERY ACCURATE; THE EXACT PERIMETER NEEDS AN INTEGRAL).
        name = "ELLIPSE (approx.)"
        result = math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))

    print(name, "Perimeter result=", result, "units")


# ====================================================================================
#  SECTION 4 : GEOMETRY  (3-D SHAPES)
#  VOLUME, LATERAL AREA AND TOTAL AREA ALL USE THE SAME DIMENSIONS, SO ONE FUNCTION
#  (solid_properties) WORKS OUT ALL THREE AND THE MENUS BELOW JUST PICK THE ONE NEEDED.
# ====================================================================================

SHAPES_3D = "1.CUBE\n2.CUBOID\n3.CONE\n4.CYLINDER\n5.SPHERE\n6.HEMISPHERE\n7.PYRAMID\n8.PRISM"
BASE_NAMES = {"a": "SQUARE", "b": "RECTANGULAR", "c": "TRIANGULAR", "d": "PENTAGONAL", "e": "HEXAGONAL"}


def ask_height_slant(radius, what):
    """FOR CONES AND REGULAR PYRAMIDS: THE USER GIVES EITHER THE VERTICAL HEIGHT OR THE
    SLANT HEIGHT. RETURNS (VERTICAL HEIGHT, SLANT HEIGHT).  radius = DISTANCE FROM THE
    CENTRE OF THE BASE TO THE MIDDLE OF A BASE EDGE (CONE: THE RADIUS)."""
    print("1.VERTICAL HEIGHT KNOWN\n2.SLANT HEIGHT KNOWN")
    if choose("Enter choice[1,2]:", ["1", "2"]) == "1":
        height = dim(f"Enter vertical height of {what}:")
        return height, math.hypot(height, radius)
    while True:
        slant = dim(f"Enter slant height of {what}:")
        if slant > radius:
            return math.sqrt(slant * slant - radius * radius), slant
        print("Slant height must be greater than", radius, "for this base. Please try again.")


def ask_base(letter):
    """ASK FOR THE BASE OF A PYRAMID OR PRISM. RETURNS ITS AREA, PERIMETER AND 'inr'
    (DISTANCE FROM CENTRE TO THE MIDDLE OF A SIDE, NEEDED FOR PYRAMID SLANT HEIGHTS)."""
    if letter == "a":
        s = dim("Enter side length of base:")
        return {"area": s * s, "perim": 4 * s, "inr": s / 2}
    if letter == "b":
        length = dim("Enter length of base:")
        width = dim("Enter width of base:")
        return {"area": length * width, "perim": 2 * (length + width), "inr": None, "lw": (length, width)}
    if letter == "c":
        a, b, c = ask_triangle()
        base_area = heron(a, b, c)
        perim = a + b + c
        return {"area": base_area, "perim": perim, "inr": 2 * base_area / perim}
    n = 5 if letter == "d" else 6          # REGULAR PENTAGON OR HEXAGON
    s = dim("Enter side length of base:")
    t = math.tan(math.pi / n)
    return {"area": n * s * s / (4 * t), "perim": n * s, "inr": s / (2 * t)}


def pyramid_height_and_lateral(base):
    """RETURNS (VERTICAL HEIGHT, LATERAL SURFACE AREA) OF A RIGHT PYRAMID."""
    if base["inr"] is None:                # RECTANGULAR BASE: TWO DIFFERENT SLANT HEIGHTS
        length, width = base["lw"]
        height = dim("Enter height of pyramid:")
        lateral = length * math.hypot(height, width / 2) + width * math.hypot(height, length / 2)
        return height, lateral
    height, slant = ask_height_slant(base["inr"], "pyramid")
    return height, base["perim"] * slant / 2


def solid_properties(ch):
    """ASK FOR THE DIMENSIONS OF A 3-D SHAPE AND RETURN (NAME, VOLUME, LATERAL AREA, TOTAL AREA)."""
    if ch == "1":
        s = dim("Enter side length of cube:")
        return "CUBE", s ** 3, 4 * s * s, 6 * s * s
    if ch == "2":
        length = dim("Enter length of cuboid:")
        width = dim("Enter width of cuboid:")
        height = dim("Enter height of cuboid:")
        return ("CUBOID", length * width * height, 2 * height * (length + width),
                2 * (length * width + width * height + length * height))

    if ch in ("3", "4", "5", "6"):
        r = dim("Enter diameter length:") / 2
        if ch == "3":
            height, slant = ask_height_slant(r, "cone")
            return "CONE", math.pi * r * r * height / 3, math.pi * r * slant, math.pi * r * (slant + r)
        if ch == "4":
            height = dim("Enter height length:")
            return "CYLINDER", math.pi * r * r * height, 2 * math.pi * r * height, 2 * math.pi * r * (r + height)
        if ch == "5":     # A SPHERE HAS ONLY A CURVED SURFACE, SO LATERAL = TOTAL
            return "SPHERE", 4 / 3 * math.pi * r ** 3, 4 * math.pi * r * r, 4 * math.pi * r * r
        return "HEMISPHERE", 2 / 3 * math.pi * r ** 3, 2 * math.pi * r * r, 3 * math.pi * r * r

    solid = "PYRAMID" if ch == "7" else "PRISM"
    print(solid, "OPERATIONS")
    for letter, name in BASE_NAMES.items():
        print(f"{letter}.{name} {solid}")
    letter = choose("Enter choice[a,b,c,d,e]:", list("abcde"))
    base = ask_base(letter)
    name = f"{BASE_NAMES[letter]} {solid}"
    if ch == "7":
        height, lateral = pyramid_height_and_lateral(base)
        return name, base["area"] * height / 3, lateral, base["area"] + lateral
    height = dim("Enter height of prism:")
    return name, base["area"] * height, base["perim"] * height, 2 * base["area"] + base["perim"] * height


# THIS FUNCTION WILL DO THE OPERATIONS RELATED TO FINDING VOLUME OF DIFFERENT SHAPES.
def menu_volume():
    print(SHAPES_3D)
    ch = choose("Enter choice[1,2,..,8]:", list("12345678"))
    name, vol, _, _ = solid_properties(ch)
    print(name, "Volume result=", vol, "cu.units")


# THIS FUNCTION WILL DO THE OPERATIONS RELATED TO FINDING LATERAL SURFACE AREAS OF 3-D SHAPES.
def menu_lateral_surface_area():
    print("LATERAL SURFACE AREA OPERATIONS")
    print(SHAPES_3D)
    ch = choose("Enter choice[1,2,..,8]:", list("12345678"))
    name, _, lateral, _ = solid_properties(ch)
    print(name, "LATERAL SURFACE AREA result=", lateral, "sq.units")


# THIS FUNCTION WILL DO THE OPERATIONS RELATED TO FINDING TOTAL SURFACE AREA OF DIFFERENT SHAPES.
def menu_total_surface_area():
    print("TOTAL SURFACE AREA OPERATIONS")
    print(SHAPES_3D)
    ch = choose("Enter choice[1,2,..,8]:", list("12345678"))
    name, _, _, total = solid_properties(ch)
    print(name, "TOTAL SURFACE AREA result=", total, "sq.units")


# ====================================================================================
#  SECTION 5 : CONVERTERS, TABLES AND TRIGONOMETRY
# ====================================================================================

# (TITLE, NAME OF GIVEN UNIT, GIVEN -> CELSIUS, CELSIUS -> ANSWER)
TEMPERATURE = {
    "a": ("CELSIUS TO KELVIN", "celsius", lambda x: x, lambda c: c + 273.15),
    "b": ("KELVIN TO CELSIUS", "kelvin", lambda x: x - 273.15, lambda c: c),
    "c": ("FAHRENHEIT TO CELSIUS", "fahrenheit", lambda x: (x - 32) * 5 / 9, lambda c: c),
    "d": ("CELSIUS TO FAHRENHEIT", "celsius", lambda x: x, lambda c: c * 9 / 5 + 32),
    "e": ("FAHRENHEIT TO KELVIN", "fahrenheit", lambda x: (x - 32) * 5 / 9, lambda c: c + 273.15),
    "f": ("KELVIN TO FAHRENHEIT", "kelvin", lambda x: x - 273.15, lambda c: c * 9 / 5 + 32),
}


# THIS FUNCTION WILL CONVERT ONE TEMPERATURE READING TO ANOTHER TEMPERATURE UNIT.
def menu_temp_converter():
    print("TEMPERATURE CONVERSION OPERATIONS")
    print("a.CELSIUS TO KELVIN\nb.KELVIN TO CELSIUS\nc.FAHRENHEIT TO CELSIUS\n"
          "d.CELSIUS TO FAHRENHEIT\ne.FAHRENHEIT TO KELVIN\nf.KELVIN TO FAHRENHEIT")
    ch = choose("Enter choice[a,b,c,d,e,f]:", list("abcdef"))
    title, unit, to_celsius, from_celsius = TEMPERATURE[ch]
    given = ask(f"Enter {unit} temperature:")
    celsius = to_celsius(given)
    if celsius < -273.15 - 1e-9:
        print("That is below absolute zero (-273.15 C), which is not possible.")
    else:
        print(title, "result=", from_celsius(celsius))


# THIS FUNCTION WILL GENERATE THE MULTIPLICATION TABLE OF A NUMBER.
def menu_table_generator():
    num = ask("Enter number to generate table:")
    for i in range(1, 11):
        product = num * i
        if isinstance(product, float):
            product = round(product, 10)
        print(num, "x", i, "=", product)


# THIS FUNCTION WILL CONVERT DEGREE VALUE TO ITS RADIAN VALUE.
def menu_deg_rad():
    value = ask("enter degree value:")
    print("DEGREE TO RADIAN result=", math.radians(value))


# THIS FUNCTION WILL CONVERT RADIAN VALUE TO DEGREE VALUE.
def menu_rad_deg():
    value = ask("enter radian value (you can type things like pi/2):")
    print("RADIAN TO DEGREE result=", math.degrees(value))


# THIS FUNCTION WILL HELP YOU WITH FINDING DIFFERENT THETA VALUES IN TRIGONOMETRY.
def menu_theta_value():
    degree = ask("enter the degree value:")
    print("1.sin\n2.cos\n3.tan\n4.cot\n5.sec\n6.cosec")
    option = choose("choice{1,2....,6}:", list("123456"))

    radian = math.radians(degree)
    s = zero(math.sin(radian))
    c = zero(math.cos(radian))
    # None MEANS THE VALUE IS UNDEFINED (DIVISION BY ZERO), E.g. tan(90) OR cot(0).
    table = {
        "1": ("sin", s),
        "2": ("cos", c),
        "3": ("tan", s / c if c else None),
        "4": ("cot", c / s if s else None),
        "5": ("sec", 1 / c if c else None),
        "6": ("cosec", 1 / s if s else None),
    }
    name, value = table[option]
    shown = "UNDEFINED" if value is None else clean(value)
    print("THE VALUE OF", name, "(", degree, ")", "IS =", shown)


# ====================================================================================
#  SECTION 6 : EVERYDAY CALCULATIONS
# ====================================================================================

# THIS FUNCTION WILL DO THE OPERATIONS RELATED TO FINDING SPEED, TIME AND DISTANCE.
def menu_minor_opns():
    print("1.SPEED USING DISTANCE & TIME\n2.DISTANCE USING SPEED & TIME\n3.TIME USING SPEED & DISTANCE")
    ch = choose("enter your choice[1,2,3]:", ["1", "2", "3"])
    if ch == "1":
        distance = dim("enter distance:")
        time = dim("enter time period taken:")
        print("SPEED=", distance / time)
    elif ch == "2":
        speed = dim("enter speed:")
        time = dim("enter time period taken:")
        print("DISTANCE=", speed * time)
    else:
        distance = dim("enter distance:")
        speed = dim("enter total speed:")
        print("TIME=", distance / speed)


# IF YOU WANT TO CALCULATE YOUR BMI VALUE THEN THIS FUNCTION WILL HELP YOU.
def menu_bmi():
    print("FOR CALCULATING YOUR BMI SOME DATAS ARE REQUIRED. SO PROCEEDING TO COLLECT DATAS................")
    weight = dim("Enter your weight in kg :")
    print("1.HEIGHT IN METRES\n2.HEIGHT IN CENTIMETRES")
    unit = choose("Enter choice[1,2]:", ["1", "2"])
    if unit == "1":
        height = dim("Enter your height in metres :")
    else:
        height = dim("Enter your height in centimetres :") / 100
    value = weight / (height * height)
    print("Your BMI is :", round(value, 2))
    # WORLD HEALTH ORGANIZATION ADULT CATEGORIES
    if value < 18.5:
        print("Category : Underweight")
    elif value < 25:
        print("Category : Normal weight")
    elif value < 30:
        print("Category : Overweight")
    else:
        print("Category : Obese")


# IF YOU DON'T KNOW THE VALUES OF DIFFERENT CONSTANTS THEN THIS FUNCTION WILL HELP YOU.
def menu_values():
    print("HERE ARE THE LIST OF SOME CONSTANTS WHOSE VALUES ARE LISTED BELOW......")
    print("---------------------------------------------------------------------------")
    print("Speed of Light [c] = 2.998 x 10^8 m/s")
    print("Planck's Constant [h] = 6.626 x 10^-34 Js = 4.136 x 10^-15 eV.s")
    print("Gravitation Constant [G] = 6.674 x 10^-11 m^3 kg^-1 s^-2")
    print("Boltzmann Constant [k] = 1.381 x 10^-23 J/K")
    print("Molar gas Constant [R] = 8.314 J/(mol.K)")
    print("Avogadro's Number [NA] = 6.022 x 10^23 /mol")
    print("Charge of Electron [e] = 1.602 x 10^-19 C")
    print("Permittivity of Vacuum [ε0] = 8.854 x 10^-12 F/m")
    print("Coulomb Constant [1/4.pi.ε0] = 8.988 x 10^9 N m^2/C^2 (about 9 x 10^9)")
    print("Faraday Constant [F] = 96485 C/mol")
    print("Mass of Electron [Me] = 9.109 x 10^-31 kg")
    print("Mass of Proton [Mp] = 1.6726 x 10^-27 kg")
    print("Mass of Neutron [Mn] = 1.6749 x 10^-27 kg")
    print("Stefan-Boltzmann Constant [σ] = 5.670 x 10^-8 W/(m^2.K^4)")
    print("Rydberg Constant [R∞] = 1.097 x 10^7 m^-1")
    print("Bohr Magneton [µB] = 9.274 x 10^-24 J/T")
    print("Bohr Radius [a0] = 0.529 x 10^-10 m")
    print("Standard Atmospheric Pressure [atm] = 1.01325 x 10^5 Pa")
    print("Wien Displacement Constant [b] = 2.898 x 10^-3 mK")
    print("Average Velocity [Vavg] = Δx/Δt  (Δx = displacement, Δt = elapsed time)")
    print("Average Velocity, constant acceleration [Vavg] = (Vi + Vf)/2")
    print("---------------------------------------------------------------------------")


# THIS FUNCTION WILL DO THE OPERATION RELATED TO FINDING SQUARE ROOT OF A GIVEN NUMBER.
def menu_roots():
    number = ask("Enter a number for finding root value:")
    if number >= 0:
        print("Your resultant square root of the given input number is ", math.sqrt(number))
    else:
        print("The square root of a negative number is imaginary: ±", f"{math.sqrt(-number)}i")


# ====================================================================================
#  SECTION 7 : MAIN PROGRAM
# ====================================================================================

MENU_ITEMS = [
    ("ADDITION", menu_add), ("SUBTRACTION", menu_subtract), ("MULTIPLICATION", menu_multiply),
    ("DIVISION", menu_divide), ("AVERAGE", menu_average), ("PERCENTAGE", menu_percentage),
    ("FACTORIAL", menu_factorial), ("AREA", menu_area), ("PERIMETER", menu_perimeter),
    ("VOLUME", menu_volume), ("LATERAL SURFACE AREA", menu_lateral_surface_area),
    ("TOTAL SURFACE AREA", menu_total_surface_area), ("TEMPERATURE CONVERTER", menu_temp_converter),
    ("TABLE GENERATOR", menu_table_generator), ("DEGREE TO RADIAN", menu_deg_rad),
    ("RADIAN TO DEGREE", menu_rad_deg), ("THETA VALUE OPERATION", menu_theta_value),
    ("MINOR OPERATIONS", menu_minor_opns), ("BMI CALCULATION", menu_bmi),
    ("CONSTANTS & FORMULAS", menu_values), ("SQUARE ROOT", menu_roots),
]


def menu_main():
    print("####----CALCULATION----OPERATIONS----####")
    print("WELCOME TO THE WORLD OF CALCULATION WHERE IT MAKES YOUR LIFE EASIER.")
    try:
        while True:
            print("CHOOSE ONE OF THESE WHICH YOU WANT TO DO!")
            for number, (title, _) in enumerate(MENU_ITEMS, start=1):
                print(f"{number:>2}.{title:<26}", end="\n" if number % 3 == 0 else "")
            choice = choose(f"Enter choice[1,2,3,......,{len(MENU_ITEMS)}]:",
                            [str(i) for i in range(1, len(MENU_ITEMS) + 1)])
            MENU_ITEMS[int(choice) - 1][1]()
            print("CALCULATION SUCCESSFUL. THANK YOU......................")

            print("DO YOU WANT TO CONTINUE FURTHER?\nIF THEN...........")
            if choose("CHOOSE[y/n/Y/N]:", ["y", "n"]) == "n":
                break
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")
