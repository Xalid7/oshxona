document.addEventListener("DOMContentLoaded", () => {
    const serveMealForm = document.getElementById("serveMealForm");
    const serveMealSelect = document.getElementById("serveMealSelect");
    const serveMessage = document.getElementById("serveMessage");
    const portionTableBody = document.getElementById("portionTableBody");

    // 1. Ovqatlar ro'yxatini yuklash
    function loadMealOptions() {
        fetch("/api/meals/")
            .then(res => res.json())
            .then(data => {
                serveMealSelect.innerHTML = "";
                data.forEach(meal => {
                    const option = document.createElement("option");
                    option.value = meal.id;
                    option.textContent = meal.name;
                    serveMealSelect.appendChild(option);
                });
            });
    }

    // 2. Ovqat berish formasi yuborilganda
    serveMealForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const mealId = serveMealSelect.value;

        fetch("/api/serve-meal/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ meal_id: mealId })
        })
        .then(res => res.json().then(data => ({ status: res.status, data })))
        .then(({ status, data }) => {
            serveMessage.classList.remove("d-none", "alert-danger", "alert-success");

            if (status === 200) {
                serveMessage.classList.add("alert-success");
                serveMessage.textContent = "✅ Ovqat muvaffaqiyatli berildi!";
                updatePortionTable(); // yangilash
            } else {
                serveMessage.classList.add("alert-danger");
                serveMessage.textContent = "❌ Xatolik: " + (data.detail || "Ingredient yetarli emas");
            }
        })
        .catch(err => {
            serveMessage.classList.remove("d-none");
            serveMessage.classList.add("alert-danger");
            serveMessage.textContent = "❌ Tarmoq xatosi: " + err.message;
        });
    });

    // 3. Porsiyalar jadvalini yangilash
    function updatePortionTable() {
        fetch("/api/meal-portions/")
            .then(res => res.json())
            .then(data => {
                portionTableBody.innerHTML = "";
                data.forEach(item => {
                    const row = `
                        <tr>
                            <td>${item.meal_name}</td>
                            <td>${item.portions}</td>
                        </tr>`;
                    portionTableBody.innerHTML += row;
                });
            });
    }

    // Boshlanishida yuklab qo'yish
    loadMealOptions();
    updatePortionTable();
});
