#installing dependencies
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np
import joblib
import os
import pandas as pd
import seaborn as sns

data = pd.read_csv("/Users/ronavpoonekar/Documents/GitHub/AWSFitnes/weight_change_dataset.csv")


#Preprocessing
train = data.drop(['Daily Calories Consumed', 'Sleep Quality', 'BMR (Calories)', 'Weight Change (lbs)', 'Stress Level', 'Participant ID'], axis=1, errors='ignore')
test_calories = data['Daily Calories Consumed']


train['Gender'] = train['Gender'].map({'M': 1, 'F': 0})


activity_level_mapping = {
    'sedentary': 0,
    'lightly active': 1,
    'moderately active': 2,
    'very active': 3 
}


#generalize the string so that whatever caps, etc . 
train['Physical Activity Level'] = train['Physical Activity Level'].str.strip().str.lower().map({'sedentary': 0,'lightly active': 1,'moderately active': 2,'very active': 3})

#makes sure there are no unmapped values
#if train['Physical Activity Level'].isnull().any():
    #raise ValueError("Some activity levels in the dataset could not be mapped. Please check the dataset.")

required_features = ['Current Weight (lbs)', 'Gender', 'Age', 'Final Weight (lbs)', 'Physical Activity Level', 'Duration (weeks)']

# Handle column names dynamically
numerical_features = [col for col in required_features if col in train.columns]


if not numerical_features:
    raise ValueError("No valid numerical features found in the dataset!")


scaler = StandardScaler()
train[numerical_features] = scaler.fit_transform(train[numerical_features])

print(f"Numerical features used for training: {numerical_features}")

#print("Columns in training data:", train.columns)
#print("First few rows of training data:")
#print(train.head())



#Predict Daily Calories Consumed
X_train_calories, X_test_calories, y_train_calories, y_test_calories = train_test_split(train[numerical_features], test_calories, test_size=0.3, random_state=2)

regr_calories = LinearRegression()
regr_calories.fit(X_train_calories, y_train_calories)
pred_calories = regr_calories.predict(X_test_calories)

#print("Predicted Daily Calories Consumed:", pred_calories)
#print(regr_calories.score(X_test_calories, y_test_calories))


def predict_daily_calories():
    # Collect user input
    try:
        weight = float(input("Enter Weight (lbs): "))
        gender = input("Enter Gender (M/F): ").strip().upper()
        age = int(input("Enter Age: "))
        goal_weight = float(input("Enter Goal Weight (lbs): "))
        activity_level = input("Enter Physical Activity Level (Sedentary, Lightly Active, Moderately Active , Very Active): ").strip().lower()
        duration = int(input("How fast do you want to get to your final weight: "))
         # Debugging user input
        print(f"User-entered activity level: '{activity_level}'")

        # Preprocess inputs
        gender_encoded = 1 if gender == 'M' else 0
        activity_level_encoded = activity_level_mapping.get(activity_level, -1)

        # Debugging mapping
        #print(f"Mapped activity level: {activity_level_encoded}")

        if activity_level_encoded == -1:
            raise ValueError(f"Unrecognized Physical Activity Level: {activity_level}")
        # Normalize inputs using the same scaler as during training
        
        # Create input data as a DataFrame with column names
        input_data = pd.DataFrame(
            [[weight, gender_encoded, age,  goal_weight, activity_level_encoded, duration]],
            columns=numerical_features  # Match training feature names
        )

        # Normalize inputs using the same scaler as during training
        input_data_scaled = scaler.transform(input_data)
        
        #input_data = np.array([[weight, age, goal_weight, activity_level_encoded, duration]])
       #input_data_scaled = scaler.transform(input_data)

        # Make prediction
        predicted_calories = regr_calories.predict(input_data_scaled)
        print(f"Predicted Daily Calories Consumed: {predicted_calories[0]:.2f} kcal")
    except Exception as e:
        print(f"Error: {e}")

# Call the function to test
predict_daily_calories()




# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to save the model
model_path = os.path.join(current_dir, 'model.pkl')
joblib.dump(regr_calories, model_path)


scaler_path = os.path.join(current_dir, 'scaler.pkl')
joblib.dump(scaler, scaler_path)


