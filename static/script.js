document.getElementById("calorie-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    
    console.log("Predict button clicked!");

    // Shift the form left
    const formSection = document.querySelector(".container form");
    formSection.classList.add("shift-left");

    // Select the result and macros sections
    const resultSection = document.getElementById("result");
    const macrosSection = document.getElementById("macros-section");

    // Animate the sections
    resultSection.classList.add("animate");
    macrosSection.classList.add("animate");

    // Simulate fetching data
    const weight = document.getElementById("weight").value;
    const gender = document.getElementById("gender").value;
    const age = document.getElementById("age").value;
    const goal_weight = document.getElementById("goal_weight").value;
    const activity_level = document.getElementById("activity_level").value;
    const duration = document.getElementById("duration").value;

    const data = {
        weight,
        gender,
        age,
        goal_weight,
        activity_level,
        duration
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Update the results section
            resultSection.innerHTML = `
                <h2>Predicted Calories: ${result.predicted_calories} kcal/day</h2>
            `;

            // Update the macros section
            macrosSection.innerHTML = `
                <h2>Macros Breakdown</h2>
                <div id="macros-result">
                        <li>
                            <span>Protein:</span> <span>${result.macros.protein_grams}g (${result.macros.protein_calories} kcal)</span>
                        </li>
                        <li>
                            <span>Fat:</span> <span>${result.macros.fat_grams}g (${result.macros.fat_calories} kcal)</span>
                        </li>
                        <li>
                            <span>Carbs:</span> <span>${result.macros.carbs_grams}g (${result.macros.carbs_calories} kcal)</span>
                        </li>
                </div>
            `;
        } else {
            resultSection.innerHTML = `Error: ${result.error}`;
        }
    } catch (error) {
        console.error("Error:", error);
        resultSection.innerHTML = "An unexpected error occurred.";
    }
});
