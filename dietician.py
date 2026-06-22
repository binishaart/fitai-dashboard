def calculate_bmi(weight, height):
    return weight / (height ** 2)


def get_diet_plan(bmi):

    if bmi > 25:
        return "Weight Loss Diet: oats, salad, protein"

    elif bmi < 18.5:
        return "Weight Gain Diet: rice, milk, nuts"

    else:
        return "Maintenance Diet: balanced meals"


def run_diet():

    print("\n🥗 AI DIET COACH")

    weight = float(input("Enter weight (kg): "))
    height = float(input("Enter height (m): "))

    bmi = weight / (height ** 2)

    print(f"\nBMI: {bmi:.2f}")

    if bmi > 25:
        diet = "Rice, Milk, Nuts"
        dish = "Weight Loss Bowl"
        groceries = "Rice, Milk, Almonds, Oats, Vegetables"

    elif bmi < 18.5:
        diet = "Rice, Milk, Nuts"
        dish = "Weight Gain Shake + Meal"
        groceries = "Rice, Milk, Banana, Peanut Butter, Nuts"

    else:
        diet = "Rice, Milk, Nuts"
        dish = "Balanced Plate"
        groceries = "Rice, Milk, Eggs, Vegetables, Fruits"

    # ✅ PROPER FORMATTED OUTPUT
    print("\nDiet:", dish)
    print("\nGrocery list:", groceries)