def macroCalculator():
   fat_percent = 0.25
   protien_percent = 0.25 
   carbs_percent = 0.5

   calories = float(input ("How many calories: "))
   

   protien = calories * protien_percent
   fat = calories * fat_percent
   carbs = calories * carbs_percent
   
   
   protien_Gram = protien / 4
   fat_Gram =fat / 9
   carbs_Gram = carbs / 4 
   
   sugar_calories = 0.1 * calories
   sugar_grams = (sugar_calories / 4) / 2

   sodium = calories * (2300/2000)

   



   print("Protien Calories: ", protien," Protien Grams: ", protien_Gram)
   print("Fat Calories: ", fat, " Fat Grams: ", fat_Gram)
   print("Carbs Calories: ", carbs, " Carbs Grams: ", carbs_Gram)
   print("Sugar Calories: ", sugar_calories, "Sugar Grams: ", sugar_grams)
   print("Sodium Miligrams: ", sodium)
   print("Cholesterol Miligrams: 300", )


macroCalculator()